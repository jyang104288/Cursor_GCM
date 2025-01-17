import os
import warnings
import openpyxl
from groq import Groq
from datetime import datetime
import ipywidgets as widgets
from IPython.display import display, HTML, clear_output
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font
import os
from datetime import datetime
from tkinter import filedialog
import tkinter as tk
import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
from flask_cors import CORS

# Suppress warnings
warnings.filterwarnings('ignore')

# Set the API Key as an Environment Variable
#os.environ['GROQ_API_KEY'] = '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'

os.environ['GROQ_API_KEY'] = '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'



# Set USER_AGENT environment variable
os.environ['USER_AGENT'] = 'GMA_News_AI_Research_Tool/1.0'

# Chatbot Setup
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# File Paths
file_path = r"C:\Users\104288\UL Solutions\GMA - Global Market Access - AI POC\GMA News\Input\GMA_News_URL_Input_EUR-Lex.xlsx"
#save_path = r"C:\Users\104288\cursor-tutor\Cursor_GCM\GMA_NEWS"


# = r"C:\Users\104288\UL Solutions\GMA - Global Market Access - AI POC\GMA News\Output"
# Load the workbook and select the sheets
wb = openpyxl.load_workbook(file_path, data_only=True)
output_sheet = wb['Output']

# List of attributes
attributes = [
    "Title", "Summary", "Affected Products", "Summary Details", "Conformity Assessment",
    "Marking Requirement", "Technical Requirement", "Publish Date", "Effective Date",
    "Mandatory Date", "Consultation Closing"
]

def display_topic_info( topic, url):
    info = f'<b>Processing Topic:</b> {topic}<br>'
   
    if url:
        info += f'<b>URL:</b> {url}<br>'
    display(HTML(info + '<br>'))

def get_text_content(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup.get_text()


def get_text_content(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup.get_text()

def process_url(topic, url):
    attribute_outputs = {}  # Initialize the dictionary to store prompts and responses

    try:
        # Get URL content
        text_content = get_text_content(url)
        if not text_content:
            raise ValueError("Unable to retrieve URL content")
        
        # Process each attribute
        for row_index, output_row in enumerate(output_sheet.iter_rows(min_row=2, values_only=True), start=2):
            if not output_row or len(output_row) < 4:
                continue
            
            try:
                attribute, prompt = output_row[0], output_row[1]
                if not attribute or not prompt:
                    continue
                
                # Construct the prompt
                formatted_prompt = (
                    f"As a product regulatory compliance officer, analyze the following text content. "
                    f"Focus on the attribute: '{attribute}'. "
                    f"Specific Question: {prompt} "
                    "Answer the specific question based on the provided text content, but do not repeat the question in the answer. "
                    "Be very concise and give answer directly. When giving a negative answer, simply state 'Not Need'. "
                    "Avoid repeating the question or using multiple sentences to say the same thing. "
                    "Only use information from the provided text content. "
                    "If your answer contains multiple points, please use bullet points and ensure each point is on a new line."
                    "If your answer contains date, please just output the date without description."
                )
                
                # Get AI response
                full_prompt = formatted_prompt + f"\nText content: {text_content[:16000]}... "
                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that refines and improves answers."},
                        {"role": "user", "content": full_prompt}
                    ],
                    model="llama3-8b-8192",
                )
                
                final_answer = chat_completion.choices[0].message.content.strip()
                
                # Store the prompt and AI output in the attribute_outputs dictionary
                attribute_outputs[attribute] = {
                    'prompt': formatted_prompt,
                    'ai_output': final_answer
                }
                
            except Exception as row_error:
                attribute_outputs[attribute] = {
                    'error': f"Error processing row {row_index}: {str(row_error)}"
                }
        
    except Exception as e:
        return {"error": str(e)}

    return attribute_outputs

app = Flask(__name__)
CORS(app)

# Initialize the Groq client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# Load the workbook and select the sheets
wb = openpyxl.load_workbook(file_path, data_only=True)
output_sheet = wb['Output']

# List of attributes
attributes = [
    "Title", "Summary", "Affected Products", "Summary Details", "Conformity Assessment",
    "Marking Requirement", "Technical Requirement", "Publish Date", "Effective Date",
    "Mandatory Date", "Consultation Closing"
]


@app.route('/process', methods=['POST'])
def process_request():
    data = request.json
    topic = data.get('topic')
    url = data.get('url')

    if not topic or not url:
        return jsonify({"error": "Topic and URL are required."}), 400

    try:
        # Call the processing function
        results = process_url(topic, url)
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
