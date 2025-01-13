import docx
import pandas as pd
from typing import List, Dict, Optional
import re
from dataclasses import dataclass
import requests
import time
import logging
from collections import defaultdict

@dataclass
class RegulatoryQuestion:
    category: str
    question: str
    context: str
    suggested_prompts: List[str]

class RegulatoryBot:
    def __init__(self, doc_path: str, auth_token: str, user_id: str):
        self.doc_path = doc_path
        self.auth_token = auth_token
        self.user_id = user_id
        self.base_url = "https://prod.ulchatbot.com/api/chats/chat/advanced"
        self.rate_limit = 1.0  # 1 second between requests
        self.last_request_time = 0
        
        self.document_content = self.load_document()
        self.categories = self.extract_categories()
        self.common_questions = self.generate_common_questions()
        self.country_requirements = self.extract_country_requirements()

    def call_api(self, messages: List[Dict[str, str]]) -> Dict:
        """Call the LLM API with rate limiting and retries"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.rate_limit:
            time.sleep(self.rate_limit - time_since_last_request)

        headers = {
            "accept": "application/json",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9",
            "authorization": f"Bearer {self.auth_token}",
            "content-type": "application/json",
            "cookie": "tosAccepted=true",
            "origin": "https://prod.ulchatbot.com",
            "referer": "https://prod.ulchatbot.com/",
            "sec-ch-ua": '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
        }
        
        payload = {
            "approach": "RetrieveThenRead",
            "userId": self.user_id,
            "conversationId": "d6929919-701d-4d12-7b57-08dd1f597649",
            "history": messages,
            "isRagUsed": False
        }

        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.post(self.base_url, headers=headers, json=payload)
                self.last_request_time = time.time()
                
                if response.status_code != 200:
                    logging.error(f"Response text: {response.text}")
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    logging.error(f"API request failed after {max_retries} attempts: {str(e)}")
                    raise
                time.sleep(1 * (attempt + 1))

    def get_llm_response(self, prompt: str) -> str:
        """Get response from LLM using the API"""
        messages = [{
            "role": "user",
            "content": prompt,
            "date": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }]
        
        try:
            response = self.call_api(messages)
            return response['choices'][0]['message']['content']
        except Exception as e:
            logging.error(f"Error getting LLM response: {str(e)}")
            return "I apologize, but I encountered an error processing your request. Please try again."

    def load_document(self) -> Dict[str, str]:
        """Load and parse the compliance plan document"""
        doc = docx.Document(self.doc_path)
        content = {}
        current_section = ""
        current_text = []
        
        for paragraph in doc.paragraphs:
            if paragraph.style.name.startswith('Heading'):
                if current_section and current_text:
                    content[current_section] = '\n'.join(current_text)
                current_section = paragraph.text
                current_text = []
            else:
                current_text.append(paragraph.text)
                
        if current_section and current_text:
            content[current_section] = '\n'.join(current_text)
            
        return content
    
    def extract_categories(self) -> List[str]:
        """Extract regulatory categories from the document"""
        categories = []
        overview_section = self.document_content.get('Regulatory Categories Overview', '')
        if overview_section:
            # Extract categories listed in the overview section
            lines = overview_section.split('\n')
            for line in lines:
                if line.strip() and not line.startswith('This compliance plan'):
                    categories.append(line.strip())
        return categories
    
    def extract_country_requirements(self) -> Dict[str, Dict[str, List[str]]]:
        """Extract country-specific requirements from the summary section"""
        requirements = {}
        
        for section, content in self.document_content.items():
            if section.endswith('Action Items'):
                country = section.replace(' Action Items', '')
                requirements[country] = defaultdict(list)
                
                current_category = None
                for line in content.split('\n'):
                    if line.strip():
                        if not line.startswith('•'):
                            current_category = line.strip()
                        else:
                            if current_category:
                                requirements[country][current_category].append(line.strip('• '))
                                
        return requirements
    
    def generate_common_questions(self) -> List[RegulatoryQuestion]:
        """Generate a list of common regulatory compliance questions"""
        questions = []
        
        # General template questions for each category
        for category in self.categories:
            questions.extend([
                RegulatoryQuestion(
                    category=category,
                    question=f"What are the {category.lower()} requirements for selling a cooktop in [COUNTRY]?",
                    context=f"Requirements under {category} category",
                    suggested_prompts=[
                        f"List all {category.lower()} requirements for [COUNTRY]",
                        f"What standards apply for {category.lower()} in [COUNTRY]?",
                        f"Are there any specific {category.lower()} certifications needed in [COUNTRY]?"
                    ]
                ),
                RegulatoryQuestion(
                    category=category,
                    question=f"What testing is required for {category.lower()} compliance in [COUNTRY]?",
                    context=f"Testing requirements under {category}",
                    suggested_prompts=[
                        f"Explain the testing process for {category.lower()} in [COUNTRY]",
                        f"What test standards apply for {category.lower()} in [COUNTRY]?",
                        f"Which labs can perform {category.lower()} testing in [COUNTRY]?"
                    ]
                )
            ])
            
        # Add specific questions based on common regulatory needs
        questions.extend([
            RegulatoryQuestion(
                category="General",
                question="What are the marking requirements for [COUNTRY]?",
                context="Product marking and labeling requirements",
                suggested_prompts=[
                    "List all required marks for [COUNTRY]",
                    "What information must be shown on the product label?",
                    "Are there language requirements for marking?"
                ]
            ),
            RegulatoryQuestion(
                category="Safety",
                question="What safety certifications are required in [COUNTRY]?",
                context="Safety certification requirements",
                suggested_prompts=[
                    "List mandatory safety certifications",
                    "What is the process to obtain safety certification?",
                    "Which certification bodies are accepted?"
                ]
            )
        ])
        
        return questions
    
    def get_suggested_questions(self, category: Optional[str] = None, country: Optional[str] = None) -> List[str]:
        """Get suggested questions based on category and/or country"""
        suggestions = []
        
        for question in self.common_questions:
            if (not category or question.category == category):
                if country:
                    suggestions.append(question.question.replace('[COUNTRY]', country))
                else:
                    suggestions.append(question.question)
                    
        return suggestions
    
    def get_answer(self, question: str) -> str:
        """Get answer for a specific question by searching the document content and using LLM"""
        # Extract country and category from question if present
        country_match = re.search(r'in\s+(\w+)', question)
        country = country_match.group(1) if country_match else None
        
        category_matches = [cat for cat in self.categories if cat.lower() in question.lower()]
        category = category_matches[0] if category_matches else None
        
        # Gather relevant information from the document
        context = []
        
        # Look in country-specific requirements first
        if country and category and country in self.country_requirements:
            country_reqs = self.country_requirements[country]
            if category in country_reqs:
                context.append(f"Requirements for {category} in {country}:\n" + "\n".join(country_reqs[category]))
        
        # Add relevant sections from detailed analysis
        for section, content in self.document_content.items():
            if (not category or category in section) and (not country or country in content):
                context.append(content)
        
        if not context:
            return "I could not find specific information for your question. Please try rephrasing or ask about a different aspect of regulatory compliance."
        
        # Create prompt for LLM
        prompt = f"""Based on the following regulatory compliance information:

