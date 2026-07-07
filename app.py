import streamlit as st

# Import your compiled graph
from linkedin_graph import app   # <-- Rename your LangGraph file to linkedin_graph.py

st.set_page_config(
    page_title="Byline AI",
    page_icon="✍️",
    layout="wide"
)

# ---------------------------
# Custom CSS
# ---------------------------
st.markdown("""
<style>

/* Google Font */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"]{
    font-family: 'Inter', sans-serif;
}

/* Background */
.stApp{
    background:
        radial-gradient(circle at top left,#6366F1 0%,transparent 35%),
        radial-gradient(circle at bottom right,#06B6D4 0%,transparent 35%),
        linear-gradient(135deg,#0F172A,#111827,#020617);
    color:white;
}

/* Main */
.block-container{
    max-width:950px;
    padding-top:2rem;
    padding-bottom:2rem;
}

/* Headings */
h1,h2,h3{
    color:white !important;
}

/* Caption */
.stCaption{
    color:#cbd5e1 !important;
}

/* Text Area */
textarea{
    background:rgba(255,255,255,.07)!important;
    color:white!important;
    border-radius:16px!important;
    border:1px solid rgba(255,255,255,.15)!important;
}

/* Buttons */
.stButton>button{
    width:100%;
    height:55px;
    border:none;
    border-radius:14px;
    background:linear-gradient(90deg,#6366F1,#3B82F6);
    color:white;
    font-weight:600;
    transition:.25s;
}

.stButton>button:hover{
    transform:translateY(-2px);
    box-shadow:0 10px 25px rgba(59,130,246,.4);
}

/* Download Button */
.stDownloadButton>button{
    width:100%;
    border-radius:14px;
}

/* Metric Card */
[data-testid="metric-container"]{
    background:rgba(255,255,255,.08);
    border:1px solid rgba(255,255,255,.12);
    border-radius:18px;
    padding:15px;
}

/* Status */
.approved{
    color:#22C55E;
    font-weight:700;
}

.rejected{
    color:#EF4444;
    font-weight:700;
}

/* Success/Info */
.stSuccess,.stInfo{
    border-radius:14px;
}

</style>
""", unsafe_allow_html=True)


# ---------------------------
# Header
# ---------------------------

st.title("✍️ Byline AI")

st.caption(
    "Generate professional LinkedIn posts using LangGraph + Gemini + Groq + Tavily"
)

st.divider()

# ---------------------------
# Topic Input
# ---------------------------

topic = st.text_area(
    "Topic",
    placeholder="Example: Why AI Agents are changing software development...",
    height=320,
)

generate = st.button("🚀 Generate LinkedIn Post")

# ---------------------------
# Generate
# ---------------------------

if generate:

    if topic.strip() == "":
        st.warning("Please enter a topic.")
        st.stop()

    initial_state = {
        "topic": topic,
        "messages": [],
        "draft": "",
        "review_feedback": "",
        "is_approved": False,
        "attempt": 0,
    }

    with st.spinner("Generating and reviewing your LinkedIn post..."):

        final_state = app.invoke(initial_state)

    st.success("Done!")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        if final_state["is_approved"]:
            st.markdown(
                "<h3 class='approved'>✅ Approved</h3>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                "<h3 class='rejected'>❌ Not Approved</h3>",
                unsafe_allow_html=True
            )

    with col2:
        st.metric(
            "Attempts",
            final_state["attempt"]
        )

    st.subheader("LinkedIn Post")

    st.text_area(
        "",
        value=final_state["draft"],
        height=350,
        key="draft"
    )

    draft = str(final_state["draft"])

    st.download_button(
        "📄 Download Post",
        data=draft.encode("utf-8"),
        file_name="linkedin_post.txt",
        mime="text/plain",
    )

    st.subheader("Reviewer Feedback")

    st.info(final_state["review_feedback"])