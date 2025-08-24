# ==============================
# File: aegis/web_interface/pages/1_Security_Dashboard.py
# ==============================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import sys
import os
from datetime import date

# --- Path Correction ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from aegis.core.database.manager import DatabaseManager

# --- Page Configuration ---
st.set_page_config(page_title="Aegis Security Dashboard", page_icon="🛡️", layout="wide")

# --- Caching ---
@st.cache_resource
def get_db_manager():
    return DatabaseManager()

@st.cache_data(ttl=30)
def load_data():
    db_manager = get_db_manager()
    df = db_manager.get_all_results_as_df()
    if df.empty:
        return pd.DataFrame()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    # Normalize classification casing for consistency
    df['classification'] = df['classification'].str.upper()
    df = df.sort_values(by="timestamp", ascending=False)
    return df

# --- Helpers ---
def apply_filters(df: pd.DataFrame,
                  sessions: list,
                  models: list,
                  categories: list,
                  classes: list,
                  start_date: pd.Timestamp | None,
                  end_date: pd.Timestamp | None,
                  prompt_query: str | None):
    if df.empty:
        return df

    mask = pd.Series([True] * len(df), index=df.index)

    if sessions and "All Sessions" not in sessions:
        mask &= df['session_id'].isin(sessions)

    if models and "All Models" not in models:
        mask &= df['model_name'].isin(models)

    if categories and "All Categories" not in categories:
        mask &= df['category'].isin(categories)

    if classes and "All" not in classes:
        mask &= df['classification'].isin(classes)

    if start_date is not None:
        mask &= df['timestamp'] >= pd.to_datetime(start_date)
    if end_date is not None:
        mask &= df['timestamp'] <= pd.to_datetime(end_date) + pd.to_timedelta(1, unit='D')

    if prompt_query:
        q = prompt_query.strip().lower()
        if q:
            mask &= df['prompt_id'].str.lower().str.contains(q)

    return df[mask].copy()


def kpi_card(label: str, value: str, help_text: str | None = None):
    col = st.container()
    with col:
        st.metric(label, value, help=help_text)


# --- Main App ---
st.title("Security Dashboard")
st.caption("Enterprise-grade analytics for Aegis red-teaming results. Use the filters to slice & dice, then dive into regression deltas.")

raw_df = load_data()

if raw_df.empty:
    st.info("No evaluation data found. Run tests in the Sandbox to populate this dashboard.")
    st.stop()

# =============== Sidebar Filters ===============
st.sidebar.header("Filters")
all_sessions = sorted(raw_df['session_id'].unique().tolist())
all_models = sorted(raw_df['model_name'].unique().tolist())
all_categories = sorted([c for c in raw_df['category'].dropna().unique().tolist()])
all_classes = sorted(raw_df['classification'].dropna().unique().tolist())

# Date range
min_d = raw_df['timestamp'].min().date()
max_d = raw_df['timestamp'].max().date()
start_date, end_date = st.sidebar.date_input(
    "Date range", value=(min_d, max_d), min_value=min_d, max_value=max_d
)

sessions_sel = st.sidebar.multiselect("Sessions", options=["All Sessions"] + all_sessions, default=["All Sessions"])
models_sel = st.sidebar.multiselect("Models", options=["All Models"] + all_models, default=["All Models"])
categories_sel = st.sidebar.multiselect("Categories", options=["All Categories"] + all_categories, default=["All Categories"])
classes_sel = st.sidebar.multiselect("Classifications", options=["All"] + all_classes, default=["All"])

prompt_query = st.sidebar.text_input("Search Prompt ID contains…")

# Saved views (session-local)
if 'saved_views' not in st.session_state:
    st.session_state.saved_views = {}

view_name = st.sidebar.text_input("Save current filter as view (name)")
cols_btn = st.sidebar.columns(2)
with cols_btn[0]:
    if st.button("Save View", use_container_width=True, disabled=not view_name):
        st.session_state.saved_views[view_name] = {
            'sessions': sessions_sel,
            'models': models_sel,
            'categories': categories_sel,
            'classes': classes_sel,
            'start': start_date,
            'end': end_date,
            'q': prompt_query,
        }
        st.sidebar.success(f"Saved view '{view_name}'.")
