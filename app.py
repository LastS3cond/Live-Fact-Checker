# app.py
import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# Set up page configuration
st.set_page_config(page_title="Text Modifier with Gemini", page_icon="✨")

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    st.error("❌ Google API key not found in .env file")
    st.stop()

# Main interface
st.title("📝 Text Modifier with Gemini")
st.write("Upload a text file or enter text to modify it using Gemini!")

# System prompt (hidden from user but can be modified in code)
SYSTEM_PROMPT = """Your task is to parse a speech, and you are 
going to identify any claims made within the speech that assert 
some fact which can be fact-checked using external resources. The 
claims may or may not be true, however you are not going to determine 
the validity of the truth. You must wrap any claims with a <claim></claim> 
tag. For all speakers, try to infer their names and if no name can be 
inferred, call them by Speaker #X. Separate each speaker\u0027s transcript 
with [Speaker name]: [Speaker text]."""

# Initialize Gemini model
def initialize_model():
    genai.configure(api_key=GOOGLE_API_KEY)
    return genai.GenerativeModel('gemini-1.5-flash', system_instruction=SYSTEM_PROMPT)

# Text input options
input_method = st.radio("Choose input method:", ("Upload Text File", "Type Text"))

user_text = ""
if input_method == "Upload Text File":
    uploaded_file = st.file_uploader("Upload text file", type=['txt'])
    if uploaded_file:
        user_text = uploaded_file.read().decode("utf-8")
else:
    user_text = st.text_area("Enter your text here:", height=200)

# Process text when button is clicked
if st.button("Modify Text") and user_text.strip():
    
    try:
        model = initialize_model()
        with st.spinner("Modifying text with Gemini..."):
            response = model.generate_content(user_text)
            modified_text = response.text
            
            st.subheader("Modified Text")
            st.markdown(f"```\n{modified_text}\n```")
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

elif user_text.strip():
    st.warning("Click the 'Modify Text' button to process your input")