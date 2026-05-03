import streamlit as st
from youtube_analyzer import build_youtube_agent, analyze_video, extract_video_id, get_video_metadata

st.set_page_config(
    page_title="YouTube Video Analyzer",
    layout="centered"
)

st.title("🎬 AI YouTube Video Analyzer")

@st.cache_resource
def get_agent():
    return build_youtube_agent()

agent = get_agent()

video_url = st.text_input("🔗 Enter YouTube Video URL")

if st.button("🚀 Analyze Video"):

    if not video_url:
        st.warning("Please enter a valid URL")

    else:
        video_id = extract_video_id(video_url)

        if not video_id:
            st.error("Invalid YouTube URL")
        else:
            # -------------------------------
            # 🎥 Show Video Preview
            # -------------------------------
            metadata = get_video_metadata(video_id)

            if metadata:
                st.image(metadata["thumbnail"], use_container_width=True)
                st.markdown(f"### {metadata['title']}")
                st.markdown(f"👤 {metadata['author']}")
            else:
                st.info("Could not fetch video details")

            st.divider()

            # -------------------------------
            # 🤖 Analysis
            # -------------------------------
            with st.spinner("Analyzing video..."):
                result = analyze_video(agent, video_url)

            st.markdown("## 📊 Analysis Result")
            st.markdown(result)