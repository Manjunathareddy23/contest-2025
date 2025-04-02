import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import os
import json

from db_handler import DatabaseHandler
from utils import (
    generate_unique_id, get_default_due_date, validate_task_input,
    format_remaining_days, priority_color, status_color,
    format_tags, load_css, format_priority, format_status
)
from task_visualizer import create_task_visualizations
from ai_helper import AiTaskHelper, check_ai_available

# Set Streamlit page configuration
st.set_page_config(
    page_title="Advanced Task Manager",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
load_css()

# Initialize database handler
@st.cache_resource
def get_db_handler():
    return DatabaseHandler()

# Initialize AI helper if available
@st.cache_resource
def get_ai_helper():
    if check_ai_available():
        return AiTaskHelper()
    return None

# Initialize session state for various UI components
if "show_task_form" not in st.session_state:
    st.session_state.show_task_form = False

if "edit_task_id" not in st.session_state:
    st.session_state.edit_task_id = None

if "filter_tag" not in st.session_state:
    st.session_state.filter_tag = None

if "sort_by" not in st.session_state:
    st.session_state.sort_by = "Priority"

if "show_completed" not in st.session_state:
    st.session_state.show_completed = False

if "ai_analyzing" not in st.session_state:
    st.session_state.ai_analyzing = False

if "ai_suggestions" not in st.session_state:
    st.session_state.ai_suggestions = None

# Get database and AI helper
db = get_db_handler()
ai_helper = get_ai_helper()

# Define callback functions for UI interactions
def toggle_task_form():
    st.session_state.show_task_form = not st.session_state.show_task_form
    st.session_state.edit_task_id = None
    st.session_state.ai_suggestions = None
    st.session_state.ai_analyzing = False

def edit_task(task_id):
    st.session_state.edit_task_id = task_id
    st.session_state.show_task_form = True
    st.session_state.ai_suggestions = None
    st.session_state.ai_analyzing = False

def cancel_edit():
    st.session_state.edit_task_id = None
    st.session_state.show_task_form = False
    st.session_state.ai_suggestions = None
    st.session_state.ai_analyzing = False

def set_filter_tag(tag):
    st.session_state.filter_tag = tag if st.session_state.filter_tag != tag else None

def analyze_with_ai(description):
    if ai_helper:
        st.session_state.ai_analyzing = True
        st.session_state.ai_suggestions = ai_helper.analyze_task_description(description)
    else:
        st.session_state.ai_suggestions = {"success": False, "message": "AI helper not available. Check your Gemini API key."}
    st.session_state.ai_analyzing = False

# Main app content
st.markdown("<h1 class='fade-in'>✅ Advanced Task Manager</h1>", unsafe_allow_html=True)

# Create sidebar
with st.sidebar:
    st.markdown("<h2>Task Management</h2>", unsafe_allow_html=True)
    
    # Button to toggle task form
    if st.session_state.show_task_form:
        form_button_text = "❌ Cancel" if st.session_state.edit_task_id is None else "❌ Cancel Edit"
    else:
        form_button_text = "➕ New Task"
    
    st.button(form_button_text, on_click=toggle_task_form, key="toggle_form")
    
    st.markdown("<hr/>", unsafe_allow_html=True)
    st.markdown("<h2>Search & Filter</h2>", unsafe_allow_html=True)
    
    # Search box
    search_query = st.text_input("🔍 Search tasks", key="search_input")
    
    # Sort options
    sort_options = ["Priority", "Due Date", "Status"]
    st.session_state.sort_by = st.selectbox("Sort by", sort_options, index=sort_options.index(st.session_state.sort_by))
    
    # Filter by tag
    all_tags = db.get_all_tags()
    if all_tags:
        st.markdown("<h3>Filter by Tag</h3>", unsafe_allow_html=True)
        selected_tag = st.session_state.filter_tag
        
        # Display tags as clickable buttons
        tags_html = "<div class='tag-list'>"
        for tag in all_tags:
            tag_class = "tag-selected" if tag == selected_tag else "tag"
            tags_html += f"<span class='{tag_class}' onclick='setFilterTag(\"{tag}\")'>{tag}</span> "
        tags_html += "</div>"
        
        st.markdown(tags_html, unsafe_allow_html=True)
        
        # Create hidden button for tag selection (workaround for click events)
        if st.button(f"Select: {selected_tag if selected_tag else 'None'}", key="tag_selector"):
            st.session_state.filter_tag = None
    
    # Filter completed tasks
    st.markdown("<h3>Show Completed Tasks</h3>", unsafe_allow_html=True)
    st.session_state.show_completed = st.checkbox("Show completed tasks", value=st.session_state.show_completed)
    
    # Statistics section
    st.markdown("<hr/>", unsafe_allow_html=True)
    st.markdown("<h2>Quick Stats</h2>", unsafe_allow_html=True)
    
    stats = db.get_task_statistics()
    
    st.markdown(f"<div class='stat-card'>", unsafe_allow_html=True)
    st.markdown(f"<div class='stat-number'>{stats['total_tasks']}</div>", unsafe_allow_html=True)
    st.markdown("<div class='stat-label'>Total Tasks</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"<div class='stat-card'>", unsafe_allow_html=True)
        st.markdown(f"<div class='stat-number'>{stats['overdue_count']}</div>", unsafe_allow_html=True)
        st.markdown("<div class='stat-label'>Overdue</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"<div class='stat-card'>", unsafe_allow_html=True)
        st.markdown(f"<div class='stat-number'>{stats['due_soon_count']}</div>", unsafe_allow_html=True)
        st.markdown("<div class='stat-label'>Due Soon</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# Task Form (Create/Edit)
if st.session_state.show_task_form:
    form_container = st.container()
    with form_container:
        st.markdown("<div class='fade-in'>", unsafe_allow_html=True)
        
        if st.session_state.edit_task_id:
            task_to_edit = db.get_task_by_id(st.session_state.edit_task_id)
            st.subheader(f"✏️ Edit Task: {task_to_edit.get('title', '')}")
        else:
            st.subheader("➕ Create New Task")
        
        with st.form(key="task_form"):
            # Form Fields
            if st.session_state.edit_task_id:
                task_to_edit = db.get_task_by_id(st.session_state.edit_task_id)
                title = st.text_input("Title", value=task_to_edit.get("title", ""))
                description = st.text_area("Description", value=task_to_edit.get("description", ""), height=100)
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    priority = st.selectbox(
                        "Priority",
                        ["High", "Medium", "Low"],
                        index=["High", "Medium", "Low"].index(task_to_edit.get("priority", "Medium"))
                    )
                with col2:
                    status = st.selectbox(
                        "Status",
                        ["Not Started", "In Progress", "Completed"],
                        index=["Not Started", "In Progress", "Completed"].index(task_to_edit.get("status", "Not Started"))
                    )
                with col3:
                    due_date_default = datetime.strptime(task_to_edit.get("due_date", ""), "%Y-%m-%d").date() if task_to_edit.get("due_date") else get_default_due_date()
                    due_date = st.date_input("Due Date", value=due_date_default)
                
                tags_default = ", ".join(task_to_edit.get("tags", [])) if isinstance(task_to_edit.get("tags", []), list) else task_to_edit.get("tags", "")
                tags = st.text_input("Tags (comma-separated)", value=tags_default)
                
                assigned_to = st.text_input("Assigned To", value=task_to_edit.get("assigned_to", ""))
                
                col1, col2 = st.columns(2)
                with col1:
                    recurring = st.checkbox("Recurring Task", value=task_to_edit.get("recurring", False))
                with col2:
                    if recurring:
                        recurring_pattern = st.selectbox(
                            "Repeat Pattern",
                            ["Daily", "Weekly", "Monthly"],
                            index=["Daily", "Weekly", "Monthly"].index(task_to_edit.get("recurring_pattern", "Weekly")) if task_to_edit.get("recurring_pattern") in ["Daily", "Weekly", "Monthly"] else 1
                        )
                    else:
                        recurring_pattern = None
                
                submit_button = st.form_submit_button("Update Task")
                cancel_button = st.form_submit_button("Cancel")
                
                if cancel_button:
                    cancel_edit()
                
                if submit_button:
                    validation_result = validate_task_input(title, description)
                    
                    if validation_result["valid"]:
                        # Process tags
                        tags_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
                        
                        task_data = {
                            "title": title,
                            "description": description,
                            "priority": priority,
                            "status": status,
                            "due_date": due_date.strftime("%Y-%m-%d"),
                            "tags": tags_list,
                            "assigned_to": assigned_to,
                            "recurring": recurring,
                            "recurring_pattern": recurring_pattern if recurring else None
                        }
                        
                        db.update_task(st.session_state.edit_task_id, task_data)
                        st.success("Task updated successfully!")
                        
                        # Clear form
                        cancel_edit()
                        st.rerun()
                    else:
                        st.error(validation_result["message"])
            else:
                # Create new task form
                title = st.text_input("Title", placeholder="Enter task title")
                description = st.text_area("Description", placeholder="Enter task description", height=100)
                
                # AI Analysis Button
                col1, col2 = st.columns([3, 1])
                with col2:
                    if ai_helper and description.strip() and not st.session_state.ai_analyzing and not st.session_state.ai_suggestions:
                        ai_button = st.button("✨ Analyze with AI", on_click=analyze_with_ai, args=(description,))
                
                # Display AI suggestions if available
                if st.session_state.ai_analyzing:
                    st.info("Analyzing task with AI...")
                
                if st.session_state.ai_suggestions and st.session_state.ai_suggestions.get("success"):
                    st.markdown("<div class='ai-suggestion'>", unsafe_allow_html=True)
                    st.markdown("<div class='ai-suggestion-title'>✨ AI Suggestions</div>", unsafe_allow_html=True)
                    
                    suggestions = st.session_state.ai_suggestions.get("suggestions", {})
                    
                    ai_priority = suggestions.get("priority")
                    ai_tags = suggestions.get("tags", [])
                    ai_effort = suggestions.get("effort")
                    ai_summary = suggestions.get("summary")
                    
                    if ai_priority:
                        st.markdown(f"**Suggested Priority:** {ai_priority}")
                    
                    if ai_tags:
                        st.markdown(f"**Suggested Tags:** {', '.join(ai_tags)}")
                    
                    if ai_effort:
                        st.markdown(f"**Estimated Effort:** {ai_effort}")
                    
                    if ai_summary:
                        st.markdown(f"**Summary:** {ai_summary}")
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                elif st.session_state.ai_suggestions and not st.session_state.ai_suggestions.get("success"):
                    st.warning(st.session_state.ai_suggestions.get("message", "AI analysis failed. Try again later."))
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    priority_options = ["High", "Medium", "Low"]
                    ai_priority = None
                    
                    if st.session_state.ai_suggestions and st.session_state.ai_suggestions.get("success"):
                        suggestions = st.session_state.ai_suggestions.get("suggestions", {})
                        ai_priority = suggestions.get("priority")
                        
                        if ai_priority in priority_options:
                            priority_index = priority_options.index(ai_priority)
                        else:
                            priority_index = 1  # Default to Medium
                    else:
                        priority_index = 1  # Default to Medium
                    
                    priority = st.selectbox("Priority", priority_options, index=priority_index)
                
                with col2:
                    status = st.selectbox("Status", ["Not Started", "In Progress", "Completed"], index=0)
                
                with col3:
                    due_date = st.date_input("Due Date", value=get_default_due_date())
                
                # Use AI-suggested tags if available
                tags_default = ""
                if st.session_state.ai_suggestions and st.session_state.ai_suggestions.get("success"):
                    suggestions = st.session_state.ai_suggestions.get("suggestions", {})
                    ai_tags = suggestions.get("tags", [])
                    if ai_tags:
                        tags_default = ", ".join(ai_tags)
                
                tags = st.text_input("Tags (comma-separated)", value=tags_default, placeholder="work, important, project, etc.")
                
                assigned_to = st.text_input("Assigned To", placeholder="Leave blank for self-assignment")
                
                col1, col2 = st.columns(2)
                with col1:
                    recurring = st.checkbox("Recurring Task")
                with col2:
                    if recurring:
                        recurring_pattern = st.selectbox("Repeat Pattern", ["Daily", "Weekly", "Monthly"], index=1)
                    else:
                        recurring_pattern = None
                
                submit_button = st.form_submit_button("Create Task")
                
                if submit_button:
                    validation_result = validate_task_input(title, description)
                    
                    if validation_result["valid"]:
                        # Process tags
                        tags_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
                        
                        task_id = generate_unique_id()
                        task_data = {
                            "title": title,
                            "description": description,
                            "priority": priority,
                            "status": status,
                            "due_date": due_date.strftime("%Y-%m-%d"),
                            "tags": tags_list,
                            "assigned_to": assigned_to,
                            "recurring": recurring,
                            "recurring_pattern": recurring_pattern if recurring else None,
                            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        
                        db.add_task(task_id, task_data)
                        st.success("Task created successfully!")
                        
                        # Reset form
                        st.session_state.show_task_form = False
                        st.session_state.ai_suggestions = None
                        st.rerun()
                    else:
                        st.error(validation_result["message"])
        
        st.markdown("</div>", unsafe_allow_html=True)

# Display tasks
tasks_container = st.container()

with tasks_container:
    # Get filtered tasks
    filtered_tasks = db.get_filtered_tasks(
        search_query=search_query,
        filter_tag=st.session_state.filter_tag,
        sort_by=st.session_state.sort_by
    )
    
    # Handle display options
    if not st.session_state.show_completed:
        # Filter out completed tasks if not showing them
        filtered_tasks = {
            task_id: task for task_id, task in filtered_tasks.items() 
            if task.get("status") != "Completed"
        }
    
    if st.session_state.filter_tag:
        st.markdown(f"<div class='search-filter fade-in'>Filtering by tag: <span class='tag'>{st.session_state.filter_tag}</span> <a href='javascript:void(0);' onclick='clearTagFilter()'>Clear</a></div>", unsafe_allow_html=True)
    
    if search_query:
        st.markdown(f"<div class='search-filter fade-in'>Search results for: '{search_query}'</div>", unsafe_allow_html=True)
    
    if not filtered_tasks:
        st.info("No tasks found. Create a new task using the sidebar.")
    else:
        # Actions for selected tasks
        st.markdown("<div class='fade-in'>", unsafe_allow_html=True)
        
        tasks_to_display = {}
        tasks_completed = {}
        
        # Split tasks by completion status for display
        for task_id, task in filtered_tasks.items():
            if task.get("status") == "Completed":
                tasks_completed[task_id] = task
            else:
                tasks_to_display[task_id] = task
        
        # Function to render task cards
        def render_task_cards(tasks):
            for task_id, task in tasks.items():
                # Card container
                st.markdown(f"<div class='task-card' id='task-{task_id}'>", unsafe_allow_html=True)
                
                # Task header row
                col1, col2, col3 = st.columns([5, 3, 2])
                
                with col1:
                    st.markdown(f"<h3>{task.get('title', 'Unnamed Task')}</h3>", unsafe_allow_html=True)
                
                with col2:
                    priority = task.get("priority", "Medium")
                    status = task.get("status", "Not Started")
                    
                    st.markdown(f"{format_priority(priority)} {format_status(status)}", unsafe_allow_html=True)
                
                with col3:
                    due_date = task.get("due_date", "")
                    if due_date:
                        st.markdown(format_remaining_days(due_date), unsafe_allow_html=True)
                
                # Task details row
                st.markdown(f"<p>{task.get('description', '')}</p>", unsafe_allow_html=True)
                
                # Tags
                tags = task.get("tags", [])
                if tags:
                    st.markdown(format_tags(tags), unsafe_allow_html=True)
                
                # Task footer row
                col1, col2, col3 = st.columns([5, 3, 2])
                
                with col1:
                    assigned_to = task.get("assigned_to", "")
                    if assigned_to:
                        st.markdown(f"Assigned to: {assigned_to}", unsafe_allow_html=True)
                
                with col3:
                    # Action buttons
                    st.button("✏️ Edit", key=f"edit_{task_id}", on_click=edit_task, args=(task_id,))
                
                st.markdown("</div>", unsafe_allow_html=True)
                st.markdown("<hr/>", unsafe_allow_html=True)
        
        # Show active tasks
        if tasks_to_display:
            st.subheader("Active Tasks")
            render_task_cards(tasks_to_display)
        
        # Show completed tasks
        if tasks_completed and st.session_state.show_completed:
            st.subheader("Completed Tasks")
            render_task_cards(tasks_completed)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # JavaScript for handling tag filter interactions
    st.markdown("""
    <script>
    function setFilterTag(tag) {
        // Use the hidden button to trigger a click
        document.querySelector('button[data-testid="baseButton-secondary"]').click();
    }
    
    function clearTagFilter() {
        // Use the hidden button to trigger a click
        document.querySelector('button[data-testid="baseButton-secondary"]').click();
    }
    </script>
    """, unsafe_allow_html=True)

# Task Visualizations
if filtered_tasks:
    st.markdown("<hr/>", unsafe_allow_html=True)
    st.markdown("<h2 class='fade-in'>📊 Task Analytics</h2>", unsafe_allow_html=True)
    
    # Display the task visualizations
    create_task_visualizations(filtered_tasks)

# Add the help menu
with st.expander("ℹ️ Help & Information"):
    st.markdown("""
    ## Advanced Task Manager Help
    
    This task management application helps you organize, track, and visualize your tasks with advanced features
    including AI-assisted task analysis, priority suggestions, and comprehensive analytics.
    
    ### Key Features:
    
    - **Create and Edit Tasks**: Add new tasks or modify existing ones with title, description, priority, status, and due date.
    - **AI-Powered Analysis**: Get AI suggestions for task priority, tags, and effort estimation.
    - **Task Filtering**: Search tasks, filter by tags, or hide/show completed tasks.
    - **Data Visualization**: View task statistics and analytics through interactive charts.
    - **Database Storage**: All tasks are securely stored in a PostgreSQL database.
    
    ### Getting Started:
    
    1. Create a new task using the "New Task" button in the sidebar
    2. Use AI analysis to get suggestions based on your task description
    3. Filter tasks using search or tags
    4. Sort tasks by priority, due date, or status
    5. View task analytics in the charts section
    
    ### Keyboard Shortcuts:
    
    - **Ctrl/Cmd + F**: Focus the search box
    - **Esc**: Clear current selection or close modals
    - **N**: Create a new task (when not in a text field)
    
    For more information or support, please contact the development team.
    """)

# Footer
st.markdown("<hr/>", unsafe_allow_html=True)
st.markdown("<footer class='fade-in'>Advanced Task Manager - Developed with Streamlit & Tailwind CSS - © 2025</footer>", unsafe_allow_html=True)
