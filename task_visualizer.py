import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, Any

def create_task_visualizations(tasks: Dict[str, Dict[str, Any]]) -> None:
    """
    Create and display visualizations for task statistics.
    
    Args:
        tasks: Dictionary of tasks to visualize
    """
    if not tasks:
        st.info("No tasks available for visualization")
        return
    
    # Create a DataFrame from tasks for easier data manipulation
    task_df = pd.DataFrame.from_dict(tasks, orient='index')
    
    # Display summary statistics
    st.subheader("Summary Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_tasks = len(task_df)
        st.metric("Total Tasks", total_tasks)
    
    with col2:
        completed_tasks = len(task_df[task_df['status'] == 'Completed'])
        completion_rate = f"{int(completed_tasks / total_tasks * 100)}%" if total_tasks > 0 else "0%"
        st.metric("Completed Tasks", completed_tasks, completion_rate)
    
    with col3:
        in_progress = len(task_df[task_df['status'] == 'In Progress'])
        st.metric("In Progress", in_progress)
    
    with col4:
        not_started = len(task_df[task_df['status'] == 'Not Started'])
        st.metric("Not Started", not_started)
    
    # Task status distribution
    st.subheader("Task Status Distribution")
    status_counts = task_df['status'].value_counts().reset_index()
    status_counts.columns = ['Status', 'Count']
    
    fig_status = px.pie(
        status_counts, 
        values='Count', 
        names='Status',
        color='Status',
        color_discrete_map={
            'Not Started': '#888888',
            'In Progress': '#4286f4',
            'Completed': '#42f48f'
        },
        title="Task Status Distribution"
    )
    st.plotly_chart(fig_status, use_container_width=True)
    
    # Task priority distribution
    st.subheader("Task Priority Distribution")
    priority_counts = task_df['priority'].value_counts().reset_index()
    priority_counts.columns = ['Priority', 'Count']
    
    fig_priority = px.bar(
        priority_counts, 
        x='Priority', 
        y='Count',
        color='Priority',
        color_discrete_map={
            'Low': '#4286f4',
            'Medium': '#f49e42',
            'High': '#f44242'
        },
        title="Task Priority Distribution"
    )
    st.plotly_chart(fig_priority, use_container_width=True)
    
    # Due date analysis
    st.subheader("Due Date Analysis")
    
    # Convert due dates to datetime
    task_df['due_date_parsed'] = pd.to_datetime(task_df['due_date'], errors='coerce')
    
    # Calculate due date status
    today = datetime.now().date()
    task_df['days_until_due'] = (task_df['due_date_parsed'].dt.date - today).dt.days
    
    task_df['due_status'] = 'Future'
    task_df.loc[task_df['days_until_due'] < 0, 'due_status'] = 'Overdue'
    task_df.loc[(task_df['days_until_due'] >= 0) & (task_df['days_until_due'] <= 7), 'due_status'] = 'Next 7 days'
    
    # Due date status counts
    due_status_counts = task_df['due_status'].value_counts().reset_index()
    due_status_counts.columns = ['Due Status', 'Count']
    
    fig_due_status = px.bar(
        due_status_counts, 
        x='Due Status', 
        y='Count',
        color='Due Status',
        color_discrete_map={
            'Overdue': '#f44242',
            'Next 7 days': '#f49e42',
            'Future': '#4286f4'
        },
        title="Tasks by Due Date Status"
    )
    st.plotly_chart(fig_due_status, use_container_width=True)
    
    # Tags analysis
    st.subheader("Tags Analysis")
    
    # Extract all tags from tasks
    all_tags = []
    for _, task in tasks.items():
        tags = task.get('tags', [])
        all_tags.extend(tags)
    
    # Count tag occurrences
    tag_counts = pd.Series(all_tags).value_counts().reset_index()
    tag_counts.columns = ['Tag', 'Count']
    
    if len(tag_counts) > 0:
        # Only display top 10 tags if there are many
        if len(tag_counts) > 10:
            tag_counts = tag_counts.head(10)
            chart_title = "Top 10 Tags"
        else:
            chart_title = "Tags Distribution"
        
        fig_tags = px.bar(
            tag_counts, 
            x='Tag', 
            y='Count',
            title=chart_title
        )
        st.plotly_chart(fig_tags, use_container_width=True)
    else:
        st.info("No tags available for analysis")
    
    # Task creation timeline
    if 'created_date' in task_df.columns:
        st.subheader("Task Creation Timeline")
        
        try:
            # Convert created dates to datetime
            task_df['created_date_parsed'] = pd.to_datetime(task_df['created_date'], errors='coerce')
            
            # Group by creation date
            timeline_data = task_df.groupby(task_df['created_date_parsed'].dt.date).size().reset_index()
            timeline_data.columns = ['Date', 'Tasks Created']
            
            fig_timeline = px.line(
                timeline_data, 
                x='Date', 
                y='Tasks Created',
                title="Task Creation Timeline",
                markers=True
            )
            st.plotly_chart(fig_timeline, use_container_width=True)
        except:
            st.info("Could not create timeline due to missing or invalid creation dates")
    
    # Completion rate over time
    if 'status' in task_df.columns and 'created_date' in task_df.columns:
        st.subheader("Task Completion Analysis")
        
        try:
            # Calculate cumulative counts
            task_df = task_df.sort_values('created_date_parsed')
            task_df['cumulative_total'] = range(1, len(task_df) + 1)
            
            completed_tasks_df = task_df[task_df['status'] == 'Completed'].copy()
            completed_tasks_df['cumulative_completed'] = range(1, len(completed_tasks_df) + 1)
            
            # Create data for plotting
            dates = pd.date_range(
                start=task_df['created_date_parsed'].min(),
                end=datetime.now(),
                freq='D'
            )
            
            plot_data = pd.DataFrame({'Date': dates})
            for i, row in plot_data.iterrows():
                current_date = row['Date']
                total_tasks = len(task_df[task_df['created_date_parsed'] <= current_date])
                completed_tasks = len(completed_tasks_df[completed_tasks_df['created_date_parsed'] <= current_date])
                
                plot_data.at[i, 'Total Tasks'] = total_tasks
                plot_data.at[i, 'Completed Tasks'] = completed_tasks
                plot_data.at[i, 'Completion Rate'] = completed_tasks / total_tasks * 100 if total_tasks > 0 else 0
            
            fig_completion = px.line(
                plot_data,
                x='Date',
                y=['Total Tasks', 'Completed Tasks'],
                title="Tasks Over Time"
            )
            st.plotly_chart(fig_completion, use_container_width=True)
            
            fig_rate = px.line(
                plot_data,
                x='Date',
                y='Completion Rate',
                title="Task Completion Rate Over Time (%)"
            )
            st.plotly_chart(fig_rate, use_container_width=True)
        except:
            st.info("Could not create completion analysis due to missing or invalid data")
