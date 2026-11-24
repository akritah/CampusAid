# Streamlit entrypoint for the CampusAid Policy Chatbot

"""Standalone Streamlit app that reuses the backend policy retrieval and Gemini answer generation.

Features:
- Answers are always grounded in official policy documents.
- Citations show document name and the quoted passage.
- Out‑of‑scope or unsupported questions receive a refusal.
- Heavy models (sentence‑transformers, Whisper) are lazy‑loaded by the backend, keeping the Streamlit process lightweight.
- API keys are read securely from Streamlit Secrets (`st.secrets`).
"""

import os
import sys
from pathlib import Path
import streamlit as st

# Make the backend package importable.
BASE_DIR = Path(__file__).parent
BACKEND_DIR = BASE_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.append(str(BACKEND_DIR))

# Load secrets – Gemini API key is required.
if "GEMINI_API_KEY" not in os.environ:
    if "GEMINI_API_KEY" not in st.secrets:
        st.error("Gemini API key not configured. Add `GEMINI_API_KEY` to Streamlit Secrets.")
        st.stop()
    os.environ["GEMINI_API_KEY"] = st.secrets["GEMINI_API_KEY"]

# Optional model override.
if "GEMINI_MODEL" in st.secrets:
    os.environ["GEMINI_MODEL"] = st.secrets["GEMINI_MODEL"]

# Import the core answer function after environment is ready.
from backend.app.policy_qa import answer  # type: ignore

# Streamlit UI.
st.set_page_config(page_title="CampusAid Policy Chatbot", page_icon="📚", layout="centered")
st.title("CampusAid Policy Chatbot")
st.caption(
    "Ask any question about Bennett University policies. "
    "Answers are extracted from official policy documents and cite the source file and passage."
)

# Initialise chat history in session state.
if "chat" not in st.session_state:
    st.session_state.chat = []  # list of dicts {role, content, sources}

def render_message(entry):
    if entry["role"] == "user":
        st.markdown(f"**You:** {entry['content']}")
    else:
        st.markdown(f"**CampusAid:** {entry['content']}")
        sources = entry.get("sources", [])
        if sources:
            st.markdown("**Sources:**")
            for src in sources:
                doc = src.get("document", "unknown")
                quote = src.get("quote", "").replace("\n", " ")
                relevance = src.get("relevance", "")
                st.markdown(f"- **{doc}** (relevance {relevance}):\n  > {quote}")

# Show previous conversation.
for msg in st.session_state.chat:
    render_message(msg)

# Input field.
question = st.text_input("Your question", "")
if st.button("Ask") and question.strip():
    # Record user message.
    st.session_state.chat.append({"role": "user", "content": question.strip()})
    with st.spinner("Thinking…"):
        try:
            result = answer(question.strip())
        except Exception as e:
            st.error(f"Error while processing the question: {e}")
            result = {"answer": "Sorry, I could not process your request.", "abstained": True, "sources": []}
        # Handle explicit refusal when no sources are found
        if not result.get("sources"):
            content = "I’m unable to find policy evidence to answer that question."
            abstained = True
        else:
            content = result.get("answer", "")
            abstained = result.get("abstained", False)
        assistant_msg = {
            "role": "assistant",
            "content": content,
            "sources": result.get("sources", []),
            "abstained": abstained,
        }
    st.session_state.chat.append(assistant_msg)
    st.experimental_rerun()

st.divider()
st.subheader("Try these example questions")
example_questions = [
    "What is the attendance requirement for appearing in exams?",
    "Can I get a fee refund if I drop a course after the deadline?",
    "Is ragging allowed on campus?",
    "How do I submit a grievance about hostel food?",
    "What should I do if I miss a scholarship deadline?",
    "Tell me about the university's policy on academic dishonesty.",
    "Do you offer any support for international students?",  # Expected refusal / out‑of‑scope
]
for q in example_questions:
    st.caption(f"- {q}")

st.caption("---")
st.caption(
    "**Privacy notice:** No personal data is stored. All processing happens on the server. "
    "API keys are kept in Streamlit Secrets and never exposed to the client."
)
