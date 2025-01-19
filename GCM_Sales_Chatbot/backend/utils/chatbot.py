from groq import Groq
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)
import os

class Chatbot:
    def __init__(self, doc_processor=None):
        # Set up Groq client
        os.environ['GROQ_API_KEY'] = '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'
        self.client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        self.doc_processor = doc_processor
        
        self.conversation_history = [
            {"role": "system", "content": """You are a helpful sales assistant for GCM (Global Compliance Management) products and services. 
            Your role is to assist sales team members and customers by providing information STRICTLY from the knowledge base provided.
            
            IMPORTANT RULES:
            1. ONLY use information from the provided context to answer questions
            2. If the context doesn't contain the information needed to answer the question, say "I apologize, but I don't have enough information in the knowledge base to answer this question accurately."
            3. DO NOT make up or infer information that's not in the context
            4. If only partial information is available, provide what's available and clearly state what information is missing
            5. Always cite the information as coming from the knowledge base
            
            Be professional and accurate in your responses."""}
        ]

    def get_response(self, user_message):
        """Process user message and generate response."""
        try:
            # Search for relevant content in the knowledge base
            context = []
            if self.doc_processor:
                context = self.doc_processor.search_similar_content(user_message, k=5)  # Increased k for more context
            
            if not context:
                return "I apologize, but I don't have enough information in the knowledge base to answer this question accurately."
            
            # Prepare the message with context
            prompt = f"""Context from knowledge base:
            {' '.join(context)}
            
            User question: {user_message}
            
            Instructions:
            1. Answer ONLY using the information provided in the context above
            2. If the context doesn't contain enough information to fully answer the question, say so
            3. Do not make up or infer any information not present in the context
            4. Begin your response with 'Based on the knowledge base, ...'"""
            
            # Add user message to conversation history
            self.conversation_history.append({"role": "user", "content": prompt})
            
            # Get response from Groq
            chat_completion = self.client.chat.completions.create(
                messages=self.conversation_history,
                model="mixtral-8x7b-32768",
                temperature=0.3,  # Reduced temperature for more focused responses
                max_tokens=1024
            )
            
            # Extract the response
            response = chat_completion.choices[0].message.content
            
            # Verify response starts with the required prefix
            if not response.startswith("Based on the knowledge base"):
                response = "Based on the knowledge base, " + response
            
            # Add AI response to conversation history
            self.conversation_history.append({"role": "assistant", "content": response})
            
            return response
        
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return "I apologize, but I encountered an error processing your request. Please try again."

    def clear_conversation(self):
        """Clear the conversation history except for the system message."""
        self.conversation_history = self.conversation_history[:1] 