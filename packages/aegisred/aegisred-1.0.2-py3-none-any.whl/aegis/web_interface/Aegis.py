# File: aegis/web_interface/Aegis.py
# Purpose: Main Aegis page with reliable session-wide persistence of provider/API keys
#          + CSV & Compliance PDF exports for Single and Batch evaluations

import streamlit as st
import sys
import os
import pandas as pd
import json
from datetime import datetime
from io import BytesIO
import re
import plotly.express as px

# --- Path Correction ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from aegis.core.analyzer import LLMAnalyzer
from aegis.core.connectors import (
    OpenRouterConnector,
    CustomEndpointConnector,
    UserProvidedGeminiConnector,
    OpenAIConnector,
    AnthropicConnector
)
from aegis.core.models import AdversarialPrompt, MultiModalInput
from aegis.core.library import PromptLibrary
from aegis.core.database.manager import DatabaseManager
from aegis.core.reporting import generate_pdf_report

# --- Page Configuration (Professional) ---
st.set_page_config(page_title="Aegis Sandbox", page_icon="A", layout="wide")

# --- Session Defaults (ensure persistence across reruns & navigation) ---
def _init_session_defaults():
    ss = st.session_state
    ss.setdefault("provider_option", "Gemini")

    # Credentials & model names per provider – persist across pages
    ss.setdefault("gemini_api_key", "")
    ss.setdefault("gemini_model_name", "gemini-1.5-flash-latest")

    ss.setdefault("openai_api_key", "")
    ss.setdefault("openai_model_name", "gpt-4o-mini")

    ss.setdefault("anthropic_api_key", "")
    ss.setdefault("anthropic_model_name", "claude-3-5-sonnet-20240620")

    ss.setdefault("openrouter_api_key", "")
    ss.setdefault("openrouter_model_name", "google/gemma-2-9b-it:free")

    ss.setdefault("custom_endpoint_url", "http://localhost:8000/generate")
    ss.setdefault("custom_endpoint_headers_json", '{"Authorization": "Bearer YOUR_KEY"}')

    # UI state
    ss.setdefault('explorer_expanded', False)
    ss.setdefault('is_processing', False)
    ss.setdefault('single_result', None)
    ss.setdefault('prompt_text', "")
    ss.setdefault('active_tab', "Single Prompt Evaluation")
    ss.setdefault('raw_batch_results', [])

    # For exports (filenames & attribution)
    ss.setdefault('last_single_session_id', None)
    ss.setdefault('last_batch_session_id', None)

_init_session_defaults()

# --- Resource Loading ---
@st.cache_resource
def load_resources():
    library = PromptLibrary()
    library.load_prompts()
    return library, LLMAnalyzer(), DatabaseManager()

library, analyzer, db_manager = load_resources()

# --- Helper Functions ---
def sanitize_for_filename(text: str) -> str:
    return re.sub(r'[\\/*?:"<>|]',"", text)

def convert_result_to_flat_dict(result_data, session_id):
    return {
        "session_id": session_id,
        "prompt_id": result_data["prompt"].id,
        "category": result_data["prompt"].category,
        "prompt_text": result_data["prompt"].prompt_text,
        "model_name": result_data["response"].model_name,
        "model_output": result_data["response"].output_text,
        "classification": result_data["analysis"].classification.name,
        "aegis_risk_score": result_data["analysis"].aegis_risk_score,
        "explanation": result_data["analysis"].explanation
    }

# Build classification chart image buffer (PNG) for PDF

def build_classification_chart_image(results_list):
    buf = BytesIO()
    try:
        classes = [r["analysis"].classification.name for r in results_list]
        ser = pd.Series(classes).value_counts()
        fig = px.bar(ser, x=ser.index, y=ser.values,
                     labels={'x': 'Classification', 'y': 'Count'},
                     title='Classification Breakdown')
        # Requires kaleido (already in requirements)
        fig.write_image(buf, format="png")
    except Exception:
        # Leave buffer empty if kaleido/plotting fails; PDF generator handles empty buffer
        pass
    return buf

# Connector factory that reads from session_state

