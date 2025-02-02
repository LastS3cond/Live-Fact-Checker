# app.py
import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# Set up page configuration
st.set_page_config(page_title="Live Fact Check", page_icon="✨")

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
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
FACT_CHECK_PROMPT = """You will be given a list of claims, with each claim 
contained in the tags <claim claimIdx = X, claimPos = Y, claimLen = Z> </claim>. Your job is 
to use search engines to determine the truth value, bias in terms of left/right, 
relative harm, and hate of a the claim as best you can. Any sources used for the 
truth value should be cited. The format should be in a json object, with each claim
in json, like {claim:[claim text with no tags], claimIdx = [numIdx], claimPos = [numPos], claimLen = [claimLen],
truthVal = [truthVal], bias = [bias], harm = [harm]}. The accepted values for truthVal
are "Certainly False", "Somewhat False", "Neutral/Ambiguous", "Somewhat True", 
"Certainly True". The accepted values for bias are "Right Bias", "Slight Right Bias", 
"Neutral/Ambiguous", "Slight Left Bias", "Left Bias". The accepted values for harm
are "Extremely harmful to [groups harmed]", "Harmful to [groups harmed]", 
"Somewhat Harmful to [groups harmed]", "Slightly Harmful to [groups harmed]",
"Harmful to no groups". Do not modify the claimIdx, claim text (other than removing the tags), or claimPos"""

# Initialize Gemini model
def initialize_model(system_prompt):
    genai.configure(api_key=GOOGLE_API_KEY)
    return genai.GenerativeModel('gemini-1.5-flash', system_instruction=system_prompt)

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
    sentence = ''

    while i < len(user_text):
        if cap_sentence == True:
            sentence += user_text[i]

        if user_text[i] == '>' and i-6 and user_text[i-6] != '/':
            cap_sentence = True
            currentTextIndex = i
    
        if cap_sentence == True and user_text[i] == '<':
            #sentence += user_text[i]
            cap_sentence == False
            claims.append((sentence, currentTextIndex, i - currentTextIndex))
            currentClaimNum += 1
            sentence = ''
        i += 1
    return claims 

import streamlit as st
import html

def highlight_claims(original_text, claims):
    # Sort claims by position and check for overlaps
    sorted_claims = sorted(claims, key=lambda x: x['claimPos'])
    for i in range(1, len(sorted_claims)):
        prev_end = sorted_claims[i-1]['claimPos'] + sorted_claims[i-1]['claimLen']
        if sorted_claims[i]['claimPos'] < prev_end:
            st.error("Error: Overlapping claims detected")
            return None

    # Build HTML with highlighted claims
    html_parts = []
    current_pos = 0
    
    for claim in sorted_claims:
        start = claim['claimPos']
        end = start + claim['claimLen']
        
        # Add preceding text
        html_parts.append(html.escape(original_text[current_pos:start]))
        
        # Add highlighted claim
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

    # Add remaining text
    html_parts.append(html.escape(original_text[current_pos:]))
    
    return css + "".join(html_parts)


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
        model = initialize_model(CLAIM_PROMPT)
        print("testing gemini")
        with st.spinner("Modifying text with Gemini..."):
            response = model.generate_content(user_text)
            modified_text = response.text

            claims = record_claims(modified_text)
            print(claims)
            model = initialize_model(FACT_CHECK_PROMPT)
            claimInfo = model.generate_content(claims)
            st.subheader("Modified Text")
            highlighted_html = highlight_claims(user_text.strip(), claimInfo)
            if highlighted_html:
                st.markdown(highlighted_html, unsafe_allow_html=True)
            else:
                st.write("Original text:", modified_text)
            
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

elif user_text.strip():
    st.warning("Click the 'Modify Text' button to process your input")


        

        

