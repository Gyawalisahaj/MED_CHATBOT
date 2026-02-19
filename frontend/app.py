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
# CUSTOM STYLING
# ============================================================================

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

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "api_client" not in st.session_state:
    st.session_state.api_client = MedicalChatAPIClient()

if "show_welcome" not in st.session_state:
    st.session_state.show_welcome = True

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
    
    # API Status
    if st.session_state.api_client.health_check():
        st.success("✅ Backend Online")
    else:
        st.error("❌ Backend Offline")
    
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
            if st.session_state.api_client.clear_history(st.session_state.session_id):
                st.session_state.chat_history = []
                st.success("History cleared!")
                st.rerun()
    
    st.divider()
    
    # Settings
    st.markdown("### ⚙️ Settings")
    backend_url = st.text_input(
        "Backend URL",
        value=os.getenv("BACKEND_URL", "http://localhost:8000"),
        help="Change if backend is on different host"
    )
    if backend_url != st.session_state.api_client.base_url:
        st.session_state.api_client = MedicalChatAPIClient(backend_url)
    
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
    
    st.markdown("### ⚠️ Disclaimer")
    st.warning(
        "**Educational Use Only**: This tool is for learning purposes. "
        "Always consult qualified healthcare professionals for medical advice."
    )

# ============================================================================
# MAIN CONTENT
# ============================================================================

# Header
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

chat_container = st.container()

with chat_container:
    # Welcome message
    if st.session_state.show_welcome and len(st.session_state.chat_history) == 0:
        st.info(
            "### Welcome to MediQuery AI 👋\n\n"
            "Ask any medical question and get answers backed by medical literature. "
            "Sources are provided for every answer.\n\n"
            "**Example questions:**\n"
            "- What are the symptoms of diabetes mellitus?\n"
            "- Explain the pathophysiology of hypertension\n"
            "- What is the treatment for pneumonia?\n"
            "- What are the side effects of aspirin?"
        )
    
    # Display chat history
    for msg in st.session_state.chat_history:
        # User message
        st.markdown(
            f"""
            <div class='user-message'>
                <b>You:</b><br>{msg.get('message', '')}
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Assistant message
        st.markdown(
            f"""
            <div class='assistant-message'>
                <b>MediQuery AI:</b><br>{msg.get('response', '')}
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Sources
        sources = msg.get('sources', [])
        if sources:
            with st.expander(f"📄 Sources ({len(sources)})"):
                for source in sources:
                    st.markdown(
                        f"<div class='source-item'>{source}</div>",
                        unsafe_allow_html=True
                    )
        
        st.divider()

# ============================================================================
# INPUT & PROCESSING
# ============================================================================

# Query input
# The first positional argument of chat_input serves as the placeholder in
# newer Streamlit versions, so we only supply it and avoid keyword conflicts.
user_input = st.chat_input(
    placeholder="Type your medical question... (e.g., What are the symptoms of diabetes?)"
)

if user_input:
    st.session_state.show_welcome = False
    
    # Display user message immediately
    st.markdown(
        f"""
        <div class='user-message'>
            <b>You:</b><br>{user_input}
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Processing with spinner
    with st.spinner("🔍 Searching medical database..."):
        try:
            response = st.session_state.api_client.send_message(
                message=user_input,
                session_id=st.session_state.session_id
            )
            
            answer = response.get("answer", "No answer found")
            sources = response.get("sources", [])
            
            # Display assistant response
            st.markdown(
                f"""
                <div class='assistant-message'>
                    <b>MediQuery AI:</b><br>{answer}
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Display sources
            if sources:
                with st.expander(f"📄 Sources ({len(sources)})"):
                    for source in sources:
                        st.markdown(
                            f"<div class='source-item'>{source}</div>",
                            unsafe_allow_html=True
                        )
            
            # Add to history
            st.session_state.chat_history.append({
                "message": user_input,
                "response": answer,
                "sources": sources,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            st.error(
                f"""
                ❌ Error processing query: {str(e)}
                
                **Troubleshooting:**
                - Check if backend is running at {st.session_state.api_client.base_url}
                - Ensure VDMS vector database is available
                - Check your Groq API key is valid
                """
            )

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
    backend_status = "✅ Online" if st.session_state.api_client.health_check() else "❌ Offline"
    st.markdown(
        f"<p style='text-align: center;'><b>Backend:</b> {backend_status}</p>",
        unsafe_allow_html=True
    )

st.markdown(
    """
    <div class='disclaimer'>
        <b>⚠️ Important Disclaimer:</b><br>
        This application is for educational purposes only. Information provided 
        is not a substitute for professional medical advice. Always consult qualified 
        healthcare professionals for medical decisions.
    </div>
    """,
    unsafe_allow_html=True
)


# Load Styles
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize Session State
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "last_audio_ts" not in st.session_state:
    st.session_state.last_audio_ts = None

# Backend API Configuration
BACKEND_URL = st.secrets.get("BACKEND_URL", "http://localhost:8000")
client = MedicalChatAPIClient(BACKEND_URL)

st.title("🩺 MediQuery Assistant")
st.markdown("---")

# --- SIDEBAR: Voice Input ---
with st.sidebar:
    st.header("🎙️ Voice Control")
    st.info("Record your question if you prefer not to type.")
    # audio_input may not be available in this Streamlit version
    audio_data = None
    if hasattr(st, "audio_input"):
        try:
            audio_data = st.audio_input("Microphone")
        except Exception:
            audio_data = None
    
    # Process Voice Input if new audio is detected
    voice_query = None
    if audio_data:
        # Simple check to avoid re-processing same recording on every rerun
        with st.spinner("🎙️ Transcribing voice..."):
            try:
                voice_query = client.transcribe_audio(audio_data.getvalue())
            except Exception:
                st.error("Transcription failed.")

# --- MAIN: Chat Display ---
for i, chat in enumerate(st.session_state.chat_history):
    with st.chat_message("user"):
        st.markdown(chat["user"])
    
    with st.chat_message("assistant"):
        st.markdown(chat["assistant"])
        
        # Accessibility: Read Aloud Button
        if st.button(f"🔊 Read Aloud", key=f"speak_{i}"):
            with st.spinner("Preparing audio..."):
                audio_b64 = client.get_text_to_speech(chat["assistant"])
                # Inject autoplaying audio element
                st.markdown(
                    f'<audio src="data:audio/mp3;base64,{audio_b64}" autoplay hidden></audio>', 
                    unsafe_allow_html=True
                )

# --- USER INPUT LOGIC ---
user_input = st.chat_input("Type your medical query...")

# Priority: If voice_query exists from the sidebar, use it. Otherwise use text input.
final_query = voice_query or user_input

if final_query:
    # Add User Message
    with st.chat_message("user"):
        st.markdown(final_query)

    # Generate Response
    with st.chat_message("assistant"):
        with st.spinner("🔍 Consulting medical database..."):
            try:
                response = client.send_message(
                    message=final_query,
                    history=st.session_state.chat_history
                )
                answer = response.get("answer", "I couldn't find an answer.")
                sources = response.get("sources", [])

                st.markdown(answer)
                
                # Show Sources if available
                if sources:
                    with st.expander("📄 View Sources"):
                        for s in sources: st.markdown(f"- {s}")

                # Save to History
                st.session_state.chat_history.append({
                    "user": final_query,
                    "assistant": answer
                })
                
                # Rerun to clear the voice input and show the new history
                st.rerun()

            except Exception as e:
                st.error("The medical server is currently unavailable.")