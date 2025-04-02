import streamlit as st
import json
import pandas as pd
from datetime import datetime, timedelta
import os
import matplotlib.pyplot as plt

# JSON file setup
TASKS_FILE = "tasks.json"
USERS = {"user1": "pass1", "user2": "pass2", "user3": "pass3", "user4": "pass4", "user5": "pass5"}

# Load and save tasks
def load_tasks():
    if not os.path.exists(TASKS_FILE):
        save_tasks([])
    try:
        with open(TASKS_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_tasks(tasks):
    with open(TASKS_FILE, "w", encoding="utf-8") as file:
        json.dump(tasks, file, indent=4)

def add_task(title, description, priority, due_date, tags, user, assigned_to=None, recurrence=None):
    tasks = load_tasks()
    task_id = len(tasks) + 1
    tasks.append({
        "ID": task_id,
        "Title": title,
        "Description": description,
        "Priority": priority,
        "Status": "Pending",
        "Due Date": due_date,
        "Tags": tags,
        "User": user,
        "Assigned To": assigned_to,
        "Recurrence": recurrence
    })
    save_tasks(tasks)

def get_tasks(user):
    tasks = load_tasks()
    return [task for task in tasks if task.get('User') == user or task.get('Assigned To') == user]

def update_task(task_id, status):
    tasks = load_tasks()
    for task in tasks:
        if task["ID"] == int(task_id):
            task["Status"] = status
    save_tasks(tasks)

def delete_task(task_id):
    tasks = load_tasks()
    tasks = [task for task in tasks if task["ID"] != int(task_id)]
    save_tasks(tasks)

def export_tasks(user, file_format):
    tasks = get_tasks(user)
    df = pd.DataFrame(tasks)
    file_path = f"tasks.{file_format.lower()}"
    if file_format == "CSV":
        df.to_csv(file_path, index=False, encoding="utf-8")
    elif file_format == "JSON":
        df.to_json(file_path, orient="records", force_ascii=False)
    st.success(f"Tasks exported as {file_format} successfully! File: {file_path}")

def search_tasks(user, query):
    tasks = get_tasks(user)
    return [task for task in tasks if query.lower() in task['Title'].lower() or query.lower() in task['Tags'].lower()]

def sort_tasks(user, sort_by):
    tasks = get_tasks(user)
    if sort_by == "Priority":
        priority_order = {"High": 1, "Medium": 2, "Low": 3}
        tasks.sort(key=lambda x: priority_order.get(x["Priority"], 3))
    elif sort_by == "Due Date":
        tasks.sort(key=lambda x: datetime.strptime(x["Due Date"], "%Y-%m-%d"))
    return tasks

def task_statistics(user):
    tasks = get_tasks(user)
    df = pd.DataFrame(tasks)
    if not df.empty:
        completed = df[df['Status'] == 'Completed'].shape[0]
        pending = df[df['Status'] == 'Pending'].shape[0]
        overdue = df[(df['Status'] == 'Pending') & (df['Due Date'] < datetime.now().strftime("%Y-%m-%d"))].shape[0]
        
        fig, ax = plt.subplots()
        ax.pie([completed, pending, overdue], labels=['Completed', 'Pending', 'Overdue'], autopct='%1.1f%%', colors=['green', 'blue', 'red'])
        st.pyplot(fig)

def main():
    st.set_page_config(page_title='Task Manager', layout='wide')
    st.title("🚀 Advanced Task Manager")
    
    if 'authenticated_user' not in st.session_state:
        st.session_state['authenticated_user'] = None
    
    if st.session_state['authenticated_user'] is None:
        st.subheader("🔐 User Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if username in USERS and USERS[username] == password:
                st.session_state['authenticated_user'] = username
                st.success(f"Welcome, {username}!")
                st.rerun()
            else:
                st.error("Invalid credentials!")
    else:
        user = st.session_state['authenticated_user']
        menu = ["Add Task", "View Tasks", "Update Task", "Delete Task", "Export Tasks", "Search Tasks", "Sort Tasks", "Task Statistics", "Logout"]
        choice = st.sidebar.selectbox("Menu", menu)
        
        if choice == "Add Task":
            st.subheader("📝 Add New Task")
            title = st.text_input("Task Title")
            description = st.text_area("Task Description")
            priority = st.selectbox("Priority", ["High", "Medium", "Low"])
            due_date = st.date_input("Due Date", min_value=datetime.today()).strftime("%Y-%m-%d")
            tags = st.text_input("Tags (comma-separated)")
            assigned_to = st.text_input("Assign To (optional)")
            recurrence = st.selectbox("Recurrence", [None, "Daily", "Weekly", "Monthly"])
            if st.button("Add Task"):
                add_task(title, description, priority, due_date, tags, user, assigned_to, recurrence)
                st.success("Task added successfully!")
        
        elif choice == "View Tasks":
            st.subheader("📋 Your Tasks")
            tasks = get_tasks(user)
            st.write(pd.DataFrame(tasks))
        
        elif choice == "Update Task":
            st.subheader("✅ Update Task Status")
            task_id = st.number_input("Enter Task ID", min_value=1, step=1)
            status = st.selectbox("Status", ["Pending", "Completed"])
            if st.button("Update Task"):
                update_task(task_id, status)
                st.success("Task updated successfully!")
        
        elif choice == "Delete Task":
            st.subheader("❌ Delete Task")
            task_id = st.number_input("Enter Task ID", min_value=1, step=1)
            if st.button("Delete Task"):
                delete_task(task_id)
                st.success("Task deleted successfully!")
        
        elif choice == "Export Tasks":
            st.subheader("📤 Export Tasks")
            file_format = st.selectbox("Choose Format", ["CSV", "JSON"])
            if st.button("Export"):
                export_tasks(user, file_format)
        
        elif choice == "Search Tasks":
            st.subheader("🔎 Search Tasks")
            query = st.text_input("Enter search query")
            if st.button("Search"):
                results = search_tasks(user, query)
                st.write(pd.DataFrame(results))
        
        elif choice == "Sort Tasks":
            st.subheader("🔽 Sort Tasks")
            sort_by = st.selectbox("Sort by", ["Priority", "Due Date"])
            if st.button("Sort"):
                sorted_tasks = sort_tasks(user, sort_by)
                st.write(pd.DataFrame(sorted_tasks))
        
        elif choice == "Task Statistics":
            st.subheader("📊 Task Statistics")
            task_statistics(user)
        
        elif choice == "Logout":
            st.session_state['authenticated_user'] = None
            st.success("Logged out successfully!")
            st.rerun()

if __name__ == "__main__":
    main()
