import os
from openai import OpenAI
import time
from dotenv import load_dotenv
load_dotenv() 


client = OpenAI(
    base_url="https://api.studio.nebius.com/v1/",
    api_key=os.environ.get("NEBIUS_API_KEY"),
)

# Upload a training dataset
training_dataset = client.files.create(
    file=open("fine-tuning/nl_sql_finetune_dataset.jsonl", "rb"),
    purpose="fine-tune"
)

# Fine-tuning job parameters
job_request = {
    "model": "meta-llama/Llama-3.1-8B-Instruct",
    "suffix": "nl-to-sql-finetuned",
    "training_file": training_dataset.id,
    "hyperparameters": {
        "batch_size": 8,
        "learning_rate": 2e-5,
        "n_epochs": 10,
        "warmup_ratio": 0.1,
        "weight_decay": 0.01,
        "lora": True,
        "lora_r": 8,
        "lora_alpha": 16,
        "lora_dropout": 0.05,
        "packing": True,
        "max_grad_norm": 1,
    },
}

# Create and run the fine-tuning job
job = client.fine_tuning.jobs.create(**job_request)

# Make sure that the job has been finished or cancelled
active_statuses = ["validating_files", "queued", "running"]
while job.status in active_statuses:
    time.sleep(15)
    job = client.fine_tuning.jobs.retrieve(job.id)
    print("current status is", job.status)

print("Job ID:", job.id)

if job.status == "succeeded":
    # Check the job events
    events = client.fine_tuning.jobs.list_events(job.id)
    print(events)

    for checkpoint in client.fine_tuning.jobs.checkpoints.list(job.id).data:
        print("Checkpoint ID:", checkpoint.id)

        # Create a directory for every checkpoint
        os.makedirs(f"fine-tuning/model_checkpoints/{checkpoint.id}", exist_ok=True)

        for model_file_id in checkpoint.result_files:
            # Get the name of a model file
            filename = client.files.retrieve(model_file_id).filename

            # Retrieve the contents of the file
            file_content = client.files.content(model_file_id)

            # Save the contents into a local file
            file_content.write_to_file(filename)
