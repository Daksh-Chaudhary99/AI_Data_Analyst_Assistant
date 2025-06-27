from dotenv import load_dotenv
load_dotenv() 
import os
import chromadb
import re
import logging 
from sqlalchemy import create_engine
from uuid import uuid4 
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.nebius import NebiusEmbedding
from llama_index.core import SQLDatabase
from llama_index.core.schema import TextNode 

# Configure logging
logging.basicConfig(level=logging.INFO) 

# --- Configuration ---
DATABASE_PATH = os.path.join('data', 'sales_database.db')

# CORRECTED PATHS based on your clarification:
# schema is under knowledge_base
SCHEMA_DIR = os.path.join('knowledge_base', 'schema') 
DATA_DICTIONARY_PATH = os.path.join(SCHEMA_DIR, 'data_dictionary.md') 
SALES_SCHEMA_SQL_PATH = os.path.join(SCHEMA_DIR, 'sales_schema.sql') 

# kpi_definitions.md is under business_glossary
KPI_DEFINITIONS_PATH = os.path.join('knowledge_base', 'business_glossary', 'kpi_definitions.md') 

CHROMA_DB_SCHEMA_PATH = os.path.join('.', 'chroma_db_schema') 
CHROMA_DB_KPI_PATH = os.path.join('.', 'chroma_db_kpi') 

# Ensure NEBIUS_API_KEY is set
if "NEBIUS_API_KEY" not in os.environ:
    logging.critical("NEBIUS_API_KEY environment variable not set. Please set it before running this script.")
    raise ValueError("NEBIUS_API_KEY environment variable not set. Please set it before running this script.")

# --- Initialize Nebius AI Embedding Model (Global for consistency) ---
print("\n--- Initializing Nebius AI Embedding Model ---")
try:
    embed_model = NebiusEmbedding(
        api_key=os.environ["NEBIUS_API_KEY"], 
        model_name="BAAI/bge-en-icl", # Consistent with schema_retriever_tool for now
        api_base="https://api.studio.nebius.com/v1/" # Verify this base URL is correct for the model
    )
    test_string = "This is a test string to generate an embedding for diagnostic purposes."
    test_embedding = embed_model.get_text_embedding(test_string)
    
    if test_embedding is None or not isinstance(test_embedding, list) or not all(isinstance(x, (int, float)) for x in test_embedding):
        logging.critical(f"FATAL ERROR: NebiusEmbedding returned invalid output for test string. Type: {type(test_embedding)}, Value: {test_embedding[:10] if isinstance(test_embedding, list) else test_embedding}")
        raise ValueError("NebiusEmbedding test failed: returned invalid embedding. Cannot proceed with RAG index creation.")
    
    logging.info(f"Nebius AI Embedding Model initialized and tested successfully. Embedding length: {len(test_embedding)}")

except Exception as e:
    logging.critical(f"UNRECOVERABLE ERROR during Nebius AI Embedding Model initialization or testing: {e}")
    print(f"\n!!!! UNRECOVERABLE ERROR: {e} !!!!") 
    print("Please check your NEBIUS_API_KEY, model_name, and api_base configuration carefully.")
    raise 

print("--- Nebius AI Embedding Model setup complete. Proceeding to Knowledge Base setup. ---")

# --- Helper Function to parse Data Dictionary ---
def parse_data_dictionary_md(md_path: str) -> dict:
    table_descriptions = {}
    if not os.path.exists(md_path):
        logging.error(f"Data dictionary file not found: {md_path}")
        return {} 

    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    table_headers = re.finditer(r'## Table: `(\w+)`\n\*\*Purpose:\*\* (.+?)(?=\n## Table: `|\Z)', content, re.DOTALL)

    for match in table_headers:
        table_name = match.group(1).strip()
        purpose = match.group(2).strip()
        table_descriptions[table_name] = purpose
        logging.info(f"Parsed table: {table_name}, Purpose length: {len(purpose)}")

    return table_descriptions

