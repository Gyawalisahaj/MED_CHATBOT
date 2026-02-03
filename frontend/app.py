import streamlit as st
from api_client import MedicalChatAPIClient

# -------------------------------
# Page Configuration
# -------------------------------
st.set_page_config(
    page_title="Medical RAG Chatbot",
    page_icon="🩺",
    layout="centered",
)

# -------------------------------
# Load Styles
# -------------------------------
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# -------------------------------
# Header
# -------------------------------
st.title("🩺 Medical Information Assistant")
st.caption(
    "Educational medical information powered by Retrieval-Augmented Generation (RAG)"
)

# -------------------------------
# Backend Client
# -------------------------------
BACKEND_URL = st.secrets.get("BACKEND_URL", "http://localhost:8000")
client = MedicalChatAPIClient(BACKEND_URL)

# -------------------------------
# Session State Initialization
# -------------------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# -------------------------------
# Display Chat History
# -------------------------------
for msg in st.session_state.chat_history:
    with st.chat_message("user"):
        st.markdown(msg["user"])
    with st.chat_message("assistant"):
        st.markdown(msg["assistant"])

# -------------------------------
# User Input
# -------------------------------
user_input = st.chat_input("Ask a medical question (educational only)...")

if user_input:
    # Show user message
    with st.chat_message("user"):
        st.markdown(user_input)

    # Call backend
    with st.chat_message("assistant"):
        with st.spinner("Retrieving medical information..."):
            try:
                response = client.send_message(
                    message=user_input,
                    history=st.session_state.chat_history,
                )

                answer = response.get("answer", "")
                sources = response.get("sources", [])

                st.markdown(answer)

                if sources:
                    with st.expander("📄 Sources"):
                        for src in sources:
                            st.markdown(f"- {src}")

                # Save conversation
                st.session_state.chat_history.append({
                    "user": user_input,
                    "assistant": answer,
                })

            except Exception as e:
                st.error("Unable to fetch response from server.")
                st.caption(str(e))
