import streamlit as st
import pandas as pd
import datetime
from data_handler import DataHandler
from utils import generate_unique_id, get_default_due_date, validate_task_input
from task_visualizer import create_task_visualizations

# Page configuration
st.set_page_config(
    page_title="Advanced Task Manager",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables if they don't exist
if 'edit_task_id' not in st.session_state:
    st.session_state.edit_task_id = None
if 'show_delete_confirmation' not in st.session_state:
    st.session_state.show_delete_confirmation = False
if 'delete_task_id' not in st.session_state:
    st.session_state.delete_task_id = None
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""
if 'filter_tag' not in st.session_state:
    st.session_state.filter_tag = "All"
if 'sort_by' not in st.session_state:
    st.session_state.sort_by = "Priority"
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = "Tasks"

# Initialize data handler
data_handler = DataHandler()

# Application header
st.title("Advanced Task Manager")

# Sidebar navigation
with st.sidebar:
    st.header("Navigation")
    view_options = ["Tasks", "Statistics"]
    view_mode = st.radio("View", view_options, index=view_options.index(st.session_state.view_mode))
    
    if view_mode != st.session_state.view_mode:
        st.session_state.view_mode = view_mode
        # Reset editing states when switching views
        st.session_state.edit_task_id = None
        st.session_state.show_delete_confirmation = False
        st.session_state.delete_task_id = None
        st.rerun()

# Tasks view
if st.session_state.view_mode == "Tasks":
    # Task creation section
    with st.expander("Create New Task", expanded=st.session_state.edit_task_id is None):
        with st.form(key="task_form", clear_on_submit=True):
            # Task input fields
            title = st.text_input("Title", value="" if st.session_state.edit_task_id is None else 
                               data_handler.get_task_by_id(st.session_state.edit_task_id).get('title', ''))
            
            description = st.text_area("Description", value="" if st.session_state.edit_task_id is None else 
                                   data_handler.get_task_by_id(st.session_state.edit_task_id).get('description', ''))
            
            col1, col2 = st.columns(2)
            with col1:
                priority_options = ["Low", "Medium", "High"]
                priority = st.selectbox("Priority", 
                                     options=priority_options, 
                                     index=0 if st.session_state.edit_task_id is None else 
                                     priority_options.index(data_handler.get_task_by_id(st.session_state.edit_task_id).get('priority', 'Low')))
            
            with col2:
                status_options = ["Not Started", "In Progress", "Completed"]
                status = st.selectbox("Status", 
                                   options=status_options, 
                                   index=0 if st.session_state.edit_task_id is None else 
                                   status_options.index(data_handler.get_task_by_id(st.session_state.edit_task_id).get('status', 'Not Started')))
            
            # Due date handling
            default_date = get_default_due_date()
            if st.session_state.edit_task_id is not None:
                task = data_handler.get_task_by_id(st.session_state.edit_task_id)
                if task and 'due_date' in task:
                    try:
                        default_date = datetime.datetime.strptime(task['due_date'], '%Y-%m-%d').date()
                    except ValueError:
                        pass
            
            due_date = st.date_input("Due Date", value=default_date)
            
            # Tags input
            tags_input = st.text_input("Tags (comma separated)", 
                                    value="" if st.session_state.edit_task_id is None else 
                                    ", ".join(data_handler.get_task_by_id(st.session_state.edit_task_id).get('tags', [])))
            
            # Form submit buttons
            col1, col2 = st.columns(2)
            with col1:
                submit_button = st.form_submit_button("Save Task")
            
            with col2:
                if st.session_state.edit_task_id is not None:
                    cancel_button = st.form_submit_button("Cancel")
                    if cancel_button:
                        st.session_state.edit_task_id = None
                        st.rerun()
            
            # Process form submission
            if submit_button:
                # Validate input
                validation_result = validate_task_input(title, description)
                if validation_result["valid"]:
                    # Process tags
                    tags = [tag.strip() for tag in tags_input.split(",")] if tags_input else []
                    tags = [tag for tag in tags if tag]  # Remove empty tags
                    
                    task_data = {
                        "title": title,
                        "description": description,
                        "priority": priority,
                        "status": status,
                        "due_date": due_date.strftime('%Y-%m-%d'),
                        "tags": tags
                    }
                    
                    # Save or update task
                    if st.session_state.edit_task_id is not None:
                        data_handler.update_task(st.session_state.edit_task_id, task_data)
                        st.success(f"Task '{title}' updated successfully!")
                        st.session_state.edit_task_id = None
                    else:
                        task_id = generate_unique_id()
                        data_handler.add_task(task_id, task_data)
                        st.success(f"Task '{title}' created successfully!")
                    
                    st.rerun()
                else:
                    st.error(validation_result["message"])

    # Search and filter section
    st.subheader("Search and Filter Tasks")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_query = st.text_input("Search by title or description", value=st.session_state.search_query)
        if search_query != st.session_state.search_query:
            st.session_state.search_query = search_query
            st.rerun()
    
    with col2:
        all_tags = data_handler.get_all_tags()
        tag_options = ["All"] + all_tags
        filter_tag = st.selectbox("Filter by tag", options=tag_options, index=tag_options.index(st.session_state.filter_tag) if st.session_state.filter_tag in tag_options else 0)
        if filter_tag != st.session_state.filter_tag:
            st.session_state.filter_tag = filter_tag
            st.rerun()
    
    with col3:
        sort_options = ["Priority", "Due Date", "Status"]
        sort_by = st.selectbox("Sort by", options=sort_options, index=sort_options.index(st.session_state.sort_by))
        if sort_by != st.session_state.sort_by:
            st.session_state.sort_by = sort_by
            st.rerun()

    # Task display section
    st.subheader("Your Tasks")
    
    # Get filtered and sorted tasks
    filtered_tasks = data_handler.get_filtered_tasks(
        search_query=st.session_state.search_query,
        filter_tag=st.session_state.filter_tag if st.session_state.filter_tag != "All" else None,
        sort_by=st.session_state.sort_by
    )
    
    if not filtered_tasks:
        st.info("No tasks found. Create a new task to get started!")
    else:
        # Display tasks
        for task_id, task in filtered_tasks.items():
            with st.container():
                col1, col2, col3 = st.columns([5, 2, 1])
                
                # Task title and description
                with col1:
                    title_markdown = f"### {task['title']}"
                    if task['status'] == 'Completed':
                        title_markdown = f"### ~~{task['title']}~~"
                    st.markdown(title_markdown)
                    
                    st.write(task['description'])
                    
                    # Display tags
                    if task.get('tags'):
                        st.write("Tags: " + ", ".join([f"`{tag}`" for tag in task['tags']]))
                
                # Task details
                with col2:
                    priority_color = {
                        "Low": "blue",
                        "Medium": "orange",
                        "High": "red"
                    }.get(task['priority'], "gray")
                    
                    status_color = {
                        "Not Started": "gray",
                        "In Progress": "blue",
                        "Completed": "green"
                    }.get(task['status'], "gray")
                    
                    st.markdown(f"**Priority:** <span style='color:{priority_color}'>{task['priority']}</span>", unsafe_allow_html=True)
                    st.markdown(f"**Status:** <span style='color:{status_color}'>{task['status']}</span>", unsafe_allow_html=True)
                    
                    # Calculate days remaining
                    try:
                        due_date = datetime.datetime.strptime(task['due_date'], '%Y-%m-%d').date()
                        today = datetime.date.today()
                        days_remaining = (due_date - today).days
                        
                        if days_remaining < 0:
                            st.markdown(f"**Due Date:** <span style='color:red'>{task['due_date']} (Overdue by {abs(days_remaining)} days)</span>", unsafe_allow_html=True)
                        elif days_remaining == 0:
                            st.markdown(f"**Due Date:** <span style='color:orange'>{task['due_date']} (Due today)</span>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"**Due Date:** {task['due_date']} ({days_remaining} days left)")
                    except (ValueError, KeyError):
                        st.markdown(f"**Due Date:** {task.get('due_date', 'Not set')}")
                
                # Task actions
                with col3:
                    edit_button = st.button("Edit", key=f"edit_{task_id}")
                    delete_button = st.button("Delete", key=f"delete_{task_id}")
                    
                    if edit_button:
                        st.session_state.edit_task_id = task_id
                        st.rerun()
                    
                    if delete_button:
                        st.session_state.show_delete_confirmation = True
                        st.session_state.delete_task_id = task_id
                        st.rerun()
            
            st.divider()
    
    # Delete confirmation dialog
    if st.session_state.show_delete_confirmation and st.session_state.delete_task_id:
        task = data_handler.get_task_by_id(st.session_state.delete_task_id)
        if task:
            st.warning(f"Are you sure you want to delete the task '{task['title']}'?")
            col1, col2 = st.columns(2)
            with col1:
                confirm_delete = st.button("Yes, delete it", key="confirm_delete")
                if confirm_delete:
                    data_handler.delete_task(st.session_state.delete_task_id)
                    st.success("Task deleted successfully!")
                    st.session_state.show_delete_confirmation = False
                    st.session_state.delete_task_id = None
                    st.rerun()
            with col2:
                cancel_delete = st.button("Cancel", key="cancel_delete")
                if cancel_delete:
                    st.session_state.show_delete_confirmation = False
                    st.session_state.delete_task_id = None
                    st.rerun()

# Statistics view
elif st.session_state.view_mode == "Statistics":
    st.header("Task Statistics and Visualization")
    
    # Get all tasks for analysis
    all_tasks = data_handler.get_all_tasks()
    
    if not all_tasks:
        st.info("No tasks available for statistics. Create some tasks first!")
    else:
        # Create visualizations
        create_task_visualizations(all_tasks)
