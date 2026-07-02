import streamlit as st
from PIL import Image

def render_vision_studio(genai_client):
    st.title("🖼️ Vision Studio (Image to Prompt)")
    st.markdown("Upload any picture to generate descriptive AI prompts or ask questions about the image.")

    uploaded_image = st.file_uploader("Upload an Image", type=["jpg", "jpeg", "png"])

    if uploaded_image is not None:
        try:
            image = Image.open(uploaded_image)
            
            # Show image preview
            st.image(image, caption="Uploaded Image Preview", use_container_width=True)
            
            st.divider()
            
            # Columns for Image to Prompt and Visual Q&A
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("✨ Image to Prompt")
                st.markdown("Describe this image in detail so you can use it to recreate or style similar images.")
                if st.button("Generate Art Prompt", type="primary", use_container_width=True):
                    with st.spinner("Analyzing image details..."):
                        try:
                            response = genai_client.models.generate_content(
                                model='gemini-2.5-flash',
                                contents=[
                                    image,
                                    "Provide a detailed, highly descriptive prompt that describes the subject, style, lighting, art medium, and color palette of this image. The output should be optimized to be copied directly as a prompt for a text-to-image generator. Output ONLY the prompt itself."
                                ]
                            )
                            st.success("Prompt Generated Successfully!")
                            st.text_area("Copy this prompt:", value=response.text, height=150)
                        except Exception as e:
                            st.error(f"Error generating prompt: {e}")
            
            with col2:
                st.subheader("💬 Visual Q&A")
                st.markdown("Ask anything about this picture (e.g. object locations, text, emotions, colors).")
                user_question = st.text_input("What would you like to know about this image?", placeholder="e.g. What is written on the sign? What style of painting is this?")
                
                if st.button("Ask AI about Image", use_container_width=True):
                    if not user_question.strip():
                        st.warning("Please enter a question first!")
                    else:
                        with st.spinner("Analyzing image details to answer..."):
                            try:
                                response = genai_client.models.generate_content(
                                    model='gemini-2.5-flash',
                                    contents=[image, user_question]
                                )
                                st.info(response.text)
                            except Exception as e:
                                st.error(f"Error answering question: {e}")
        except Exception as e:
            st.error(f"Error loading image: {e}")
    else:
        st.info("Please upload an image (JPG, JPEG, or PNG) above to begin.")
