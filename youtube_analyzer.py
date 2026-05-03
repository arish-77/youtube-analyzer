from dotenv import load_dotenv
import os
import time
import requests
from agno.agent import Agent
from agno.models.openai import OpenAIResponses
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
from urllib.parse import urlparse, parse_qs
load_dotenv()


# ✅ Build agent ONLY
def build_youtube_agent():
    return Agent(
        name="YouTube Agent",
        model=OpenAIResponses(
            id="llama-3.1-8b-instant",
            base_url="https://api.groq.com/openai/v1",
            api_key=os.getenv("GROQ_API_KEY"),
        ),
        markdown=True,
    )


def extract_video_id(url):
    parsed = urlparse(url)

    if "youtube.com" in parsed.netloc:
        return parse_qs(parsed.query).get("v", [None])[0]
    elif "youtu.be" in parsed.netloc:
        return parsed.path.lstrip("/")
    return None


def get_video_metadata(video_id):
    try:
        url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
        res = requests.get(url)
        data = res.json()

        return {
            "title": data.get("title"),
            "author": data.get("author_name"),
            "thumbnail": data.get("thumbnail_url")
        }
    except:
        return None

# ✅ Main analyzer function
def analyze_video(agent, video_url: str):
    try:
        video_id = extract_video_id(video_url)

        if not video_id:
            return "❌ Invalid YouTube URL"

        # -------------------------------
        # Try Transcript
        # -------------------------------
        try:
            api = YouTubeTranscriptApi()
            transcript_list = api.list(video_id)

            try:
                transcript = transcript_list.find_transcript(['en'])
            except:
                transcript = transcript_list.find_generated_transcript(['en'])

            data = transcript.fetch()
            full_text = " ".join([t.text for t in data])

        except Exception:
            # 🔥 FALLBACK (THIS IS THE KEY FIX)
            response = agent.run(f"""
            Analyze this YouTube video:

            {video_url}

            Return:
            ## Summary
            ## Key Points
            ## Insights
            ## Final Takeaway
            """)
            return response.content

        # -------------------------------
        # Continue normal flow
        # -------------------------------
        def chunk_text(text, chunk_size=3000):
            return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

        chunks = chunk_text(full_text)

        summaries = []
        for chunk in chunks:
            response = agent.run(f"Summarize:\n{chunk}")
            summaries.append(response.content)

        combined = "\n".join(summaries)

        final_response = agent.run(f"""
        Combine into final structured analysis:

        {combined}

        Return:
        ## Summary
        ## Key Points
        ## Insights
        ## Final Takeaway
        """)

        return final_response.content

    except Exception as e:
        return f"❌ Error: {str(e)}"