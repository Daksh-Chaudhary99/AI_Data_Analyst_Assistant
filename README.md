---
title: AI-Powered Data Analyst Assistant
emoji: 📊
colorFrom: indigo
colorTo: indigo
sdk: gradio
sdk_version: 5.25.2
app_file: app.py
pinned: false
---

# 📊 AI-Powered Data Analyst Assistant

### Empowering Business Users with Self-Service Analytics via Conversational AI

---

## 🚀 Project Overview

The **AI-Powered Data Analyst Assistant** is a cutting-edge conversational AI application designed to revolutionize how business users interact with complex sales data. Instead of relying on technical teams for custom reports, users can simply ask questions in natural language, and the assistant will retrieve precise answers, either by querying a database or providing definitions from a business knowledge base.

This project showcases a sophisticated multi-agent architecture leveraging **Large Language Models (LLMs)**, **Retrieval Augmented Generation (RAG)**, and **fine-tuning** to deliver accurate, context-aware, and actionable insights, bridging the gap between raw data and business understanding.

Link to Project Demo: https: https://huggingface.co/spaces/DakshChaudhary/Data_Analyst_Assistant

Link to Project Demo Video: https://www.dropbox.com/scl/fi/7lo9j75h36ic5xipqt7gq/AI_Data_Analyst_Assistant_Demo.mp4?rlkey=2suvkn076goi52nsrokz407eq&st=zmtyyg3u&dl=0 

## 🗄️ Database Schema & Data Scale

The application operates over a transactional sales database, meticulously designed and populated with realistic dummy data to simulate a diverse business environment. This ensures the agent's analytical capabilities are tested against varied scenarios.

**Data Scale:**
* **Sales Records:** Over **15,000** individual sales transactions.
* **Customers:** **20** unique customer profiles.
* **Products:** **13** distinct products across **4** categories (Electronics, Furniture, Stationery, Apparel).
* **Regions:** **5** geographical sales regions (North, South, East, West, Central).
* **Temporal Coverage:** Sales data spans the **last 2 years**, with a bias towards recent activity and seasonal trends for realistic time-series analysis.

**Core Tables Overview:**

### `regions` Table
Stores information about geographical sales regions.
| region_id | region_name |
| :-------- | :---------- |
| 1         | North       |
| 2         | South       |
| 3         | East        |
| 4         | West        |
| 5         | Central     |

### `products` Table
Contains details about products sold.
| product_id | product_name                | category    | price    |
| :--------- | :-------------------------- | :---------- | :------- |
| 101        | Laptop Basic                | Electronics | 800.00   |
| 102        | Laptop Pro                  | Electronics | 1500.00  |
| 103        | Smartphone X                | Electronics | 700.00   |
| 104        | Smartwatch                  | Electronics | 250.00   |
| 201        | Office Desk Standard        | Furniture   | 200.00   |
| ...        |                             |             |          |

### `customers` Table
Stores customer information and their assigned region.
| customer_id | customer_name   | email                   | region_id |
| :---------- | :-------------- | :---------------------- | :-------- |
| 1           | Alice Smith     | alicesmith@example.com  | 1         |
| 2           | Bob Johnson     | bobjohnson@example.com  | 3         |
| 3           | Charlie Brown   | charliebrown@example.com| 1         |
| 4           | Diana Prince    | dianaprince@example.com | 5         |
| 5           | Eve Adams       | eveadams@example.com    | 4         |
| ...         |                 |                         |           |

### `sales` Table
Records individual sales transactions, linking products, customers, and regions by ID.
| sale_id | product_id | customer_id | region_id | sale_date  | quantity | amount    |
| :------ | :--------- | :---------- | :-------- | :--------- | :------- | :-------- |
| 1       | 401        | 16           | 2         | 2025-06-21 | 2        | 1600.00   |
| 2       | 103        | 1           | 1         | 2025-06-15 | 1        | 700.00    |
| 3       | 201        | 10          | 1         | 2025-05-30 | 3        | 600.00    |
| 4       | 302        | 12          | 4         | 2025-06-01 | 5        | 150.00    |
| 5       | 405        | 15          | 5         | 2025-06-25 | 1        | 110.00    |
| ...     |            |             |           |            |          |           |


