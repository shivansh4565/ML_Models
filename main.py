import os
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph , START , END
from langgraph.prebuilt import ToolNode
from langchain_groq import ChatGroq
from langgraph.graph.message import add_messages
from langchain_tavily import TavilySearch
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

search_tool = TavilySearch(max_result = 5)

tools = [search_tool]

# llms

#writer
writer_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash",
    temperature=0.8,)
writer_llm_with_tools =  writer_llm.bind_tools(tools)

#reviewer
reviewer_llm = ChatGroq(model = "llama-3.3-70b-versatile",temperature=0.3)

#state building 

class State(TypedDict):
    topic : str 
    messages : Annotated[list,add_messages]
    draft : str 
    review_feedback : str
    is_approved : bool 
    attempt : int

#nodes 

WRITER_SYSTEM_PROMPT = (
    "You are an expert LinkedIn content writer. Your job is to write "
    "engaging, professional LinkedIn posts about the given topic. "
    "If the topic requires up-to-date information, statistics, or "
    "current trends, use the web search tool to gather fresh context "
    "before writing. If you have already received feedback on a "
    "previous draft, carefully address every point in the new draft. "
    "Rules for good LinkedIn posts: strong hook in the first line, "
    "1 clear takeaway, easy to skim (short paragraphs), around "
    "150–200 words, ends with a question or call-to-action to invite "
    "engagement. Do not use hashtags."
)

def writer_node(state : State) -> dict:
    """Writes (or rewrites) the LinkedIn post. Can call Tavily to search first."""
    attempt = state.get("attempt",0) + 1 
    topic = state["topic"]
    previous_feedback = state['review_feedback']

    if attempt == 1:
        user_message = (
            f"Write a LinkedIn post on this topic {topic}"
            f"if you need current info search the web first "
        )
    else:
        user_message = (
            f"your previous draft on '{topic}' was rejected"
            f"Here is the reviewer's feedback \n\n {previous_feedback}\n\n"
            f"Write a new, improved draft that fixes every issue mentiond"
            f"do not repeat the same mistake"
        )
    messages = [
    ("system", WRITER_SYSTEM_PROMPT),
    *state["messages"],
    ("human", user_message),
    ]
    response = writer_llm_with_tools.invoke(messages)

    return {
        "messages" : [("human",user_message),response],
        "attempt" : attempt
    }

tool_node = ToolNode(tools)


def extract_draft_node(state:State) -> dict:
    """After the writer finishes tool calls, pulls the final text out as the draft."""
    last_message = state['messages'][-1]
    draft = last_message.content 
    print(f"\n\n generated post \n {draft} \n ")
    return {"draft" : draft}
    

REVIEWER_SYSTEM_PROMPT = (
    "You are a strict LinkedIn content reviewer. You judge whether a "
    "post is publish-ready. Evaluate against these criteria:\n"
    "1. Strong hook in the first line\n"
    "2. One clear, valuable takeaway\n"
    "3. Easy to skim — uses short paragraphs\n"
    "4. Roughly 150-200 words\n"
    "5. Ends with an engaging question or CTA\n"
    "6. Professional but human tone (not corporate-robotic)\n"
    "7. No hashtags\n\n"
    "Respond in exactly this format:\n"
    "VERDICT: APPROVED or REJECTED\n"
    "FEEDBACK: <one short paragraph explaining why>\n\n"
    "Be strict but fair. Approve only if the post genuinely meets all "
    "criteria. Reject if even one criterion is clearly missing."
)

def reviewer_node(state:State) -> dict:
    """Reviews the draft and decides: approve or reject with feedback."""
    draft = state['draft']

    prompt = (
        f"review this LinkedIn post draft : \n"
        f"{draft}\n"
        f"give your reviews"
    )
    response = reviewer_llm.invoke(
        [("system",REVIEWER_SYSTEM_PROMPT),("human",prompt)]
    )
    review_text = response.content.strip()
    
    is_approved = "APPROVED" in review_text.upper().split("FEEDBACK")[0]

    if "FEEDBACK:" in review_text:
        feedback = review_text.split("FEEDBACK:", 1)[1].strip()
    else:
        feedback = review_text

    verdict = "APPROVED" if is_approved else "REJECTED"
    print(f"[Verdict: {verdict}]")
    print(f"[Feedback: {feedback}]")

    return {
        "review_feedback": feedback,
        "is_approved": is_approved,
    }

#router function 

def should_use_tool(state:State):
    last_message = state['messages'][-1]

    if getattr(last_message,'tool_calls',None):
        return "tools"
    return "extract_draft"