{' '.join(context)}

Please answer this question: {question}

Provide a clear and concise answer focusing on specific requirements, standards, and actions needed. Use professional business language."""
        
        return self.get_llm_response(prompt)
    
    def suggest_related_questions(self, current_question: str) -> List[str]:
        """Suggest related questions based on the current question"""
        related = []
        
        # Extract context from current question
        country_match = re.search(r'in\s+(\w+)', current_question)
        country = country_match.group(1) if country_match else None
        
        category_matches = [cat for cat in self.categories if cat.lower() in current_question.lower()]
        category = category_matches[0] if category_matches else None
        
        # Get questions for the same category/country
        for question in self.common_questions:
            if category and question.category == category:
                if country:
                    related.append(question.question.replace('[COUNTRY]', country))
                else:
                    related.append(question.question)
                    
        return related[:5]  # Return top 5 related questions

if __name__ == "__main__":
    doc_path = r"C:\Users\104288\.cursor-tutor\Cursor_GCM\Multi_Country_Compliance_Plan.docx"
    auth_token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6InoxcnNZSEhKOS04bWdndDRIc1p1OEJLa0JQdyIsImtpZCI6InoxcnNZSEhKOS04bWdndDRIc1p1OEJLa0JQdyJ9.eyJhdWQiOiJhcGk6Ly83NzMxZWM3NC1mMWNhLTQxZDUtYTBlNS04MWY2ODM3YWMyNDciLCJpc3MiOiJodHRwczovL3N0cy53aW5kb3dzLm5ldC83MDExNTk1NC0wY2NkLTQ1ZjAtODdiZC0wM2IyYTM1ODc1NjkvIiwiaWF0IjoxNzM2NTM4MDA4LCJuYmYiOjE3MzY1MzgwMDgsImV4cCI6MTczNjU0MjUxNSwiYWNyIjoiMSIsImFpbyI6IkFWUUFxLzhZQUFBQTB3Q05FUDh0UEloOEMxMnJRbGhlbmhUeHV1MEFRNTU2K2JxQTkxbDBTNHNtSVN6WklJZXk2V1dkSTNHVzNXSkt5NHBSZldwMFJBMExyempsVS9QVWFLZzc3T0FmVGJYY1BEU0tVWE54ZkNvPSIsImFtciI6WyJwd2QiLCJyc2EiLCJtZmEiXSwiYXBwaWQiOiI3NzMxZWM3NC1mMWNhLTQxZDUtYTBlNS04MWY2ODM3YWMyNDciLCJhcHBpZGFjciI6IjAiLCJkZXZpY2VpZCI6IjMyOTk1Y2U1LTM0NjMtNGE4Yy1iM2MyLWFkNjRlZmY0ZjhkNyIsImZhbWlseV9uYW1lIjoiWWFuZyIsImdpdmVuX25hbWUiOiJKZW5ueSIsImlwYWRkciI6IjIwNS4xNzguMzAuNDUiLCJuYW1lIjoiWWFuZywgSmVubnkiLCJvaWQiOiI1YTVlNDNjNi0wMWEzLTQ4MjItOGE0My0yY2E2OThlYjViNTYiLCJvbnByZW1fc2lkIjoiUy0xLTUtMjEtMzYzODA4OTg2OC0zMDgxMTc1MTE1LTMxMzI5NzcyOS0zMjE1MzMiLCJyaCI6IjEuQVJzQVZGa1JjTTBNOEVXSHZRT3lvMWgxYVhUc01YZks4ZFZCb09XQjlvTjZ3a2NiQU9rYkFBLiIsInNjcCI6IkFwaS5SZWFkIiwic3ViIjoiRTFWeklZblc2RWI0aE5ZU0xZNE9LUTVBbXQ4SVBUaVRPWXZCSHZaNzYxZyIsInRpZCI6IjcwMTE1OTU0LTBjY2QtNDVmMC04N2JkLTAzYjJhMzU4NzU2OSIsInVuaXF1ZV9uYW1lIjoiMTA0Mjg4QGdsb2JhbC51bC5jb20iLCJ1cG4iOiIxMDQyODhAZ2xvYmFsLnVsLmNvbSIsInV0aSI6IndxTWFhaF9ndEVxNHNoMFVFQ1EtQUEiLCJ2ZXIiOiIxLjAifQ.eb8rDFkRtheAj_5PUoTjVVheDYXQuCBqGE0fQ9TbetFKWwfYfHCq09BufkUar6bm1im383Ldc_9Y2mngB69AvYflDQnJpw-FZmDxMWBPU7etisCO1P9j9SlIV18lm-jHMaOy23e33Deq70aZ5op3ecotRUANB2pTkrG8M8kG9dQSd1_m02iRFYhhCItJwAtVz6KFZeEdYG3xG9126dLBYOYJu3mQQ32DCUKPDZc4pQ9k-Hetb40OgGA-z1TMGBs_hySR7OYNgLnmx-7bjQQruEXKJj8D5PHLCXWhix6JqGB9CJdOLej5V53kRouNYpGNpIGcjo8Ro48fFvuWTkP7ag'
    user_id = '5a5e43c6-01a3-4822-8a43-2ca698eb5b56'
    
    bot = RegulatoryBot(doc_path, auth_token, user_id)
    
    # Example usage
    print("Available categories:", bot.categories)
    print("\nSuggested questions for Safety category:")
    print(bot.get_suggested_questions(category="Safety"))
    
    # Example question
    question = "What are the safety requirements for selling a cooktop in Finland?"
    print(f"\nQuestion: {question}")
    print("Answer:", bot.get_answer(question))
    print("\nRelated questions:", bot.suggest_related_questions(question)) 