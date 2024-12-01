import streamlit as st
import openai
import time
import io
import os, re
import random
import fitz
from create_assistant import create_assistant
import requests
from bs4 import BeautifulSoup
import tldextract
from functions import generate_answer, save_result
from prompts import questions
import certifi

import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader


# Load the configuration
with open('users.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

# Initialize the authenticator
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)


# Function to extract links from a PDF
def extract_links_from_pdf(pdf_path):
    pdf_document = fitz.open(pdf_path)
    links = []

    for page_number in range(len(pdf_document)):
        page = pdf_document[page_number]
        page_links = page.get_links()
        for link in page_links:
            uri = link.get('uri')
            if uri:
                links.append(uri)

    filtered_links = [link for link in links if not link.startswith("mailto:") and "meet.google.com" not in link]
    return filtered_links

# Function to scrape content from a link and save it to a file
def scrape_and_save_content(link, folder):
    # try:
    #     response = requests.get(link, verify=certifi.where())
    #     response.raise_for_status()
    # except requests.exceptions.RequestException as e:
    #     print(f"Failed to retrieve {link}: {e}")
    #     return

    # soup = BeautifulSoup(response.text, 'html.parser')
    # text_content = soup.get_text(separator='\n', strip=True)

    # domain = tldextract.extract(link).domain
    # random_number = random.randint(1000, 9999)
    # file_name = f"{domain}_{random_number}.txt"

    # file_path = os.path.join(folder, file_name)

    # with open(file_path, 'w', encoding='utf-8') as file:
    #     file.write(text_content)

    print(f"Content from {link} saved to ...")


# Main function to generate data
def generate_data(uploaded_pdf_file, file_name):
    # Generate a unique folder name
    unique_folder_name = f"{file_name}_data_{random.randint(1000, 9999)}"
    os.makedirs(unique_folder_name, exist_ok=True)

    # Save the uploaded PDF file to the unique folder
    pdf_path = os.path.join(unique_folder_name, uploaded_pdf_file.name)
    with open(pdf_path, 'wb') as f:
        f.write(uploaded_pdf_file.read())

    # Extract links from the PDF
    links = extract_links_from_pdf(pdf_path)

    # Scrape content from each link and save to the unique folder
    for link in links:
        scrape_and_save_content(link, unique_folder_name)
    
    # Creating assistant
    print(f"Data has been successfully generated and saved in the folder: {unique_folder_name}")
    return create_assistant(data_path=unique_folder_name)


# Function to run when the button is clicked
def process_file(file, file_name):
    return generate_data(file, file_name)


def generate_answer_for_custom_question(assistant_id, custom_question):
    # Generate answer for a custom question using the assistant
    return generate_answer(assistant_id, custom_question)

def generate_result(assistant_id):
    result = []
    result_display = st.empty()  # Empty container to display results dynamically
    html_content = "<html><head><title>Results</title></head><body>"

    for i, question in enumerate(questions):
        answer = generate_answer(assistant_id, question)
        cleaned_answer = re.sub(r'【\d+:\d+†source】', '', answer)
        result.append({"question": question, "answer": cleaned_answer})

        # Append question and answer to HTML content
        html_content += f"<h3>Question {i + 1}:</h3>"
        html_content += f"<p><strong>{question}</strong></p>"
        html_content += f"<p>{cleaned_answer}</p><hr>"

        # Display question and answer with HTML rendering for the answer
        st.write(f"**Question {i + 1}:** {question}")
        st.markdown(cleaned_answer, unsafe_allow_html=True)
        st.write("---")

        time.sleep(1)  # Simulate time delay; you can remove this in production

    html_content += "</body></html>"

    # Save results in case you need to store them
    save_result(result)
    st.success("All results have been generated successfully!")
    
    # Return the HTML content for download
    return html_content



# Main page for PDF Q&A
def main_page():
    st.title("PDF Q&A with OpenAI Assistant")

    uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

    cleaned_file_name  =""

    if uploaded_file is not None:
        file_name = os.path.splitext(uploaded_file.name)[0]
        cleaned_file_name = re.sub(r'[^A-Za-z0-9]', '', file_name)

        if st.button("Generate Results"):
            assistant_id = process_file(uploaded_file, cleaned_file_name)

            # Generate results and get HTML content
            html_content = generate_result(assistant_id)

            # Store the assistant_id, results, and HTML content in session state
            st.session_state['assistant_id'] = assistant_id
            st.session_state['result_generated'] = True  # Set the flag to True after results are generated
            st.session_state['html_content'] = html_content  # Save the HTML content
            st.session_state['questions_answers'] = html_content  # Keep the displayed answers

    # Check if results have been generated and show download button + results
    if st.session_state.get('result_generated', False):
        st.download_button(
            label="Download Results",
            data=st.session_state['html_content'],
            file_name=f"{cleaned_file_name}_results.html",
            mime="text/html"
        )

        # Display previously generated results
        st.markdown(st.session_state['html_content'], unsafe_allow_html=True)


# Page to ask a custom question (only available after generating results)
def ask_question_page():
    st.title("Ask a Question")

    # Ensure assistant_id exists and results are generated
    if 'assistant_id' not in st.session_state or not st.session_state.get('result_generated', False):
        st.error("Please generate results from a PDF file on the main page first.")
        return

    # Get the assistant_id from session state
    assistant_id = st.session_state['assistant_id']

    # Custom question input
    custom_question = st.text_input("Type your question here:")

    if st.button("Get Answer"):
        if custom_question:
            # Generate answer for the custom question
            answer = generate_answer_for_custom_question(assistant_id, custom_question)
            cleaned_answer = re.sub(r'【\d+:\d+†source】', '', answer)

            # Display the question and answer
            st.write(f"**Question:** {custom_question}")
            st.markdown(cleaned_answer, unsafe_allow_html=True)
        else:
            st.warning("Please enter a question before submitting.")


# Main function to manage the flow
def main():

    try:
        authenticator.login()
    except Exception as e:
        st.error(e)
    # Only show "Ask a Question" page if results have been generated


    if st.session_state['authentication_status']:
        authenticator.logout("Logout", "sidebar")
        if st.session_state.get('result_generated', False):
            page = st.sidebar.selectbox("Navigate", ["Main Page", "Ask a Question"])
        else:
            page = "Main Page"  # Default to the main page if results aren't generated

        if page == "Main Page":
            main_page()
        elif page == "Ask a Question":
            ask_question_page()
    elif st.session_state['authentication_status'] is False:
        st.error("Username/password is incorrect")
    elif st.session_state['authentication_status'] is None:
        st.warning("Please enter your username and password")



if __name__ == "__main__":
    # Initialize session state if it doesn't exist
    if 'result_generated' not in st.session_state:
        st.session_state['result_generated'] = False
    
    main()
