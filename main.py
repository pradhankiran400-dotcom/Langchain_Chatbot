import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from dotenv import load_dotenv
import requests
import urllib.parse
import os

load_dotenv()

st.set_page_config(
    page_title="Personalized AI Studio",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "system_prompt" not in st.session_state:
    st.session_state.system_prompt = "You are a helpful assistant."

if "messages" not in st.session_state:
    st.session_state.messages = []
    
# Initialize LangChain Groq Model
@st.cache_resource
def get_model():
    return ChatGroq(model="llama-3.1-8b-instant")

model = get_model()


st.sidebar.title("✨ Custom AI Studio")


app_mode = st.sidebar.radio("Navigation", ["💬 AI Chat Studio", "🎨 AI Art Studio"])

st.sidebar.divider()
st.sidebar.subheader("🤖 Bot Behavior & Persona")

# Persona Text Area
user_system_prompt = st.sidebar.text_area(
    "Set AI Persona / System Prompt:",
    value=st.session_state.system_prompt,
    height=100,
    help="Define how the AI should act (e.g. 'You are a pirate', 'You are a Python expert')"
)

if user_system_prompt != st.session_state.system_prompt:
    st.session_state.system_prompt = user_system_prompt
    st.sidebar.success("Updated Persona!")

# Quick Presets
st.sidebar.markdown("**Quick Presets:**")
col1, col2 = st.sidebar.columns(2)
with col1:
    if st.button("💡 Assistant", use_container_width=True):
        st.session_state.system_prompt = "You are a helpful assistant."
        st.rerun()
    if st.button("🏴‍☠️ Pirate", use_container_width=True):
        st.session_state.system_prompt = "You are a pirate matey! Speak like a legendary sea captain in every response!"
        st.rerun()
with col2:
    if st.button("💻 Developer", use_container_width=True):
        st.session_state.system_prompt = "You are an expert Python software engineer. Provide concise, clean code examples."
        st.rerun()

st.sidebar.divider()
if st.sidebar.button("🗑️ Clear Chat History", use_container_width=True):
    st.session_state.messages = []
    st.rerun()

if app_mode == "💬 AI Chat Studio":
    st.title("💬 AI Chat Studio")
    st.caption(f"🎯 **Active Persona:** *{st.session_state.system_prompt}*")

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Accept user input
    if prompt := st.chat_input("Ask anything..."):
        # Display user message in chat message container
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Build LangChain message history starting with SystemMessage
        langchain_messages = [SystemMessage(content=st.session_state.system_prompt)]
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                langchain_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                langchain_messages.append(AIMessage(content=msg["content"]))

        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = model.invoke(langchain_messages)
                st.markdown(response.content)
        
        st.session_state.messages.append({"role": "assistant", "content": response.content})

elif app_mode == "🎨 AI Art Studio":
    st.title("🎨 AI Art Studio")
    st.markdown("Transform your creative text prompts into AI artwork.")

    art_prompt = st.text_input("Describe the image you want to create:", placeholder="e.g., A futuristic cyberpunk city at sunset with neon lights")

    if st.button("✨ Generate Artwork", type="primary"):
        if not art_prompt.strip():
            st.warning("Please enter a description first!")
        else:
            with st.spinner("Crafting your visual masterpiece..."):
                fallback_url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(art_prompt)}"
                img_response = requests.get(fallback_url)
                
                if img_response.status_code == 200:
                    st.image(img_response.content, caption=art_prompt, use_column_width=True)
                    st.download_button(
                        label="📥 Download Artwork",
                        data=img_response.content,
                        file_name="generated_artwork.png",
                        mime="image/png"
                    )
                else:
                    st.error("Failed to generate image. Please try again.")


                    