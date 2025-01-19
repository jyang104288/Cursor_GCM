from flask import Flask, request, jsonify, render_template
from utils.document_processor import DocumentProcessor
from utils.chatbot import Chatbot
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize document processor and chatbot
doc_processor = DocumentProcessor()
print("Loading knowledge base...")
KNOWLEDGE_PATH = r"C:\Users\104288\UL Solutions\GMA - Global Market Access - AI POC\GCM_Sales_Chatbot\GCM_Knowledge.docx"
if doc_processor.load_document(KNOWLEDGE_PATH):
    print("Knowledge base loaded successfully!")
else:
    print("Warning: Failed to load knowledge base!")

# Initialize chatbot with document processor
chatbot = Chatbot(doc_processor=doc_processor)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Process the message and get response
        response = chatbot.get_response(user_message)
        
        return jsonify({
            'response': response,
            'status': 'success'
        })
    
    except Exception as e:
        print(f"Chat error: {str(e)}")
        return jsonify({
            'error': str(e),
            'status': 'error'
        }), 500

@app.route('/api/suggested-questions', methods=['GET'])
def get_suggested_questions():
    try:
        # Get document content
        content = doc_processor.get_document_topics()
        print(f"Document content length: {len(content)} paragraphs")
        
        if not content:
            print("No content found in the document!")
            return jsonify({
                'questions': [
                    "What services does GCM offer?",
                    "Can you explain the compliance management features?",
                    "What are the key benefits of using GCM?",
                    "How does GCM help with regulatory compliance?",
                    "What industries does GCM primarily serve?"
                ],
                'status': 'success'
            })
        
        # Use Groq to analyze content and generate questions
        prompt = f"""Based on the available information about GCM (Global Compliance Management) products and services, generate 5 specific questions that would be relevant for a sales team member or customer to ask.
        Focus on questions about:
        1. Product features and capabilities
        2. Services offered
        3. Key benefits
        4. Technical specifications
        5. Implementation details

        Format the response as a JSON array of strings, each string being a question."""

        print("Generating questions with Groq...")
        # Get questions from Groq
        chat_completion = chatbot.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="mixtral-8x7b-32768",
            temperature=0.3,
            max_tokens=1024
        )
        
        print("Got response from Groq")
        # Extract and parse the response
        try:
            import json
            questions = json.loads(chat_completion.choices[0].message.content)
            print(f"Successfully parsed {len(questions)} questions")
            return jsonify({
                'questions': questions,
                'status': 'success'
            })
        except json.JSONDecodeError as e:
            print(f"JSON parsing failed: {str(e)}")
            # If JSON parsing fails, return the raw response
            questions = chat_completion.choices[0].message.content.split('\n')
            questions = [q.strip().strip('- ') for q in questions if q.strip()]
            print(f"Extracted {len(questions)} questions from raw response")
            return jsonify({
                'questions': questions,
                'status': 'success'
            })
    
    except Exception as e:
        print(f"Error in suggested questions: {str(e)}")
        # Return default questions if there's an error
        return jsonify({
            'questions': [
                "What services does GCM offer?",
                "Can you explain the compliance management features?",
                "What are the key benefits of using GCM?",
                "How does GCM help with regulatory compliance?",
                "What industries does GCM primarily serve?"
            ],
            'status': 'success'
        })

if __name__ == '__main__':
    app.run(debug=True, port=5000) 