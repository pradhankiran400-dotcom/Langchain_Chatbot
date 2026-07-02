import streamlit as st
import urllib.parse
import requests

def render_art_studio(hf_token):
    st.title("🎨 AI Art Studio")
    st.markdown("Transform your creative text prompts into AI artwork.")

    # Select Generator Engine
    col_sel1, col_sel2 = st.columns(2)
    with col_sel1:
        engine = st.radio(
            "Select AI Generator Engine:",
            ["Pollinations AI (Fast, Free)", "Hugging Face Inference (High Quality)"]
        )
    
    selected_hf_model = "stabilityai/stable-diffusion-xl-base-1.0"
    if engine == "Hugging Face Inference (High Quality)":
        with col_sel2:
            selected_hf_model = st.selectbox(
                "Select Hugging Face Model:",
                [
                    "stabilityai/stable-diffusion-xl-base-1.0",
                    "runwayml/stable-diffusion-v1-5",
                    "black-forest-labs/FLUX.1-schnell"
                ],
                help="Choose a text-to-image model hosted on Hugging Face"
            )

    art_prompt = st.text_input("Describe the image you want to create:", placeholder="e.g., A futuristic cyberpunk city at sunset with neon lights")

    if st.button("✨ Generate Artwork", type="primary"):
        if not art_prompt.strip():
            st.warning("Please enter a description first!")
        else:
            with st.spinner("Crafting your visual masterpiece..."):
                if engine == "Pollinations AI (Fast, Free)":
                    url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(art_prompt)}"
                    img_response = requests.get(url)
                    if img_response.status_code == 200:
                        st.image(img_response.content, caption=art_prompt, use_container_width=True)
                        st.download_button(
                            label="📥 Download Artwork",
                            data=img_response.content,
                            file_name="generated_artwork.png",
                            mime="image/png"
                        )
                    else:
                        st.error("Failed to generate image via Pollinations AI. Please try again.")
                else:
                    # Hugging Face image generation
                    if not hf_token:
                        st.error("Please provide a Hugging Face API Token (either in the sidebar or in the .env file as HUGGINGFACEHUB_API_TOKEN).")
                    else:
                        api_url = f"https://api-inference.huggingface.co/models/{selected_hf_model}"
                        headers = {"Authorization": f"Bearer {hf_token}"}
                        try:
                            # Send request to Hugging Face
                            response = requests.post(api_url, headers=headers, json={"inputs": art_prompt})
                            
                            if response.status_code == 200:
                                content_type = response.headers.get("content-type", "")
                                if "image" in content_type:
                                    st.image(response.content, caption=art_prompt, use_container_width=True)
                                    st.download_button(
                                        label="📥 Download Artwork",
                                        data=response.content,
                                        file_name="huggingface_artwork.png",
                                        mime="image/png"
                                    )
                                else:
                                    # Might be a JSON response warning about loading
                                    try:
                                        res_json = response.json()
                                        if "error" in res_json:
                                            st.error(f"Hugging Face Error: {res_json['error']}")
                                            if "estimated_time" in res_json:
                                                st.warning(f"Model is currently loading. Estimated time: {res_json['estimated_time']:.1f} seconds. Please wait a bit and try again.")
                                        else:
                                            st.error("Unexpected response from Hugging Face.")
                                    except Exception:
                                        st.error(f"Hugging Face API returned non-image data: {response.text[:200]}")
                            elif response.status_code == 503:
                                # Model loading state
                                try:
                                    res_json = response.json()
                                    st.warning(f"Hugging Face Model is loading: {res_json.get('error', 'Please try again.')}")
                                    if "estimated_time" in res_json:
                                        st.info(f"Estimated time remaining: {res_json['estimated_time']:.1f} seconds.")
                                except Exception:
                                    st.warning("Model is currently loading or server is busy. Please try again in a few seconds.")
                            else:
                                st.error(f"Hugging Face API returned error status {response.status_code}: {response.text[:200]}")
                        except Exception as e:
                            st.error(f"Error querying Hugging Face API: {e}")
