# app.py

import streamlit as st
import requests
import io
import time
import os
from PIL import Image
from dotenv import load_dotenv

# Load the Hugging Face token from .env file
load_dotenv()
API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")

# Set up API URL and headers
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-3.5-large-turbo"
headers = {"Authorization": f"Bearer {API_TOKEN}"}

# Function to send prompt to Hugging Face and get back image bytes
def query(payload, retries=5, delay=5):
    for i in range(retries):
        try:
            start_time = time.time()
            response = requests.post(API_URL, headers=headers, json=payload)
            response.raise_for_status()
            st.success(f"Image generated in {time.time() - start_time:.2f} seconds")
            return response.content
        except requests.exceptions.RequestException as e:
            if response.status_code == 503 and i < retries - 1:
                st.warning(f"Model loading... Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                raise e

# Convert image bytes to a PIL Image object
def generate_image(prompt):
    image_bytes = query({"inputs": prompt})
    try:
        return Image.open(io.BytesIO(image_bytes))
    except Exception as e:
        st.error("Failed to convert response to image.")
        st.text(image_bytes[:200])
        raise e

# ------------------------
# Set up the Streamlit page
# ------------------------
st.set_page_config(page_title="AI Image Generator", layout="centered")
st.title("🎨 AI Image Generator")

st.write("Choose a style and prompt to generate a custom AI image!")

# -------------------
# Define styles
# -------------------
style_prompts = {
    "🖤 B/W Graphic Novel": "black-and-white animation sketch style with sharp marks",
    "🍂 Earthy Cartoon": "simple animation cartoon with white outline, earthy tones, yellow, orange",
    "🖌️ Watercolor": "watercolor painting with soft edges, natural brushstrokes, subtle gradients",
    "📸 Photorealistic Render": "photorealistic render with sharp details and realistic lighting",
    "🌈 Surreal Dreamscape": "surreal dreamlike scene with vibrant colors, impossible structures",
    "🌌 Sci‑fi Concept Art": "futuristic sci-fi digital concept art with dramatic lighting and cool tones"
}

# ---------------------------
# Session State Initialization
# ---------------------------
if "selected_style" not in st.session_state:
    st.session_state.selected_style = list(style_prompts.keys())[0]

if "user_prompt" not in st.session_state:
    st.session_state.user_prompt = ""

if "generated_image" not in st.session_state:
    st.session_state.generated_image = None

if "caption" not in st.session_state:
    st.session_state.caption = ""

# -------------------
# Style selection
# -------------------
st.markdown("**🎨 Choose a style:**")
style_cols = st.columns(3)
for i, label in enumerate(style_prompts.keys()):
    if style_cols[i % 3].button(label):
        st.session_state.selected_style = label  # Remember the selection

# Show the currently selected style
st.info(f"Current style: {st.session_state.selected_style}")

# -------------------
# Prompt Entry
# -------------------
example_prompts = [
    "a whale leaping over the moon",
    "a majestic lion with a flowing mane, digital art",
    "a landscape with a waterfall and mountains, fantasy art",
    "a princess watching a cruise ship in the distance, fantasy art",
    "a colorful frosted cupcake sitting on a bakery counter",
    "beagle and a duck sitting by a picnic basket"
]

prompt_options = example_prompts + ["Custom..."]
selected_prompt_option = st.selectbox(
    "📝 Select an example prompt or choose 'Custom...'",
    options=prompt_options,
    index=0
)

# Show text box if "Custom..." is selected
if selected_prompt_option == "Custom...":
    st.session_state.user_prompt = st.text_input(
        "✏️ Enter your custom prompt:",
        value=st.session_state.user_prompt
    )
else:
    st.session_state.user_prompt = selected_prompt_option

# -------------------
# Generate Image Button
# -------------------
if st.button("🚀 Generate Image"):
    prompt_text = st.session_state.user_prompt.strip()
    if not prompt_text:
        st.warning("Please enter a prompt first.")
    else:
        full_prompt = f"{style_prompts[st.session_state.selected_style]} of {prompt_text}"
        with st.spinner("Generating image..."):
            try:
                # Save image and caption in session_state so it persists
                img = generate_image(full_prompt)
                st.session_state.generated_image = img
                st.session_state.caption = f"{prompt_text} — {st.session_state.selected_style}"
            except Exception as e:
                st.error(f"Image generation failed: {e}")

# -------------------
# Display Generated Image (if available)
# -------------------
if st.session_state.generated_image:
    st.image(
        st.session_state.generated_image,
        caption=st.session_state.caption,
        use_column_width=True
    )

    # -------------------
    # Add Download Button
    # -------------------
    # Convert image to bytes in memory
    buffer = io.BytesIO()
    st.session_state.generated_image.save(buffer, format="PNG")
    img_bytes = buffer.getvalue()

    st.download_button(
        label="⬇️ Download Image",
        data=img_bytes,
        file_name="generated_image.png",
        mime="image/png"
    )
