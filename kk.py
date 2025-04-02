import streamlit as st
import json
import pandas as pd
from datetime import datetime, timedelta
import os
import threading
import time

# JSON file setup
TASKS_FILE = "tasks.json"

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

def add_task(title, description, priority, due_date, tags, user, recurrence=None):
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
        "Recurrence": recurrence
    })
    save_tasks(tasks)

def get_tasks(user):
    tasks = load_tasks()
    return [task for task in tasks if task.get('User') == user]

def update_task(task_id, status):
    tasks = load_tasks()
    task_found = False
    for task in tasks:
        if task["ID"] == int(task_id):
            task["Status"] = status
            task_found = True
    if task_found:
        save_tasks(tasks)

def delete_task(task_id):
    tasks = load_tasks()
    new_tasks = [task for task in tasks if task["ID"] != int(task_id)]
    if len(new_tasks) < len(tasks):
        save_tasks(new_tasks)

def export_tasks(user, file_format):
    tasks = get_tasks(user)
    df = pd.DataFrame(tasks)
    file_path = f"tasks.{file_format.lower()}"
    if file_format == "CSV":
        df.to_csv(file_path, index=False, encoding="utf-8")
    elif file_format == "JSON":
        df.to_json(file_path, orient="records", force_ascii=False)
    return f"Tasks exported as {file_format} successfully! File: {file_path}"

# Search tasks
def search_tasks(user, query):
    tasks = get_tasks(user)
    return [task for task in tasks if query.lower() in task['Title'].lower() or query.lower() in task['Tags'].lower()]

# Sort tasks
def sort_tasks(user, sort_by):
    tasks = get_tasks(user)
    if sort_by == "Priority":
        priority_order = {"High": 1, "Medium": 2, "Low": 3}
        tasks.sort(key=lambda x: priority_order.get(x["Priority"], 3))
    elif sort_by == "Due Date":
        tasks.sort(key=lambda x: datetime.strptime(x["Due Date"], "%Y-%m-%d"))
    return tasks

# Reminder system
def check_reminders():
    while True:
        tasks = load_tasks()
        now = datetime.now().strftime("%Y-%m-%d")
        for task in tasks:
            if task["Due Date"] == now and task["Status"] == "Pending":
                print(f"Reminder: Task '{task['Title']}' is due today!")
        time.sleep(86400)  # Check every 24 hours

# Start the reminder thread
reminder_thread = threading.Thread(target=check_reminders, daemon=True)
reminder_thread.start()

def main():
    st.set_page_config(page_title='Task Manager', layout='wide')
    st.title("🚀 Advanced Task Manager")
    
    menu = ["Add Task", "View Tasks", "Update Task", "Delete Task", "Export Tasks", "Search Tasks", "Sort Tasks"]
    choice = st.sidebar.selectbox("Menu", menu)
    user = st.sidebar.text_input("Enter your username")
    
    if choice == "Add Task":
        st.subheader("📌 Add New Task")
        title = st.text_input("Task Title")
        description = st.text_area("Task Description")
        priority = st.selectbox("Priority", ["High", "Medium", "Low"])
        due_date = st.date_input("Due Date")
        tags = st.text_input("Tags (comma-separated)")
        recurrence = st.selectbox("Recurrence", ["None", "Daily", "Weekly", "Monthly"])
        
        if st.button("Add Task"):
            if title and user:
                add_task(title, description, priority, str(due_date), tags, user, recurrence)
                st.success("Task added successfully!")
            else:
                st.error("Please enter a title and username.")
    
    elif choice == "View Tasks":
        st.subheader("📋 Your Tasks")
        tasks = get_tasks(user)
        df = pd.DataFrame(tasks)
        st.dataframe(df)

    elif choice == "Update Task":
        st.subheader("✅ Update Task Status")
        task_id = st.text_input("Task ID")
        status = st.selectbox("New Status", ["Pending", "Completed", "In Progress"])
        if st.button("Update Task"):
            update_task(task_id, status)
            st.success("Task updated successfully!")
    
    elif choice == "Delete Task":
        st.subheader("❌ Delete Task")
        task_id = st.text_input("Task ID")
        if st.button("Delete Task"):
            delete_task(task_id)
            st.warning("Task deleted!")
    
    elif choice == "Export Tasks":
        st.subheader("📤 Export Tasks")
        file_format = st.selectbox("Select Format", ["CSV", "JSON"])
        if st.button("Export"):
            result = export_tasks(user, file_format)
            st.success(result)
    
    elif choice == "Search Tasks":
        st.subheader("🔍 Search Tasks")
        query = st.text_input("Search by title or tags")
        if st.button("Search"):
            results = search_tasks(user, query)
            st.dataframe(pd.DataFrame(results))
    
    elif choice == "Sort Tasks":
        st.subheader("📌 Sort Tasks")
        sort_by = st.selectbox("Sort by", ["Priority", "Due Date"])
        if st.button("Sort"):
            sorted_tasks = sort_tasks(user, sort_by)
            st.dataframe(pd.DataFrame(sorted_tasks))

if __name__ == "__main__":
    main()
