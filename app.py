import streamlit as st
import engine
import os

# Premium color scheme styling via CSS
st.set_page_config(page_title="Guardian Chef Intelligence", layout="wide", page_icon="🍝")

st.markdown("""
    <style>
    .stApp {
        background-color: #F5F5DC; /* Beige */
        color: #1A3622; /* Dark Green */
    }
    h1, h2, h3, h4, h5, h6 {
        color: #1A3622 !important;
    }
    .stButton>button {
        background-color: #1A3622;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 24px;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #2a5234;
        color: white;
    }
    .content-box {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        color: #1A3622;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🤌 Authentic Italian Culinary Intelligence")
st.markdown("Analyze viral trends and generate authentic counter-content.")

st.sidebar.header("🔍 Search Parameters")
query = st.sidebar.text_input("Search Query", "Italian food")
order = st.sidebar.selectbox("Sort Order", ["viewCount", "date", "relevance"])
timeframe = st.sidebar.selectbox("Timeframe", ["All Time", "Last 30 Days", "This Year"])

st.sidebar.header("🗣️ Script Settings")
brand_voice_file = st.sidebar.file_uploader("Upload Brand Voice Guide (.txt, .md)", type=["txt", "md"])
if brand_voice_file is not None:
    brand_voice = brand_voice_file.getvalue().decode("utf-8")
else:
    brand_voice = st.sidebar.text_area("Or type Brand Voice here", "An authentic Italian chef who is passionate, slightly dramatic about food crimes, but educational.")

script_style = st.sidebar.selectbox("Script Style", ["Aggressive Hook", "Educational", "Comedic", "Storytelling"])

if st.button("Trigger Trend Scan"):
    with st.spinner(f"Fetching YouTube Data for '{query}' and Analyzing..."):
        try:
            titles = engine.main(query=query, order=order, timeframe=timeframe, brand_voice=brand_voice, script_style=script_style)
            st.success("Pipeline executed successfully!")
            
            # Split screen layout
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.markdown("### 🔍 Discovered Viral Titles")
                st.markdown("<div class='content-box'>", unsafe_allow_html=True)
                for i, video in enumerate(titles, 1):
                    if isinstance(video, dict):
                        st.markdown(f"**{i}. [{video['title']}]({video['url']})**")
                        st.markdown(f"*{video['channel']}* • 👁️ {video['views']} views")
                        st.markdown("---")
                    else:
                        st.markdown(f"**{i}.** {video}")
                st.markdown("</div>", unsafe_allow_html=True)
                
            with col2:
                st.markdown("### 📝 Diagnosis & Production Brief")
                st.markdown("<div class='content-box'>", unsafe_allow_html=True)
                try:
                    with open("youtube_production_brief.md", "r", encoding="utf-8") as f:
                        brief_content = f.read()
                    st.markdown(brief_content)
                except FileNotFoundError:
                    st.error("Could not find the generated brief. Please try running again.")
                st.markdown("</div>", unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"An error occurred: {e}")
else:
    st.info("Click the button above to start the live trend scan.")