## ✨ Practical Use Cases & Impact

* **Self-Service Business Intelligence (BI):** Empowers non-technical users to access and analyze data independently, reducing reliance on data teams.
* **Faster Decision Making:** Get real-time answers to data-related questions, enabling quicker, data-driven decisions.
* **Improved Data Accessibility:** Makes complex database schemas and business metrics understandable and queryable for a wider audience.
* **Enhanced Productivity:** Automates routine data retrieval tasks, freeing up data analysts for more strategic work.
* **Democratization of Data:** Fosters a data-literate culture by making data exploration intuitive and conversational.

## 🛠️ Technical Proficiencies & Highlights

This project demonstrates expertise across a range of advanced AI and data engineering concepts:

* **Multi-Agent Architecture:**
    * **Orchestrator Agent:** Utilizes the **LlamaIndex ReAct Agent** framework (Reasoning and Acting) to intelligently route user queries to the appropriate specialized sub-agent (NL-to-SQL or KPI Explainer) based on intent detection. This showcases complex agentic workflow design.
    * **Specialized Agents:** Distinct agents for distinct tasks (Data Querying, KPI Explanation) ensuring modularity and focused expertise.

* **Natural Language to SQL (NL2SQL):**
    * **Fine-tuning (LoRA on Nebius AI):** A **Meta-Llama-3.1-8B-Instruct-LoRa** model was fine-tuned on a custom dataset (`nl_sql_finetune_dataset.jsonl`) of ~70 natural language questions and their corresponding **SQLite** SQL queries. This demonstrates specialized model adaptation for domain-specific accuracy.
    * **Synthetic Data Generation:** The NL-to-SQL dataset itself was (partially) generated using conversational AI tools like **ChatGPT**.
    * **Robust SQL Execution:** The `SqlExecutorTool` securely executes only `SELECT` queries against the SQLite database, returning results in a structured format (CSV) for LLM interpretation.

