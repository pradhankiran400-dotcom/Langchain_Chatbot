from langchain_groq import ChatGroq
import streamlit as st
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from dotenv import load_dotenv

# Load environment variables (API Keys)
load_dotenv()

# App Title
st.title("Langchain Chatbot")

# Initialize the model
model = ChatGroq(model="llama-3.1-8b-instant")

# 1. Initialize Chat History in Session State
# Ye check karta hai ki kya memory pehle se exist karti hai. Agar nahi, toh create karta hai.
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        SystemMessage(content='you are a helpful AI assistant')
    ]

# 2. Display previous chat history in the UI
# Hum SystemMessage ko UI mein nahi dikhate, sirf Human aur AI messages render karte hain.
for msg in st.session_state.chat_history:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.markdown(msg.content)
    elif isinstance(msg, AIMessage):
        with st.chat_message("assistant"):
            st.markdown(msg.content)

# 3. Get User Input via Streamlit UI (Replaces terminal input())
user_input = st.chat_input("Type your message here...")

if user_input:
    # Handle 'stop' condition if you still want it, though usually not needed in web UIs
    if user_input.lower() == 'stop':
        st.warning("Chat stopped by user. Refresh page to restart.")
    else:
        # Display the new user message immediately
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Append user message to the session state history
        st.session_state.chat_history.append(HumanMessage(content=user_input))
        
        # Generate and display the AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                result = model.invoke(st.session_state.chat_history)
                st.markdown(result.content)
        
        # Append AI response to the session state history
        st.session_state.chat_history.append(AIMessage(content=result.content))