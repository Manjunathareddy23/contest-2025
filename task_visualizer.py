import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any
from datetime import datetime, timedelta
import pandas as pd

def create_task_visualizations(tasks: Dict[str, Dict[str, Any]]) -> None:
    """
    Create and display visualizations for task statistics.
    
    Args:
        tasks: Dictionary of tasks to visualize
    """
    if not tasks:
        st.info("No tasks available for visualization. Create some tasks to see statistics.")
        return
    
    # Convert tasks dictionary to list for easier processing
    task_list = list(tasks.values())
    
    # Create a container for visualizations with styling
    with st.container():
        st.markdown("<div class='chart-container fade-in'>", unsafe_allow_html=True)
        st.subheader("📊 Task Dashboard")
        
        # Create columns for KPI metrics
        col1, col2, col3, col4 = st.columns(4)
        
        # Total tasks
        with col1:
            st.markdown("<div class='stat-card'>", unsafe_allow_html=True)
            st.markdown(f"<div class='stat-number'>{len(task_list)}</div>", unsafe_allow_html=True)
            st.markdown("<div class='stat-label'>Total Tasks</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Tasks by status
        status_counts = {}
        for task in task_list:
            status = task.get("status", "Not Started")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Completed tasks
        with col2:
            st.markdown("<div class='stat-card'>", unsafe_allow_html=True)
            completed_count = status_counts.get("Completed", 0)
            st.markdown(f"<div class='stat-number'>{completed_count}</div>", unsafe_allow_html=True)
            st.markdown("<div class='stat-label'>Completed</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Tasks due soon (next 3 days)
        with col3:
            st.markdown("<div class='stat-card'>", unsafe_allow_html=True)
            today = datetime.now().date()
            due_soon_count = 0
            for task in task_list:
                due_date_str = task.get("due_date", "")
                status = task.get("status", "")
                if status != "Completed" and due_date_str:
                    try:
                        due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
                        if due_date <= today + timedelta(days=3) and due_date >= today:
                            due_soon_count += 1
                    except (ValueError, TypeError):
                        pass
            
            st.markdown(f"<div class='stat-number'>{due_soon_count}</div>", unsafe_allow_html=True)
            st.markdown("<div class='stat-label'>Due Soon</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        # Overdue tasks
        with col4:
            st.markdown("<div class='stat-card'>", unsafe_allow_html=True)
            today = datetime.now().date()
            overdue_count = 0
            for task in task_list:
                due_date_str = task.get("due_date", "")
                status = task.get("status", "")
                if status != "Completed" and due_date_str:
                    try:
                        due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
                        if due_date < today:
                            overdue_count += 1
                    except (ValueError, TypeError):
                        pass
            
            st.markdown(f"<div class='stat-number'>{overdue_count}</div>", unsafe_allow_html=True)
            st.markdown("<div class='stat-label'>Overdue</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<hr/>", unsafe_allow_html=True)
        
        # Create two columns for the main charts
        col1, col2 = st.columns(2)
        
        # Status distribution pie chart
        with col1:
            # Prepare data for the chart
            status_data = []
            for status, count in status_counts.items():
                status_data.append({"status": status, "count": count})
            
            if status_data:
                df_status = pd.DataFrame(status_data)
                
                # Color mapping for status
                status_colors = {
                    "Completed": "#2ECC71",
                    "In Progress": "#3498DB",
                    "Not Started": "#95A5A6"
                }
                
                # Create pie chart
                fig_status = px.pie(
                    df_status, 
                    values="count", 
                    names="status",
                    title="Tasks by Status",
                    color="status",
                    color_discrete_map=status_colors,
                    hole=0.4
                )
                
                fig_status.update_layout(
                    legend=dict(orientation="h", yanchor="bottom", y=-0.15),
                    margin=dict(t=40, b=40, l=40, r=40),
                    height=350
                )
                
                fig_status.update_traces(textposition='inside', textinfo='percent+label')
                
                st.plotly_chart(fig_status, use_container_width=True)
        
        # Priority distribution bar chart
        with col2:
            # Count tasks by priority
            priority_counts = {}
            for task in task_list:
                priority = task.get("priority", "Medium")
                priority_counts[priority] = priority_counts.get(priority, 0) + 1
            
            # Prepare data for the chart
            priority_data = []
            for priority, count in priority_counts.items():
                priority_data.append({"priority": priority, "count": count})
            
            if priority_data:
                df_priority = pd.DataFrame(priority_data)
                
                # Sort by priority level
                priority_order = ["High", "Medium", "Low"]
                df_priority["priority"] = pd.Categorical(
                    df_priority["priority"], 
                    categories=priority_order, 
                    ordered=True
                )
                df_priority = df_priority.sort_values("priority")
                
                # Color mapping for priority
                priority_colors = {
                    "High": "#E74C3C",
                    "Medium": "#F39C12",
                    "Low": "#3498DB"
                }
                
                # Create bar chart
                fig_priority = px.bar(
                    df_priority,
                    x="priority",
                    y="count",
                    title="Tasks by Priority",
                    color="priority",
                    color_discrete_map=priority_colors,
                    text="count"
                )
                
                fig_priority.update_layout(
                    xaxis_title="",
                    yaxis_title="Number of Tasks",
                    showlegend=False,
                    margin=dict(t=40, b=40, l=40, r=40),
                    height=350
                )
                
                fig_priority.update_traces(textposition='auto')
                
                st.plotly_chart(fig_priority, use_container_width=True)
        
        # Task due dates timeline
        upcoming_tasks = [task for task in task_list if task.get("status") != "Completed"]
        if upcoming_tasks:
            st.markdown("<hr/>", unsafe_allow_html=True)
            st.subheader("📅 Upcoming Deadlines")
            
            # Prepare timeline data
            timeline_data = []
            for task in upcoming_tasks:
                due_date_str = task.get("due_date", "")
                if due_date_str:
                    try:
                        due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
                        priority = task.get("priority", "Medium")
                        
                        # Color based on priority
                        color = "#3498DB"  # Default blue
                        if priority == "High":
                            color = "#E74C3C"  # Red
                        elif priority == "Medium":
                            color = "#F39C12"  # Orange
                        
                        timeline_data.append({
                            "task": task.get("title", "Unnamed task"),
                            "due_date": due_date,
                            "priority": priority,
                            "color": color
                        })
                    except (ValueError, TypeError):
                        pass
            
            if timeline_data:
                # Sort by due date
                timeline_data.sort(key=lambda x: x["due_date"])
                
                # Create DataFrame
                df_timeline = pd.DataFrame(timeline_data)
                
                # Limit to the next 10 tasks
                if len(df_timeline) > 10:
                    df_timeline = df_timeline.head(10)
                
                # Create horizontal timeline
                fig_timeline = go.Figure()
                
                for i, row in df_timeline.iterrows():
                    fig_timeline.add_trace(go.Scatter(
                        x=[row["due_date"]],
                        y=[row["task"]],
                        mode="markers",
                        marker=dict(
                            size=12,
                            color=row["color"],
                            symbol="circle"
                        ),
                        name=row["priority"],
                        hovertemplate=f"<b>{row['task']}</b><br>Due: {row['due_date']}<br>Priority: {row['priority']}"
                    ))
                
                # Calculate date range for x-axis
                today = datetime.now().date()
                min_date = today
                max_date = today + timedelta(days=14)
                
                if not df_timeline.empty:
                    task_min_date = df_timeline["due_date"].min()
                    task_max_date = df_timeline["due_date"].max()
                    
                    if task_min_date < min_date:
                        min_date = task_min_date
                    
                    if task_max_date > max_date:
                        max_date = task_max_date
                
                # Adjust date range to include a bit of padding
                min_date = min_date - timedelta(days=1)
                max_date = max_date + timedelta(days=1)
                
                fig_timeline.update_layout(
                    title="Task Timeline",
                    xaxis=dict(
                        title="Due Date",
                        type="date",
                        range=[min_date, max_date]
                    ),
                    yaxis=dict(
                        title="",
                        autorange="reversed"  # Reverses the order to have earliest task at the top
                    ),
                    height=max(300, 50 * len(df_timeline)),
                    margin=dict(l=10, r=10, t=40, b=40),
                    hovermode="closest",
                    showlegend=False
                )
                
                # Add a vertical line for today
                fig_timeline.add_vline(
                    x=today,
                    line_dash="dash",
                    line_color="gray",
                    opacity=0.7,
                    annotation_text="Today",
                    annotation_position="top right"
                )
                
                st.plotly_chart(fig_timeline, use_container_width=True)
            else:
                st.info("No upcoming deadlines with valid due dates.")
        
        # Add tag distribution if there are tags
        all_tags = []
        for task in task_list:
            tags = task.get("tags", [])
            if isinstance(tags, list):
                all_tags.extend(tags)
            elif isinstance(tags, str) and tags:
                # Handle case where tags might be stored as comma-separated string
                tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
                all_tags.extend(tag_list)
        
        if all_tags:
            st.markdown("<hr/>", unsafe_allow_html=True)
            st.subheader("🏷️ Popular Tags")
            
            # Count tag occurrences
            tag_counts = {}
            for tag in all_tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
            
            # Sort tags by frequency
            sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
            
            # Limit to top 10 tags
            top_tags = sorted_tags[:10]
            
            # Prepare data for the chart
            tag_data = [{"tag": tag, "count": count} for tag, count in top_tags]
            
            if tag_data:
                df_tags = pd.DataFrame(tag_data)
                
                # Create horizontal bar chart
                fig_tags = px.bar(
                    df_tags,
                    y="tag",
                    x="count",
                    title="Top Tags",
                    text="count",
                    orientation="h",
                    color="count",
                    color_continuous_scale="Blues"
                )
                
                fig_tags.update_layout(
                    xaxis_title="Number of Tasks",
                    yaxis_title="",
                    showlegend=False,
                    coloraxis_showscale=False,
                    margin=dict(t=40, b=40, l=40, r=40),
                    height=350
                )
                
                fig_tags.update_traces(textposition='auto')
                
                st.plotly_chart(fig_tags, use_container_width=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
