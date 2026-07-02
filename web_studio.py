import streamlit as st
import urllib.parse
import requests
import re
from langchain_core.messages import HumanMessage

def extract_youtube_transcript(url):
    """
    Extracts the transcript of a YouTube video using youtube-transcript-api.
    """
    # Highly robust regex to extract 11-character YouTube video ID
    regex = r'(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/|youtube\.com\/shorts\/)([^"&?\/\s]{11})'
    match = re.search(regex, url)
    video_id = match.group(1) if match else None

    if not video_id:
        raise ValueError("Could not extract a valid 11-character YouTube video ID from the provided link.")

    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        # Instantiate and fetch using the API instance
        api_instance = YouTubeTranscriptApi()
        transcript_list = api_instance.fetch(video_id)
        
        # Safely extract text from snippet objects or dictionaries
        snippets = []
        for item in transcript_list:
            if isinstance(item, dict):
                snippets.append(item.get("text", ""))
            else:
                snippets.append(getattr(item, "text", ""))
        
        transcript = " ".join(snippets)
        return transcript
    except Exception as e:
        error_name = type(e).__name__
        if "TranscriptsDisabled" in error_name:
            raise Exception("Subtitles/Transcripts are disabled for this YouTube video. Please try a video that has captions/subtitles enabled.")
        elif "NoTranscriptFound" in error_name:
            raise Exception("No transcript found in English or other auto-generated languages. Please try a different video.")
        elif "VideoUnavailable" in error_name or "InvalidVideoId" in error_name:
            raise Exception("This YouTube video is unavailable, private, or the link is invalid.")
        else:
            raise Exception(f"Failed to fetch YouTube transcript: {e}")

def extract_webpage_text(url):
    """
    Scrapes a webpage and extracts clean body text using BeautifulSoup.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Remove scripts, styles, navs and footers
        for element in soup(["script", "style", "nav", "footer", "header"]):
            element.decompose()
            
        text = soup.get_text(separator=" ")
        # Clean whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        cleaned_text = "\n".join(chunk for chunk in chunks if chunk)
        return cleaned_text
    except Exception as e:
        raise Exception(f"Failed to parse webpage content: {e}")

def render_web_studio(model, transcribe_audio):
    st.title("🌐 Link Chat (RAG)")
    st.markdown("Analyze any YouTube video transcript or website article and ask questions about its content.")

    # Initialize session state variables for this module
    if "web_messages" not in st.session_state:
        st.session_state.web_messages = []
    if "web_context" not in st.session_state:
        st.session_state.web_context = ""
    if "active_url" not in st.session_state:
        st.session_state.active_url = ""

    url_input = st.text_input("Enter Link (YouTube or Website):", placeholder="e.g. https://www.youtube.com/watch?v=... or https://example.com/article")

    if st.button("🚀 Analyze Link", type="primary"):
        if not url_input.strip():
            st.warning("Please enter a link first!")
        else:
            with st.spinner("Extracting contents from the link..."):
                try:
                    url = url_input.strip()
                    # Check if it is a YouTube link
                    if "youtube.com" in url or "youtu.be" in url:
                        content = extract_youtube_transcript(url)
                        source_type = "YouTube Video Transcript"
                    else:
                        content = extract_webpage_text(url)
                        source_type = "Webpage Article Text"
                    
                    if content and len(content.strip()) > 0:
                        st.session_state.web_context = content
                        st.session_state.active_url = url
                        # Reset history when loading a new link
                        st.session_state.web_messages = []
                        st.success(f"✅ Successfully analyzed {source_type}! ({len(content)} characters extracted)")
                    else:
                        st.error("Could not extract any content from the provided link.")
                except Exception as e:
                    st.error(f"Error: {e}")

    # If context exists, show RAG chat interface
    if st.session_state.web_context:
        st.divider()
        st.markdown(f"📍 **Currently chatting about:** *{st.session_state.active_url}*")
        
        # Show a preview of the content
        with st.expander("🔍 Show Extracted Content Preview"):
            st.write(st.session_state.web_context[:1000] + ("..." if len(st.session_state.web_context) > 1000 else ""))

        # Sidebar Voice Chat input
        st.sidebar.subheader("🎙️ Voice Chat")
        web_audio_file = st.sidebar.audio_input("Speak your question:", key="web_voice_input")
        
        if web_audio_file is not None:
            web_audio_key = f"{web_audio_file.name}_{web_audio_file.size}"
            if st.session_state.get("last_web_audio_key") != web_audio_key:
                st.session_state.last_web_audio_key = web_audio_key
                
                with st.spinner("Transcribing..."):
                    transcribed_text = transcribe_audio(web_audio_file)
                
                if transcribed_text:
                    st.session_state.web_messages.append({"role": "user", "content": transcribed_text})
                    
                    # Build prompt with context (limit to 12000 chars to avoid token limits)
                    rag_prompt = f"Context extracted from link:\n{st.session_state.web_context[:12000]}\n\nUser Question: {transcribed_text}\nAnswer accurately and concisely based on the context."
                    
                    with st.spinner("Analyzing context and generating answer..."):
                        response = model.invoke([HumanMessage(content=rag_prompt)])
                        st.session_state.web_messages.append({"role": "assistant", "content": response.content})
                    st.rerun()

        st.sidebar.divider()
        if st.sidebar.button("🗑️ Clear Link Chat History", use_container_width=True):
            st.session_state.web_messages = []
            st.rerun()

        # Display Chat History
        for message in st.session_state.web_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat Input
        if query := st.chat_input("Ask a question about this link..."):
            st.session_state.web_messages.append({"role": "user", "content": query})
            with st.chat_message("user"):
                st.markdown(query)

            # Build Prompt
            rag_prompt = f"Context extracted from link:\n{st.session_state.web_context[:12000]}\n\nUser Question: {query}\nAnswer accurately and concisely based on the context."
            
            with st.chat_message("assistant"):
                with st.spinner("Analyzing context and generating answer..."):
                    response = model.invoke([HumanMessage(content=rag_prompt)])
                    st.markdown(response.content)
            
            st.session_state.web_messages.append({"role": "assistant", "content": response.content})
    else:
        st.info("Please enter a link and analyze it above to begin chatting.")
