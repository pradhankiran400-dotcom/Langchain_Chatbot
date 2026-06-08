from langchain_groq import ChatGroq
import streamlit as st
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from dotenv import load_dotenv

# Load environment variables (API Keys)
load_dotenv()

# Set Streamlit page config
st.set_page_config(
    page_title="Custom Persona Llama-3 Chatbot",
    page_icon="🤖",
    layout="wide",
)

# Custom Sleek CSS for styling
st.markdown("""
<style>
    /* Main container styling */
    .reportview-container {
        background: #0e1117;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #1a1c24;
        border-right: 1px solid #2d3139;
    }
    
    /* Title and subheader formatting */
    .main-title {
        font-family: 'Outfit', 'Inter', sans-serif;
        background: linear-gradient(45deg, #FF4B4B, #FF8F00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    
    .persona-badge {
        background-color: #262730;
        color: #FF4B4B;
        border: 1px solid #3d4250;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-size: 0.9rem;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 1.5rem;
    }
    
    /* Streamlit chat inputs & buttons */
    .stButton>button {
        border-radius: 8px;
        transition: all 0.2s ease-in-out;
    }
</style>
""", unsafe_allow_html=True)

# 1. Sidebar for Role Selection & Config
st.sidebar.title("🤖 Chatbot Persona Setup")
st.sidebar.markdown("---")

# Define Preset Roles
presets = {
    "Helpful Assistant": "You are a helpful, friendly, and knowledgeable AI assistant.",
    "Python Code Tutor": "You are a senior Python developer and teacher. Explain coding concepts simply, provide clean, documented code, and help debug issues.",
    "Creative Writer": "You are a creative writer and storyteller. Use rich, engaging language to help the user write stories, brainstorm plots, or compose poetry.",
    "Strict Critic": "You are a critical reviewer. Analyze the user's ideas with constructive skepticism, pointing out potential flaws, logic gaps, or improvements.",
    "Custom Role...": "" # Handled dynamically below
}

# Select box for presets
preset_choice = st.sidebar.selectbox(
    "Choose a Preset Persona:",
    options=list(presets.keys())
)

# Dynamic prompt input based on choice
if preset_choice == "Custom Role...":
    custom_role = st.sidebar.text_area(
        "Define Your Custom Role:",
        value="You are a specialized AI assistant that helps with...",
        height=150
    )
    selected_role_prompt = custom_role
else:
    selected_role_prompt = presets[preset_choice]
    st.sidebar.info(f"**Description:**\n{selected_role_prompt}")

st.sidebar.markdown("---")

# Reset Conversation Button
if st.sidebar.button("🔄 Restart Chat with Selected Role", use_container_width=True):
    # Clear chat history and reinitialize with the new system message
    st.session_state.chat_history = [
        SystemMessage(content=selected_role_prompt)
    ]
    st.success("Chat history reset with new persona!")
    st.rerun()

# 2. Main Page Layout
st.markdown("<h1 class='main-title'>My Llama-3 Chatbot 🤖</h1>", unsafe_allow_html=True)
st.markdown(f"<div class='persona-badge'>Active Persona: {preset_choice}</div>", unsafe_allow_html=True)

# Initialize Chat History in Session State if not present
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        SystemMessage(content=selected_role_prompt)
    ]

# If the system prompt has changed in the sidebar and chat has not started (or we want to update it dynamically)
# we can update the first message in the chat history
if len(st.session_state.chat_history) > 0 and isinstance(st.session_state.chat_history[0], SystemMessage):
    if st.session_state.chat_history[0].content != selected_role_prompt:
        st.session_state.chat_history[0] = SystemMessage(content=selected_role_prompt)

# Initialize the Llama model
# We wrap this to avoid recreating the object constantly
@st.cache_resource
def get_model():
    return ChatGroq(model="llama-3.1-8b-instant")

try:
    model = get_model()
except Exception as e:
    st.error(f"Error initializing model: {e}")

# 3. Display Chat Messages (Skipping SystemMessage at index 0)
for msg in st.session_state.chat_history[1:]:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.markdown(msg.content)
    elif isinstance(msg, AIMessage):
        with st.chat_message("assistant"):
            st.markdown(msg.content)

# 4. Chat Input
user_input = st.chat_input("Type your message here...")

if user_input:
    # Display human message immediately
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Append human message to history
    st.session_state.chat_history.append(HumanMessage(content=user_input))
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                result = model.invoke(st.session_state.chat_history)
                st.markdown(result.content)
                # Append assistant response to history
                st.session_state.chat_history.append(AIMessage(content=result.content))
            except Exception as e:
                st.error(f"Failed to generate response: {e}")