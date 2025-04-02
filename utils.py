import uuid
import datetime
from typing import Dict, Any, Optional, List
import streamlit as st

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
    if not title or len(title.strip()) == 0:
        return {
            "valid": False,
            "message": "Task title cannot be empty"
        }
    
    if len(title) > 100:
        return {
            "valid": False,
            "message": "Task title is too long (maximum 100 characters)"
        }
    
    if not description or len(description.strip()) == 0:
        return {
            "valid": False,
            "message": "Task description cannot be empty"
        }
    
    return {
        "valid": True,
        "message": "Task data is valid"
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
        due_date = datetime.datetime.strptime(due_date_str, "%Y-%m-%d").date()
        today = datetime.date.today()
        days_remaining = (due_date - today).days
        
        if days_remaining < 0:
            return f"<span class='due-date due-date-overdue'>Overdue by {abs(days_remaining)} day{'s' if abs(days_remaining) != 1 else ''}</span>"
        elif days_remaining == 0:
            return "<span class='due-date due-date-today'>Due today</span>"
        elif days_remaining == 1:
            return "<span class='due-date due-date-today'>Due tomorrow</span>"
        elif days_remaining < 7:
            return f"<span class='due-date due-date-upcoming'>Due in {days_remaining} days</span>"
        else:
            return f"<span class='due-date'>Due in {days_remaining} days</span>"
    except (ValueError, TypeError):
        return "<span class='due-date'>Invalid date</span>"

def priority_color(priority: str) -> str:
    """
    Get the color code for a priority level.
    
    Args:
        priority: Priority level ("Low", "Medium", or "High")
        
    Returns:
        Color code for the priority
    """
    priority_colors = {
        "High": "#E74C3C",
        "Medium": "#F39C12",
        "Low": "#3498DB"
    }
    return priority_colors.get(priority, "#95A5A6")

def status_color(status: str) -> str:
    """
    Get the color code for a status.
    
    Args:
        status: Task status ("Not Started", "In Progress", or "Completed")
        
    Returns:
        Color code for the status
    """
    status_colors = {
        "Completed": "#2ECC71",
        "In Progress": "#3498DB",
        "Not Started": "#95A5A6"
    }
    return status_colors.get(status, "#95A5A6")

def format_tags(tags: Optional[List[str]]) -> str:
    """
    Format a list of tags as HTML.
    
    Args:
        tags: List of tag strings
        
    Returns:
        HTML-formatted tags
    """
    if not tags:
        return ""
    
    # Ensure tags is a list
    if isinstance(tags, str):
        tags = [tag.strip() for tag in tags.split(",") if tag.strip()]
    
    formatted_tags = ""
    for tag in tags:
        formatted_tags += f"<span class='tag'>{tag}</span> "
    
    return formatted_tags

def load_css() -> None:
    """
    Load custom CSS for the application.
    """
    with open("styles.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

def format_priority(priority: str) -> str:
    """
    Format a priority level as an HTML badge.
    
    Args:
        priority: Priority level ("Low", "Medium", or "High")
        
    Returns:
        HTML-formatted priority badge
    """
    priority_class = f"badge badge-{priority.lower()}"
    return f"<span class='{priority_class}'>{priority}</span>"

def format_status(status: str) -> str:
    """
    Format a status as an HTML badge.
    
    Args:
        status: Task status ("Not Started", "In Progress", or "Completed")
        
    Returns:
        HTML-formatted status badge
    """
    status_lower = status.lower().replace(" ", "-")
    status_class = f"badge badge-{status_lower}"
    return f"<span class='{status_class}'>{status}</span>"
