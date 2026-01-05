import streamlit as st
import requests
import pandas as pd
import time

import os

# --- Configuration ---
DEFAULT_API_URL = os.getenv("DEFAULT_API_URL", "http://localhost:8000/api")
# Check if running locally (outside docker)
# For local dev, you might access localhost:8000. 
# But in docker-compose, streamlit talks to backend service.
# We will allow override via sidebar.

st.set_page_config(
    page_title="Manufacturing Quality Assistant",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Polish ---
st.markdown("""
<style>
    /* Global Styling */
    .stApp {
        background-color: #f8f9fa; /* Light grey background */
    }
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Chat Message Styling */
    .stChatMessage {
        border-radius: 12px;
        padding: 10px;
        margin-bottom: 15px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    [data-testid="stChatMessageContent"] {
        padding: 5px;
    }
    
    /* User Message */
    .stChatMessage[data-testid="chat_message_user"] {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    
    /* Assistant Message */
    .stChatMessage[data-testid="chat_message_assistant"] {
        background-color: #ffffff;
        border-left: 4px solid #4caf50;
    }
    
    /* Header Styling */
    h1 {
        font-family: 'Helvetica Neue', sans-serif;
        color: #2c3e50;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e0e0e0;
    }
    
    /* Citation Card */
    .citation-card {
        background-color: white;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        margin-bottom: 10px;
        font-size: 0.9em;
    }
    .citation-header {
        font-weight: bold;
        color: #1976d2;
        margin-bottom: 5px;
    }
    .citation-metric {
        font-size: 0.8em;
        color: #757575;
    }
</style>
""", unsafe_allow_html=True)

# --- Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "api_url" not in st.session_state:
    st.session_state.api_url = DEFAULT_API_URL

# --- Sidebar ---
with st.sidebar:
    st.title("🏭 Controls")
    
    st.markdown("### ⚙️ Settings")
    api_url_input = st.text_input("Backend URL", value=st.session_state.api_url)
    if api_url_input:
        st.session_state.api_url = api_url_input.rstrip("/")

    st.markdown("---")
    st.markdown("### 📂 Document Upload")
    uploaded_files = st.file_uploader("Upload PDF Standard/SOP", type=["pdf"], accept_multiple_files=True)
    
    if uploaded_files:
        if st.button("Upload & Index", type="primary"):
            with st.spinner(f"Uploading {len(uploaded_files)} files..."):
                for uploaded_file in uploaded_files:
                    try:
                        files = {"file": (uploaded_file.name, uploaded_file, "application/pdf")}
                        response = requests.post(f"{st.session_state.api_url}/admin/upload", files=files)
                        if response.status_code == 200:
                            st.success(f"✅ {uploaded_file.name} uploaded & indexing started.")
                        else:
                            st.error(f"❌ {uploaded_file.name} failed: {response.text}")
                    except Exception as e:
                        st.error(f"❌ {uploaded_file.name} error: {e}")

    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; font-size: 0.8rem;'>
            Manufacturing Quality Assistant<br>
            v1.0.0
        </div>
        """, unsafe_allow_html=True
    )

# --- Main Interface ---
st.title("Manufacturing Quality Assistant")
st.markdown("Ask questions about your SOPs, Inspection Standards, and Safety Procedures.")

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "citations" in message and message["citations"]:
            with st.expander("📚 Sources & Citations"):
                for cite in message["citations"]:
                   st.markdown(
                       f"""
                       <div class="citation-card">
                           <div class="citation-header">📄 {cite['doc_name']} (Page {cite['page']})</div>
                           <div class="citation-metric">Relevance Score: {cite['score']:.4f}</div>
                       </div>
                       """, 
                       unsafe_allow_html=True
                   )
        if "raw_context" in message and message["raw_context"]:
             with st.expander("🔍 Debug: Raw Context"):
                 for ctx in message["raw_context"]:
                     st.text(f"--- {ctx['doc_name']} (Page {ctx['page']}) ---\n{ctx['content']}")

# Input Area
if prompt := st.chat_input("Ex: What are the inspection steps for N-BK7?"):
    # Determine URL to call: if loopback is needed for local dev when running app locally
    # but backend in docker? No, assume user sets correct URL or defaults work for docker-docker.
    # If running purely local: localhost:8000.
    
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        citations = []
        raw_context = []

        with st.spinner("Analyzing documents..."):
            try:
                payload = {"question": prompt}
                response = requests.post(f"{st.session_state.api_url}/query", json=payload)
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data.get("answer", "No answer provided.")
                    citations = data.get("citations", [])
                    raw_context = data.get("raw_context", [])
                    
                    # Streaming effect simulation
                    for chunk in answer.split():
                        full_response += chunk + " "
                        time.sleep(0.02)
                        message_placeholder.markdown(full_response + "▌")
                    message_placeholder.markdown(full_response)
                    
                    # Show Citations immediately after
                    if citations:
                         with st.expander("📚 Sources & Citations", expanded=True):
                            # Create a DataFrame for cleaner look if many
                            # but custom HTML cards are nicer.
                            for cite in citations:
                                st.markdown(
                                   f"""
                                   <div class="citation-card">
                                       <div class="citation-header">📄 {cite['doc_name']} (Page {cite['page']})</div>
                                       <div class="citation-metric">Relevance Score: {cite['score']:.4f}</div>
                                   </div>
                                   """, 
                                   unsafe_allow_html=True
                               )

                else:
                    full_response = f"⚠️ Error {response.status_code}: {response.text}"
                    message_placeholder.markdown(full_response)
            except Exception as e:
                full_response = f"⚠️ Connection Error: {str(e)}"
                message_placeholder.markdown(full_response)
        
        # Save to history
        st.session_state.messages.append({
            "role": "assistant", 
            "content": full_response,
            "citations": citations,
            "raw_context": raw_context
        })
