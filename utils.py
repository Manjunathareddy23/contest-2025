import uuid
import datetime
from typing import Dict, Any

def generate_unique_id() -> str:
    """
    Generate a unique identifier for a task.
    
    Returns:
        A unique string ID
    """
    return str(uuid.uuid4())

def get_default_due_date() -> datetime.date:
    """
    Get a default due date for new tasks (one week from today).
    
    Returns:
        Date object for the default due date
    """
    return datetime.date.today() + datetime.timedelta(days=7)

def validate_task_input(title: str, description: str) -> Dict[str, Any]:
    """
    Validate task input data.
    
    Args:
        title: Task title
        description: Task description
        
    Returns:
        Dictionary with validation result and message
    """
    if not title:
        return {
            "valid": False,
            "message": "Title is required"
        }
    
    if len(title) > 100:
        return {
            "valid": False,
            "message": "Title must be 100 characters or less"
        }
    
    if len(description) > 1000:
        return {
            "valid": False,
            "message": "Description must be 1000 characters or less"
        }
    
    return {
        "valid": True,
        "message": "Validation successful"
    }

def format_remaining_days(due_date_str: str) -> str:
    """
    Format the number of days remaining until the due date.
    
    Args:
        due_date_str: Due date as a string in format 'YYYY-MM-DD'
        
    Returns:
        Formatted string describing days remaining
    """
    try:
        due_date = datetime.datetime.strptime(due_date_str, '%Y-%m-%d').date()
        today = datetime.date.today()
        days_remaining = (due_date - today).days
        
        if days_remaining < 0:
            return f"Overdue by {abs(days_remaining)} days"
        elif days_remaining == 0:
            return "Due today"
        elif days_remaining == 1:
            return "Due tomorrow"
        else:
            return f"{days_remaining} days left"
    except (ValueError, TypeError):
        return "No due date"

def priority_color(priority: str) -> str:
    """
    Get the color code for a priority level.
    
    Args:
        priority: Priority level ("Low", "Medium", or "High")
        
    Returns:
        Color code for the priority
    """
    return {
        "Low": "#4286f4",      # Blue
        "Medium": "#f49e42",   # Orange
        "High": "#f44242"      # Red
    }.get(priority, "#888888") # Default gray

def status_color(status: str) -> str:
    """
    Get the color code for a status.
    
    Args:
        status: Task status ("Not Started", "In Progress", or "Completed")
        
    Returns:
        Color code for the status
    """
    return {
        "Not Started": "#888888",  # Gray
        "In Progress": "#4286f4",  # Blue
        "Completed": "#42f48f"     # Green
    }.get(status, "#888888")       # Default gray
