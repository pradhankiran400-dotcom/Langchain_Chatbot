import streamlit as st
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from google import genai
from google.genai import types

import importlib

# Import custom navigation modules
import chat_studio
import pdf_studio
import art_studio
import vision_studio
import web_studio

# Force reload modules during development so changes take effect immediately
importlib.reload(chat_studio)
importlib.reload(pdf_studio)
importlib.reload(art_studio)
importlib.reload(vision_studio)
importlib.reload(web_studio)

# Load environment variables
load_dotenv()

# Verify that required API keys are configured (especially when deployed to Streamlit Cloud)
groq_key = os.environ.get("GROQ_API_KEY", "").strip()
google_key = os.environ.get("GOOGLE_API_KEY", "").strip()

if not groq_key or not google_key:
    st.set_page_config(page_title="API Configuration Required", page_icon="🔑")
    st.error("🔑 **Required API Keys are Missing**")
    st.info(
        """
        To run this Custom AI Studio, you must configure your API keys.
        
        **For Local Development:**
        Create a `.env` file in the project folder:
        ```env
        GROQ_API_KEY=gsk_your_groq_key_here
        GOOGLE_API_KEY=your_google_api_key_here
        HUGGINGFACEHUB_API_TOKEN=your_huggingface_token_here
        ```
        
        **For Streamlit Cloud Deployment:**
        Go to your **Streamlit Dashboard**, select your app, click **Manage App > Settings > Secrets**, and paste your keys in TOML format:
        ```toml
        GROQ_API_KEY = "gsk_your_groq_key_here"
        GOOGLE_API_KEY = "your_google_api_key_here"
        HUGGINGFACEHUB_API_TOKEN = "your_huggingface_token_here"
        ```
        """
    )
    st.stop()

st.set_page_config(
    page_title="Personalized AI Studio",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

DEFAULT_SYSTEM_PROMPT = """You are the official assistant for Custom AI Studio.
Your goal is to guide users, answer questions, and suggest how to use this platform.

Here are the details of the Custom AI Studio features:
1. 💬 AI Chat Studio:
   - Customize Bot Persona: Change the prompt in the sidebar, or use presets (Assistant, Pirate, Developer).
   - Voice input: Use the voice chat microphone in the sidebar to chat using speech.
2. 📄 PDF Chat (RAG):
   - Upload any PDF document to ask questions about its content. Supports voice/text.
3. 🎨 AI Art Studio:
   - Generate images from text descriptions.
   - Choose between Pollinations AI (free, no key) or Hugging Face Inference (SDXL, SD 1.5, Flux Schnell). If using HF, enter your API token in the sidebar.
4. 🖼️ Vision Studio (Image to Prompt):
   - Upload a PNG/JPG/JPEG image.
   - Click "Generate Art Prompt" to describe the image in detail, or ask questions about the picture.
5. 🌐 Link Chat (RAG):
   - Input a YouTube link or website URL. Click "Analyze Link" to load context, then ask questions about it.
6. 💡 Alternative Links:
   - Check the bottom of the sidebar for quick links to Google Gemini, ChatGPT, and Claude.

Always be friendly, guide users to appropriate tabs, and suggest features of this AI Studio.

*IMPORTANT CONSTRAINTS:*
- If a user sends/pastes a website link or YouTube video URL, or asks you to read/analyze/summarize a link in this general chat room: explain politely that you cannot load or analyze external links here, and redirect them to the "🌐 Link Chat (RAG)" screen in the sidebar where they can easily analyze it.
- If a user asks you to analyze, look at, describe, or answer questions about an image or picture: explain politely that you cannot see images or files in this general chat room, and redirect them to the "🖼️ Vision Studio (Image to Prompt)" screen in the sidebar where they can upload and ask questions about the picture.
"""

# Initialize Session State Variables
if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = DEFAULT_SYSTEM_PROMPT

if "messages" not in st.session_state:
    st.session_state.messages = []

if "pdf_messages" not in st.session_state:
    st.session_state.pdf_messages = []

# Initialize LangChain Groq Model
@st.cache_resource
def get_model():
    return ChatGroq(model="llama-3.1-8b-instant")

model = get_model()

# Initialize Google GenAI Client
@st.cache_resource
def get_genai_client():
    return genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

genai_client = get_genai_client()

def transcribe_audio(audio_file):
    """
    Transcribes audio using Google's Gemini Generative AI model (gemini-2.5-flash).
    """
    try:
        audio_bytes = audio_file.read()
        audio_part = types.Part.from_bytes(
            data=audio_bytes,
            mime_type=audio_file.type
        )
        response = genai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[
                audio_part,
                "Transcribe the following audio accurately. Output ONLY the plain transcription text, with no additional commentary, headings, or markdown formatting."
            ]
        )
        return response.text.strip() if response.text else ""
    except Exception as e:
        st.error(f"Error transcribing audio with GenAI: {e}")
        return None

# Sidebar Setup
st.sidebar.title("✨ Custom AI Studio")

# Check for Hugging Face API Token in Environment
hf_token = os.environ.get("HUGGINGFACEHUB_API_TOKEN", "")

# If not found, prompt in sidebar
if not hf_token:
    st.sidebar.subheader("🔑 Hugging Face Config")
    hf_token = st.sidebar.text_input("Enter HF API Token:", type="password", help="Get a free token from huggingface.co to unlock high quality image models.")

# Navigation Radio
app_mode = st.sidebar.radio("Navigation", ["💬 AI Chat Studio", "📄 PDF Chat (RAG)", "🎨 AI Art Studio", "🖼️ Vision Studio (Image to Prompt)", "🌐 Link Chat (RAG)"])

st.sidebar.divider()

# Fallback Assistant Links
st.sidebar.subheader("💡 Need alternatives?")
st.sidebar.markdown(
    """
    If you don't find the answer from this chatbot, try:
    - 🌐 [Gemini](https://gemini.google.com)
    - 💬 [ChatGPT](https://chatgpt.com)
    - 🧠 [Claude](https://claude.ai)
    """
)
st.sidebar.divider()

# Route to the appropriate module
if app_mode == "💬 AI Chat Studio":
    chat_studio.render_chat_studio(model, genai_client, transcribe_audio, DEFAULT_SYSTEM_PROMPT)

elif app_mode == "📄 PDF Chat (RAG)":
    pdf_studio.render_pdf_studio(model, transcribe_audio)

elif app_mode == "🎨 AI Art Studio":
    art_studio.render_art_studio(hf_token)

elif app_mode == "🖼️ Vision Studio (Image to Prompt)":
    vision_studio.render_vision_studio(genai_client)

elif app_mode == "🌐 Link Chat (RAG)":
    web_studio.render_web_studio(model, transcribe_audio)