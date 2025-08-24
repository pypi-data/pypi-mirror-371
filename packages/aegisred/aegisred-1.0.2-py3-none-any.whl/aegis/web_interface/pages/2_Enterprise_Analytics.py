# ==============================
# File: aegis/web_interface/pages/3_Enterprise_Analytics.py
# ==============================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import sys
import os

# --- Path Correction ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from aegis.core.database.manager import DatabaseManager

st.set_page_config(page_title="Aegis Enterprise Analytics", page_icon="📈", layout="wide")

@st.cache_resource
def get_db_manager():
    return DatabaseManager()

@st.cache_data(ttl=45)
def load_data():
    db = get_db_manager()
    df = db.get_all_results_as_df()
    if df.empty:
        return pd.DataFrame()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['classification'] = df['classification'].str.upper()
    return df.sort_values('timestamp')

st.title("Enterprise Analytics")
st.caption("Deeper visuals for trends, dispersion and watchlists across sessions and models.")

df = load_data()
if df.empty:
    st.info("Run some evaluations first to populate analytics.")
    st.stop()

# Boxplot by Category
c1, c2 = st.columns(2)
with c1:
    st.subheader("Risk Distribution by Category (Box)")
    fig = px.box(df, x='category', y='aegis_risk_score', points='outliers', title="ARS Distribution per Category")
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("Risk Distribution by Model (Violin)")
    fig = px.violin(df, x='model_name', y='aegis_risk_score', box=True, points='outliers', title="ARS Distribution per Model")
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# Cohort Trend: avg ARS per model over time (by session)
st.subheader("Cohort Trend: Avg ARS per Model over Sessions")
sess = df.groupby(['session_id','model_name'], as_index=False).agg(avg_ars=('aegis_risk_score','mean'), last_ts=('timestamp','max'))
fig = px.line(sess, x='last_ts', y='avg_ars', color='model_name', markers=True, hover_data=['session_id'], title="Model Cohorts over Time")
st.plotly_chart(fig, use_container_width=True)

st.divider()

# Pareto: top risky prompts overall
st.subheader("Pareto: Top Risky Prompts (Avg ARS)")
prompt_stats = df.groupby(['prompt_id','category'], as_index=False).agg(avg_ars=('aegis_risk_score','mean'), runs=('prompt_id','count'))
prompt_stats = prompt_stats.sort_values('avg_ars', ascending=False).head(30)
fig = px.bar(prompt_stats, x='prompt_id', y='avg_ars', color='category', title="Top 30 Prompts by Avg ARS")
st.plotly_chart(fig, use_container_width=True)

st.divider()

# Regression Watchlist: compare two most recent sessions
st.subheader("Regression Watchlist (Last 2 Sessions)")
recent_sessions = df['session_id'].drop_duplicates().tolist()
if len(recent_sessions) >= 2:
    last_two = recent_sessions[-2:]
    a, b = last_two[0], last_two[1]
    da = df[df['session_id']==a][['prompt_id','category','aegis_risk_score']].rename(columns={'aegis_risk_score':'ARS_A'})
    db = df[df['session_id']==b][['prompt_id','category','aegis_risk_score']].rename(columns={'aegis_risk_score':'ARS_B'})
    m = pd.merge(da, db, on=['prompt_id','category'], how='inner')
    if not m.empty:
        m['delta'] = m['ARS_B'] - m['ARS_A']
        watch = m.sort_values('delta', ascending=False).head(20)
        st.dataframe(watch[['prompt_id','category','ARS_A','ARS_B','delta']], use_container_width=True)
    else:
        st.info("No overlapping prompts between the last two sessions.")
else:
    st.info("Need at least two sessions for a watchlist.")