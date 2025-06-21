

# Import Libraries
import streamlit as st
import requests
from dotenv import load_dotenv
import os
import io 
import time
import random # for random prompt selection
from PIL import Image # Pillow (PIL) Image module


# --- API Setup --- Authorization
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-3.5-large-turbo"
load_dotenv()
API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")
headers = {"Authorization": f"Bearer {API_TOKEN}"}



# --- Core Function to Query Model ---
def query(payload, retries=5, delay=5): # Added retries and delay parameters
    for i in range(retries):
      try:
        start_time = time.time()  # Record the start time
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status() # Raise an exception for bad status codes
        end_time = time.time()  # Record the end time
        generation_time = end_time - start_time  # Calculate the generation time
        print(f"Image generated in {generation_time:.2f} seconds")  # Print the time
        return response.content # capture response from server
      except requests.exceptions.RequestException as e:
        if response.status_code != 200: # report failed executions
          if response.status_code == 503 and i < retries - 1:
            # If 503 and not the last retry, attempt retry after delay
            print(f"Model loading... Retrying in {delay} seconds...")
            time.sleep(delay) # Pause before retrying
      else:
        raise Exception(f"API request failed with status {response.status_code}: {response.text}")



# --- Image Generation Function ---
#function to generate an image based on the given text prompt
def generate_image(prompt):
  image_bytes = query({"inputs": prompt})
  
  # Check if the response looks like an image
  try:
      image = Image.open(io.BytesIO(image_bytes))
      return image
  except Exception as e:
      print("Failed to identify image. Possibly received non-image content.")
      print("Response preview (first 200 bytes):", image_bytes[:200])
      raise e

#prompt to add a specific style to the output
style_prompt = "simple animation cartoon with a white outline utilizing earthy tones, yellow, and orange"



# --- Prompt Options ---
# Example usage with random prompt selection
example_prompts = [
    "of a whale leaping over the moon",
    "a majestic lion with a flowing mane, digital art",
    "landscape with a waterfall and mountains, fantasy art",
    "a princess watching a cruise ship in the distance, fantasy art",
    "colforful frosted cupcake sitting on a bakery counter"
]

# Randomly select a prompt from the list
selected_prompt = style_prompt + " of " + random.choice(example_prompts)
print(f"Selected prompt: {selected_prompt}")  # Print the selected prompt

image = generate_image(selected_prompt)

# For local development and testing, dispaly image
#if image:
#  image.show() # Display the image (within an external window using system's default image viewer)
#else:
#  print("Failed to generate or load image.")



# --- Streamlit UI ---
st.title("🖼️ AI Image Generator (via Hugging Face)")
st.write("Generate AI images with a predefined artistic style using Stable Diffusion.")

# Prompt input options
prompt_choice = st.selectbox("Choose a prompt or type your own:", ["🔀 Random"] + example_prompts)
custom_prompt = st.text_input("Or write your own idea:")

if prompt_choice == "🔀 Random":
    base_prompt = random.choice(example_prompts)
elif prompt_choice:
    base_prompt = prompt_choice
else:
    base_prompt = ""

# Final combined prompt (style + user prompt)
core_prompt = custom_prompt if custom_prompt else base_prompt
final_prompt = style_prompt + " " + core_prompt

if st.button("🎨 Generate Image"):
    if core_prompt.strip():
        st.info(f"Generating: **{core_prompt}**")
        with st.spinner("Generating image..."):
            try:
                image = generate_image(final_prompt)
                st.image(image, caption=core_prompt)
            except Exception as e:
                st.error(f"Generation failed: {e}")
    else:
        st.warning("Please select or enter a prompt.")
