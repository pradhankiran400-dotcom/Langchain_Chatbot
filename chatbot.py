from langchain_groq import ChatGroq
import streamlit as st
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from dotenv import load_dotenv

load_dotenv()

st.title("🤖 Personalized LangChain Chatbot")

with st.sidebar:
    st.header("⚙️ Chatbot Persona")
    st.write("Tell the chatbot how to behave:")
    
    custom_persona = st.text_area(
        "System Prompt",
        value="You are a helpful and polite AI assistant.",
        height=150
    )
    
    if st.button("Reset Chat"):
        st.session_state.chat_history = [SystemMessage(content=custom_persona)]
        st.rerun()

model = ChatGroq(model="llama-3.1-8b-instant")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        SystemMessage(content=custom_persona)
    ]
else:
    if st.session_state.chat_history and isinstance(st.session_state.chat_history[0], SystemMessage):
        st.session_state.chat_history[0] = SystemMessage(content=custom_persona)

for msg in st.session_state.chat_history:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.markdown(msg.content)
    elif isinstance(msg, AIMessage):
        with st.chat_message("assistant"):
            st.markdown(msg.content)

user_input = st.chat_input("Type your message here...")

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)
    
    st.session_state.chat_history.append(HumanMessage(content=user_input))
    
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result = model.invoke(st.session_state.chat_history)
            st.markdown(result.content)
    
    st.session_state.chat_history.append(AIMessage(content=result.content))