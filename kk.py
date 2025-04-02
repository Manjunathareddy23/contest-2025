import streamlit as st
import json
import pandas as pd
from datetime import datetime, timedelta
import os
import threading
import time
import matplotlib.pyplot as plt
import unittest

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

# Unit Testing Class
class TestTaskManager(unittest.TestCase):
    def test_add_task(self):
        add_task("Test Task", "Description", "High", "2025-04-10", "test", "user1")
        tasks = get_tasks("user1")
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["Title"], "Test Task")

# Main function
def main():
    st.set_page_config(page_title='Task Manager', layout='wide')
    st.title("🚀 Advanced Task Manager")
    
    menu = ["Login", "Add Task", "View Tasks", "Update Task", "Delete Task", "Export Tasks", "Search Tasks", "Sort Tasks", "Task Statistics"]
    choice = st.sidebar.selectbox("Menu", menu)
    
    if choice == "Login":
        st.subheader("🔐 User Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if username in USERS and USERS[username] == password:
                st.session_state['authenticated_user'] = username
                st.success(f"Welcome, {username}!")
            else:
                st.error("Invalid credentials!")
    
    elif 'authenticated_user' in st.session_state:
        user = st.session_state['authenticated_user']
        if choice == "Add Task":
            st.subheader("📌 Add New Task")
            title = st.text_input("Task Title")
            description = st.text_area("Task Description")
            priority = st.selectbox("Priority", ["High", "Medium", "Low"])
            due_date = st.date_input("Due Date")
            tags = st.text_input("Tags (comma-separated)")
            assigned_to = st.text_input("Assign Task To (optional)")
            recurrence = st.selectbox("Recurrence", ["None", "Daily", "Weekly", "Monthly"])
            
            if st.button("Add Task"):
                if title:
                    add_task(title, description, priority, str(due_date), tags, user, assigned_to, recurrence)
                    st.success("Task added successfully!")
                else:
                    st.error("Please enter a title.")
        
        elif choice == "View Tasks":
            st.subheader("📋 Your Tasks")
            tasks = get_tasks(user)
            df = pd.DataFrame(tasks)
            st.dataframe(df)

if __name__ == "__main__":
    main()
