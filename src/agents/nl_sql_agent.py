import os
import logging
import sys
from llama_index.llms.openai import OpenAI 
from llama_index.core.agent import ReActAgent
from agent_tools.sql_executor_tool import get_sql_executor_tool
from agent_tools.schema_retriever_tool import get_schema_retriever_tool
from agent_models.models import get_finetuned_model

# Configure logging for better visibility into agent's thought process
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

class NLSQLAgent:
    def __init__(self, model_name: str, api_key: str, base_url: str):
        """
        Initializes the NL-to-SQL Agent, which translates natural language to SQL, executes it, and provides answers.

        Args:
            model_name (str): The name/ID of fine-tuned model deployed on Nebius AI.
            api_key (str): Nebius AI API key.
            base_url (str): The base URL for the Nebius AI API endpoint
        """
        self.llm = get_finetuned_model()
        self.system_prompt = (
        "You are an expert SQL assistant for a sales database. Your task is to accurately translate "
        "natural language questions into SQL queries, execute them using the provided tools, and then "
        "provide concise, natural language answers based on the query results. "
        "You MUST strictly follow the Thought-Action-Action Input-Observation format for ALL steps. "
        "Pay extreme attention to the 'Action Input' format, which MUST be a valid JSON dictionary "
        "matching the tool's parameters. **ALWAYS provide ALL required parameters.**\n"
        "Follow these rules strictly:\n"
        "1. **Analyze the query:** Understand the user's intent and identify if schema context is needed.\n"
        "2. **Schema Retrieval (if needed):** If the user's question requires knowledge about the "
        "   database structure (tables, columns, relationships) that you might not implicitly know, "
        "   **FIRST, ALWAYS call `retrieve_schema_context`** using the user's original query. "
        "   The Action Input for `retrieve_schema_context` MUST be a JSON object like: "
        "   `{\"natural_language_query\": \"user's exact question here\"}`. "
        "   Process the retrieved schema before generating SQL.\n"
        "3. **SQL Generation (Crucial):** Generate a syntactically correct and semantically accurate SQL SELECT query "
        "   that directly answers the user's question based on the available schema information (either "
        "   from `retrieve_schema_context` or your fine-tuned knowledge). Only use tables and columns "
        "   that exist in the schema. Do not include semicolons at the end of the query.\n"
        "4. **SQL Execution (MANDATORY):** **IMMEDIATELY AFTER generating a SQL query, you MUST call the `execute_sql_query` tool to run it.** " 
        "   The Action Input for `execute_sql_query` MUST be a JSON object like: "
        "   `{\"sql_query\": \"your generated SQL query here\"}`.\n"
        "5. **Answer Formulation (Only after SQL Execution and Observation):** Analyze the results from `execute_sql_query` "
        "   and formulate a clear, concise, and helpful natural language answer to the user's original question. "
        "   If the query returns no results, state that clearly.\n"
        "6. **Error Handling:** If a question cannot be answered from the database, explain why politely. "
        "   Do not make up data or generate SQL for non-existent tables/columns.\n"
        "7. **Iterative Refinement:** If a tool call fails or provides unexpected output, consider revising your approach "
        "   or informing the user about the issue. Continue the thought-process until a final answer is derived.\n"
        "8. The database schema includes tables such as `regions`, `products`, `customers`, and `sales`. "
        "   You should understand their structures and relationships from your training and schema context. "
        "   For example: `sales` table likely has columns like `sale_id`, `customer_id`, `product_id`, `date`, `amount`. "
        "   `customers` table might have `customer_id`, `customer_name`, `region_id`. `products` table might have `product_id`, `product_name`, `price`. "
        "   `regions` table might have `region_id`, `region_name`."
        "Remember, your final output should be an `Answer:` tag with the natural language response, not raw SQL or tool calls unless explicitly asked to show your work." 
    )

        self.tools = [get_schema_retriever_tool(), get_sql_executor_tool()]

        self.agent = ReActAgent.from_tools(
            llm=self.llm,
            tools=self.tools, 
            context=self.system_prompt, 
            verbose=True,
        )

    async def process_query(self, user_query: str) -> str:
        """
        Processes a user's natural language query using the NL-to-SQL agent.
        This method executes the agent's Thought-Action-Observation loop.

        Args:
            user_query (str): The natural language question from the user.

        Returns:
            str: The final natural language answer based on SQL execution, or an error/explanation.
        """
        try:
            response_object = await self.agent.achat(user_query)
            return str(response_object) 
        except Exception as e:
            logging.error(f"Error in NLSQLAgent.process_query: {e}")
            return f"I encountered an error while processing your request: {e}. Please try again or rephrase."

# Example Usage (for testing the NLSQLAgent directly)
if __name__ == "__main__":
    NEBIUS_API_KEY = os.environ.get("NEBIUS_API_KEY") 
    NEBIUS_BASE_URL = "https://api.studio.nebius.com/v1/openai" # Example: Verify with Nebius AI docs
    YOUR_FINETUNED_MODEL_ID = "meta-llama/Meta-Llama-3.1-8B-Instruct-LoRa:nl-to-sql-finetuned-jbkN" # Replace this

    if not NEBIUS_API_KEY:
        print("Error: NEBIUS_API_KEY environment variable not set.")
        print("Please set it before running the agent.")
    elif YOUR_FINETUNED_MODEL_ID == "your-finetuned-model-id":
        print("Error: Please replace 'your-finetuned-model-id' with your actual model ID.")
    else:
        nl_sql_agent = NLSQLAgent(
            model_name=YOUR_FINETUNED_MODEL_ID,
            api_key=NEBIUS_API_KEY,
            base_url=NEBIUS_BASE_URL
        )

        print("\nNL-to-SQL Agent initialized. Ask a question about your sales database.")

        async def main_loop():
            while True:
                user_input = input("\nYou: ")
                if user_input.lower() in ["exit", "quit"]:
                    print("Exiting agent.")
                    break
                
                response = await nl_sql_agent.process_query(user_input)
                print(f"Agent: {response}")
                
                # For multi-turn conversations, ReActAgent handles history automatically.
                # If you need to explicitly reset, you might re-instantiate or call agent.reset()
        
        import asyncio
        asyncio.run(main_loop())