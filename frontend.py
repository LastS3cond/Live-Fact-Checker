# frontend.py
import streamlit as st
import subprocess
import json

# Set up page configuration
st.set_page_config(page_title="Live Fact Checker", page_icon="✨")

# Title and description
st.title("📝 Live Fact Checker with Gemini")
st.write("Upload a text file or enter text to modify and fact-check using Gemini!")

# Add CSS styles for highlights
css = """
<style>
.highlight {
    background-color: #fff3cd;
    border-bottom: 2px solid #ffc107;
    cursor: help;
    position: relative;
    display: inline-block;
}

.highlight .tooltip {
    visibility: hidden;
    background-color: #333;
    color: #fff;
    padding: 8px;
    border-radius: 4px;
    position: absolute;
    z-index: 1000;
    bottom: 125%;
    left: 50%;
    transform: translateX(-50%);
    width: max-content;
    max-width: 300px;
    opacity: 0;
    transition: opacity 0.3s;
    font-size: 14px;
    text-align: left;
    pointer-events: none;
}

.highlight:hover .tooltip {
    visibility: visible;
    opacity: 1;
}
</style>
"""

# Display the CSS on the page
st.markdown(css, unsafe_allow_html=True)

# Text input options
input_method = st.radio("Choose input method:", ("Upload Text File", "Type Text"))

user_text = ""
if input_method == "Upload Text File":
    uploaded_file = st.file_uploader("Upload a text file", type=['txt'])
    if uploaded_file:
        user_text = uploaded_file.read().decode("utf-8")
else:
    user_text = st.text_area("Enter your text here:", height=200)

# Process text when button is clicked
if st.button("Modify Text") and user_text.strip():
    try:
        with st.spinner("Modifying text with Gemini..."):
            # Call app.py via subprocess
            result = subprocess.run(
                ['python3', 'app.py', user_text],
                capture_output=True,
                text=True
            )

            # Parse the JSON output from app.py
            result_data = json.loads(result.stdout)

            modified_text = result_data["modified_text"]
            fact_check_results = result_data["fact_check_results"]

            # Display the modified text and claims
            st.subheader("Modified Text")
            st.write(modified_text)

            st.subheader("Fact Check Results")
            for fact in fact_check_results:
                st.write(f"Claim: {fact['claim']}")
                st.write(f"Truth Value: {fact['truthVal']}")
                st.write(f"Bias: {fact['bias']}")
                st.write(f"Harm: {fact['harm']}")

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

elif user_text.strip():
    st.warning("Click the 'Modify Text' button to process your input")