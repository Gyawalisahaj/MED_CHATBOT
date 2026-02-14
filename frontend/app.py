import streamlit as st
from api_client import MedicalChatAPIClient
import base64

# --- Page Setup ---
st.set_page_config(page_title="MediQuery AI", page_icon="🩺", layout="centered")

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
    audio_data = st.audio_input("Microphone")
    
    # Process Voice Input if new audio is detected
    voice_query = None
    if audio_data:
        # Simple check to avoid re-processing same recording on every rerun
        with st.spinner("🎙️ Transcribing voice..."):
            try:
                voice_query = client.transcribe_audio(audio_data.getvalue())
            except Exception as e:
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