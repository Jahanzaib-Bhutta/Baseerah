import streamlit as st
import os
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image
import sys

# --- DEBUG 1: PAGE CONFIG MUST BE FIRST ---
st.set_page_config(layout="wide", page_title="Baseerah: AI Turath Reasoner")

# --- DEBUG 2: UI VISIBILITY CHECK ---
st.title("Baseerah: AI Turath Reasoner")
st.write("System Status: 🟢 Online | Model: Gemini 3 Pro")

# --- DEBUG 3: SAFE IMPORT ---
# We try to import the prompt. If it fails, we don't crash the app.
try:
    from prompt import SYSTEM_PROMPT
except ImportError:
    st.error("⚠️ CRITICAL ERROR: Could not read 'prompt.py'. Make sure the file exists and has 'SYSTEM_PROMPT = ...'")
    SYSTEM_PROMPT = ""

# --- SETUP ---
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("❌ API Key is missing. Please check your .env file.")
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.header("Configuration")
    
    # WE USE YOUR EXACT MODELS HERE
    model_choice = st.selectbox(
        "Select Model:",
        [
            "models/gemini-2.0-flash",       # <--- Your verified model
            "models/gemini-flash-latest",
            "models/gemini-3-pro-preview",  # <--- THE HACKATHON WINNER
            "models/gemini-2.5-pro",
            "models/gemini-2.0-flash"
        ]
    )
    
    st.markdown("---")
    uploaded_file = st.file_uploader("Upload Manuscript", type=["png", "jpg", "jpeg"])
    st.caption("Supported formats: PNG, JPG")

# --- MAIN LOGIC ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. The Manuscript")
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Text", use_container_width=True)
    else:
        st.info("👈 Please upload an image in the sidebar.")

with col2:
    st.subheader("2. Baseerah Reasoning")
    
    # Only show button if image is there
    if uploaded_file:
        analyze_btn = st.button("Analyze with Gemini", type="primary")
        
        if analyze_btn:
            if not SYSTEM_PROMPT:
                st.error("Cannot analyze: System Prompt is empty.")
            else:
                try:
                    # CONFIGURING GEMINI
                    genai.configure(api_key=api_key)
                    
                    model = genai.GenerativeModel(
                        model_name=model_choice,
                        system_instruction=SYSTEM_PROMPT
                    )
                    
                    # RUNNING THE MODEL
                    with st.spinner(f"Using {model_choice} to decode text..."):
                        response = model.generate_content(image)
                        st.markdown(response.text)
                        
                except Exception as e:
                    st.error(f"Analysis Failed: {e}")
                    st.warning("Tip: If you get a 404, try switching the model in the sidebar.")

    else:
        st.write("Waiting for image...")