def build_connector_from_state():
    provider = st.session_state.provider_option
    model_name_for_session = "default_model"
    connector = None

    if provider == "Gemini":
        api_key = st.session_state.gemini_api_key
        model_name = st.session_state.gemini_model_name
        if api_key and model_name:
            connector = UserProvidedGeminiConnector(model_name=model_name, api_key=api_key)
            model_name_for_session = sanitize_for_filename(model_name)

    elif provider == "OpenAI":
        api_key = st.session_state.openai_api_key
        model_name = st.session_state.openai_model_name
        if api_key and model_name:
            connector = OpenAIConnector(model_name=model_name, api_key=api_key)
            model_name_for_session = sanitize_for_filename(model_name)

    elif provider == "Claude (Anthropic)":
        api_key = st.session_state.anthropic_api_key
        model_name = st.session_state.anthropic_model_name
        if api_key and model_name:
            connector = AnthropicConnector(model_name=model_name, api_key=api_key)
            model_name_for_session = sanitize_for_filename(model_name)

    elif provider == "OpenRouter":
        api_key = st.session_state.openrouter_api_key
        model_name = st.session_state.openrouter_model_name
        if api_key and model_name:
            connector = OpenRouterConnector(model_name=model_name, api_key=api_key)
            model_name_for_session = sanitize_for_filename(model_name.split('/')[-1])

    elif provider == "Custom Endpoint":
        endpoint_url = st.session_state.custom_endpoint_url
        headers_str = st.session_state.custom_endpoint_headers_json
        try:
            headers = json.loads(headers_str) if headers_str else {}
        except json.JSONDecodeError:
            st.error("Invalid JSON for headers.")
            headers = {}
        if endpoint_url:
            connector = CustomEndpointConnector(endpoint_url=endpoint_url, headers=headers)
            model_name_for_session = "custom_endpoint"

    return connector, model_name_for_session

# --- UI Sidebar ---
with st.sidebar:
    st.title("Aegis Framework")
    st.markdown("## Configuration")

    st.selectbox(
        "Choose a Provider",
        ("Gemini", "OpenAI", "Claude (Anthropic)", "OpenRouter", "Custom Endpoint"),
        key="provider_option"
    )

    if st.session_state.provider_option == "Gemini":
        st.text_input("Google Gemini API Key", type="password", key="gemini_api_key")
        st.text_input("Gemini Model Name", key="gemini_model_name")

    elif st.session_state.provider_option == "OpenAI":
        st.text_input("OpenAI API Key", type="password", key="openai_api_key")
        st.text_input("OpenAI Model Name", key="openai_model_name")

    elif st.session_state.provider_option == "Claude (Anthropic)":
        st.text_input("Anthropic API Key", type="password", key="anthropic_api_key")
        st.text_input("Claude Model Name", key="anthropic_model_name")

    elif st.session_state.provider_option == "OpenRouter":
        st.text_input("OpenRouter API Key", type="password", key="openrouter_api_key")
        st.text_input("OpenRouter Model Path", key="openrouter_model_name")

    elif st.session_state.provider_option == "Custom Endpoint":
        st.text_input("Endpoint URL", key="custom_endpoint_url")
        st.text_area("Headers (JSON)", key="custom_endpoint_headers_json")

st.title("Red Team Sandbox")

connector, model_name_for_session = build_connector_from_state()

# --- Tabs ---
tab1, tab2 = st.tabs(["Single Prompt Evaluation", "Batch Evaluation"])

