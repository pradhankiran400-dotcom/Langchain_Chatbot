import streamlit as st
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from google import genai
from google.genai import types

# Import custom navigation modules
import chat_studio
import pdf_studio
import art_studio
import vision_studio
import web_studio

# Load environment variables
load_dotenv()

st.set_page_config(
    page_title="Personalized AI Studio",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State Variables
if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = "You are a helpful assistant."

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
    chat_studio.render_chat_studio(model, genai_client, transcribe_audio)

elif app_mode == "📄 PDF Chat (RAG)":
    pdf_studio.render_pdf_studio(model, transcribe_audio)

elif app_mode == "🎨 AI Art Studio":
    art_studio.render_art_studio(hf_token)

elif app_mode == "🖼️ Vision Studio (Image to Prompt)":
    vision_studio.render_vision_studio(genai_client)

elif app_mode == "🌐 Link Chat (RAG)":
    web_studio.render_web_studio(model, transcribe_audio)