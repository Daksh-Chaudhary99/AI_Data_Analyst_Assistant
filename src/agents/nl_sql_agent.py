import os
import logging
import sys
from llama_index.llms.openai import OpenAI 
from llama_index.core.agent import ReActAgent
from .agent_tools.sql_executor_tool import get_sql_executor_tool
from .agent_tools.schema_retriever_tool import get_schema_retriever_tool
from .agent_models.models import get_finetuned_model

# Configure logging for better visibility into agent's thought process
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

class NLSQLAgent:
    def __init__(self):
        """
        Initializes the NL-to-SQL Agent, which translates natural language to SQL, executes it, and provides answers.

        Args:
            model_name (str): The name/ID of fine-tuned model deployed on Nebius AI.
            api_key (str): Nebius AI API key.
            base_url (str): The base URL for the Nebius AI API endpoint
        """
        self.llm = get_finetuned_model()
        self.system_prompt = (
            "You are an expert SQL data analyst. Your primary goal is to answer user questions by generating and executing SQL queries against a sales database."
            "\n\nYou MUST operate in a loop, strictly following this format:"
            "\n1. **Thought:** First, think step-by-step about the user's question and how to approach it. Analyze what you know and what you need to find out."
            "\n2. **Action:** Based on your thought, choose one of the available tools."
            "\n3. **Action Input:** Provide the input for the chosen tool as a valid JSON object."
            "\n\n**AVAILABLE TOOLS:**"
            "\n- **retrieve_schema_context**: Use this tool FIRST if you need to understand the database's tables, columns, or relationships to answer a question. Input is the user's query."
            "\n- **execute_sql_query**: Use this tool to run a SQL SELECT query against the database. Do not use semicolons at the end of the query."
            "\n\n**IMPORTANT RULES:**"
            "\n- **Always use `retrieve_schema_context` before generating complex SQL** if you are unsure about table or column names."
            "\n- When dealing with dates in SQL, remember to use SQLite-compatible functions like `DATE('now', '-1 month')` and `STRFTIME('%Y-%m', sale_date)`."
            "\n- After you have the final answer from your tools, conclude your response with the `Answer:` tag."
            "\n- If you receive an error, try to correct your approach in your next thought."
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
        nl_sql_agent = NLSQLAgent()

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