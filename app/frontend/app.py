import streamlit as st
import requests
import time
import os
import re
from datetime import datetime

# --- Configuration ---
DEFAULT_API_URL = os.getenv("DEFAULT_API_URL", "http://localhost:8000/api")

st.set_page_config(
    page_title="Industrial IQ | Autonomous Intelligence",
    page_icon="🦾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Icons ---
ICON_FILE = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>'
ICON_STATUS = '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 8v4l3 3"/></svg>'
ICON_WAV = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 12h-4l-3 9L9 3l-3 9H2"/></svg>'

# --- Industrial Monochrome CSS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=JetBrains+Mono&display=swap');

/* --- Global --- */
html, body, [data-testid="stAppViewContainer"], .stMarkdown, p, button, input {
    font-family: 'DM Sans', sans-serif !important;
}

/* Background: Dotted Technical Grid */
.stApp {
    background-color: #fcfcfc;
    background-image: radial-gradient(#e0e0e0 1px, transparent 1px);
    background-size: 30px 30px;
    background-attachment: fixed;
}

.block-container { padding: 3rem 2.5rem; max-width: 1000px !important; }

/* Sidebar: Strict Manufacturing Sidebar */
[data-testid="stSidebar"] {
    background-color: #ffffff;
    border-right: 2px solid #000000;
}

#MainMenu, footer { visibility: hidden; }
header { background: transparent !important; }

/* --- Industrial Header --- */
.hero { text-align: left; margin-bottom: 3rem; position: relative; }
.hero h1 { 
    font-weight: 700; color: #000000; font-size: 3.2rem; margin: 0; 
    letter-spacing: -0.06em; text-transform: uppercase;
}
.hero::before {
    content: "SYSTEM LOG // AF-01";
    position: absolute; top: -20px; left: 0;
    font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: #adb5bd;
}
.hero p { color: #868e96; font-size: 1rem; margin-top: 4px; font-weight: 500; letter-spacing: 0.05em; }

/* Status Panel */
.status-panel {
    border: 1px solid #000000; padding: 16px; margin-bottom: 24px;
    background: #ffffff; box-shadow: 4px 4px 0px #000000;
}
.status-item { 
    display: flex; justify-content: space-between; align-items: center; 
    font-size: 0.75rem; color: #1a1a1a; margin-bottom: 8px; font-family: 'JetBrains Mono', monospace;
}
.status-dot { width: 6px; height: 6px; border-radius: 50%; background: #000; animation: blink 1.5s infinite; }
@keyframes blink { 0% { opacity: 0.2; } 50% { opacity: 1; } 100% { opacity: 0.2; } }

/* Chat Bubbles: Reduced margin for tighter conversation */
.stChatMessage { background: transparent !important; margin-bottom: 18px !important; }

[data-testid="chat_message_user"] [data-testid="stChatMessageContent"] {
    background: #000000 !important;
    color: #ffffff !important;
    border-radius: 0 !important;
    padding: 16px 20px !important;
    box-shadow: 8px 8px 0px rgba(0,0,0,0.1);
}

[data-testid="chat_message_assistant"] [data-testid="stChatMessageContent"] {
    background: #ffffff !important;
    color: #000000 !important;
    border: 2px solid #000000 !important;
    border-radius: 0 !important;
    padding: 24px 28px !important;
    box-shadow: 8px 8px 0px rgba(0,0,0,0.03);
}

/* --- MONOCHROME TECHNICAL STACK --- */
.file-card-box {
    background: #ffffff;
    border: 1px solid #000000;
    padding: 12px 14px; margin-bottom: 10px;
    display: flex; align-items: center; gap: 10px;
    transition: all 0.2s;
}
.file-card-box:hover { background: #f8f9fa; transform: translateX(4px); }

/* Buttons: Strict Solid Black */
.stButton > button {
    background-color: #000000 !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 0 !important;
    padding: 8px 20px !important;
    font-weight: 700 !important;
    text-transform: uppercase;
    font-size: 0.75rem !important;
    letter-spacing: 0.1em;
    transition: all 0.1s ease !important;
}
.stButton > button:hover { background-color: #343a40 !important; }

/* Chat Input Refinement */
[data-testid="stChatInput"] {
    background-color: #ffffff !important;
    border: 2px solid #000000 !important;
    border-radius: 0 !important;
    padding: 2px 0 !important;
}
[data-testid="stChatInput"] > div {
    border-radius: 0 !important;
    border: none !important;
}
[data-testid="stChatInput"] textarea {
    padding: 12px 16px !important;
    font-size: 0.95rem !important;
}

/* Source Tags: Expanded horizontally */
.source-long {
    border: 1px solid #000;
    padding: 6px 14px;
    font-size: 0.75rem;
    font-weight: 700;
    margin-right: 10px;
    margin-bottom: 8px;
    display: inline-flex;
    align-items: center;
    background: #ffffff;
    font-family: 'JetBrains Mono', monospace;
    min-width: 200px;
    max-width: 100%;
}

/* Custom Scrollbar */
::-webkit-scrollbar { width: 12px; }
::-webkit-scrollbar-track { background: #fcfcfc; }
::-webkit-scrollbar-thumb { background: #000000; border: 3px solid #fcfcfc; }
</style>
""", unsafe_allow_html=True)

# --- Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "indexed_files" not in st.session_state:
    st.session_state.indexed_files = []
if "api_url" not in st.session_state:
    st.session_state.api_url = DEFAULT_API_URL

# --- Actions ---
def clean_answer(text):
    text = re.sub(r'\[[^\]]*\]', '', text)
    text = re.sub(r'\(Source:[^)]*\)', '', text)
    text = re.sub(r'\*\s+', '', text)
    return text.strip()

# --- Sidebar ---
with st.sidebar:
    st.markdown('<div style="font-size: 1.4rem; font-weight:700; color:#000000; margin-bottom:1.5rem; letter-spacing:-1px;">ARCHIVES</div>', unsafe_allow_html=True)
    
    # Industrial Status Panel
    st.markdown(f'''
    <div class="status-panel">
        <div class="status-item"><span>CORE STATUS</span> <span style="font-weight:700;">ACTIVE</span></div>
        <div class="status-item"><span>CONNECTION</span> <span style="font-weight:700;">LINKED</span></div>
        <div class="status-item"><span>DOCUMENTS</span> <span style="font-weight:700;">{len(st.session_state.indexed_files)}</span></div>
        <div style="height:10px;"></div>
        <div style="display:flex; justify-content:center; color:#ccc;">{ICON_WAV}</div>
    </div>
    ''', unsafe_allow_html=True)
    
    if not st.session_state.indexed_files:
        files = st.file_uploader("Upload", type=["pdf"], accept_multiple_files=True, label_visibility="collapsed")
        if files:
            if st.button("UPLOAD", use_container_width=True):
                with st.spinner("Processing..."):
                    for f in files:
                        try:
                            resp = requests.post(f"{st.session_state.api_url}/admin/upload", files={"file": (f.name, f)})
                            if resp.status_code == 200 and f.name not in st.session_state.indexed_files:
                                st.session_state.indexed_files.append(f.name)
                        except: pass
                    st.rerun()
    else:
        for i, fname in enumerate(st.session_state.indexed_files):
            col1, col2 = st.columns([5, 1])
            with col1:
                st.markdown(f'<div class="file-card-box">{ICON_FILE} <span style="font-size:0.8rem; font-weight:600;">{fname}</span></div>', unsafe_allow_html=True)
            with col2:
                if st.button("×", key=f"del_{i}"):
                    st.session_state.indexed_files.pop(i)
                    st.rerun()
        
        st.markdown('<div style="height:2rem;"></div>', unsafe_allow_html=True)
        if st.button("CLEAR ALL", use_container_width=True):
            st.session_state.indexed_files = []
            st.rerun()

# --- Main App ---
st.markdown('''
<div class="hero">
    <h1>Autonomous Intelligence</h1>
    <p>MANUFACTURING CONTROL & TECHNICAL STANDARDS ENGINE</p>
</div>
''', unsafe_allow_html=True)

# Chat history
for idx, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        content = clean_answer(msg["content"]) if msg["role"] == "assistant" else msg["content"]
        st.markdown(content)
        
        if msg["role"] == "assistant":
            if "citations" in msg and msg["citations"]:
                unique = {(c['doc_name'], c['page']) for c in msg["citations"]}
                pills = ""
                for doc, pg in unique:
                    pills += f'<div class="source-long">{doc} // PG.{pg}</div>'
                st.markdown(f'<div style="margin-top:20px; display:flex; flex-wrap:wrap; gap:10px;">{pills}</div>', unsafe_allow_html=True)
            
            ts = msg.get("timestamp", "")
            st.markdown(f'<div style="text-align:right; color:#adb5bd; font-family:JetBrains Mono; font-size:0.75rem; margin-top:8px;">{ts}</div>', unsafe_allow_html=True)

# Input
if prompt := st.chat_input("Input technical query..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    with st.chat_message("assistant"):
        placeholder = st.empty()
        response_text = ""
        citations = []
        
        with st.spinner("PROBING ARCHIVES..."):
            try:
                resp = requests.post(f"{st.session_state.api_url}/query", json={"question": prompt})
                if resp.status_code == 200:
                    data = resp.json()
                    answer = clean_answer(data.get("answer", ""))
                    citations = data.get("citations", [])
                    
                    for word in answer.split():
                        response_text += word + " "
                        time.sleep(0.01)
                        placeholder.markdown(response_text + "▌")
                    placeholder.markdown(response_text.strip())
                    
                    if citations:
                        unique = {(c['doc_name'], c['page']) for c in citations}
                        pills = ""
                        for doc, pg in unique:
                            pills += f'<div class="source-long">{doc} // PG.{pg}</div>'
                        st.markdown(f'<div style="margin-top:20px; display:flex; flex-wrap:wrap; gap:10px;">{pills}</div>', unsafe_allow_html=True)
                    
                    ts = datetime.now().strftime("%H:%M")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response_text,
                        "citations": citations,
                        "timestamp": ts
                    })
                    # st.rerun() removed to avoid RerunException inside try block
            except Exception as e:
                # We log error if it's not a rerun initiated by Streamlit
                st.error(f"SYSTEM CONNECTION FAILED: {str(e)}")
        
    st.rerun() # Rerun outside chat message for clean state update