with cols_btn[1]:
    if st.button("Clear Views", use_container_width=True):
        st.session_state.saved_views = {}
        st.sidebar.info("Cleared saved views.")

if st.session_state.saved_views:
    sel = st.sidebar.selectbox("Load saved view", options=["-"] + list(st.session_state.saved_views.keys()))
    if sel and sel != "-":
        v = st.session_state.saved_views[sel]
        sessions_sel = v['sessions']
        models_sel = v['models']
        categories_sel = v['categories']
        classes_sel = v['classes']
        start_date, end_date = v['start'], v['end']
        prompt_query = v['q']

# Apply filters
fdf = apply_filters(raw_df, sessions_sel, models_sel, categories_sel, classes_sel, start_date, end_date, prompt_query)

# =============== KPI Row ===============
st.subheader("Key Metrics")
k1, k2, k3, k4 = st.columns(4)
with k1:
    kpi_card("Average ARS", f"{fdf['aegis_risk_score'].mean():.2f}")
with k2:
    non_compliant_pct = ( (fdf['classification'] == 'NON_COMPLIANT').mean() * 100.0 ) if not fdf.empty else 0.0
    kpi_card("Non-Compliant %", f"{non_compliant_pct:.1f}%")
with k3:
    kpi_card("Total Tests Run", f"{len(fdf)}")
with k4:
    kpi_card("Sessions in View", f"{fdf['session_id'].nunique()}")

st.divider()

# =============== Overview Charts ===============
o1, o2 = st.columns(2)
with o1:
    st.subheader("Avg ARS by Session (Trend)")
    sess = (fdf.groupby('session_id', as_index=False)
               .agg(avg_ars=('aegis_risk_score','mean'),
                    last_ts=('timestamp','max'))
               .sort_values('last_ts'))
    if not sess.empty:
        fig = px.line(sess, x='last_ts', y='avg_ars', markers=True, hover_data=['session_id'],
                      labels={'last_ts':'Session Time','avg_ars':'Average ARS'},
                      title="Session-wise Average Risk Over Time")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Not enough data to plot session trend.")

with o2:
    st.subheader("Classification Breakdown (Counts)")
    cls_counts = fdf['classification'].value_counts().reset_index()
    cls_counts.columns = ['classification','count']
    if not cls_counts.empty:
        fig = px.bar(cls_counts, x='classification', y='count', color='classification',
                     title="Total Evaluation Outcomes")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No classifications to display.")

st.divider()

# =============== Heatmap & Category Breakdown ===============
h1, h2 = st.columns(2)
with h1:
    st.subheader("Vulnerability Heatmap (Avg ARS)")
    try:
        heatmap_data = (fdf.pivot_table(index='category', columns='model_name', values='aegis_risk_score', aggfunc='mean')
                          .fillna(0))
        if heatmap_data.size > 0:
            fig_heatmap = px.imshow(
                heatmap_data, text_auto=".1f", aspect="auto", color_continuous_scale='Reds',
                labels=dict(x="Model", y="Category", color="Avg ARS"),
                title="Average Risk Score by Model & Category"
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)
        else:
            st.info("Heatmap needs multiple models & categories.")
    except Exception:
        st.warning("Heatmap requires data from multiple models and categories to render.")

with h2:
    st.subheader("Category-wise Classification Mix")
    cat_mix = (fdf.groupby(['category','classification'])
                  .size().reset_index(name='count'))
    if not cat_mix.empty:
        fig = px.bar(cat_mix, x='category', y='count', color='classification', barmode='stack',
                     title="Stacked Outcomes per Category")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No category breakdown to show.")

st.divider()

# =============== Comparative Delta Analysis ===============
st.header("Comparative Delta Analysis")
st.caption("Measure regressions between two sessions. Positive Δ (delta) means session B is riskier than session A.")

all_sessions_no_all = raw_df['session_id'].unique().tolist()
colA, colB, colC = st.columns([1,1,1])
with colA:
    session_a = st.selectbox("Baseline Session (A)", options=all_sessions_no_all, index=0)
