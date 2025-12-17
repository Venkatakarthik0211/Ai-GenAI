"""Streamlit UI for ML Pipeline."""

import streamlit as st
import requests
import json
from datetime import datetime
from typing import Optional, Dict, Any
import pandas as pd

# API Configuration
API_BASE_URL = "http://backend:8000/api"  # Docker service name
# For local development, use: API_BASE_URL = "http://localhost:8000/api"

# Page configuration
st.set_page_config(
    page_title="ML Pipeline Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize page state
if 'current_page' not in st.session_state:
    st.session_state.current_page = "Create Pipeline"

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stage-card {
        padding: 1rem;
        border-radius: 0.5rem;
        border: 2px solid #ddd;
        margin: 0.5rem 0;
    }
    .stage-active {
        border-color: #1f77b4;
        background-color: #e7f3ff;
    }
    .stage-completed {
        border-color: #2ca02c;
        background-color: #e8f5e9;
    }
    .stage-pending {
        border-color: #ddd;
        background-color: #f9f9f9;
    }
    .metric-card {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables."""
    if 'pipeline_run_id' not in st.session_state:
        st.session_state.pipeline_run_id = None
    if 'mlflow_run_id' not in st.session_state:
        st.session_state.mlflow_run_id = None
    if 'current_node' not in st.session_state:
        st.session_state.current_node = None
    if 'data_profile' not in st.session_state:
        st.session_state.data_profile = None
    if 'pipeline_status' not in st.session_state:
        st.session_state.pipeline_status = "Not Started"

    # Natural language extraction details
    if 'extracted_config' not in st.session_state:
        st.session_state.extracted_config = None
    if 'config_confidence' not in st.session_state:
        st.session_state.config_confidence = None
    if 'config_reasoning' not in st.session_state:
        st.session_state.config_reasoning = None
    if 'config_assumptions' not in st.session_state:
        st.session_state.config_assumptions = None
    if 'config_warnings' not in st.session_state:
        st.session_state.config_warnings = None


def call_load_data_api(
    data_path: str,
    user_prompt: Optional[str] = None,
    target_column: Optional[str] = None,
    experiment_name: str = "ml_pipeline_experiment",
    test_size: float = 0.2,
    random_state: int = 42,
    user_hints: Optional[Dict[str, Any]] = None
) -> Optional[Dict[str, Any]]:
    """
    Call the FastAPI load-data endpoint.

    Supports two modes:
    1. Natural Language: Provide user_prompt + data_path
    2. Traditional: Provide target_column + data_path + config params

    Args:
        data_path: Path to data file
        user_prompt: Natural language description (for NL mode)
        target_column: Target column name (for traditional mode)
        experiment_name: MLflow experiment name
        test_size: Test set size ratio
        random_state: Random state for reproducibility
        user_hints: Optional hints for Bedrock extraction

    Returns:
        Response dict or None if failed
    """
    try:
        url = f"{API_BASE_URL}/pipeline/load-data"

        # Build payload based on mode
        if user_prompt:
            # Natural language mode
            payload = {
                "data_path": data_path,
                "user_prompt": user_prompt,
                "experiment_name": experiment_name
            }
            if user_hints:
                payload["user_hints"] = user_hints
            spinner_text = "🤖 Analyzing prompt with AWS Bedrock and loading data..."
        else:
            # Traditional mode
            payload = {
                "data_path": data_path,
                "target_column": target_column,
                "experiment_name": experiment_name,
                "test_size": test_size,
                "random_state": random_state
            }
            spinner_text = "Loading data and initializing MLflow..."

        with st.spinner(spinner_text):
            response = requests.post(url, json=payload, timeout=120)

        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code}")
            st.json(response.json())
            return None

    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to API backend. Make sure the backend service is running.")
        return None
    except Exception as e:
        st.error(f"❌ Error calling API: {str(e)}")
        return None


def get_pipeline_state(pipeline_run_id: str) -> Optional[Dict[str, Any]]:
    """Get pipeline state from API."""
    try:
        url = f"{API_BASE_URL}/pipeline/state/{pipeline_run_id}"
        response = requests.get(url, timeout=30)

        if response.status_code == 200:
            return response.json()
        else:
            return None

    except Exception as e:
        st.error(f"Error getting pipeline state: {str(e)}")
        return None


def get_all_pipeline_runs() -> Optional[Dict[str, Any]]:
    """Get all pipeline runs from API."""
    try:
        url = f"{API_BASE_URL}/pipeline/runs"
        response = requests.get(url, timeout=30)

        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code}")
            return None

    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to API backend.")
        return None
    except Exception as e:
        st.error(f"Error getting pipeline runs: {str(e)}")
        return None


def stop_pipeline(pipeline_run_id: str) -> bool:
    """Stop a running pipeline."""
    try:
        url = f"{API_BASE_URL}/pipeline/stop/{pipeline_run_id}"
        response = requests.post(url, timeout=30)

        if response.status_code == 200:
            return True
        else:
            st.error(f"Failed to stop pipeline: {response.status_code}")
            return False

    except Exception as e:
        st.error(f"Error stopping pipeline: {str(e)}")
        return False


def delete_pipeline(pipeline_run_id: str, delete_experiment: bool = False) -> bool:
    """Delete a pipeline run."""
    try:
        url = f"{API_BASE_URL}/pipeline/delete/{pipeline_run_id}"
        params = {"delete_experiment": delete_experiment}
        response = requests.delete(url, params=params, timeout=30)

        if response.status_code == 200:
            return True
        else:
            st.error(f"Failed to delete pipeline: {response.status_code}")
            return False

    except Exception as e:
        st.error(f"Error deleting pipeline: {str(e)}")
        return False


def display_pipeline_stages(current_node: str = None, completed_nodes: list = None):
    """Display pipeline stages with status indicators."""
    stages = [
        {"name": "Load Data", "node": "load_data", "icon": "📥"},
        {"name": "Clean Data", "node": "clean_data", "icon": "🧹"},
        {"name": "Handle Missing", "node": "handle_missing", "icon": "🔧"},
        {"name": "Encode Features", "node": "encode_features", "icon": "🔢"},
        {"name": "Scale Features", "node": "scale_features", "icon": "⚖️"},
        {"name": "Split Data", "node": "split_data", "icon": "✂️"},
        {"name": "Train Models", "node": "train_models", "icon": "🤖"},
        {"name": "Evaluate", "node": "evaluate", "icon": "📊"},
    ]

    completed = completed_nodes or []

    st.markdown("### Pipeline Stages")

    cols = st.columns(4)
    for idx, stage in enumerate(stages):
        col = cols[idx % 4]

        with col:
            if stage["node"] in completed:
                status_class = "stage-completed"
                status_icon = "✅"
            elif current_node == stage["node"]:
                status_class = "stage-active"
                status_icon = "🔄"
            else:
                status_class = "stage-pending"
                status_icon = "⏳"

            st.markdown(f"""
            <div class="stage-card {status_class}">
                <div style="font-size: 2rem;">{stage['icon']} {status_icon}</div>
                <div style="font-weight: bold;">{stage['name']}</div>
                <div style="font-size: 0.8rem; color: #666;">{stage['node']}</div>
            </div>
            """, unsafe_allow_html=True)


def show_pipeline_management_page():
    """Display pipeline management page with list of all runs."""
    st.markdown('<div class="main-header">📋 Pipeline Management</div>', unsafe_allow_html=True)

    # Refresh button
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    with col2:
        auto_refresh = st.checkbox("Auto-refresh", value=False)

    if auto_refresh:
        import time
        time.sleep(5)
        st.rerun()

    # Get all pipeline runs
    result = get_all_pipeline_runs()

    if result:
        runs = result.get("runs", [])
        total = result.get("total", 0)

        st.markdown(f"### Total Pipelines: {total}")

        if runs:
            # Create DataFrame for display
            df_data = []
            for run in runs:
                status_emoji = {
                    "running": "🟢",
                    "completed": "✅",
                    "failed": "❌",
                    "stopped": "🛑",
                    "unknown": "❓"
                }.get(run.get("status", "unknown"), "❓")

                df_data.append({
                    "Status": f"{status_emoji} {run.get('status', 'unknown').upper()}",
                    "Pipeline ID": run.get("pipeline_run_id", "N/A"),
                    "Current Node": run.get("current_node", "N/A"),
                    "Start Time": run.get("start_time", "N/A")[:19].replace("T", " ") if run.get("start_time") else "N/A",
                    "Data Path": run.get("data_path", "N/A"),
                    "Target": run.get("target_column", "N/A"),
                    "Completed": len(run.get("completed_nodes", [])),
                    "Failed": len(run.get("failed_nodes", [])),
                })

            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True, hide_index=True)

            st.divider()

            # Detailed view for each pipeline
            for idx, run in enumerate(runs):
                pipeline_id = run.get("pipeline_run_id", "N/A")
                status = run.get("status", "unknown")

                with st.expander(f"📊 {pipeline_id} - {status.upper()}", expanded=False):
                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("#### Pipeline Details")
                        st.write(f"**Pipeline ID:** {pipeline_id}")
                        st.write(f"**Status:** {status}")
                        st.write(f"**Current Node:** {run.get('current_node', 'N/A')}")
                        st.write(f"**Start Time:** {run.get('start_time', 'N/A')[:19].replace('T', ' ') if run.get('start_time') else 'N/A'}")
                        if run.get('end_time'):
                            st.write(f"**End Time:** {run.get('end_time', 'N/A')[:19].replace('T', ' ')}")

                    with col2:
                        st.markdown("#### Configuration")
                        st.write(f"**Data Path:** {run.get('data_path', 'N/A')}")
                        st.write(f"**Target Column:** {run.get('target_column', 'N/A')}")
                        st.write(f"**MLflow Run ID:** {run.get('mlflow_run_id', 'N/A')}")
                        st.write(f"**MLflow Experiment ID:** {run.get('mlflow_experiment_id', 'N/A')}")

                    # Progress
                    st.markdown("#### Progress")
                    completed = run.get("completed_nodes", [])
                    failed = run.get("failed_nodes", [])

                    if completed:
                        st.success(f"✅ Completed Nodes: {', '.join(completed)}")
                    if failed:
                        st.error(f"❌ Failed Nodes: {', '.join(failed)}")

                    # Errors
                    errors = run.get("errors", [])
                    if errors:
                        st.markdown("#### Errors")
                        for error in errors:
                            st.error(f"**{error.get('node_name', 'Unknown')}:** {error.get('error_message', 'No message')}")

                    # Action buttons
                    st.markdown("#### Actions")
                    btn_col1, btn_col2, btn_col3, btn_col4 = st.columns(4)

                    with btn_col1:
                        if status == "running":
                            if st.button("🛑 Stop", key=f"stop_{idx}", use_container_width=True):
                                if stop_pipeline(pipeline_id):
                                    st.success(f"Stopped pipeline {pipeline_id}")
                                    st.rerun()

                    with btn_col2:
                        if st.button("🗑️ Delete", key=f"delete_{idx}", use_container_width=True, type="secondary"):
                            if delete_pipeline(pipeline_id, delete_experiment=False):
                                st.success(f"Deleted pipeline {pipeline_id}")
                                st.rerun()

                    with btn_col3:
                        if st.button("🗑️ Delete + Experiment", key=f"delete_exp_{idx}", use_container_width=True, type="secondary"):
                            if delete_pipeline(pipeline_id, delete_experiment=True):
                                st.success(f"Deleted pipeline and experiment {pipeline_id}")
                                st.rerun()

                    with btn_col4:
                        mlflow_url = f"http://localhost:5000/#/experiments/{run.get('mlflow_experiment_id')}/runs/{run.get('mlflow_run_id')}"
                        st.markdown(f"[🔬 View in MLflow]({mlflow_url})", unsafe_allow_html=True)

        else:
            st.info("No pipeline runs found. Create a new pipeline to get started!")
            if st.button("➕ Create New Pipeline"):
                st.session_state.current_page = "Create Pipeline"
                st.rerun()


def get_pipeline_flow_diagram(current_node: str = None, mode: str = "natural_language") -> str:
    """
    Generate Mermaid diagram for pipeline flow.

    Args:
        current_node: Currently executing node (to highlight)
        mode: "natural_language" or "traditional"

    Returns:
        Mermaid diagram string
    """
    # Define node styles based on current execution
    current_style = "fill:#4CAF50,stroke:#2E7D32,stroke-width:4px,color:#fff"

    # Build style definitions
    styles = ""
    if current_node:
        styles = f"    style {current_node} {current_style}\n"

    # Natural language mode includes analyze_prompt
    entry_point = """    Start([🚀 Start]) --> Conditional{{Input Mode?}}
    Conditional -->|Natural Language| analyze_prompt[🤖 Analyze Prompt<br/>Bedrock Config Extraction]
    Conditional -->|Traditional Config| load_data[📂 Load Data]
    analyze_prompt --> load_data""" if mode == "natural_language" else """    Start([🚀 Start]) --> load_data[📂 Load Data]"""

    diagram = f"""```mermaid
graph TD
{entry_point}
    load_data --> clean_data[🧹 Clean Data<br/>Remove invalid rows]
    clean_data --> handle_missing[🔧 Handle Missing<br/>Imputation strategies]
    handle_missing --> encode_features[🔤 Encode Features<br/>Categorical encoding]
    encode_features --> scale_features[📊 Scale Features<br/>Normalization]
    scale_features --> split_data[✂️ Split Data<br/>Train/Test split]
    split_data --> train_models[🎓 Train Models<br/>Multiple algorithms]
    train_models --> evaluate_models[📈 Evaluate Models<br/>Performance metrics]
    evaluate_models --> select_best[🏆 Select Best<br/>Model selection]
    select_best --> generate_report[📝 Generate Report<br/>Results & artifacts]
    generate_report --> End([✅ Complete])

{styles}
    classDef default fill:#E3F2FD,stroke:#1976D2,stroke-width:2px
    classDef startEnd fill:#F3E5F5,stroke:#7B1FA2,stroke-width:3px
    classDef decision fill:#FFF3E0,stroke:#F57C00,stroke-width:2px

    class Start,End startEnd
    class Conditional decision
```"""

    return diagram


def show_create_pipeline_page():
    """Display create pipeline page with natural language prompt interface."""
    initialize_session_state()

    # Header
    st.markdown('<div class="main-header">🤖 ML Pipeline with Natural Language</div>', unsafe_allow_html=True)

    # Show pipeline flow diagram
    with st.expander("📊 View Pipeline Workflow", expanded=False):
        st.markdown("### LangGraph Pipeline Flow Diagram")

        # Determine current node
        current_node = st.session_state.get("current_node")
        mode = "natural_language"

        # Display diagram
        diagram = get_pipeline_flow_diagram(current_node, mode)
        st.markdown(diagram, unsafe_allow_html=True)

        # Show legend and status
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            **Legend:**
            - 🟢 **Green**: Currently executing
            - 🔵 **Blue**: Pending nodes
            - 🟣 **Purple**: Start/End points
            - 🟠 **Orange**: Decision points
            """)
        with col2:
            if current_node:
                st.info(f"**Current Node:** `{current_node}`")
            else:
                st.info("**Status:** Not started")

    st.divider()

    # Sidebar for data path
    with st.sidebar:
        st.header("📁 Data Configuration")

        data_path = st.text_input(
            "Data File Path",
            value="data/sample/test_data.csv",
            help="Path to your training data file (CSV, Parquet, or Excel)"
        )

        st.divider()
        st.markdown("### 💡 Example Prompts")
        st.markdown("""
        - *Classify iris species with high accuracy*
        - *Predict house prices using regression with 80/20 split*
        - *Detect fraud in credit card transactions, optimize for recall*
        - *Classify sentiment in reviews, try multiple algorithms*
        """)

        st.divider()

        # Refresh state button
        if st.session_state.pipeline_run_id:
            if st.button("🔄 Refresh Status", use_container_width=True):
                state = get_pipeline_state(st.session_state.pipeline_run_id)
                if state:
                    st.session_state.current_node = state.get("current_node")
                    st.session_state.pipeline_status = state.get("pipeline_status")
                    st.rerun()

    # Main content area
    if st.session_state.pipeline_run_id:
        # Display status metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 2rem;">📋</div>
                <div style="font-weight: bold; margin-top: 0.5rem;">Pipeline Run ID</div>
                <div style="font-size: 0.9rem; color: #666;">{st.session_state.pipeline_run_id}</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 2rem;">🔬</div>
                <div style="font-weight: bold; margin-top: 0.5rem;">MLflow Run ID</div>
                <div style="font-size: 0.9rem; color: #666;">{st.session_state.mlflow_run_id or 'N/A'}</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 2rem;">📍</div>
                <div style="font-weight: bold; margin-top: 0.5rem;">Current Node</div>
                <div style="font-size: 0.9rem; color: #666;">{st.session_state.current_node or 'N/A'}</div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            status_icon = "🟢" if st.session_state.pipeline_status == "Running" else "🔵"
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size: 2rem;">{status_icon}</div>
                <div style="font-weight: bold; margin-top: 0.5rem;">Status</div>
                <div style="font-size: 0.9rem; color: #666;">{st.session_state.pipeline_status}</div>
            </div>
            """, unsafe_allow_html=True)

        st.divider()

        # Display pipeline stages
        display_pipeline_stages(
            current_node=st.session_state.current_node,
            completed_nodes=["load_data"] if st.session_state.current_node else []
        )

        st.divider()

        # Display AI extraction details if available (natural language mode)
        if st.session_state.extracted_config:
            st.markdown("### 🤖 AI Configuration Extraction")

            config = st.session_state.extracted_config
            confidence = st.session_state.config_confidence

            # Confidence indicator
            if confidence:
                confidence_color = "green" if confidence >= 0.8 else "orange" if confidence >= 0.6 else "red"
                st.markdown(f"""
                <div style="padding: 1rem; background-color: #f0f2f6; border-radius: 0.5rem; border-left: 4px solid {confidence_color}; margin-bottom: 1rem;">
                    <strong>Extraction Confidence:</strong> {confidence * 100:.1f}%
                </div>
                """, unsafe_allow_html=True)

            # Extracted configuration
            st.markdown("#### 📋 Extracted Configuration")
            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"**Target Column:** `{config.get('target_column', 'N/A')}`")
                st.markdown(f"**Analysis Type:** `{config.get('analysis_type', 'N/A')}`")
                st.markdown(f"**Experiment Name:** `{config.get('experiment_name', 'N/A')}`")

            with col2:
                st.markdown(f"**Test Size:** `{config.get('test_size', 0.2)}`")
                st.markdown(f"**Random State:** `{config.get('random_state', 42)}`")
                if config.get('primary_metric'):
                    st.markdown(f"**Optimization Metric:** `{config.get('primary_metric')}`")

            # Reasoning
            if st.session_state.config_reasoning:
                with st.expander("💭 AI Reasoning"):
                    st.markdown(st.session_state.config_reasoning)

            # Assumptions
            if st.session_state.config_assumptions:
                with st.expander("📝 Assumptions"):
                    for assumption in st.session_state.config_assumptions:
                        st.markdown(f"- {assumption}")

            # Warnings
            if st.session_state.config_warnings:
                with st.expander("⚠️ Warnings", expanded=True):
                    for warning in st.session_state.config_warnings:
                        st.warning(warning)

            st.divider()

        # Display data profile
        if st.session_state.data_profile:
            st.markdown("### 📊 Data Profile")

            profile = st.session_state.data_profile

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Number of Samples", profile.get("n_samples", 0))

            with col2:
                st.metric("Number of Features", profile.get("n_features", 0))

            with col3:
                st.metric("Target Column", profile.get("target_column", "N/A"))

            # Feature names
            if profile.get("feature_names"):
                with st.expander("📝 Feature Names"):
                    st.write(", ".join(profile["feature_names"]))

            # Target distribution
            if profile.get("target_distribution"):
                with st.expander("📈 Target Distribution"):
                    dist_df = pd.DataFrame([
                        {"Class": str(k), "Count": v}
                        for k, v in profile["target_distribution"].items()
                    ])
                    st.dataframe(dist_df, use_container_width=True)

    else:
        # Natural language prompt interface
        st.markdown("### 💬 Describe Your ML Task")
        st.markdown("""
        Tell me what you want to achieve in natural language. I'll use **AWS Bedrock**
        to understand your requirements and automatically configure the pipeline.
        """)

        user_prompt = st.text_area(
            "Your ML Task",
            value="",
            height=150,
            placeholder="Example: Classify iris species using all available algorithms and optimize for accuracy",
            help="Describe your machine learning task in natural language. Be specific about the target, analysis type, and any preferences."
        )

        # Experiment name input
        experiment_name = st.text_input(
            "Experiment Name",
            value="ml_pipeline_experiment",
            help="Name for the MLflow experiment"
        )

        # Start pipeline button
        if st.button("🚀 Start Pipeline with AI Configuration", type="primary", use_container_width=True):
            if not user_prompt.strip():
                st.error("⚠️ Please enter a description of your ML task")
            elif not data_path.strip():
                st.error("⚠️ Please enter a data file path in the sidebar")
            else:
                # Call unified load-data endpoint with user_prompt
                result = call_load_data_api(
                    data_path=data_path,
                    user_prompt=user_prompt,
                    experiment_name=experiment_name
                )

                if result and result.get("success"):
                    # Store pipeline information
                    st.session_state.pipeline_run_id = result.get("pipeline_run_id")
                    st.session_state.mlflow_run_id = result.get("mlflow_run_id")
                    st.session_state.data_profile = result.get("data_profile")
                    st.session_state.current_node = "load_data"
                    st.session_state.pipeline_status = "Running"

                    # Store extraction details if provided
                    st.session_state.extracted_config = result.get("extracted_config")
                    st.session_state.config_confidence = result.get("confidence")
                    st.session_state.config_reasoning = result.get("reasoning")
                    st.session_state.config_assumptions = result.get("assumptions")
                    st.session_state.config_warnings = result.get("config_warnings")

                    st.success("✅ Pipeline started successfully!")
                    st.rerun()

        st.divider()

        # Info section
        st.markdown("""
        ### Welcome to the Natural Language ML Pipeline

        This intelligent dashboard uses **AWS Bedrock** to understand your ML requirements:

        #### ✨ Features:
        - 🤖 **Natural Language Configuration** - Describe your task in plain English
        - 🧠 **AI-Powered Extraction** - AWS Bedrock extracts pipeline configuration automatically
        - 📊 **Context-Aware** - Analyzes your data structure for better suggestions
        - 🔬 **MLflow Integration** - Automatic experiment tracking
        - 📈 **Real-time Progress** - Monitor your pipeline execution

        #### 🚀 Getting Started:
        1. Enter your data file path in the sidebar (e.g., `data/iris.csv`)
        2. Describe your ML task in natural language above
        3. Click "Start Pipeline with AI Configuration"
        4. Monitor the pipeline progress and view extracted configuration

        #### 💡 Tip:
        Be specific about what you want to achieve. Mention:
        - The target variable or prediction goal
        - Type of problem (classification/regression)
        - Any preferences for algorithms or metrics
        - Train/test split preferences
        """)


def main():
    """Main Streamlit app."""

    # Sidebar navigation
    with st.sidebar:
        st.markdown("## 🧭 Navigation")
        page = st.radio(
            "Select Page:",
            ["Create Pipeline", "Manage Pipelines"],
            index=0 if st.session_state.current_page == "Create Pipeline" else 1,
            label_visibility="collapsed"
        )
        st.session_state.current_page = page
        st.divider()

    # Route to appropriate page
    if st.session_state.current_page == "Create Pipeline":
        show_create_pipeline_page()
    elif st.session_state.current_page == "Manage Pipelines":
        show_pipeline_management_page()


if __name__ == "__main__":
    main()
