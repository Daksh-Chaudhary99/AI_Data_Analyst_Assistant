import sqlite3
import pandas as pd
import io
import os
from llama_index.core.tools import FunctionTool

current_dir = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.path.join(current_dir, '..', '..', '..', 'data', 'sales_database.db')

def execute_sql_query(sql_query: str) -> str:
    """
    Executes a SQL SELECT query against the sales database and returns the results as a formatted string (CSV representation).

    This tool should only be used to retrieve data using SELECT statements.
    It does not support INSERT, UPDATE, DELETE, or DDL commands for security reasons.

    Args:
        sql_query (str): The complete and correct SQL SELECT query to execute.
                         Do not include semicolons at the end of the query.

    Returns:
        str: A CSV string representation of the query results, or an error message.
    """
    # Safety check: Only allow SELECT queries
    if not sql_query.strip().upper().startswith("SELECT"):
        return "Error: Only SELECT queries are allowed for security reasons."

    conn = None 
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        df = pd.read_sql_query(sql_query, conn)
        
        if df.empty:
            return "Query executed successfully, but no results were found."
        
        # Convert DataFrame to a CSV string for LLM consumption
        output = io.StringIO()
        df.to_csv(output, index=False)
        return output.getvalue()

    except pd.io.sql.DatabaseError as e:
        return f"Database Query Error: {e}"
    except Exception as e:
        return f"An unexpected error occurred during SQL execution: {e}"
    finally:
        if conn:
            conn.close()

def get_sql_executor_tool() -> FunctionTool:
    """
    Returns a LlamaIndex FunctionTool for executing SQL SELECT queries.
    """
    return FunctionTool.from_defaults(
        fn=execute_sql_query,
        name="execute_sql_query",
        description=(
            "Executes a SQL SELECT query against the sales database and returns the results. "
            "Use this tool to get actual data to answer the user's question. "
            "Always generate the full, correct SQL query to answer the question before calling this tool. "
            "Only SELECT queries are allowed. "
            "Input should be the complete and correct SQL SELECT query string."
        )
    )