import requests
import os
from openai import OpenAI
import time
from dotenv import load_dotenv
load_dotenv() 

api_key=os.environ.get('NEBIUS_API_KEY')
api_url="https://api.studio.nebius.com"

client = OpenAI(
    base_url=api_url+"/v1",
    api_key=api_key,
)


def create_lora_from_job(name, ft_job, ft_checkpoint, base_model):
    fine_tuning_result = f"{ft_job}:{ft_checkpoint}"
    lora_creation_request = {
        "source": fine_tuning_result,
        "base_model": base_model,
        "name": name,
        "description": "Deploying fine-tuned LoRA model"
    }

    response = requests.post(
        f"{api_url}/v0/models",
        json=lora_creation_request,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    )

    print("Model creation response code:", response.status_code)
    print("Model creation response body:", response.text)

    response.raise_for_status()
    return response.json()

# Get the custom model information, check its status and wait for the validation to complete
def wait_for_validation(name, delay=5):
    while True:
        time.sleep(delay)
        print(f"Validating LORA: {name}")
        lora_info=requests.get(
            f"{api_url}/v0/models/{name}",
            headers={"Content-Type": "application/json","Authorization": f"Bearer {api_key}"}
        ).json()
        if lora_info.get("status") in {"active", "error"}:
            return lora_info

# Create a multi-message request
def get_completion(model):
    completion = client.chat.completions.create(
        model=model,
        messages=[{"role":"user","content":"Hello"}],
    )
    return completion.choices[0].message.content

# Deploy a LoRA adapter model by using IDs of a fine-tuning job and its checkpoint
lora_name=create_lora_from_job("nl-to-sql-adapter", "ftjob-b8246b132b234b78a73e4b508817868d", "ftckpt_db41d377-7e1c-43f8-838a-73801db71444", "meta-llama/Meta-Llama-3.1-8B-Instruct").get("name")

# Check the custom model status
lora_info = wait_for_validation(lora_name)

# If the custom model validation is successful, create a multi-message request with this model
if lora_info.get("status") == "active":
    print(get_completion(lora_name))
# If there is an error, display the reason
elif lora_info.get("status") == "error":
    print(f"An error occurred: {lora_info["status_reason"]}")

