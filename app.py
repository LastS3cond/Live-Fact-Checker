# app.py
import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# Set up page configuration
st.set_page_config(page_title="Live Fact Check", page_icon="✨")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    st.error("❌ Google API key not found in .env file")
    st.stop()

# Main interface
st.title("📝 Text Modifier with Gemini")
st.write("Upload a text file or enter text to modify it using Gemini!")

# Add CSS styles
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

# System prompt (hidden from user but can be modified in code)
CLAIM_PROMPT = """Your task is to parse a speech, and you are 
going to identify any claims made within the speech that assert 
some fact which can be fact-checked using external resources. The 
claims may or may not be true, however you are not going to determine 
the validity of the truth. You must wrap any claims with a <claim></claim> 
tag. For all speakers, try to infer their names and if no name can be 
inferred, call them by Speaker #X. Separate each speaker\u0027s transcript 
with [Speaker name]: [Speaker text]."""

# System prompt (hidden from user but can be modified in code)
FACT_CHECK_PROMPT = """You will be given a claim. Your job is 
to use web search to determine the truth value and relative harm of the given claim. Any sources used for the 
truth value should be cited. Your output should be a truth value seperated by a line, harm value 
separated by a line and a short paragraph explaining your decision. The accepted values for the truth
are "Certainly False", "Somewhat False", "Neutral/Ambiguous", "Somewhat True", "Certainly True". 
The accepted values for harm are "Extremely harmful to [groups harmed]", "Harmful to [groups harmed]", 
"Somewhat Harmful to [groups harmed]", "Slightly Harmful to [groups harmed]",
"Harmful to no groups".
"""

genai.configure(api_key=GOOGLE_API_KEY)


# Initialize Gemini model
def init_claim_model(system_prompt):
    return genai.GenerativeModel("gemini-1.5-flash", system_instruction=system_prompt)


def init_fact_check_model(system_prompt):
    return genai.GenerativeModel(
        "gemini-1.5-flash",
        system_instruction=system_prompt,
        tools="google_search_retrieval",
    )


# currentClaimNum should be global variable that get incremented everytime we add a claim
# currentTextIndex should be index where the <claim> starts.
# Test this with streamlit run app.py
# claims = [("[txt]", currentClaimNum, currentTextIndex, currentLen), ....]
def record_claims(user_text):
    currentClaimNum = 0
    currentTextIndex = 0
    claims = []
    i = 0
    cap_sentence = False
    sentence = ""

    while i < len(user_text):
        if cap_sentence == True and user_text[i] == "<":
            # sentence += user_text[i]
            cap_sentence = False
            claims.append((sentence, currentTextIndex, i - currentTextIndex))
            currentClaimNum += 1
            sentence = ""

        if cap_sentence == True:
            sentence += user_text[i]

        if user_text[i] == ">" and i - 6 and user_text[i - 6] != "/":
            cap_sentence = True
            currentTextIndex = i

        i += 1
    return claims


import streamlit as st
import html


def highlight_claim(original_text, claim, result):
    lines = claim.splitlines()
    truth = lines[0]
    harm = lines[1]

    # Build HTML with highlighted claims
    html_parts = []
    current_pos = 0

    start = claim["claimPos"]
    end = start + claim["claimLen"]

    # Add preceding text
    html_parts.append(html.escape(original_text[current_pos:start]))

    # Add highlighted claim
    claim_text = html.escape(original_text[start:end])
    tooltip = f"Truth: {truth}<br>Bias: {harm}<br>"
    html_parts.append(
        f'<span class="highlight">{claim_text}'
        f'<span class="tooltip">{tooltip}</span></span>'
    )
    current_pos = end

    # Add remaining text
    html_parts.append(html.escape(original_text[current_pos:]))

    return css + "".join(html_parts)


# Text input options
input_method = st.radio("Choose input method:", ("Upload Text File", "Type Text"))

user_text = ""
if input_method == "Upload Text File":
    uploaded_file = st.file_uploader("Upload text file", type=["txt"])
    if uploaded_file:
        user_text = uploaded_file.read().decode("utf-8")
else:
    user_text = st.text_area("Enter your text here:", height=200)

# Process text when button is clicked
if st.button("Modify Text") and user_text.strip():
    try:
        model = init_claim_model(CLAIM_PROMPT)
        print("testing gemini")
        with st.spinner("Modifying text with Gemini..."):
            response = model.generate_content(user_text)
            modified_text = response.text

            claims = record_claims(modified_text)
            print(claims)

            # Analyze each claim
            for claim in claims:
                model = init_fact_check_model(FACT_CHECK_PROMPT)
                claim_result = model.generate_content(claim)
                print(claim_result)

                st.subheader("Modified Text")
                highlighted_html = highlight_claim(
                    user_text.strip(), claim, claim_result
                )
                if highlighted_html:
                    st.markdown(highlighted_html, unsafe_allow_html=True)
                else:
                    st.write("Original text:", modified_text)

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

elif user_text.strip():
    st.warning("Click the 'Modify Text' button to process your input")
