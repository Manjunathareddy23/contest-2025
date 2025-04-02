import os
import google.generativeai as genai
from typing import Dict, List, Any, Optional

# Configure the Gemini API with the key
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

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
        
        Args:
            description: The task description to analyze
            
        Returns:
            Dictionary with suggestions
        """
        if not description or len(description) < 5:
            return {"success": False, "message": "Description too short for analysis"}
        
        try:
            prompt = f"""
            Analyze the following task description and provide:
            1. Suggested priority (High, Medium, or Low)
            2. 2-3 relevant tags (single words or short phrases)
            3. Estimated effort (Easy, Medium, Hard)
            4. A brief one-sentence summary
            
            Task Description: {description}
            
            Format your response as a JSON object with fields: priority, tags, effort, summary.
            Only include these fields, no explanation or additional text.
            """
            
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            # Extract JSON content (simple parsing) - in a real app, use json.loads
            # with proper error handling
            try:
                # Clean the response (remove markdown code blocks if present)
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0].strip()
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].split("```")[0].strip()
                
                # Very basic JSON parsing - in production use json.loads with try/except
                response_dict = {}
                lines = response_text.strip().strip("{").strip("}").split(",")
                for line in lines:
                    if ":" in line:
                        key, value = line.split(":", 1)
                        key = key.strip().strip('"')
                        value = value.strip().strip('"')
                        
                        if key == "tags":
                            # Parse tags list
                            if "[" in value and "]" in value:
                                tags_str = value.strip().strip("[").strip("]")
                                tags = [tag.strip().strip('"') for tag in tags_str.split(",")]
                                response_dict[key] = tags
                            else:
                                response_dict[key] = [value]
                        else:
                            response_dict[key] = value
                
                # Validate response has expected fields
                if "priority" in response_dict and "tags" in response_dict and "effort" in response_dict:
                    return {
                        "success": True,
                        "suggestions": response_dict
                    }
                else:
                    return {"success": False, "message": "Invalid AI response format"}
                
            except Exception as e:
                return {"success": False, "message": f"Error parsing AI response: {e}"}
            
        except Exception as e:
            return {"success": False, "message": f"AI analysis error: {e}"}
    
    def suggest_task_improvements(self, title: str, description: str) -> Dict[str, Any]:
        """
        Suggest improvements for a task's title and description.
        
        Args:
            title: The task title
            description: The task description
            
        Returns:
            Dictionary with suggested improvements
        """
        if not title or not description:
            return {"success": False, "message": "Both title and description are required"}
        
        try:
            prompt = f"""
            Review the following task title and description and suggest improvements for clarity,
            specificity, and actionability:
            
            Title: {title}
            Description: {description}
            
            Provide suggestions for:
            1. An improved title (if needed)
            2. An improved description (if needed)
            3. A specific recommendation to make the task more actionable
            
            Keep suggestions concise and practical.
            """
            
            response = self.model.generate_content(prompt)
            
            return {
                "success": True,
                "suggestions": response.text
            }
        except Exception as e:
            return {"success": False, "message": f"AI suggestion error: {e}"}
    
    def prioritize_tasks(self, tasks: List[Dict[str, Any]], context: str = "") -> Dict[str, Any]:
        """
        Suggest task prioritization based on due dates, status, and task content.
        
        Args:
            tasks: List of task dictionaries
            context: Optional contextual information about current priorities
            
        Returns:
            Dictionary with prioritization suggestions
        """
        if not tasks:
            return {"success": False, "message": "No tasks provided for prioritization"}
        
        try:
            # Create a simplified task list for the prompt
            task_list = []
            for i, task in enumerate(tasks):
                task_info = f"""
                Task {i+1}:
                - Title: {task.get('title', 'No title')}
                - Priority: {task.get('priority', 'Not set')}
                - Status: {task.get('status', 'Not set')}
                - Due date: {task.get('due_date', 'Not set')}
                - Description: {task.get('description', 'No description')}
                """
                task_list.append(task_info)
            
            tasks_text = "\n".join(task_list)
            
            prompt = f"""
            Review the following list of tasks and suggest a prioritized order based on:
            - Due dates (more urgent dates are higher priority)
            - Current status
            - Task content and importance
            
            {tasks_text}
            
            Additional context: {context}
            
            Provide your response as a numbered list of tasks in recommended priority order,
            with a brief explanation for each prioritization decision.
            """
            
            response = self.model.generate_content(prompt)
            
            return {
                "success": True,
                "prioritization": response.text
            }
        except Exception as e:
            return {"success": False, "message": f"AI prioritization error: {e}"}
    
    def generate_weekly_summary(self, completed_tasks: List[Dict[str, Any]], 
                               pending_tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a weekly summary of completed and pending tasks.
        
        Args:
            completed_tasks: List of completed task dictionaries
            pending_tasks: List of pending task dictionaries
            
        Returns:
            Dictionary with the summary
        """
        if not completed_tasks and not pending_tasks:
            return {"success": False, "message": "No tasks provided for summary"}
        
        try:
            # Prepare completed tasks
            completed_list = []
            for task in completed_tasks:
                task_info = f"- {task.get('title', 'Unnamed task')}"
                completed_list.append(task_info)
            
            # Prepare pending tasks
            pending_list = []
            for task in pending_tasks:
                task_info = f"- {task.get('title', 'Unnamed task')} (Due: {task.get('due_date', 'Not set')})"
                pending_list.append(task_info)
            
            completed_text = "\n".join(completed_list) if completed_list else "None"
            pending_text = "\n".join(pending_list) if pending_list else "None"
            
            prompt = f"""
            Generate a concise weekly summary based on the following tasks:
            
            Completed tasks:
            {completed_text}
            
            Pending tasks:
            {pending_text}
            
            Include:
            1. A summary of achievements (based on completed tasks)
            2. Key priorities for the upcoming week (based on pending tasks)
            3. A productivity tip relevant to the pending tasks
            
            Keep the summary professional, motivating, and brief.
            """
            
            response = self.model.generate_content(prompt)
            
            return {
                "success": True,
                "summary": response.text
            }
        except Exception as e:
            return {"success": False, "message": f"AI summary error: {e}"}

def check_ai_available() -> bool:
    """
    Check if the Gemini API is available and properly configured.
    
    Returns:
        True if API is available, False otherwise
    """
    try:
        # Check if API key is present
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            return False
        
        # Try a simple API call
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Respond with only the word 'working' if you can read this.")
        return "working" in response.text.lower()
    except Exception:
        return False
