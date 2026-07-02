import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

def render_chat_studio(model, genai_client, transcribe_audio):
    st.sidebar.subheader("🤖 Bot Behavior & Persona")
    user_system_prompt = st.sidebar.text_area(
        "Set AI Persona / System Prompt:",
        value=st.session_state.system_prompt,
        height=100,
        help="Define how the AI should act (e.g. 'You are a pirate', 'You are a Python expert')"
    )

    if user_system_prompt != st.session_state.system_prompt:
        st.session_state.system_prompt = user_system_prompt
        st.sidebar.success("Updated Persona!")

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
    st.sidebar.subheader("🎙️ Voice Chat")
    audio_file = st.sidebar.audio_input("Speak your message:", key="voice_chat_input")
    
    if audio_file is not None:
        audio_key = f"{audio_file.name}_{audio_file.size}"
        if st.session_state.get("last_audio_key") != audio_key:
            st.session_state.last_audio_key = audio_key
            
            with st.spinner("Transcribing..."):
                transcribed_text = transcribe_audio(audio_file)
            
            if transcribed_text:
                st.session_state.messages.append({"role": "user", "content": transcribed_text})
                
                langchain_messages = [SystemMessage(content=st.session_state.system_prompt)]
                for msg in st.session_state.messages:
                    if msg["role"] == "user":
                        langchain_messages.append(HumanMessage(content=msg["content"]))
                    elif msg["role"] == "assistant":
                        langchain_messages.append(AIMessage(content=msg["content"]))
                
                with st.spinner("Thinking..."):
                    response = model.invoke(langchain_messages)
                    st.session_state.messages.append({"role": "assistant", "content": response.content})
                st.rerun()

    st.sidebar.divider()
    if st.sidebar.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.title("💬 AI Chat Studio")
    st.caption(f"🎯 **Active Persona:** *{st.session_state.system_prompt}*")

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask anything..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        langchain_messages = [SystemMessage(content=st.session_state.system_prompt)]
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                langchain_messages.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                langchain_messages.append(AIMessage(content=msg["content"]))

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = model.invoke(langchain_messages)
                st.markdown(response.content)
        
        st.session_state.messages.append({"role": "assistant", "content": response.content})
