# app.py
import streamlit as st
import html
from llm import init_client, claim_config, fc_config
from youtube_transcript_api import YouTubeTranscriptApi
import json

# Add CSS styles for highlights
css = """
<style>
.highlight {
    background-color: #F6BE00;
    border-bottom: 2px solid #B58B00;
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
    # Build HTML with highlighted claims
    start = original_text.lower().find(claim.lower())
    end = start + len(claim)
    html_parts = []

    # Add preceding text
    html_parts.append(html.escape(original_text[currentIdx:start]))

    # Add highlighted claim
    claim_text = html.escape(original_text[start:end])
    html_parts.append(
        f'<span class="highlight">{claim_text}'
        f'<span class="tooltip">{result}</span></span>'
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


# Text input options
input_method = st.radio(
    "Choose input method:",
    ("Upload Text File", "Type Text", "YouTube Video Transcription"),
)

user_text = ""
youtube_url = ""
if input_method == "Upload Text File":
    uploaded_file = st.file_uploader("Upload text file", type=["txt"])
    if uploaded_file:
        user_text = uploaded_file.read().decode("utf-8")
elif input_method == "Type Text":
    user_text = st.text_area("Enter your text here:", height=200)
elif input_method == "YouTube Video Transcription":
    youtube_url = st.text_input("Enter the YouTube video URL:")

if input_method == "YouTube Video Transcription":
    if youtube_url.strip():
        with st.spinner("Transcribing YouTube video..."):
            transcript = extract_transcript(youtube_url)
        if transcript:
            user_text = transcript  # Use the transcript as the text to process
        else:
            st.error("Could not retrieve transcript from the provided URL.")
            st.stop()
    else:
        st.warning("Please enter a valid YouTube video URL.")
        st.stop()

# Process text when button is clicked
if st.button("Modify Text") and user_text.strip():
    client = init_client()
    try:
        with st.spinner("Modifying text with Gemini..."):
            print("Testing first gemini")
            result = client.models.generate_content(
                model="gemini-2.0-flash-exp", contents=user_text, config=claim_config
            )
            claims = json.loads(result.text)["claims"]
            print(result.text)
            st.subheader("Modified Text")
            currentIdx = 0

            print("Fact checking claims")
            # Analyze each claim
            for claim in claims:
                claim_result = client.models.generate_content(
                    model="gemini-2.0-flash-exp", contents=claim, config=fc_config
                )
                print(claim_result)
                currentIdx, highlighted_html = highlight_claim(
                    user_text.strip(),
                    claim,
                    json.loads("\n".join(claim_result.text.splitlines()[1:-1])),
                    currentIdx,
                )
                if highlighted_html:
                    st.markdown(highlighted_html, unsafe_allow_html=True)
                else:
                    st.write("Original text:", user_text)

            st.markdown(html.escape(user_text.strip()[currentIdx:]))

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

elif user_text.strip():
    st.warning("Click the 'Modify Text' button to process your input")
