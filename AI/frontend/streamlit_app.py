"""
Streamlit Frontend for ML Pipeline

Web interface for natural language ML pipeline configuration using AWS Bedrock.

Features:
- Natural language prompt input
- Optional configuration hints
- Real-time configuration extraction preview
- Execution history and analytics
"""

import streamlit as st
import requests
import json
from datetime import datetime
from typing import Dict, Any, Optional
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="ML Pipeline - Natural Language Config",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API endpoint configuration
API_BASE_URL = st.secrets.get("API_BASE_URL", "http://localhost:8000")


def run_pipeline(
    data_path: str,
    user_prompt: str,
    user_hints: Optional[Dict[str, Any]] = None,
    bedrock_model_id: str = "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
    confidence_threshold: float = 0.70
) -> Dict[str, Any]:
    """
    Call API to run pipeline with natural language configuration.

    Args:
        data_path: Path to CSV data file
        user_prompt: Natural language description
        user_hints: Optional hints to guide extraction
        bedrock_model_id: Bedrock model ID
        confidence_threshold: Minimum confidence threshold

    Returns:
        API response dictionary
    """
    endpoint = f"{API_BASE_URL}/api/v1/pipeline/run"

    payload = {
        "data_path": data_path,
        "user_prompt": user_prompt,
        "user_hints": user_hints or {},
        "bedrock_model_id": bedrock_model_id,
        "confidence_threshold": confidence_threshold
    }

    response = requests.post(endpoint, json=payload, timeout=120)
    response.raise_for_status()

    return response.json()


def search_similar_prompts(query: str, limit: int = 5) -> Dict[str, Any]:
    """Search for similar historical prompts"""
    endpoint = f"{API_BASE_URL}/api/v1/pipeline/search-prompts"

    payload = {
        "query": query,
        "limit": limit,
        "min_confidence": 0.7
    }

    response = requests.post(endpoint, json=payload, timeout=30)
    response.raise_for_status()

    return response.json()


def get_analytics() -> Dict[str, Any]:
    """Get analytics summary"""
    endpoint = f"{API_BASE_URL}/api/v1/pipeline/analytics"

    response = requests.get(endpoint, timeout=30)
    response.raise_for_status()

    return response.json()


def health_check() -> Dict[str, Any]:
    """Check API health"""
    endpoint = f"{API_BASE_URL}/api/v1/pipeline/health"

    try:
        response = requests.get(endpoint, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"status": "error", "error": str(e)}


# Main app
def main():
    st.title("🤖 ML Pipeline - Natural Language Configuration")
    st.markdown("Powered by AWS Bedrock Claude Sonnet 4.5")

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")

        # API health check
        health = health_check()
        if health.get("status") == "healthy":
            st.success("✅ API Status: Healthy")
        else:
            st.error(f"❌ API Status: {health.get('status', 'Unknown')}")

        st.divider()

        # Bedrock configuration
        st.subheader("AWS Bedrock Settings")

        bedrock_model = st.selectbox(
            "Primary Model",
            [
                "us.anthropic.claude-sonnet-4-5-20250929-v1:0",
                "anthropic.claude-3-7-sonnet-20250219-v1:0"
            ],
            index=0
        )

        confidence_threshold = st.slider(
            "Confidence Threshold",
            min_value=0.0,
            max_value=1.0,
            value=0.70,
            step=0.05,
            help="Minimum confidence required for extraction"
        )

        st.divider()

        # Navigation
        st.subheader("Navigation")
        page = st.radio(
            "Select Page",
            ["🚀 Run Pipeline", "🔍 Search History", "📊 Analytics"],
            label_visibility="collapsed"
        )

    # Page routing
    if page == "🚀 Run Pipeline":
        run_pipeline_page(bedrock_model, confidence_threshold)
    elif page == "🔍 Search History":
        search_history_page()
    elif page == "📊 Analytics":
        analytics_page()


