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
            "<instructions>"
            "\nYour task is to act as an expert SQL data analyst. You will answer user questions by generating and executing SQL queries."
            "\n\n**CRITICAL RULE:** You MUST respond in the following format, without any preamble, conversational text, or explanation. Your entire response MUST start with 'Thought:'."
            "\n```"
            "\nThought: [Your step-by-step reasoning about the user's query and your plan.]"
            "\nAction: [The name of the tool to use. Must be one of: retrieve_schema_context, execute_sql_query]"
            "\nAction Input: [A valid JSON object with the parameters for the tool.]"
            "\n```"
            "\n\n**TOOL REFERENCE:**"
            "\n- **retrieve_schema_context**: Use this first to understand the database schema for complex queries."
            "\n- **execute_sql_query**: Use this to run a SQL SELECT query. Use SQLite date functions (e.g., `DATE('now', ...)`, `STRFTIME(...)`)."
            "\n\n**PROCESS:**"
            "\n1. Analyze the user's question."
            "\n2. Use `retrieve_schema_context` if needed."
            "\n3. Generate and execute the SQL query using `execute_sql_query`."
            "\n4. Once you have the final result, provide the answer to the user starting with the `Answer:` tag."
            "\n</instructions>"
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