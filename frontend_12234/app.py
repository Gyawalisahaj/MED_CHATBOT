"""
Medical RAG Chatbot - Streamlit Frontend
Advanced medical question-answering with source attribution and chat history
"""

import streamlit as st
import requests
import json
import os
from datetime import datetime
from typing import List, Dict
import uuid

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="MediQuery AI",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM STYLING & STYLESHEET LOADING
# ============================================================================

# Native Custom CSS
st.markdown("""
<style>
    /* Main container */
    .main {
        padding: 2rem 1rem;
    }
    
    /* Message styling */
    .user-message {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #2196f3;
    }
    
    .assistant-message {
        background-color: #f5f5f5;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #4caf50;
    }
    
    .source-item {
        background-color: #fff3e0;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.25rem 0;
        border-left: 3px solid #ff9800;
    }
    
    /* Header styling */
    h1 {
        color: #1976d2;
        text-align: center;
    }
    
    .metric-card {
        background-color: #e8f5e9;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    
    .disclaimer {
        background-color: #fff3e0;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #ff9800;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Load external styles from style.css if present
css_path = os.path.join(os.path.dirname(__file__), "style.css")
if os.path.exists(css_path):
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ============================================================================
# API CLIENT
# ============================================================================

class MedicalChatAPIClient:
    """Client for communicating with Medical RAG backend"""
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or os.getenv("BACKEND_URL", "http://localhost:8000")
        self.timeout = 60
    
    def send_message(self, message: str, session_id: str) -> Dict:
        """Send a medical query to the RAG backend"""
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/chat/query",
                json={
                    "message": message,
                    "session_id": session_id
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"API Error: {str(e)}")
    
    def get_history(self, session_id: str) -> List[Dict]:
        """Retrieve chat history for a session"""
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/chat/history/{session_id}",
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.warning(f"Could not load chat history: {str(e)}")
            return []
    
    def clear_history(self, session_id: str) -> bool:
        """Clear chat history for a session"""
        try:
            response = requests.delete(
                f"{self.base_url}/api/v1/chat/history/{session_id}",
                timeout=self.timeout
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            st.error(f"Could not clear history: {str(e)}")
            return False
    
    def health_check(self) -> bool:
        """Check if backend is healthy"""
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/chat/health",
                timeout=5
            )
            return response.status_code == 200
        except:
            return False

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "api_client" not in st.session_state:
    st.session_state.api_client = MedicalChatAPIClient(BACKEND_URL)
elif st.session_state.api_client.base_url != BACKEND_URL:
    st.session_state.api_client = MedicalChatAPIClient(BACKEND_URL)

if "show_welcome" not in st.session_state:
    st.session_state.show_welcome = True

if "last_audio_ts" not in st.session_state:
    st.session_state.last_audio_ts = None

client = st.session_state.api_client

# ============================================================================
# SIDEBAR CONFIGURATION
# ============================================================================

with st.sidebar:
    st.markdown("## 🩺 Medical RAG Chatbot")
    st.divider()
    
    # Session Information
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Session ID**")
    with col2:
        st.code(st.session_state.session_id[:8] + "...")
    
    st.divider()
    
    # Chat Controls
    st.markdown("### 💬 Chat Controls")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🆕 New Chat", use_container_width=True):
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.chat_history = []
            st.session_state.show_welcome = True
            st.rerun()
    
    with col2:
        if st.button("🗑️ Clear History", use_container_width=True):
            if client.clear_history(st.session_state.session_id):
                st.session_state.chat_history = []
                st.success("History cleared!")
                st.rerun()
    
    st.divider()
    
    # Settings
    st.markdown("### Backend Configuration")
    if client.health_check():
        st.success("✅ Backend Online")
    else:
        st.error("❌ Backend Offline")
    
    backend_url_input = st.text_input(
        "Backend URL",
        value=client.base_url,
        help="Change if backend is on different host"
    )
    if backend_url_input != client.base_url:
        st.session_state.api_client = MedicalChatAPIClient(backend_url_input)
        st.rerun()
    
    st.divider()
    
    # Information
    st.markdown("### ℹ️ About")
    st.info(
        "**MediQuery AI** is an educational medical AI assistant powered by "
        "Retrieval-Augmented Generation (RAG) and Large Language Models. "
        "It provides evidence-based information from medical literature."
    )
    
    st.markdown("### 📚 Medical Sources")
    st.markdown(
        """
        - Harrison's Principles of Internal Medicine
        - Guyton and Hall Physiology
        - Kumar and Clark's Clinical Medicine
        - Pathology - Robins & Cotran
        - Pharmacology - Goodman & Gilman
        """
    )
    
    st.divider()
    
    # st.markdown("### ⚠️ Disclaimer")
    # st.warning(
    #     "**Educational Use Only**: This tool is for learning purposes. "
    #     "Always consult qualified healthcare professionals for medical advice."
    # )

# ============================================================================
# MAIN CONTENT
# ============================================================================

# Single Clean Header
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("# 🩺 MediQuery Assistant")
    st.markdown(
        "<p style='text-align: center; color: gray;'>"
        "Ask medical questions backed by comprehensive medical literature"
        "</p>",
        unsafe_allow_html=True
    )

st.divider()

# ============================================================================
# CHAT DISPLAY
# ============================================================================

# Welcome message
if st.session_state.show_welcome and len(st.session_state.chat_history) == 0:
    st.info(
        "### Welcome to MediQuery AI 👋\n\n"
        "Ask any medical question and get answers backed by medical literature. "
        "Sources are provided for every answer.\n\n"
        "Feel free to ask anything!"
    )

# Render Chat History
for i, chat in enumerate(st.session_state.chat_history):
    with st.chat_message("user"):
        st.markdown(chat["user"])
    
    with st.chat_message("assistant"):
        st.markdown(chat["assistant"])
        if "sources" in chat and chat["sources"]:
            with st.expander("📄 View Sources"):
                for s in chat["sources"]:
                    st.markdown(f"- {s}")

# ============================================================================
# USER INPUT LOGIC
# ============================================================================

user_input = st.chat_input("Type your medical query...")

if user_input:
    # Disable welcome screen on input
    st.session_state.show_welcome = False
    
    # Display user message immediately
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("🔍 Consulting medical database..."):
            try:
                response = client.send_message(
                    message=user_input,
                    session_id=st.session_state.session_id
                )
                answer = response.get("answer", "I couldn't find an answer.")
                sources = response.get("sources", [])
                
                st.markdown(answer)
                
                if sources:
                    with st.expander("📄 View Sources"):
                        for s in sources:
                            st.markdown(f"- {s}")
                
                # Save interaction to session history
                st.session_state.chat_history.append({
                    "user": user_input,
                    "assistant": answer,
                    "sources": sources
                })
                st.rerun()
            except Exception as e:
                st.error("The medical server is currently unavailable.")

# ============================================================================
# FOOTER
# ============================================================================

st.divider()

footer_col1, footer_col2, footer_col3 = st.columns(3)

with footer_col1:
    st.markdown(
        "<p style='text-align: center;'><b>Total Queries:</b> " + 
        f"{len(st.session_state.chat_history)}</p>",
        unsafe_allow_html=True
    )

with footer_col2:
    st.markdown(
        "<p style='text-align: center;'><b>Session:</b> " + 
        f"{st.session_state.session_id[:12]}...</p>",
        unsafe_allow_html=True
    )

with footer_col3:
    backend_status = "✅ Online" if client.health_check() else "❌ Offline"
    st.markdown(
        f"<p style='text-align: center;'><b>Backend:</b> {backend_status}</p>",
        unsafe_allow_html=True
    )

# st.markdown(
#     """
#     <div class='disclaimer'>
#         <b>⚠️ Important Disclaimer:</b><br>
#         This application is for educational purposes only. Information provided 
#         is not a substitute for professional medical advice. Always consult qualified 
#         healthcare professionals for medical decisions.
#     </div>
#     """,
#     unsafe_allow_html=True
# )