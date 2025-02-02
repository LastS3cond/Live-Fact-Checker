# frontend.py
import streamlit as st
from app import process_text  # Import the backend function

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
            modified_text, claim_info = process_text(user_text)
            
            # Highlight the modified text with claims
            st.subheader("Modified Text")
            highlighted_html = highlight_claims(user_text.strip(), claim_info)
            if highlighted_html:
                st.markdown(highlighted_html, unsafe_allow_html=True)
            else:
                st.write("Original text:", modified_text)
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

elif user_text.strip():
    st.warning("Click the 'Modify Text' button to process your input")

# Function to highlight claims in the text
def highlight_claims(original_text, claims):
    sorted_claims = sorted(claims, key=lambda x: x['claimPos'])
    html_parts = []
    current_pos = 0
    
    for claim in sorted_claims:
        start = claim['claimPos']
        end = start + claim['claimLen']
        html_parts.append(html.escape(original_text[current_pos:start]))
        
        claim_text = html.escape(original_text[start:end])
        tooltip = (
            f"Truth: {claim['truthVal']}<br>"
            f"Bias: {claim['bias']}<br>"
            f"Harm: {claim['harm']}<br>"
            f"Position: {start}<br>"
            f"Length: {claim['claimLen']}"
        )
        html_parts.append(
            f'<span class="highlight">{claim_text}'
            f'<span class="tooltip">{tooltip}</span></span>'
        )
        current_pos = end

    html_parts.append(html.escape(original_text[current_pos:]))
    return "".join(html_parts)