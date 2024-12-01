import json
import time
from flask import Flask, jsonify
from openai import OpenAI
import functions
from datetime import datetime
import os

# ... (keep the existing imports and initialization code)

# Initialize OpenAI client

from dotenv import load_dotenv
load_dotenv()
# Access the API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# print(f"Your OpenAI API key is: {OPENAI_API_KEY}")


client = OpenAI(api_key=OPENAI_API_KEY)

def generate_answer(assistant_id, question):
    try:
        # Create a new thread for this question
        thread = client.beta.threads.create()

        # Add the user's question to the thread
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=question
        )

        # Run the Assistant
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant_id
        )

        # Check the run status and handle function calls if necessary
        while True:
            run_status = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )

            print(f"Run status: {run_status.status}")
            
            if run_status.status == 'completed':
                break
            elif run_status.status == "incomplete":
                print("Retrying in 1 seconds")
                time.sleep(2)

                run = client.beta.threads.runs.create(
                    thread_id=thread.id,
                    assistant_id=assistant_id
                )
            elif run_status.status == 'failed':
                if run_status.last_error.code == "rate_limit_exceeded":
                    print("Retrying in 1 seconds")
                    time.sleep(2)

                    run = client.beta.threads.runs.create(
                        thread_id=thread.id,
                        assistant_id=assistant_id
                    )

                else:
                    raise Exception("Run failed")
            
            time.sleep(1)  # Wait before checking again

        # Retrieve and return the latest message from the assistant
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        response = messages.data[0].content[0].text.value

        return response

    except Exception as e:
        print(run.last_error)
        print(f"Error in generate_answer: {str(e)}")
        return f"Unable to generate answer, due to lack of information."



def save_result(results):
    """
    Save the question-answer pairs in a formatted HTML file.
    
    :param results: List of dictionaries, each containing 'question' and 'answer' keys
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"qa_results_{timestamp}.html"
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Q&A Results</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
            }}
            h1 {{
                color: #2c3e50;
                border-bottom: 2px solid #3498db;
                padding-bottom: 10px;
            }}
            .qa-pair {{
                background-color: #f9f9f9;
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 15px;
                margin-bottom: 20px;
            }}
            .question {{
                font-weight: bold;
                color: #2980b9;
            }}
            .answer {{
                margin-top: 10px;
            }}
        </style>
    </head>
    <body>
        <h1>Q&A Results</h1>
        <div class="results">
    """
    
    for item in results:
        html_content += f"""
        <div class="qa-pair">
            <div class="question">Q: {item['question']}</div>
            <div class="answer">A: {item['answer']}</div>
        </div>
        """
    
    html_content += """
        </div>
    </body>
    </html>
    """
    
    # Ensure the 'results' directory exists
    os.makedirs('results', exist_ok=True)
    
    # Save the HTML file
    with open(os.path.join('results', filename), 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return filename