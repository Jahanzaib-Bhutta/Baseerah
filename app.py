import streamlit as st
import os
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image
import pandas as pd
import json
import time

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Baseerah",
    page_icon="🕌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CUSTOM CSS ---
st.markdown("""
<style>
    .block-container {
        max_width: 800px;
        padding-top: 2rem;
        padding-bottom: 4rem;
        margin: 0 auto;
    }
    .stChatMessage {
        background-color: #262730;
        border: 1px solid #444;
        border-radius: 15px;
        padding: 15px;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 3. SETUP ---
try:
    from prompt import SYSTEM_PROMPT
except ImportError:
    SYSTEM_PROMPT = "You are Baseerah, a helpful AI tutor for Islamic manuscripts."

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# --- 4. STATE MANAGEMENT ---
if "history" not in st.session_state:
    st.session_state.history = []
if "vocab_data" not in st.session_state:
    st.session_state.vocab_data = None

# --- 5. HELPER FUNCTIONS ---

def extract_vocabulary(image):
    """Uses gemini-flash-latest (Verified in your list) to save quota."""
    try:
        # --- THE FIX IS HERE ---
        # We use 'gemini-flash-latest' because 1.5-flash was missing from your list
        model = genai.GenerativeModel("models/gemini-flash-latest")
        
        prompt = """
        Analyze the image. Identify 5 key Islamic terms.
        Return ONLY a JSON list. Format: [{"term": "Word", "root": "Root", "definition": "Meaning"}]
        """
        response = model.generate_content([image, prompt])
        
        # Clean potential markdown
        json_text = response.text.replace("```json", "").replace("```", "").strip()
        data = json.loads(json_text)
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Vocab failed: {e}")
        return None

# --- 6. SIDEBAR (The Desk) ---
with st.sidebar:
    st.title("🕌 Baseerah")
    st.caption("AI Turath Companion")
    st.markdown("---")
    
    # Model Picker
    model_choice = st.selectbox(
        "Chat Engine",
        ["models/gemini-flash-latest"]
    )
    
    st.markdown("### 1. Manuscript")
    uploaded_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Current Text", use_container_width=True)
        st.markdown("---")
        
        st.markdown("### 2. Study Tools")
        if st.button("📝 Extract Flashcards"):
            with st.spinner("Analyzing terms..."):
                df = extract_vocabulary(image)
                if df is not None:
                    st.session_state.vocab_data = df
        
        if st.session_state.vocab_data is not None:
            st.dataframe(st.session_state.vocab_data, hide_index=True)
            csv = st.session_state.vocab_data.to_csv(index=False).encode('utf-8')
            st.download_button("💾 Download CSV", csv, "vocab.csv", "text/csv")
    
    st.markdown("---")
    if st.button("🗑️ New Chat"):
        st.session_state.history = []
        st.session_state.vocab_data = None
        st.rerun()

# --- 7. MAIN CHAT AREA ---

if not api_key:
    st.warning("Please configure your API Key in .env")
    st.stop()

genai.configure(api_key=api_key)

# Welcome Message
if not st.session_state.history:
    st.markdown("<h2 style='text-align: center;'>Salam, Talib-ul-‘ilm.</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888;'>Upload a text to begin our session.</p>", unsafe_allow_html=True)

# Display History
for message in st.session_state.history:
    role = "user" if message.role == "user" else "assistant"
    with st.chat_message(role):
        st.markdown(message.parts[0].text)

# --- 8. INPUT AREA ---
user_message = st.chat_input("Ask Baseerah about the text...")

if user_message:
    if not uploaded_file:
        st.error("Please upload a manuscript in the sidebar first.")
    else:
        # 1. User Bubble
        with st.chat_message("user"):
            st.markdown(user_message)
        
        # 2. AI Response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    chat_model = genai.GenerativeModel(
                        model_name=model_choice, 
                        system_instruction=SYSTEM_PROMPT
                    )
                    
                    chat = chat_model.start_chat(history=st.session_state.history)
                    
                    # Pass image context if new chat
                    if not st.session_state.history:
                        response = chat.send_message([image, user_message])
                    else:
                        response = chat.send_message(user_message)
                    
                    st.markdown(response.text)
                    st.session_state.history = chat.history
                    
                except Exception as e:
                    st.error(f"Error: {e}")
                    st.info("💡 Tip: If you get a 429 error, switch the 'Chat Engine' to 'gemini-flash-latest'.")
