# Live-Fact-Checker (Hackviolet)

## Inspiration

With the rise of misinformation online, we wanted to build a tool that helps
people verify the accuracy of statements quickly. Whether it’s a speech, a news
report, a viral video, or just some text we aimed to create an AI fact checking
assistant that allows users to easily identify false or misleading claims.

## What it does

The AI fact checker allows users to input either text or a YouTube URL. If a
video is provided, the tool automatically transcribes the speech. Then, it
analyzes the text to identify claims using Gemini’s API. Then we highlight these
claims in the displayed content. Users can hover over each highlighted claim to
see whether it is true or false and also read background information about it.

## How we built it

We used Streamlit for the frontend of this project and we have a simple and
interactive interface where users can input text or a YouTube URL. To process
videos, we integrated the YouTube API, which automatically retrieves the
transcript of the video. Once we get the text, we use Gemini’s API to analyze
the text and identify all of the claims. Each claim is highlighted in the
displayed text, allowing users to quickly these statements. We then use the same
API to fact check those claims by searching for reliable sources and providing
context on their accuracy. When a user hovers over a highlighted claim, they can
see whether it is true or false and background information about the claim as
well as sources if possible.

## Challenges we ran into

Initially we wanted to do the fact checking live; however, we realized that
would be a very ambitious step for a project that should be done in 24 hours. We
decided to just extract the transcript and do all the fact checking at once
where all the claims are congregated to make it simpler for us.

## Accomplishments that we're proud of

Accomplishments was successfully integrating YouTube video transcription. We
were trying to find ways to get transcripts of videos and happened to stumble
upon Youtube's API and it was big time saver. Another achievement we’re proud of
is the claim highlighting, which allows users to see key statements stand out in
the text. Overall, we are proud of how everything integrates to make fact
checking more accessible.

## What we learned

While most of our team was already familiar with the technologies we used since
we were using Python and Streamlit, this project still provided valuable
learning experiences for all of us. For one team member, Streamlit was a new
framework. The biggest learning curve for all of us was working with Gemini’s
API which we had to understand how to use it for both claim detection and fact
checking.

## What's next for AI Based Realtime Factchecking

In the future, we may go back to the original plan of doing real-time fact
checking as it could be done given we have more time. Another key improvement
would be expanding our data sources beyond Gemini’s API by using multiple fact
checking databases, such as PolitiFact or government and academic sources, to
improve accuracy and reliability.
