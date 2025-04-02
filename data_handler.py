import os
import json
import datetime
import pandas as pd
from typing import Dict, List, Optional, Any

class DataHandler:
    """
    Handles all data operations for the task manager application.
    Responsible for loading, saving, filtering, and managing task data.
    """
    def __init__(self, data_file: str = "tasks.json"):
        """
        Initialize the data handler with the specified data file.
        
        Args:
            data_file: Path to the JSON file for storing tasks
        """
        self.data_file = data_file
        self.tasks = self._load_tasks()
    
    def _load_tasks(self) -> Dict[str, Dict[str, Any]]:
        """
        Load tasks from the JSON file.
        
        Returns:
            Dictionary of tasks with task IDs as keys
        """
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as file:
                    return json.load(file)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading tasks: {e}")
                return {}
        return {}
    
    def _save_tasks(self) -> None:
        """
        Save tasks to the JSON file.
        """
        try:
            with open(self.data_file, 'w') as file:
                json.dump(self.tasks, file, indent=4)
        except IOError as e:
            print(f"Error saving tasks: {e}")
    
    def get_all_tasks(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all tasks.
        
        Returns:
            Dictionary of all tasks
        """
        return self.tasks
    
    def get_task_by_id(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a task by its ID.
        
        Args:
            task_id: The ID of the task to retrieve
            
        Returns:
            The task data or None if not found
        """
        return self.tasks.get(task_id)
    
    def add_task(self, task_id: str, task_data: Dict[str, Any]) -> None:
        """
        Add a new task.
        
        Args:
            task_id: Unique ID for the task
            task_data: Dictionary containing task details
        """
        # Add created_date if not present
        if 'created_date' not in task_data:
            task_data['created_date'] = datetime.datetime.now().strftime('%Y-%m-%d')
        
        self.tasks[task_id] = task_data
        self._save_tasks()
    
    def update_task(self, task_id: str, task_data: Dict[str, Any]) -> bool:
        """
        Update an existing task.
        
        Args:
            task_id: ID of the task to update
            task_data: New task data
            
        Returns:
            True if update was successful, False otherwise
        """
        if task_id in self.tasks:
            # Preserve created_date if it exists
            if 'created_date' in self.tasks[task_id]:
                task_data['created_date'] = self.tasks[task_id]['created_date']
            
            self.tasks[task_id] = task_data
            self._save_tasks()
            return True
        return False
    
    def delete_task(self, task_id: str) -> bool:
        """
        Delete a task by its ID.
        
        Args:
            task_id: ID of the task to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        if task_id in self.tasks:
            del self.tasks[task_id]
            self._save_tasks()
            return True
        return False
    
    def get_all_tags(self) -> List[str]:
        """
        Get a list of all unique tags across all tasks.
        
        Returns:
            List of unique tags
        """
        all_tags = set()
        for task in self.tasks.values():
            tags = task.get('tags', [])
            all_tags.update(tags)
        return sorted(list(all_tags))
    
    def get_filtered_tasks(self, 
                           search_query: str = "", 
                           filter_tag: Optional[str] = None,
                           sort_by: str = "Priority") -> Dict[str, Dict[str, Any]]:
        """
        Get tasks filtered by search query and tag, and sorted by the specified criterion.
        
        Args:
            search_query: String to search in task title and description
            filter_tag: Tag to filter tasks by
            sort_by: Criterion to sort tasks by ("Priority", "Due Date", or "Status")
            
        Returns:
            Dictionary of filtered and sorted tasks
        """
        filtered_tasks = {}
        
        # Filter tasks
        for task_id, task in self.tasks.items():
            # Search filter
            if search_query:
                title = task.get('title', '').lower()
                description = task.get('description', '').lower()
                if search_query.lower() not in title and search_query.lower() not in description:
                    continue
            
            # Tag filter
            if filter_tag:
                tags = task.get('tags', [])
                if filter_tag not in tags:
                    continue
            
            filtered_tasks[task_id] = task
        
        # Convert to DataFrame for easier sorting
        if filtered_tasks:
            df = pd.DataFrame.from_dict(filtered_tasks, orient='index')
            
            # Sort tasks
            if sort_by == "Priority":
                priority_order = {"High": 0, "Medium": 1, "Low": 2}
                df['priority_order'] = df['priority'].map(priority_order)
                df = df.sort_values('priority_order')
                df = df.drop('priority_order', axis=1)
            elif sort_by == "Due Date":
                df['due_date_parsed'] = pd.to_datetime(df['due_date'], errors='coerce')
                df = df.sort_values('due_date_parsed')
                df = df.drop('due_date_parsed', axis=1)
            elif sort_by == "Status":
                status_order = {"Not Started": 0, "In Progress": 1, "Completed": 2}
                df['status_order'] = df['status'].map(status_order)
                df = df.sort_values('status_order')
                df = df.drop('status_order', axis=1)
            
            # Convert back to dictionary
            return df.to_dict(orient='index')
        
        return filtered_tasks
