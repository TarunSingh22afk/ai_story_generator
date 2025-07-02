import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_KEY = os.getenv("IBM_API_KEY")
PROJECT_ID = os.getenv("PROJECT_ID")
REGION = os.getenv("REGION", "us-south")
MODEL_ID = os.getenv("MODEL_ID", "bigscience/bloomz-7b1")  # More generative model than flan-ul2
VERSION = "2023-05-29"

# Get IAM token
@st.cache_data(ttl=3000)
def get_iam_token(api_key):
    url = "https://iam.cloud.ibm.com/identity/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
        "apikey": api_key
    }
    response = requests.post(url, headers=headers, data=data)
    return response.json().get("access_token")

# Generate story using legacy v1 endpoint
def generate_story(prompt, token, story_length):
    url = f"https://{REGION}.ml.cloud.ibm.com/ml/v1/text/generation?version={VERSION}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "model_id": MODEL_ID,
        "project_id": PROJECT_ID,
        "input": f"Write a detailed, imaginative short story (200+ words) based on the following idea:\n\n{prompt}",
        "parameters": {
            "temperature": 0.8,
            "max_new_tokens": story_length,
            "top_k": 50,
            "top_p": 0.95,
            "decoding_method": "sample"
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    try:
        return response.json()["results"][0]["generated_text"]
    except Exception:
        return f"❌ API Error: {response.text}"

# Streamlit UI
st.set_page_config(page_title="AI Story Generator (Watsonx v1)", page_icon="📘")
st.title("📘 AI Story Generator (IBM Watsonx)")

prompt = st.text_input("Enter a story prompt", placeholder="e.g., A robot explores a hidden AI city in the jungle")
story_length = st.slider("Story Length (tokens)", 100, 800, 300)

if st.button("Generate Story"):
    if not prompt.strip():
        st.warning("Please enter a prompt.")
    else:
        with st.spinner("Generating your story..."):
            token = get_iam_token(API_KEY)
            story = generate_story(prompt, token, story_length)
            st.markdown("### ✨ Your Story")
            st.write(story)