with colB:
    session_b_options = [s for s in all_sessions_no_all if s != session_a]
    session_b = st.selectbox("Comparison Session (B)", options=session_b_options, index=0 if session_b_options else None)
with colC:
    delta_mode = st.selectbox("Delta Mode", options=["Absolute Δ", "% Change"], index=0)

if session_a and session_b:
    df_a = raw_df[raw_df['session_id'] == session_a]
    df_b = raw_df[raw_df['session_id'] == session_b]

    merged = pd.merge(
        df_a[['prompt_id','category','aegis_risk_score']].rename(columns={'aegis_risk_score':'ARS_A'}),
        df_b[['prompt_id','category','aegis_risk_score']].rename(columns={'aegis_risk_score':'ARS_B'}),
        on=['prompt_id','category'], how='inner'
    )

    # Direction: positive means regression (B riskier than A)
    merged['delta'] = merged['ARS_B'] - merged['ARS_A']
    if delta_mode == "% Change":
        merged['delta_pct'] = np.where(merged['ARS_A'] != 0, (merged['delta'] / merged['ARS_A']) * 100.0, np.nan)

    missing_in_b = len(df_a) - len(merged)
    missing_in_a = len(df_b) - len(merged)

    st.subheader("Delta Summary")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Prompts Compared", f"{len(merged)}", help="Common prompts present in both sessions (joined on prompt_id & category)")
    with c2:
        st.metric("Missing in B", f"{missing_in_b}")
    with c3:
        st.metric("Missing in A", f"{missing_in_a}")

    if not merged.empty:
        st.subheader("Top Regressions (Higher Risk in B)")
        top_reg = merged.sort_values(by='delta', ascending=False).head(25)
        show_cols = ['prompt_id','category','ARS_A','ARS_B','delta'] + (["delta_pct"] if delta_mode == "% Change" else [])
        st.dataframe(top_reg[show_cols], use_container_width=True)

        st.subheader("Improvements (Lower Risk in B)")
        top_imp = merged.sort_values(by='delta', ascending=True).head(25)
        st.dataframe(top_imp[show_cols], use_container_width=True)

        st.subheader("Category-Level Delta (Mean)")
        cat_delta = (merged.groupby('category', as_index=False)
                            .agg(ARS_A=('ARS_A','mean'), ARS_B=('ARS_B','mean')))
        cat_delta['delta'] = cat_delta['ARS_B'] - cat_delta['ARS_A']
        fig_cd = px.bar(cat_delta.sort_values('delta', ascending=False), x='category', y='delta',
                        title="Average Δ by Category (B - A)")
        st.plotly_chart(fig_cd, use_container_width=True)

        # Download
        st.download_button("Download merged delta CSV",
                           data=merged.to_csv(index=False).encode('utf-8'),
                           file_name=f"delta_{session_a}_vs_{session_b}.csv",
                           mime='text/csv')
    else:
        st.warning("No overlapping prompts between selected sessions.")
else:
    st.info("Select two different sessions to run a comparative analysis.")

st.divider()

# =============== Pivot / BI Table ===============
st.header("Ad-hoc Pivot (BI)")
st.caption("Build quick pivot tables over the filtered data. Use this to explore patterns and hotspots.")
if fdf.empty:
    st.info("No data for the current filters.")
else:
    cols = ['session_id','prompt_id','category','model_name','classification']
    val_options = ['aegis_risk_score']
    idx = st.multiselect("Index", options=cols, default=['category'])
    cols_sel = st.multiselect("Columns", options=[c for c in cols if c not in idx], default=['model_name'])
    value = st.selectbox("Value", options=val_options, index=0)
    agg = st.selectbox("Aggregation", options=['mean','median','count','max','min'], index=0)

    try:
        if agg == 'count':
            pvt = pd.pivot_table(fdf, index=idx, columns=cols_sel, values='prompt_id', aggfunc='count').fillna(0)
        else:
            pvt = pd.pivot_table(fdf, index=idx, columns=cols_sel, values=value, aggfunc=agg).fillna(0)
        st.dataframe(pvt)
    except Exception as e:
        st.warning(f"Pivot error: {e}")

with st.expander("Show Detailed Rows (filtered)", expanded=False):
    st.dataframe(fdf)
