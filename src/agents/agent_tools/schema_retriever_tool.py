# src/agents/tools/schema_retriever_tool.py

import os
import logging
import chromadb
from llama_index.core.tools import FunctionTool
from llama_index.embeddings.nebius import NebiusEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import VectorStoreIndex, Settings 

logging.basicConfig(level=logging.INFO)

# Define the path to your ChromaDB for schema.
current_file_dir = os.path.dirname(os.path.abspath(__file__))
# Navigate up to the project root for the ChromaDB directory
# This path is relative to the *tool file*, so three levels up to the root.
CHROMA_DB_PATH = os.path.join(current_file_dir, '..', '..', '..', 'chroma_db_schema')
logging.info(f"ChromaDB Schema Path set to: {CHROMA_DB_PATH}")

# Initialize NebiusEmbedding
embed_model_name = "BAAI/bge-en-icl" 
embed_api_base = "https://api.studio.nebius.com/v1/" 

embeddings = None
try:
    embeddings = NebiusEmbedding(
        api_key=os.environ.get("NEBIUS_API_KEY"),
        model_name=embed_model_name,
        api_base=embed_api_base
    )
    Settings.embed_model = embeddings
    # Test the embedding model
    _ = embeddings.get_text_embedding("test validation string") 
    logging.info("NebiusEmbedding initialized successfully for schema retriever.")
except Exception as e:
    logging.error(f"Error initializing NebiusEmbedding in schema_retriever_tool: {e}")
    embeddings = None

# Set the global embedding model for LlamaIndex if not already set (good practice)
if embeddings:
    Settings.embed_model = embeddings

# Main retrieval function
def retrieve_schema_context(natural_language_query: str) -> str:
    if embeddings is None: 
        return "Error: Embedding model not initialized for schema retrieval. Cannot perform RAG. Please check your Nebius API key and model configuration."
        
    try:
        db = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        chroma_collection = db.get_or_create_collection(name="schema_kb") 
        logging.info(f"ChromaDB collection 'schema_kb' opened successfully for retrieval.")

        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

        index = VectorStoreIndex.from_vector_store(
            vector_store, 
            embed_model=embeddings # Explicitly pass the initialized embeddings
        )
        query_engine = index.as_retriever(similarity_top_k=2) 
        retrieved_nodes = query_engine.retrieve(natural_language_query)

        schema_snippets = [node.get_content() for node in retrieved_nodes]
        if not schema_snippets:
            return "No relevant schema context found for your query. Please rephrase or simplify."

        return "Retrieved Database Schema Context (relevant to query):\n" + "\n---\n".join(schema_snippets)

    except Exception as e:
        logging.exception("Error in retrieve_schema_context:") 
        return f"Error retrieving schema from RAG: {str(e)}. Ensure ChromaDB is built at {CHROMA_DB_PATH} and embedding model is compatible."


# Exportable tool
def get_schema_retriever_tool() -> FunctionTool:
    return FunctionTool.from_defaults(
        fn=retrieve_schema_context,
        name="retrieve_schema_context",
        description=(
            "Retrieves relevant database schema information (tables, columns, relationships, descriptions) "
            "from the sales database knowledge base using semantic search (RAG). Always call this first "
            "if you need to understand the schema for SQL generation."
        )
    )

# Test entry point
if __name__ == "__main__":
    print("--- Testing Schema Retriever Tool Implementation (with RAG) ---")
    if not os.environ.get("NEBIUS_API_KEY"):
        print("Warning: NEBIUS_API_KEY not set. Schema retrieval might fail.")

    schema_tool = get_schema_retriever_tool()

    queries = [
        "What are the columns in the sales and products tables, and how are they related?",
        "Show me customer names and their regions.",
        "What is the purpose of the regions table?",
        "Tell me about the sales table schema and its purpose."
    ]

    for query in queries:
        print(f"\nCalling tool with: '{query}'")
        result = schema_tool.call(natural_language_query=query)
        print(f"Result:\n{result}")