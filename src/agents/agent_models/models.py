import os
from llama_index.llms.nebius import NebiusLLM
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv() 

base_agent_model_id = "Qwen/Qwen3-235B-A22B"
finetuned_model_id = "meta-llama/Meta-Llama-3.1-8B-Instruct-LoRa:nl-to-sql-finetuned-jbkN"

def get_base_agent_model():
    return NebiusLLM(api_key=os.environ["NEBIUS_API_KEY"], model=base_agent_model_id)

def get_finetuned_model():
    return NebiusLLM(api_key=os.environ["NEBIUS_API_KEY"], model=finetuned_model_id)