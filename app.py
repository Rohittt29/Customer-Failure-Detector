import json
import os

import streamlit as st
from dotenv import load_dotenv

from analysis_service import AnalysisError, MAX_CONVERSATION_CHARS, analyze_conversation

load_dotenv()
st.set_page_config(page_title="Customer Failure Detector", page_icon="◈", layout="wide")

SAMPLES = {
    "Lost package": "Agent: Thank you for calling TechBox support. How can I help?\nCustomer: I ordered a package two weeks ago and it still hasn't arrived.\nAgent: It looks like it was lost in transit. You'll need to contact the courier to file a claim.\nCustomer: Can't you do that? I bought it from you!\nAgent: Once it leaves our warehouse, it's out of our hands.\nCustomer: This is ridiculous. Cancel my account.",
    "Service outage": "Agent: Welcome to CloudHost. How may I assist?\nCustomer: My website has been down for three hours. I'm losing sales.\nAgent: There's an outage. It will be fixed soon.\nCustomer: I need a timeframe. Can you migrate me to another server?\nAgent: That's a premium feature. You have to wait.\nCustomer: We're losing thousands.\nAgent: Those are our policies. Have a good day.",
    "Billing dispute": "Agent: Hi, this is Billing Support.\nCustomer: I was charged $150 instead of my usual $50.\nAgent: You were switched to the Annual Pro plan.\nCustomer: I didn't authorize that!\nAgent: You must have clicked upgrade. It's non-refundable.\nCustomer: I haven't even logged in this month. I want a manager.",
}

st.markdown("""
<style>
.stApp {background: #f6f7f4; color: #172b29;}
.block-container {max-width: 1200px; padding-top: 2rem; padding-bottom: 3rem;}
.eyebrow {color:#547d71; font-size:.75rem; font-weight:800; letter-spacing:.14em; text-transform:uppercase;}
.hero {padding: 1.5rem 0 .8rem;}
.hero h1 {font-size:clamp(2.1rem, 4vw, 3.5rem); letter-spacing:-.045em; line-height:1.08; margin:.5rem 0; color:#183c35;}
.hero p {color:#5a6d67; font-size:1.05rem; max-width:650px; line-height:1.6;}
div[data-testid="stMetric"] {background:#e7f1ec; border:1px solid #cde1d6; border-radius:14px; padding:1rem 1.2rem;}
div.stButton > button[kind="primary"] {background:#1d594b; border-color:#1d594b; color:white;}
div.stButton > button {border-radius:8px;}
.small-note {color:#657a72; font-size:.85rem;}
</style>
""", unsafe_allow_html=True)

if "conversation" not in st.session_state:
    st.session_state.conversation = ""
if "analysis" not in st.session_state:
    st.session_state.analysis = None

with st.sidebar:
    st.markdown('<div class="eyebrow">Workspace</div>', unsafe_allow_html=True)
    st.header("Analysis settings")
    env_key = os.getenv("GEMINI_API_KEY", "")
    api_key = st.text_input("Gemini API key", type="password", help="Used for this session. Alternatively set GEMINI_API_KEY in your environment.")
    st.caption("An environment key is configured." if env_key else "Get a key from Google AI Studio, or configure GEMINI_API_KEY.")
    st.divider()
    st.subheader("Before you begin")
    st.caption("Remove personal or sensitive information before submitting. The transcript is sent to Google Gemini for analysis.")
    st.caption("AI assessments can be incomplete or mistaken. Review the transcript before acting.")

st.markdown('<div class="hero"><div class="eyebrow">Customer experience · Quality review</div><h1>Find the moment<br>things went wrong.</h1><p>Turn support conversations into clear insights and a more thoughtful next response.</p></div>', unsafe_allow_html=True)

left, right = st.columns([1.05, 1], gap="large")
with left:
    st.subheader("Conversation")
    st.caption("Paste a support exchange or start with an example.")
    sample_cols = st.columns(3)
    for col, (label, sample) in zip(sample_cols, SAMPLES.items()):
        if col.button(label, use_container_width=True):
            st.session_state.conversation = sample
            st.session_state.analysis = None
    conversation = st.text_area("Support transcript", key="conversation", height=300, max_chars=MAX_CONVERSATION_CHARS, placeholder="Agent: How can I help?\nCustomer: I'm having trouble with…", help="Include both sides of the conversation for the best context.")
    st.caption(f"{len(conversation):,} / {MAX_CONVERSATION_CHARS:,} characters")
    if st.button("Analyze conversation →", type="primary", use_container_width=True):
        st.session_state.analysis = None
        try:
            with st.spinner("Reviewing the conversation…"):
                result = analyze_conversation(api_key or env_key, conversation)
            st.session_state.analysis = result.to_dict()
            st.session_state.analyzed_conversation = conversation
        except AnalysisError as exc:
            st.error(str(exc))

with right:
    st.subheader("Analysis")
    result = st.session_state.analysis
    if result:
        def show_evidence(finding):
            quotes = result["evidence"][finding]
            if quotes:
                st.caption("Supporting excerpts")
                for quote in quotes:
                    st.code(quote, language=None)
            else:
                st.caption("No verified excerpt available for this finding.")
        if conversation != st.session_state.get("analyzed_conversation"):
            st.warning("The transcript has changed since this analysis. Run it again for updated results.")
        st.metric("Customer experience score", f"{result['cx_score']:g} / 10", help="An AI-generated assessment, not a measured customer satisfaction score.")
        st.caption("A directional quality assessment based on the supplied transcript.")
        st.markdown("#### 01 · Failure point")
        st.write(result["failure_point"])
        show_evidence("failure_point")
        st.markdown("#### 02 · Root cause")
        st.write(result["root_cause"])
        show_evidence("root_cause")
        st.markdown("#### 03 · Customer emotion")
        st.write(result["customer_emotion"])
        show_evidence("customer_emotion")
        st.markdown("#### 04 · Suggested response")
        st.info(result["ideal_response"])
        st.markdown("#### 05 · Recommended next actions")
        for index, action in enumerate(result["next_actions"], 1):
            st.write(f"{index}. {action}")
        st.caption("Excerpts are matched against the transcript; review whether they support each finding.")
        st.download_button("Download analysis as JSON", json.dumps(result, indent=2, ensure_ascii=False), file_name="customer-analysis.json", mime="application/json", use_container_width=True)
    else:
        st.info("Your analysis will appear here after you submit a conversation.")
        st.markdown("**What you’ll get**")
        st.write("A failure point, likely root cause, customer emotion, supporting excerpts, suggested response, next actions, and an overall quality score.")
