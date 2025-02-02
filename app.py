import streamlit as st
import html
import re
from llm import (
    init_claim_model,
    init_fact_check_model,
)

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


def highlight_claim(original_text, claim, result, currentIdx):

    result_text = result.candidates[0].content.parts[0].text
    # Build HTML with highlighted claims

    start = original_text.find(claim)
    end = start + len(claim)
    html_parts = []

    # Append the text preceding the claim
    html_parts.append(html.escape(original_text[currentIdx:start]))

    # Append the highlighted claim with a tooltip showing the fact-check result
    claim_text = html.escape(original_text[start:end])
    # html_parts.append(
    #     f'<span class="highlight">{claim_text}'
    #     f'<span class="tooltip">{result}</span></span>'
    # )

    html_parts.append(
        f'<span class="highlight">{claim_text}'
        f'<span class="tooltip">{html.escape(result_text)}</span></span>'
    )

    return end, css + "".join(html_parts)

def extract_transcript(youtube_video_url):
    """
    Extracts the transcript from a YouTube video.
    
    Assumes a URL format like: https://www.youtube.com/watch?v=VIDEO_ID
    """
    try:
        # Extract video id from the URL (handles additional parameters)
        video_id = youtube_video_url.split("v=")[1]
        ampersand_position = video_id.find("&")
        if ampersand_position != -1:
            video_id = video_id[:ampersand_position]
        
        transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
        # Join all transcript parts into a single string
        transcript = " ".join([entry["text"] for entry in transcript_data])
        return transcript
    except Exception as e:
        st.error(f"Error extracting transcript: {e}")
        return ""

# -----------------------------------
# Input Options
# -----------------------------------
# Now we include a third option for YouTube Video Transcription.
input_method = st.radio(
    "Choose input method:",
    ("Upload Text File", "Type Text", "YouTube Video Transcription")
)

user_text = ""
youtube_url = ""
if input_method == "Upload Text File":
    uploaded_file = st.file_uploader("Upload text file", type=["txt"])
    if uploaded_file:
        user_text = uploaded_file.read().decode("utf-8")
elif input_method == "Type Text":
    user_text = st.text_area("Enter your text here:", height=200)

# Process text when button is clicked
if st.button("Modify Text") and user_text.strip():
    try:
        model = init_claim_model()
        print("testing gemini")
        with st.spinner("Modifying text with Gemini..."):
            response = model.generate_content(user_text)
            modified_text = response.text

            claims = record_claims(modified_text)
            print(claims)
            st.subheader("Modified Text")
            currentIdx = 0

            # Process each claim with the fact-check model
            for claim in claims:
                model2 = init_fact_check_model(FACT_CHECK_PROMPT)
                # Generate fact-check result for the claim
                claim_result = model2.generate_content(claim).text
                currentIdx, highlighted_html = highlight_claim(
                    user_text.strip(), claim, claim_result, currentIdx
                )
                if highlighted_html:
                    st.markdown(highlighted_html, unsafe_allow_html=True)
                else:
                    st.write("Original text:", modified_text)

            st.markdown(html.escape(user_text.strip()[currentIdx:]))
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    else:
        st.warning("Please provide some input before processing.")