def run_pipeline_page(bedrock_model: str, confidence_threshold: float):
    """Main pipeline execution page"""

    st.header("🚀 Run ML Pipeline")

    st.markdown("""
    Describe your machine learning task in plain English. The system will automatically extract:
    - Target column to predict
    - Experiment name
    - Train/test split ratio
    - Random seed
    - Analysis type (classification/regression)
    """)

    # Input form
    with st.form("pipeline_form"):
        # Data path input
        data_path = st.text_input(
            "📁 Data File Path",
            placeholder="/data/house_prices.csv",
            help="Path to your CSV data file"
        )

        # Natural language prompt
        user_prompt = st.text_area(
            "💬 Describe Your ML Task",
            height=150,
            placeholder="Example: Predict house prices using the price column with an 80/20 train-test split",
            help="Describe what you want to predict and any specific requirements"
        )

        # Advanced options (expandable)
        with st.expander("🔧 Advanced Options (Optional)"):
            st.markdown("**Provide hints to guide configuration extraction:**")

            col1, col2 = st.columns(2)

            with col1:
                hint_target = st.text_input(
                    "Target Column Hint",
                    placeholder="e.g., price"
                )

                hint_analysis = st.selectbox(
                    "Analysis Type Hint",
                    ["", "classification", "regression"]
                )

            with col2:
                hint_test_size = st.number_input(
                    "Test Size Hint",
                    min_value=0.0,
                    max_value=1.0,
                    value=0.0,
                    step=0.05,
                    help="Leave at 0 to let AI decide"
                )

                hint_random_state = st.number_input(
                    "Random State Hint",
                    min_value=0,
                    max_value=10000,
                    value=0,
                    help="Leave at 0 to let AI decide"
                )

        # Submit button
        submit_button = st.form_submit_button(
            "🚀 Extract Config & Run Pipeline",
            type="primary",
            use_container_width=True
        )

    # Process submission
    if submit_button:
        # Validation
        if not data_path:
            st.error("❌ Please provide a data file path")
            return

        if not user_prompt or len(user_prompt.strip()) < 10:
            st.error("❌ Please provide a more detailed description (at least 10 characters)")
            return

        # Build user hints
        user_hints = {}
        if hint_target:
            user_hints["target_column"] = hint_target
        if hint_analysis:
            user_hints["analysis_type"] = hint_analysis
        if hint_test_size > 0:
            user_hints["test_size"] = hint_test_size
        if hint_random_state > 0:
            user_hints["random_state"] = hint_random_state

        # Show progress
        with st.spinner("🤖 Extracting configuration with AWS Bedrock..."):
            try:
                # Call API
                result = run_pipeline(
                    data_path=data_path,
                    user_prompt=user_prompt,
                    user_hints=user_hints if user_hints else None,
                    bedrock_model_id=bedrock_model,
                    confidence_threshold=confidence_threshold
                )

                # Display results
                if result.get("success"):
                    st.success("✅ Pipeline executed successfully!")

                    # Extract config section
                    st.subheader("📋 Extracted Configuration")

                    config = result.get("extracted_config", {})

                    # Display in columns
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric("Target Column", config.get("target_column", "N/A"))
                        st.metric("Test Size", f"{config.get('test_size', 0):.2f}")

                    with col2:
                        st.metric("Analysis Type", config.get("analysis_type", "N/A").title())
                        st.metric("Random State", config.get("random_state", "N/A"))

                    with col3:
                        confidence = config.get("confidence", 0)
                        st.metric(
                            "Confidence",
                            f"{confidence:.1%}",
                            delta=None,
                            delta_color="off"
                        )
                        st.metric("Experiment Name", config.get("experiment_name", "N/A"))

                    # Reasoning section
                    with st.expander("💡 AI Reasoning"):
                        reasoning = config.get("reasoning", {})
                        for key, value in reasoning.items():
                            st.markdown(f"**{key.replace('_', ' ').title()}:**")
                            st.markdown(f"> {value}")
                            st.markdown("")

                    # Assumptions and warnings
                    col1, col2 = st.columns(2)

                    with col1:
                        assumptions = config.get("assumptions", [])
                        if assumptions:
                            st.info("**Assumptions:**\n" + "\n".join(f"- {a}" for a in assumptions))

                    with col2:
                        warnings = config.get("warnings", [])
                        if warnings:
                            st.warning("**Warnings:**\n" + "\n".join(f"- {w}" for w in warnings))

                    # Execution metadata
                    st.divider()

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric("Pipeline Run ID", result.get("pipeline_run_id", "N/A"))

                    with col2:
                        exec_time = result.get("execution_time_seconds", 0)
                        st.metric("Execution Time", f"{exec_time:.2f}s")

                    with col3:
                        tokens = result.get("bedrock_tokens_used", 0)
                        st.metric("Bedrock Tokens", f"{tokens:,}")

                    # JSON view
                    with st.expander("🔍 View Full JSON Response"):
                        st.json(result)

                else:
                    st.error(f"❌ Pipeline failed: {result.get('error_message', 'Unknown error')}")
                    st.code(f"Error type: {result.get('error_type', 'Unknown')}")

            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to API. Please ensure the API server is running.")
            except requests.exceptions.Timeout:
                st.error("❌ Request timeout. The operation took too long.")
            except requests.exceptions.HTTPError as e:
                st.error(f"❌ HTTP Error: {e}")
            except Exception as e:
                st.error(f"❌ Unexpected error: {e}")