* **Retrieval Augmented Generation (RAG):**
    * **Schema RAG:** The `SchemaRetrieverTool` uses RAG over a `data_dictionary.md` to provide real-time, relevant database schema context (tables, columns, relationships, descriptions) to the NL-to-SQL agent. This ensures generated SQL is accurate and schema-aware, even for complex joins.
    * **KPI RAG:** A dedicated RAG component over `kpi_definitions.md` enables the KPI Answering Agent to provide precise definitions and calculation methods for key business metrics.
    * **Vector Database:** **ChromaDB** is employed as the persistent vector store to efficiently index and retrieve relevant information based on semantic similarity.
    * **Embedding Models:** Leverages **Nebius AI Embeddings** (`BAAI/bge-en-icl) for converting natural language and knowledge base content into high-dimensional vectors for semantic search.

* **Prompt Engineering:**
    * Extensive custom system prompts are designed for each agent to guide their reasoning, tool usage, and response generation, ensuring adherence to `Thought-Action-Observation` loops and specific output requirements.

* **Data Management & Orchestration:**
    * **SQLite Database:** Used as the backend for sales data, demonstrating proficiency in database interaction.
    * **Pandas:** Utilized for efficient data manipulation and preparing results for LLM consumption.
    * **Dynamic Data Generation:** Includes a robust `setup_database.py` script to generate realistic dummy sales data with temporal, regional, and product-specific biases, crucial for comprehensive testing of analytical queries.

* **Python Development:** Clean, modular, and well-structured Python codebase, following best practices for agent development and dependency management (`requirements.txt`, `.env`).

## 📂 Project Structure
```
AI_DATA_ANALYST_ASSISTANT/
├── chroma_db_schema/                 # Persistent ChromaDB for schema context
├── chroma_db_kpi/                    # Persistent ChromaDB for KPI definitions
├── data/
│   └── sales_database.db             # SQLite database for sales data
├── fine-tuning/
│   ├── model_checkpoints/            # Saved model states from fine-tuning
│   ├── finetune_script.py            # Script for fine-tuning NL-to-SQL LLM
│   ├── finetuned_model_deployment.py # Script to deploy fine-tuned model
│   └── nl_sql_finetune_dataset.jsonl # Dataset for NL-to-SQL fine-tuning
├── knowledge_base/
│   ├── business_glossary/
│   │   └── kpi_definitions.md        # KPI definitions for RAG
│   └── schema/
│       ├── data_dictionary.md        # Human-readable schema descriptions for RAG
│       └── sales_schema.sql          # SQL DDL for database creation
├── src/
│   ├── agents/
│   │   ├── agent_models/
│   │   │   └── models.py             # Centralized LLM initialization
│   │   ├── agent_tools/
│   │   │   ├── schema_retriever_tool.py # Tool for retrieving schema context
│   │   │   └── sql_executor_tool.py  # Tool for executing SQL queries
│   │   ├── nl_sql_agent.py           # Core Natural Language to SQL Agent
│   │   └── orchestrator_agent.py     # Routes queries to specialized agents
│   ├── rag_index.py                  # Script to build and persist RAG indexes
│   └── setup_database.py             # Script to setup and populate the database
├── venv/                             # Python Virtual Environment
├── .env                              # Environment variables (e.g., API keys)
├── .gitignore                        # Git ignore file
├── app.py                            # Main application entry point (e.g., API)
└── requirements.txt                  # Python dependencies
```

## ⚙️ Setup & Installation

To get the AI Data Analyst Assistant up and running locally:

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/YourGitHubUsername/AI_Data_Analyst_Assistant.git](https://github.com/YourGitHubUsername/AI_Data_Analyst_Assistant.git)
    cd AI_Data_Analyst_Assistant
    ```

2.  **Create and Activate Virtual Environment:**
    ```bash
    python -m venv venv
    # On Windows:
    .\venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    pip install tqdm # For progress bars during data generation
    ```

4.  **Set Up Environment Variables:**
    * Create a `.env` file in the project root.
    * Add your Nebius AI API Key:
        ```
        NEBIUS_API_KEY="your_nebius_ai_api_key_here"
        ```

5.  **Initialize the Database:**
    This script will create `sales_database.db` and populate it with rich dummy data.
    ```bash
    python src/setup_database.py
    ```

6.  **Build RAG Indexes:**
    This will create the `chroma_db_schema` and `chroma_db_kpi` directories with your vectorized knowledge bases.
    ```bash
    python src/rag_index.py
    ```

7.  **Fine-tune (Optional - for advanced development):**
    If you're developing the fine-tuned model, run your fine-tuning script. This project assumes you have already fine-tuned and deployed your `meta-llama/Meta-Llama-3.1-8B-Instruct-LoRa:nl-to-sql-finetuned-jbkN` model on Nebius AI as configured in `src/agents/agent_models/models.py`.

## 🚀 How to Use (Demonstration)

You can interact directly with the `NLSQLAgent` for testing purposes:

1.  **Start the Agent:**
    ```bash
    python src/nl_sql_agent.py
    ```
2.  **Ask Questions!** Try some of these examples:
    * "What is the total number of sales?"
    * "What are the names of customers in the North region?"
    * "How much revenue did we generate from Electronics products?"
    * "Which customer has the most sales in the past one month?"
    * "Show me the total revenue for each month over the last six months, ordered by month."
    * "Which are our top 5 products by total quantity sold across all time?"
    * "What is the average amount per sale for each product category?"
    * "How many unique customers have made a purchase in each region over the last year?"
    * "What is the total revenue generated by customers from each region?"
    * "Which products have not been sold in the last 3 months?" (This tests an advanced SQL pattern and might require further fine-tuning for specific dialect)