# --- Setup for Schema Retriever Agent's Knowledge Base ---
print("\n--- Setting up Schema Retriever Agent's Knowledge Base (chroma_db_schema) ---")
try:
    data_dict_descriptions = parse_data_dictionary_md(DATA_DICTIONARY_PATH)
    logging.info(f"Loaded descriptions for {len(data_dict_descriptions)} tables from data_dictionary.md")

    engine = create_engine(f"sqlite:///{DATABASE_PATH}")
    sql_database = SQLDatabase(engine)
    logging.info(f"Connected to database: {DATABASE_PATH}")

    all_table_names = sql_database.get_usable_table_names()
    
    schema_nodes = [] 
    if not all_table_names:
        logging.warning("WARNING: No tables found in the database. Schema KB will be empty.")
    
    for table_name in all_table_names:
        ddl = sql_database.get_single_table_info(table_name)
        human_description = data_dict_descriptions.get(table_name, "No specific description available for this table.")
        
        combined_context = f"Table Name: {table_name}\n" \
                           f"Description: {human_description}\n" \
                           f"Table Schema (DDL):\n{ddl if ddl else ''}"
        
        node_embedding = embed_model.get_text_embedding(combined_context)
        if node_embedding is None:
            raise ValueError(f"Failed to generate embedding for schema table: {table_name}")

        # Adding a simple metadata dictionary
        schema_nodes.append(TextNode(text=combined_context, embedding=node_embedding, id_=table_name, metadata={"table_name": table_name, "source": "data_dictionary"})) 
        
    chroma_client_schema = chromadb.PersistentClient(path=CHROMA_DB_SCHEMA_PATH)
    chroma_collection_schema = chroma_client_schema.get_or_create_collection(name="schema_kb")

    if chroma_collection_schema.count() > 0:
        logging.info(f"Clearing {chroma_collection_schema.count()} existing items from schema_kb before re-indexing.")
        chroma_collection_schema.delete(ids=[id_ for id_ in chroma_collection_schema.get()['ids']])


    logging.info(f"Adding {len(schema_nodes)} schema nodes to ChromaDB directly...")
    if schema_nodes:
        chroma_collection_schema.add(
            documents=[node.text for node in schema_nodes],
            embeddings=[node.embedding for node in schema_nodes],
            # Pass non-empty metadata dict for each node
            metadatas=[node.metadata for node in schema_nodes], 
            ids=[node.id_ for node in schema_nodes]
        )
    logging.info(f"Schema knowledge base indexed and persisted to {CHROMA_DB_SCHEMA_PATH}")
except Exception as e:
    logging.exception("Error setting up Schema KB:") 
    print(f"Error setting up Schema KB: {e}") 
    print("Please ensure your database is created and accessible and data_dictionary.md is correctly formatted.")
    print("If the error persists, there might be a deeper compatibility issue. See above for more detailed embedding checks.")
    raise 


# --- Setup for KPI Answering Agent's Knowledge Base (kpi_definitions.md) ---
print("\n--- Setting up KPI Answering Agent's Knowledge Base (chroma_db_kpi) ---")
try:
    kpi_docs = SimpleDirectoryReader(input_files=[KPI_DEFINITIONS_PATH]).load_data()
    logging.info(f"Loaded {len(kpi_docs)} documents for KPI Agent.")

    kpi_nodes = []
    for doc in kpi_docs:
        node_embedding = embed_model.get_text_embedding(doc.get_content())
        if node_embedding is None:
            raise ValueError(f"Failed to generate embedding for KPI document: {doc.id_}")
        # Adding a simple metadata dictionary
        kpi_nodes.append(TextNode(text=doc.get_content(), embedding=node_embedding, id_=str(uuid4()), metadata={"source_file": os.path.basename(KPI_DEFINITIONS_PATH), "doc_type": "kpi_definition"}))
    
    chroma_client_kpi = chromadb.PersistentClient(path=CHROMA_DB_KPI_PATH)
    chroma_collection_kpi = chroma_client_kpi.get_or_create_collection(name="kpi_kb")

    if chroma_collection_kpi.count() > 0:
        logging.info(f"Clearing {chroma_collection_kpi.count()} existing items from kpi_kb before re-indexing.")
        chroma_collection_kpi.delete(ids=[id_ for id_ in chroma_collection_kpi.get()['ids']])

    logging.info(f"Adding {len(kpi_nodes)} KPI nodes to ChromaDB directly...")
    if kpi_nodes:
        chroma_collection_kpi.add(
            documents=[node.text for node in kpi_nodes],
            embeddings=[node.embedding for node in kpi_nodes],
            # Pass non-empty metadata dict for each node
            metadatas=[node.metadata for node in kpi_nodes], 
            ids=[node.id_ for node in kpi_nodes]
        )
    logging.info(f"KPI knowledge base indexed and persisted to {CHROMA_DB_KPI_PATH}")
except Exception as e:
    logging.exception("Error setting up KPI KB:") 
    print(f"Error setting up KPI KB: {e}") 
    print("Please ensure your 'kpi_definitions.md' file exists and contains valid text content.")
    print("If the error persists, there might be a deeper compatibility issue. See above for more detailed embedding checks.")
    raise 


print("\nKnowledge base setup complete for RAG agents!")
print(f"Indices are saved in '{CHROMA_DB_SCHEMA_PATH}' and '{CHROMA_DB_KPI_PATH}' directories.")