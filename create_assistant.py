import json
import os
import time
from flask import Flask, request, jsonify
import openai
from openai import OpenAI
from flask_cors import CORS
import requests
from datetime import datetime, timedelta
import re
from prompts import assistant_instructions

# Check OpenAI version compatibility
from packaging import version

required_version = version.parse("1.1.1")
current_version = version.parse(openai.__version__)

from dotenv import load_dotenv
load_dotenv()
# Access the API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# print(f"Your OpenAI API key is: {OPENAI_API_KEY}")


if current_version < required_version:
    raise ValueError(
        f"Error: OpenAI version {openai.__version__} is less than the required version 1.1.1"
    )
else:
    print("OpenAI version is compatible.")


# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)


def create_assistant(data_path):

    assistant_file_path = 'assistant.json'

    # Create an assistant
    assistant = client.beta.assistants.create(
        name="AI",
        temperature=0.7,
        instructions=assistant_instructions,
        model="gpt-4o-mini",
        tools=[{"type": "file_search"}],
    )
    
    # List all files in the data_path directory
    file_paths = os.listdir(data_path)
    vector_store = client.beta.vector_stores.create(name="Vector-Storage")

    # Prepare non-empty file streams for upload
    file_streams = []
    for path in file_paths:
        full_path = os.path.join(data_path, path)
        if os.path.getsize(full_path) > 0:  # Check if the file is not empty
            file_streams.append(open(full_path, "rb"))
        else:
            print(f"Skipping empty file: {path}")

    # Upload files and poll status of the batch for completion
    if file_streams:
        file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
            vector_store_id=vector_store.id, files=file_streams
        )

    # Update the assistant with the vector store
    assistant = client.beta.assistants.update(
        assistant_id=assistant.id,
        tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
    )

    # Save the assistant ID to a new assistant.json file
    with open(assistant_file_path, 'w') as file:
        json.dump({'assistant_id': assistant.id}, file)
        print("Created a new assistant and saved the ID.")

    assistant_id = assistant.id

    return assistant_id