# ---------------------- Single Prompt Evaluation ----------------------
with tab1:
    with st.expander("Prompt Library Explorer", expanded=st.session_state.explorer_expanded):
        df = pd.DataFrame([p.to_dict() for p in library.get_all()])
        categories = ["All"] + sorted(df['category'].unique().tolist())
        selected_category = st.selectbox("Filter by Category", options=categories, key="single_cat_filter")
        df_filtered = df[df['category'] == selected_category] if selected_category != "All" else df
        for _, row in df_filtered.iterrows():
            with st.container():
                st.markdown(f"**ID:** `{row['id']}` | **Category:** `{row['category']}`")
                st.code(row['prompt_text'], language='text')
                if st.button("Load Prompt", key=f"load_{row['id']}"):
                    st.session_state.prompt_text = row['prompt_text']
                    st.session_state.explorer_expanded = False
                    st.rerun()
                st.divider()

    st.subheader("Adversarial Input")
    uploaded_image = st.file_uploader("Upload Image (Optional)", type=["png", "jpg", "jpeg", "webp"])
    st.text_area("Text Prompt", height=150, key="prompt_text", placeholder="Enter your adversarial prompt here...")

    if st.button("Evaluate Prompt", type="primary", use_container_width=True, disabled=st.session_state.is_processing):
        if not st.session_state.prompt_text:
            st.warning("Please enter a text prompt.")
        elif connector is None:
            st.warning("Provider configuration is incomplete.")
        else:
            st.session_state.is_processing = True
            st.session_state.single_result = None
            st.session_state.active_tab = "Single Prompt Evaluation"
            st.session_state.explorer_expanded = False
            st.rerun()

    results_placeholder = st.empty()
    if st.session_state.is_processing and st.session_state.active_tab == "Single Prompt Evaluation":
        with results_placeholder.container():
            with st.spinner("Evaluating..."):
                session_id = f"single_{sanitize_for_filename(model_name_for_session)}_{datetime.now().strftime('%Y%m%d-%H%M%S')}"
                multi_modal_inputs = []
                if uploaded_image:
                    multi_modal_inputs.append(MultiModalInput(media_type=uploaded_image.type, data=uploaded_image.getvalue()))

                temp_prompt = AdversarialPrompt(
                    id="sandbox_live_test", prompt_text=st.session_state.prompt_text,
                    category="Live_Test", subcategory="MultiModal" if uploaded_image else "Text",
                    severity="UNKNOWN", expected_behavior="REJECT", multi_modal_data=multi_modal_inputs
                )

                response = connector.send_prompt(temp_prompt)
                analysis = analyzer.analyze(response, temp_prompt)
                result_data = {"prompt": temp_prompt, "response": response, "analysis": analysis}

                db_manager.insert_result(convert_result_to_flat_dict(result_data, session_id))
                st.toast("Result saved to database!")

                st.session_state.single_result = result_data
                st.session_state.last_single_session_id = session_id
                st.session_state.is_processing = False
                st.rerun()

    def display_analysis_results(result_data):
        analysis = result_data["analysis"]
        response = result_data["response"]
        st.subheader("Analysis Results")
        color_map = {"NON_COMPLIANT": "#d63031", "COMPLIANT": "#00b894", "PARTIAL_COMPLIANCE": "#fdcb6e"}
        color = color_map.get(analysis.classification.name, "#636e72")
        st.markdown(f"""<hr style=\"height:2px;border:none;background-color:{color};\" /> """, unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        col1.metric("Model Tested", response.model_name)
        col2.metric("Classification", analysis.classification.name)
        col3.metric("Aegis Risk Score (ARS)", f"{analysis.aegis_risk_score:.1f}")
        with st.expander("Model Output", expanded=True):
            st.code(response.output_text, language=None)
        with st.expander("Analysis Explanation", expanded=True):
            st.info(analysis.explanation)

        # --- Exports: CSV + PDF for Single Result ---
        st.subheader("Export")
        single_session_id = st.session_state.last_single_session_id or "single_display"
        csv_df = pd.DataFrame([convert_result_to_flat_dict(result_data, single_session_id)])
        csv_bytes = csv_df.to_csv(index=False).encode('utf-8')

        chart_buf = build_classification_chart_image([result_data])
        pdf_buf = BytesIO()
        try:
            generate_pdf_report([result_data], pdf_buf, chart_buf)
        except Exception as e:
            st.warning(f"PDF generation failed: {e}")
        pdf_bytes = pdf_buf.getvalue()

        c1, c2 = st.columns(2)
        with c1:
            st.download_button(
                label="Download CSV",
                data=csv_bytes,
                file_name=f"aegis_single_{sanitize_for_filename(single_session_id)}.csv",
                mime='text/csv',
                use_container_width=True
            )
        with c2:
            st.download_button(
                label="Download Compliance PDF",
                data=pdf_bytes,
                file_name=f"aegis_single_{sanitize_for_filename(single_session_id)}.pdf",
                mime='application/pdf',
                use_container_width=True,
                disabled=(len(pdf_bytes) == 0)
            )

    if st.session_state.single_result and not st.session_state.is_processing:
        with results_placeholder.container():
            display_analysis_results(st.session_state.single_result)

# ---------------------- Batch Evaluation ----------------------
with tab2:
    st.subheader("Run Bulk Attacks")
    batch_source = st.radio("Prompt Source", ("From Library", "Custom Prompts"), horizontal=True, key="batch_source")
    prompts_to_run = []
    selected_batch_category = "Custom"

    if batch_source == "From Library":
        df = pd.DataFrame([p.to_dict() for p in library.get_all()])
        categories = sorted(df['category'].unique().tolist())
        selected_batch_category = st.selectbox("Select a Prompt Category", options=categories, key="batch_cat_select")
        prompts_to_run = library.filter_by_category(selected_batch_category)
    else:
        custom_prompts_text = st.text_area("Enter prompts (one per line)", height=250, key="custom_prompts_input")
        if custom_prompts_text:
            lines = [line.strip() for line in custom_prompts_text.split('\n') if line.strip()]
            prompts_to_run = [AdversarialPrompt(id=f"custom_{i+1}", prompt_text=line, category="Custom_Batch", subcategory="Custom", severity="UNKNOWN", expected_behavior="REJECT") for i, line in enumerate(lines)]

    if st.button("Run Batch Evaluation", type="primary", use_container_width=True, disabled=st.session_state.is_processing):
        if not prompts_to_run:
            st.warning("No prompts to evaluate.")
        elif connector is None:
            st.warning("Provider configuration is incomplete.")
        else:
            st.session_state.is_processing = True
            st.session_state.raw_batch_results = []
            st.session_state.active_tab = "Batch Evaluation"
            st.rerun()

    batch_results_placeholder = st.empty()
    if st.session_state.is_processing and st.session_state.active_tab == "Batch Evaluation":
        with batch_results_placeholder.container():
            with st.spinner(f"Running batch evaluation on {len(prompts_to_run)} prompts..."):
                session_id = f"batch_{sanitize_for_filename(model_name_for_session)}_{selected_batch_category}_{datetime.now().strftime('%Y%m%d-%H%M%S')}"
                progress_bar = st.progress(0, text="Starting...")
                for i, prompt in enumerate(prompts_to_run):
                    response = connector.send_prompt(prompt)
                    analysis = analyzer.analyze(response, prompt)
                    result_data = {"prompt": prompt, "response": response, "analysis": analysis}
                    st.session_state.raw_batch_results.append(result_data)
                    db_manager.insert_result(convert_result_to_flat_dict(result_data, session_id))
                    progress_bar.progress((i + 1) / len(prompts_to_run), text=f"Evaluated & Saved {prompt.id}...")

                st.toast(f"Batch evaluation complete! {len(prompts_to_run)} results saved.")
                st.session_state.last_batch_session_id = session_id
                st.session_state.is_processing = False
                st.rerun()

    if st.session_state.raw_batch_results and not st.session_state.is_processing:
        with batch_results_placeholder.container():
            st.divider()
            st.subheader("Batch Results")
            # Display table
            display_df = pd.DataFrame([convert_result_to_flat_dict(res, "batch_display") for res in st.session_state.raw_batch_results])
            st.dataframe(display_df, use_container_width=True)

            # --- Exports: CSV + PDF for Batch Results ---
            st.subheader("Export")
            batch_session_id = st.session_state.last_batch_session_id or f"batch_{sanitize_for_filename(model_name_for_session)}_{selected_batch_category}"

            # CSV bytes
            csv_df = pd.DataFrame([convert_result_to_flat_dict(res, batch_session_id) for res in st.session_state.raw_batch_results])
            csv_bytes = csv_df.to_csv(index=False).encode('utf-8')

            # PDF bytes via report generator
            chart_buf = build_classification_chart_image(st.session_state.raw_batch_results)
            pdf_buf = BytesIO()
            try:
                generate_pdf_report(st.session_state.raw_batch_results, pdf_buf, chart_buf)
            except Exception as e:
                st.warning(f"PDF generation failed: {e}")
            pdf_bytes = pdf_buf.getvalue()

            c1, c2 = st.columns(2)
            with c1:
                st.download_button(
                    label="Download CSV (Batch)",
                    data=csv_bytes,
                    file_name=f"aegis_batch_{sanitize_for_filename(batch_session_id)}.csv",
                    mime='text/csv',
                    use_container_width=True
                )
            with c2:
                st.download_button(
                    label="Download Compliance PDF (Batch)",
                    data=pdf_bytes,
                    file_name=f"aegis_batch_{sanitize_for_filename(batch_session_id)}.pdf",
                    mime='application/pdf',
                    use_container_width=True,
                    disabled=(len(pdf_bytes) == 0)
                )
