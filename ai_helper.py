import os
import google.generativeai as genai
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure the Gemini API with the key from .env
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found. Please check your .env file.")

genai.configure(api_key=GEMINI_API_KEY)

class AiTaskHelper:
    """
    A helper class that uses Google's Gemini AI to enhance the task management experience.
    """
    def __init__(self):
        """Initialize the AI helper with the Gemini model."""
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def analyze_task_description(self, description: str) -> Dict[str, Any]:
        """
        Analyze a task description to suggest priority, tags, and estimated effort.
        """
        if not description or len(description) < 5:
            return {"success": False, "message": "Description too short for analysis"}

        prompt = f"""
        Analyze the following task description and provide:
        1. Suggested priority (High, Medium, or Low)
        2. 2-3 relevant tags (single words or short phrases)
        3. Estimated effort (Easy, Medium, Hard)
        4. A brief one-sentence summary
        
        Task Description: {description}
        
        Format your response as a JSON object with fields: priority, tags, effort, summary.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return {"success": True, "suggestions": response.text}
        except Exception as e:
            return {"success": False, "message": f"AI analysis error: {e}"}

def check_ai_available() -> bool:
    """
    Check if the Gemini API is available and properly configured.
    """
    try:
        if not GEMINI_API_KEY:
            return False
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Respond with only the word 'working' if you can read this.")
        return "working" in response.text.lower()
    except Exception:
        return False
