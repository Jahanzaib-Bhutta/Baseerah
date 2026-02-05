import streamlit as st
import os
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image

# --- PAGE CONFIG (Must be first) ---
st.set_page_config(
    layout="wide", 
    page_title="Baseerah: AI Turath Reasoner",
    page_icon="📖"
)

# --- SAFE IMPORT OF PROMPT ---
try:
    from prompt import SYSTEM_PROMPT
except ImportError:
    SYSTEM_PROMPT = ""
    st.error("⚠️ Error: prompt.py not found.")

# --- SETUP ---
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# --- CUSTOM CSS (To fix the 'Long Way Down') ---
st.markdown("""
<style>
    .stTextArea textarea {font-size: 16px !important;}
    div[data-testid="stExpander"] details summary {
        font-size: 1.1rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.title("📖 Baseerah")
    st.caption("AI-Powered Classical Text Analysis")
    st.markdown("---")
    
    # Model Picker
    model_choice = st.selectbox(
        "AI Model Engine",
        ["models/gemini-flash-latest", "models/gemini-2.0-flash", "models/gemini-1.5-pro-latest"]
    )
    
    st.markdown("### Upload")
    uploaded_file = st.file_uploader("Drop Manuscript Here", type=["png", "jpg", "jpeg"])
    
    st.markdown("---")
    st.info("💡 **Tip:** Use high-quality images of Turath texts for best results.")

# --- MAIN LOGIC ---
if not api_key:
    st.error("❌ API Key missing in .env file.")
    st.stop()

# Header
st.markdown("### 🏛️ Baseerah: The Multimodal Scholar")

# Layout: Left (Image) - Right (Analysis)
col1, col2 = st.columns([1, 1.5], gap="large")

with col1:
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Manuscript Preview", use_container_width=True)
    else:
        # Placeholder when empty
        st.markdown(
            """
            <div style="border: 2px dashed #444; padding: 40px; text-align: center; border-radius: 10px;">
                <h3 style="color: #666;">No Manuscript Uploaded</h3>
                <p style="color: #888;">Upload an image from the sidebar to begin analysis.</p>
            </div>
            """, 
            unsafe_allow_html=True
        )

with col2:
    if uploaded_file:
        analyze_btn = st.button("🔍 Analyze Text with Baseerah", type="primary", use_container_width=True)
        
        if analyze_btn:
            if not SYSTEM_PROMPT:
                st.warning("⚠️ System Prompt is empty.")
            else:
                try:
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel(
                        model_name=model_choice,
                        system_instruction=SYSTEM_PROMPT
                    )
                    
                    with st.spinner("⏳ Baseerah is reading, connecting verses, and reasoning..."):
                        response = model.generate_content(image)
                        
                        # --- THE FORMATTING FIX ---
                        # Instead of one long block, we use tabs/expanders
                        st.success("Analysis Complete")
                        
                        # We display the raw markdown nicely
                        st.markdown(response.text)
                        
                        # Optional: You can ask the user to reflect
                        with st.expander("💭 Personal Reflection (Tadabbur)"):
                            st.write("Does this explanation clarify the connection between the Ayah and the ruling?")

                except Exception as e:
                    st.error(f"Analysis Failed: {e}")
