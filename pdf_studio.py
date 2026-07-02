import streamlit as st
import pypdf
from langchain_core.messages import HumanMessage

def render_pdf_studio(model, transcribe_audio):
    st.title("📄 PDF Chat ")
    st.markdown("Upload any PDF document and ask questions based on its content.")

    uploaded_file = st.file_uploader("Upload a PDF document", type=["pdf"])

    if uploaded_file is not None:
        # Extract text from PDF
        reader = pypdf.PdfReader(uploaded_file)
        pdf_text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                pdf_text += extracted + "\n"

        st.success(f"✅ PDF uploaded successfully! ({len(reader.pages)} pages extracted)")

        # Add Voice input in the sidebar for PDF Chat RAG
        st.sidebar.subheader("🎙️ Voice Chat")
        pdf_audio_file = st.sidebar.audio_input("Speak your PDF question:", key="pdf_voice_input")
        
        if pdf_audio_file is not None:
            pdf_audio_key = f"{pdf_audio_file.name}_{pdf_audio_file.size}"
            if st.session_state.get("last_pdf_audio_key") != pdf_audio_key:
                st.session_state.last_pdf_audio_key = pdf_audio_key
                
                with st.spinner("Transcribing..."):
                    transcribed_text = transcribe_audio(pdf_audio_file)
                
                if transcribed_text:
                    st.session_state.pdf_messages.append({"role": "user", "content": transcribed_text})
                    
                    rag_prompt = f"Context from uploaded PDF document:\n{pdf_text[:12000]}\n\nUser Question: {transcribed_text}\nAnswer accurately and concisely based on the PDF context."
                    
                    with st.spinner("Analyzing PDF and generating answer..."):
                        response = model.invoke([HumanMessage(content=rag_prompt)])
                        st.session_state.pdf_messages.append({"role": "assistant", "content": response.content})
                    st.rerun()

        st.sidebar.divider()
        if st.sidebar.button("🗑️ Clear PDF Chat History", use_container_width=True):
            st.session_state.pdf_messages = []
            st.rerun()

        # Display PDF Q&A Chat History
        for message in st.session_state.pdf_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat input for PDF questions
        if pdf_query := st.chat_input("Ask a question about this PDF..."):
            st.session_state.pdf_messages.append({"role": "user", "content": pdf_query})
            with st.chat_message("user"):
                st.markdown(pdf_query)

            # Build Simple RAG Prompt
            rag_prompt = f"Context from uploaded PDF document:\n{pdf_text[:12000]}\n\nUser Question: {pdf_query}\nAnswer accurately and concisely based on the PDF context."
            
            with st.chat_message("assistant"):
                with st.spinner("Analyzing PDF and generating answer..."):
                    response = model.invoke([HumanMessage(content=rag_prompt)])
                    st.markdown(response.content)
            
            st.session_state.pdf_messages.append({"role": "assistant", "content": response.content})
    else:
        st.info("Please upload a PDF file above to start asking questions.")
