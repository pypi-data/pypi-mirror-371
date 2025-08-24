# aegis/web_interface/pages/2_Community_Hub.py

import streamlit as st
import pandas as pd
import sys
import os

# --- Path Correction ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from aegis.core.database.manager import DatabaseManager

# --- Page Configuration (Professional) ---
st.set_page_config(page_title="Aegis Community Hub", page_icon="A", layout="wide")

# --- Caching ---
@st.cache_resource
def get_db_manager():
    return DatabaseManager()

@st.cache_data(ttl=60)
def load_and_process_data():
    db_manager = get_db_manager()
    df = db_manager.get_all_results_as_df()
    if df.empty: return pd.DataFrame()
    
    leaderboard = df.groupby('model_name').agg(
        average_risk_score=('aegis_risk_score', 'mean'),
        tests_run=('prompt_id', 'count')
    ).reset_index()
    
    leaderboard = leaderboard[leaderboard['tests_run'] >= 5]
    return leaderboard.sort_values(by='average_risk_score', ascending=True)

# --- Main App ---
st.title("Community Hub & Leaderboard")
st.markdown("This page provides a security-focused benchmark of models tested with the Aegis framework, based on your local test results.")
st.info("Note: This is a foundational feature. Future versions may allow users to anonymously submit results to a central, public leaderboard.", icon="ℹ️")

leaderboard_df = load_and_process_data()

if not leaderboard_df.empty:
    st.header("Model Security Leaderboard")
    st.markdown("Models are ranked by their average Aegis Risk Score (ARS). Lower is better.")
    
    st.dataframe(
        leaderboard_df,
        column_config={
            "model_name": "Model Name",
            "average_risk_score": st.column_config.ProgressColumn(
                "Average Aegis Risk Score (ARS)",
                format="%.2f", min_value=0, max_value=100,
            ),
            "tests_run": "Total Tests Run",
        },
        hide_index=True,
    )
else:
    st.warning("Insufficient data to generate a leaderboard. Please run more tests (at least 5 per model).")
