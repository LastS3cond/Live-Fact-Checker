# app.py
import streamlit as st
import html
import google.generativeai as genai
from llm import init_claim_model, init_fact_check_model
import json

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
    # Build HTML with highlighted claims
    start = original_text.find(claim)
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
        model = init_claim_model()
        print("testing gemini")
        with st.spinner("Modifying text with Gemini..."):
            result = model.generate_content(
                user_text,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    response_schema={
                        "type": "object",
                        "properties": {
                            "claims": {"type": "array", "items": {"type": "string"}}
                        },
                        "required": ["claims"],
                    },
                ),
            )
            claims = json.loads(result.text)["claims"]
            print(claims)
            st.subheader("Modified Text")
            currentIdx = 0
            # Analyze each claim
            for claim in claims:
                model2 = init_fact_check_model()
                # claim_result = model2.generate_content(claim)

                currentIdx, highlighted_html = highlight_claim(
                    user_text.strip(), claim, "", currentIdx
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


def extract_transcript(youtube_video_url):
    video_id = youtube_video_url.split("=")[1]
    transcript_text = YouTubeTranscriptApi.get_transcript(video_id)
    transcript = ""
    for i in transcript_text:
        transcript += " " + i["text"]
    return transcript