def search_history_page():
    """Search historical prompts page"""

    st.header("🔍 Search Prompt History")

    st.markdown("""
    Search for similar historical prompts to learn from past configurations.
    Uses full-text search with relevance ranking.
    """)

    # Search form
    with st.form("search_form"):
        search_query = st.text_input(
            "Search Query",
            placeholder="house price prediction"
        )

        search_limit = st.slider(
            "Number of Results",
            min_value=1,
            max_value=20,
            value=5
        )

        search_button = st.form_submit_button("🔍 Search", type="primary")

    if search_button and search_query:
        with st.spinner("Searching..."):
            try:
                results = search_similar_prompts(search_query, search_limit)

                if results.get("total_results", 0) > 0:
                    st.success(f"Found {results['total_results']} matching prompts")

                    for i, result in enumerate(results.get("results", []), 1):
                        with st.expander(f"Result {i}: {result.get('user_prompt', '')[:80]}..."):
                            st.markdown(f"**Original Prompt:**")
                            st.write(result.get("user_prompt"))

                            st.markdown(f"**Extracted Configuration:**")
                            config = result.get("extracted_config", {})
                            st.json(config)

                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Confidence", f"{result.get('confidence', 0):.1%}")
                            with col2:
                                st.metric("Relevance", f"{result.get('rank', 0):.4f}")
                            with col3:
                                timestamp = result.get("timestamp", "")
                                st.metric("Date", timestamp[:10] if timestamp else "N/A")

                else:
                    st.info("No matching prompts found")

            except Exception as e:
                st.error(f"❌ Search failed: {e}")


def analytics_page():
    """Analytics and insights page"""

    st.header("📊 Analytics & Insights")

    st.markdown("View aggregate statistics about prompt extractions and configurations.")

    # Refresh button
    if st.button("🔄 Refresh Analytics", type="primary"):
        st.rerun()

    try:
        analytics = get_analytics()

        # Overview metrics
        st.subheader("Overview")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Total Prompts", f"{analytics.get('total_prompts', 0):,}")

        with col2:
            st.metric("Successful", f"{analytics.get('successful_extractions', 0):,}")

        with col3:
            success_rate = 0
            if analytics.get('total_prompts', 0) > 0:
                success_rate = analytics['successful_extractions'] / analytics['total_prompts']
            st.metric("Success Rate", f"{success_rate:.1%}")

        with col4:
            st.metric("Avg Confidence", f"{analytics.get('avg_confidence', 0):.1%}")

        st.divider()

        # By analysis type
        st.subheader("By Analysis Type")

        by_type = analytics.get("by_analysis_type", [])
        if by_type:
            df_type = pd.DataFrame(by_type)
            df_type["avg_confidence"] = df_type["avg_confidence"].apply(lambda x: f"{x:.1%}")

            st.dataframe(
                df_type,
                column_config={
                    "analysis_type": "Analysis Type",
                    "count": st.column_config.NumberColumn("Count", format="%d"),
                    "avg_confidence": "Avg Confidence"
                },
                hide_index=True,
                use_container_width=True
            )

        # Common target columns
        st.subheader("Most Common Target Columns")

        common_targets = analytics.get("common_target_columns", [])
        if common_targets:
            df_targets = pd.DataFrame(common_targets)

            st.bar_chart(
                df_targets.set_index("target_column")["frequency"],
                use_container_width=True
            )

    except Exception as e:
        st.error(f"❌ Failed to load analytics: {e}")


if __name__ == "__main__":
    main()
