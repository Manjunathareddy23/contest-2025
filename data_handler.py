import os
import json
from typing import Dict, List, Any, Optional, Tuple
import datetime
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
import pandas as pd

class DatabaseHandler:
    """
    Handles all database operations for the task manager application.
    Responsible for loading, saving, filtering, and managing task data in PostgreSQL.
    """
    def __init__(self):
        """
        Initialize the database handler with the PostgreSQL connection.
        """
        self.conn = None
        self.metadata = sa.MetaData()
        self.engine = None
        self.tasks_table = None
        self._initialize_db()
    
    def _initialize_db(self) -> None:
        """
        Initialize the database connection and create the tasks table if it doesn't exist.
        """
        # Get PostgreSQL connection parameters from environment variables
        database_url = os.environ.get("DATABASE_URL")
        
        if not database_url:
            raise ValueError("DATABASE_URL environment variable is not set")
        
        # Create SQLAlchemy engine and connection
        self.engine = sa.create_engine(database_url)
        
        # Create the tasks table if it doesn't exist
        self.tasks_table = sa.Table(
            'tasks',
            self.metadata,
            sa.Column('id', sa.String(36), primary_key=True),
            sa.Column('title', sa.String(100), nullable=False),
            sa.Column('description', sa.Text, nullable=False),
            sa.Column('priority', sa.String(20), nullable=False, default='Medium'),
            sa.Column('status', sa.String(20), nullable=False, default='Not Started'),
            sa.Column('due_date', sa.Date, nullable=True),
            sa.Column('tags', JSONB, nullable=True),
            sa.Column('assigned_to', sa.String(100), nullable=True),
            sa.Column('created_at', sa.DateTime, default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime, default=sa.func.now(), onupdate=sa.func.now()),
            sa.Column('completed_at', sa.DateTime, nullable=True),
            sa.Column('recurring', sa.Boolean, default=False),
            sa.Column('recurring_pattern', sa.String(50), nullable=True),
            sa.Column('metadata', JSONB, nullable=True)
        )
        
        # Create the table if it doesn't exist
        self.metadata.create_all(self.engine)
    
    def _open_connection(self):
        """Open a connection to the database."""
        if self.conn is None or self.conn.closed:
            self.conn = self.engine.connect()
        return self.conn
    
    def _close_connection(self):
        """Close the database connection."""
        if self.conn is not None and not self.conn.closed:
            self.conn.close()
    
    def get_all_tasks(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all tasks from the database.
        
        Returns:
            Dictionary of all tasks with task IDs as keys
        """
        try:
            self._open_connection()
            
            # Query all tasks
            query = sa.select(self.tasks_table)
            result = self.conn.execute(query)
            
            # Convert rows to dictionary
            tasks = {}
            for row in result:
                task_dict = dict(row)
                
                # Convert date objects to strings for JSON serialization
                if task_dict.get('due_date'):
                    task_dict['due_date'] = task_dict['due_date'].strftime('%Y-%m-%d')
                
                if task_dict.get('created_at'):
                    task_dict['created_at'] = task_dict['created_at'].strftime('%Y-%m-%d %H:%M:%S')
                
                if task_dict.get('updated_at'):
                    task_dict['updated_at'] = task_dict['updated_at'].strftime('%Y-%m-%d %H:%M:%S')
                
                if task_dict.get('completed_at') and task_dict['completed_at'] is not None:
                    task_dict['completed_at'] = task_dict['completed_at'].strftime('%Y-%m-%d %H:%M:%S')
                
                # Add to tasks dictionary
                tasks[task_dict['id']] = task_dict
            
            return tasks
        except Exception as e:
            print(f"Error getting all tasks: {e}")
            return {}
        finally:
            self._close_connection()
    
    def get_task_by_id(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a task by its ID.
        
        Args:
            task_id: The ID of the task to retrieve
            
        Returns:
            The task data or None if not found
        """
        try:
            self._open_connection()
            
            # Query for the specific task
            query = sa.select(self.tasks_table).where(self.tasks_table.c.id == task_id)
            result = self.conn.execute(query)
            row = result.fetchone()
            
            if row:
                task_dict = dict(row)
                
                # Convert date objects to strings for JSON serialization
                if task_dict.get('due_date'):
                    task_dict['due_date'] = task_dict['due_date'].strftime('%Y-%m-%d')
                
                if task_dict.get('created_at'):
                    task_dict['created_at'] = task_dict['created_at'].strftime('%Y-%m-%d %H:%M:%S')
                
                if task_dict.get('updated_at'):
                    task_dict['updated_at'] = task_dict['updated_at'].strftime('%Y-%m-%d %H:%M:%S')
                
                if task_dict.get('completed_at') and task_dict['completed_at'] is not None:
                    task_dict['completed_at'] = task_dict['completed_at'].strftime('%Y-%m-%d %H:%M:%S')
                
                return task_dict
            
            return None
        except Exception as e:
            print(f"Error getting task by ID: {e}")
            return None
        finally:
            self._close_connection()
    
    def add_task(self, task_id: str, task_data: Dict[str, Any]) -> None:
        """
        Add a new task to the database.
        
        Args:
            task_id: Unique ID for the task
            task_data: Dictionary containing task details
        """
        try:
            self._open_connection()
            
            # Process due date
            due_date = task_data.get('due_date')
            if due_date and isinstance(due_date, str):
                try:
                    due_date = datetime.datetime.strptime(due_date, '%Y-%m-%d').date()
                except ValueError:
                    due_date = None
            
            # Process tags (ensure they're stored as JSON)
            tags = task_data.get('tags', [])
            if isinstance(tags, str):
                # Convert comma-separated string to list
                tags = [tag.strip() for tag in tags.split(',') if tag.strip()]
            
            # Prepare data for insertion
            insert_data = {
                'id': task_id,
                'title': task_data.get('title', ''),
                'description': task_data.get('description', ''),
                'priority': task_data.get('priority', 'Medium'),
                'status': task_data.get('status', 'Not Started'),
                'due_date': due_date,
                'tags': tags,
                'assigned_to': task_data.get('assigned_to'),
                'recurring': task_data.get('recurring', False),
                'recurring_pattern': task_data.get('recurring_pattern'),
                'metadata': task_data.get('metadata', {})
            }
            
            # Insert the task
            insert_stmt = self.tasks_table.insert().values(**insert_data)
            self.conn.execute(insert_stmt)
            
        except Exception as e:
            print(f"Error adding task: {e}")
        finally:
            self._close_connection()
    
    def update_task(self, task_id: str, task_data: Dict[str, Any]) -> bool:
        """
        Update an existing task in the database.
        
        Args:
            task_id: ID of the task to update
            task_data: New task data
            
        Returns:
            True if update was successful, False otherwise
        """
        try:
            self._open_connection()
            
            # Process due date
            due_date = task_data.get('due_date')
            if due_date and isinstance(due_date, str):
                try:
                    due_date = datetime.datetime.strptime(due_date, '%Y-%m-%d').date()
                except ValueError:
                    due_date = None
            
            # Process tags (ensure they're stored as JSON)
            tags = task_data.get('tags', [])
            if isinstance(tags, str):
                # Convert comma-separated string to list
                tags = [tag.strip() for tag in tags.split(',') if tag.strip()]
            
            # Check if task is being marked as completed
            completed_at = None
            if task_data.get('status') == 'Completed':
                # Check if the status has changed
                current_task = self.get_task_by_id(task_id)
                if current_task and current_task.get('status') != 'Completed':
                    completed_at = datetime.datetime.now()
            
            # Prepare data for update
            update_data = {
                'title': task_data.get('title'),
                'description': task_data.get('description'),
                'priority': task_data.get('priority'),
                'status': task_data.get('status'),
                'due_date': due_date,
                'tags': tags,
                'assigned_to': task_data.get('assigned_to'),
                'recurring': task_data.get('recurring'),
                'recurring_pattern': task_data.get('recurring_pattern'),
                'metadata': task_data.get('metadata')
            }
            
            if completed_at:
                update_data['completed_at'] = completed_at
            
            # Remove None values to avoid overwriting existing data with NULL
            update_data = {k: v for k, v in update_data.items() if v is not None}
            
            # Update the task
            update_stmt = self.tasks_table.update().where(self.tasks_table.c.id == task_id).values(**update_data)
            result = self.conn.execute(update_stmt)
            
            return result.rowcount > 0
        except Exception as e:
            print(f"Error updating task: {e}")
            return False
        finally:
            self._close_connection()
    
    def delete_task(self, task_id: str) -> bool:
        """
        Delete a task by its ID from the database.
        
        Args:
            task_id: ID of the task to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            self._open_connection()
            
            # Delete the task
            delete_stmt = self.tasks_table.delete().where(self.tasks_table.c.id == task_id)
            result = self.conn.execute(delete_stmt)
            
            return result.rowcount > 0
        except Exception as e:
            print(f"Error deleting task: {e}")
            return False
        finally:
            self._close_connection()
    
    def get_all_tags(self) -> List[str]:
        """
        Get a list of all unique tags across all tasks.
        
        Returns:
            List of unique tags
        """
        try:
            all_tasks = self.get_all_tasks()
            
            # Extract all tags from all tasks
            all_tags = []
            for task in all_tasks.values():
                tags = task.get('tags', [])
                if isinstance(tags, list):
                    all_tags.extend(tags)
                elif isinstance(tags, str) and tags:
                    # Handle case where tags might be stored as comma-separated string
                    tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
                    all_tags.extend(tag_list)
            
            # Return unique tags
            return sorted(list(set(all_tags)))
        except Exception as e:
            print(f"Error getting all tags: {e}")
            return []
    
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
        try:
            # Get all tasks first
            all_tasks = self.get_all_tasks()
            filtered_tasks = {}
            
            # Apply filters
            for task_id, task in all_tasks.items():
                # Apply search query filter
                if search_query and not (
                    search_query.lower() in task.get('title', '').lower() or 
                    search_query.lower() in task.get('description', '').lower()
                ):
                    continue
                
                # Apply tag filter
                if filter_tag:
                    tags = task.get('tags', [])
                    if isinstance(tags, str):
                        tags = [tag.strip() for tag in tags.split(',') if tag.strip()]
                    
                    if filter_tag not in tags:
                        continue
                
                # Add task to filtered results
                filtered_tasks[task_id] = task
            
            # Sort tasks
            if sort_by == "Priority":
                # Define priority order for sorting
                priority_order = {"High": 0, "Medium": 1, "Low": 2}
                sorted_tasks = sorted(
                    filtered_tasks.items(),
                    key=lambda x: priority_order.get(x[1].get('priority', 'Medium'), 1)
                )
            elif sort_by == "Due Date":
                # Sort by due date (None values at the end)
                def get_due_date(task):
                    due_date_str = task[1].get('due_date')
                    if not due_date_str:
                        return datetime.date.max
                    try:
                        return datetime.datetime.strptime(due_date_str, '%Y-%m-%d').date()
                    except ValueError:
                        return datetime.date.max
                
                sorted_tasks = sorted(filtered_tasks.items(), key=get_due_date)
            elif sort_by == "Status":
                # Define status order for sorting
                status_order = {"Not Started": 0, "In Progress": 1, "Completed": 2}
                sorted_tasks = sorted(
                    filtered_tasks.items(),
                    key=lambda x: status_order.get(x[1].get('status', 'Not Started'), 0)
                )
            else:
                # Default to priority sorting
                priority_order = {"High": 0, "Medium": 1, "Low": 2}
                sorted_tasks = sorted(
                    filtered_tasks.items(),
                    key=lambda x: priority_order.get(x[1].get('priority', 'Medium'), 1)
                )
            
            # Convert sorted list back to dictionary
            return {k: v for k, v in sorted_tasks}
        except Exception as e:
            print(f"Error filtering tasks: {e}")
            return {}
    
    def import_from_json(self, json_file_path: str) -> bool:
        """
        Import tasks from a JSON file to the database.
        
        Args:
            json_file_path: Path to the JSON file to import
            
        Returns:
            True if import was successful, False otherwise
        """
        try:
            with open(json_file_path, 'r') as f:
                tasks = json.load(f)
            
            # Add each task to the database
            for task_id, task_data in tasks.items():
                self.add_task(task_id, task_data)
            
            return True
        except Exception as e:
            print(f"Error importing tasks from JSON: {e}")
            return False
    
    def get_task_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the tasks.
        
        Returns:
            Dictionary with task statistics
        """
        try:
            all_tasks = self.get_all_tasks()
            
            # Count tasks by status
            status_counts = {"Not Started": 0, "In Progress": 0, "Completed": 0}
            for task in all_tasks.values():
                status = task.get('status', 'Not Started')
                status_counts[status] = status_counts.get(status, 0) + 1
            
            # Count tasks by priority
            priority_counts = {"High": 0, "Medium": 0, "Low": 0}
            for task in all_tasks.values():
                priority = task.get('priority', 'Medium')
                priority_counts[priority] = priority_counts.get(priority, 0) + 1
            
            # Count overdue tasks
            today = datetime.date.today()
            overdue_count = 0
            due_soon_count = 0
            
            for task in all_tasks.values():
                if task.get('status') == 'Completed':
                    continue
                
                due_date_str = task.get('due_date')
                if due_date_str:
                    try:
                        due_date = datetime.datetime.strptime(due_date_str, '%Y-%m-%d').date()
                        if due_date < today:
                            overdue_count += 1
                        elif due_date <= today + datetime.timedelta(days=3):
                            due_soon_count += 1
                    except ValueError:
                        pass
            
            return {
                'total_tasks': len(all_tasks),
                'status_counts': status_counts,
                'priority_counts': priority_counts,
                'overdue_count': overdue_count,
                'due_soon_count': due_soon_count
            }
        except Exception as e:
            print(f"Error getting task statistics: {e}")
            return {
                'total_tasks': 0,
                'status_counts': {"Not Started": 0, "In Progress": 0, "Completed": 0},
                'priority_counts': {"High": 0, "Medium": 0, "Low": 0},
                'overdue_count': 0,
                'due_soon_count': 0
            }
    
    def export_to_pandas(self) -> pd.DataFrame:
        """
        Export tasks to a pandas DataFrame for analytics.
        
        Returns:
            DataFrame containing all tasks
        """
        try:
            all_tasks = self.get_all_tasks()
            
            # Create a list of dictionaries for pandas
            task_list = list(all_tasks.values())
            
            # Convert to DataFrame
            df = pd.DataFrame(task_list)
            
            return df
        except Exception as e:
            print(f"Error exporting to pandas DataFrame: {e}")
            return pd.DataFrame()
