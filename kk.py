import streamlit as st
import json
import pandas as pd
from datetime import datetime

# JSON file setup
TASKS_FILE = "tasks.json"

def load_tasks():
    try:
        with open(TASKS_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_tasks(tasks):
    with open(TASKS_FILE, "w") as file:
        json.dump(tasks, file, indent=4)

def add_task(title, description, priority, due_date, tags, user):
    tasks = load_tasks()
    task_id = len(tasks) + 1
    tasks.append({"ID": task_id, "Title": title, "Description": description, "Priority": priority, "Status": "Pending", "Due Date": due_date, "Tags": tags, "User": user})
    save_tasks(tasks)

def get_tasks(user):
    tasks = load_tasks()
    return [task for task in tasks if task['User'] == user]

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
    if file_format == "CSV":
        df.to_csv("tasks.csv", index=False)
    elif file_format == "JSON":
        df.to_json("tasks.json", orient="records")
    return f"Tasks exported as {file_format} successfully!"

def main():
    st.set_page_config(page_title='Task Manager', layout='wide')
    st.title("🚀 Advanced Task Manager")
    
    menu = ["Add Task", "View Tasks", "Update Task", "Delete Task", "Export Tasks"]
    choice = st.sidebar.selectbox("Menu", menu)
    user = st.sidebar.text_input("Enter your username")
    
    if choice == "Add Task":
        st.subheader("📌 Add New Task")
        title = st.text_input("Task Title")
        description = st.text_area("Task Description")
        priority = st.selectbox("Priority", ["High", "Medium", "Low"])
        due_date = st.date_input("Due Date")
        tags = st.text_input("Tags (comma-separated)")
        
        if st.button("Add Task"):
            if title and user:
                add_task(title, description, priority, str(due_date), tags, user)
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

if __name__ == "__main__":
    main()