def should_stop_looping(state:State):
    if state['is_approved']:
        print("post haas been approved \n")
        return END
    if state['attempt'] >= 3:
        print("reached max attempts")
        return END 
    return "writer"

#build the graph 
graph = StateGraph(State)

graph.add_node("writer",writer_node)
graph.add_node("tools",tool_node)
graph.add_node("extract_draft",extract_draft_node)
graph.add_node("reviewer",reviewer_node)

graph.add_edge(START,"writer")

graph.add_conditional_edges(
    "writer",should_use_tool,
)
graph.add_edge("tools", "writer")
graph.add_edge("extract_draft", "reviewer")

graph.add_conditional_edges(
    "reviewer",should_stop_looping
)

app = graph.compile()

import streamlit as st

# ---------------- PAGE CONFIG ---------------- #
st.set_page_config(
    page_title="LinkedIn AI Writer",
    page_icon="✨",
    layout="centered"
)

# ---------------- CSS ---------------- #
st.markdown("""
<style>

.stApp{
background: linear-gradient(135deg,#0f172a,#111827,#1e293b);
background-attachment: fixed;
}

.main{
padding-top:30px;
}

.card{
background: rgba(255,255,255,0.08);
backdrop-filter: blur(18px);
-webkit-backdrop-filter: blur(18px);
border:1px solid rgba(255,255,255,.15);
border-radius:24px;
padding:35px;
box-shadow:0 8px 32px rgba(0,0,0,.25);
}

.title{
font-size:38px;
font-weight:700;
color:white;
margin-bottom:5px;
}

.subtitle{
color:#cbd5e1;
margin-bottom:30px;
font-size:17px;
}

textarea{
font-size:16px;
}

.stTextInput>div>div>input{
background:rgba(255,255,255,.08);
color:white;
border-radius:14px;
}

.stTextArea textarea{
background:rgba(255,255,255,.08);
color:white;
border-radius:14px;
}

.stButton>button{
width:100%;
height:52px;
border-radius:14px;
border:none;
background:linear-gradient(90deg,#4f46e5,#7c3aed);
color:white;
font-size:18px;
font-weight:600;
transition:.3s;
}

.stButton>button:hover{
transform:translateY(-2px);
box-shadow:0 0 20px rgba(99,102,241,.5);
}

.result-card{
background:rgba(255,255,255,.08);
backdrop-filter:blur(18px);
border-radius:20px;
padding:25px;
border:1px solid rgba(255,255,255,.15);
margin-top:20px;
}

.metric{
padding:15px;
border-radius:15px;
background:rgba(255,255,255,.08);
text-align:center;
}

.success{
color:#22c55e;
font-weight:700;
font-size:18px;
}

.fail{
color:#ef4444;
font-weight:700;
font-size:18px;
}

</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ---------------- #

st.markdown("""
<div class="card">

<div class="title">
✨ LinkedIn AI Writer
</div>

<div class="subtitle">
Generate, review and improve LinkedIn posts automatically using LangGraph.
</div>

""", unsafe_allow_html=True)

topic = st.text_area(
    "Topic",
    height=300,
    placeholder="Example: AI Agents replacing traditional workflows..."
)

generate = st.button("🚀 Generate LinkedIn Post")

st.markdown("</div>", unsafe_allow_html=True)

# ---------------- APP ---------------- #

if generate:

    if not topic.strip():
        st.warning("Please enter a topic.")
        st.stop()

    with st.spinner("Generating post..."):

        initial_state = {
            "topic": topic,
            "messages": [],
            "draft": "",
            "review_feedback": "",
            "is_approved": False,
            "attempt": 0,
        }

        final_state = app.invoke(initial_state)

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"""
        <div class="metric">
        <h4 style="color:white;">Attempts</h4>
        <h2 style="color:white;">{final_state['attempt']}</h2>
        </div>
        """, unsafe_allow_html=True)

    with col2:

        status = "Approved ✅" if final_state["is_approved"] else "Rejected ❌"

        color = "success" if final_state["is_approved"] else "fail"

        st.markdown(f"""
        <div class="metric">
        <h4 style="color:white;">Status</h4>
        <div class="{color}">
        {status}
        </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="result-card">

    <h3 style="color:white;">📝 Final LinkedIn Post</h3>

    </div>
    """, unsafe_allow_html=True)

    st.write(final_state["draft"])

    if final_state["review_feedback"]:
        st.markdown(f"""
        <div class="result-card">

        <h3 style="color:white;">🧐 Reviewer Feedback</h3>

        </div>
        """, unsafe_allow_html=True)

        st.write(final_state["review_feedback"])