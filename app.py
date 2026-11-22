import json
import os

import streamlit as st
from dotenv import load_dotenv

from analysis_service import AnalysisError, MAX_CONVERSATION_CHARS, analyze_conversation

load_dotenv()
st.set_page_config(page_title="Customer Failure Detector", page_icon="◈", layout="wide")

SAMPLES = {
    "Package": "Agent: Thank you for calling TechBox support. How can I help?\nCustomer: I ordered a package two weeks ago and it still hasn't arrived.\nAgent: It looks like it was lost in transit. You'll need to contact the courier to file a claim.\nCustomer: Can't you do that? I bought it from you!\nAgent: Once it leaves our warehouse, it's out of our hands.\nCustomer: This is ridiculous. Cancel my account.",
    "Outage": "Agent: Welcome to CloudHost. How may I assist?\nCustomer: My website has been down for three hours. I'm losing sales.\nAgent: There's an outage. It will be fixed soon.\nCustomer: I need a timeframe. Can you migrate me to another server?\nAgent: That's a premium feature. You have to wait.\nCustomer: We're losing thousands.\nAgent: Those are our policies. Have a good day.",
    "Billing": "Agent: Hi, this is Billing Support.\nCustomer: I was charged $150 instead of my usual $50.\nAgent: You were switched to the Annual Pro plan.\nCustomer: I didn't authorize that!\nAgent: You must have clicked upgrade. It's non-refundable.\nCustomer: I haven't even logged in this month. I want a manager.",
}

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;600;700;800&display=swap');
.stApp {background: #0c1918; color: #edf6ef; font-family: 'DM Sans', sans-serif;}
h1, h2, h3, h4, [data-testid="stMetricValue"] {font-family: 'Manrope', sans-serif; letter-spacing: -.035em;}
.block-container {max-width: 1440px; padding: 2rem 3rem 5rem;}
[data-testid="stSidebar"] {background: #10221f; border: 0;}
[data-testid="stSidebar"] * {color: #eef8f2;}
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {color: #d1e2da !important; line-height: 1.6;}
[data-testid="stSidebar"] input {color: #edf6ef; background: #203834;}
[data-testid="stSidebar"] hr {border-color: #31534c;}
.brand {display:flex; align-items:center; gap:12px; margin-bottom:2.5rem;}
.brand-mark {background:#c9f36d; color:#15372f !important; border-radius:12px; height:42px; width:42px; display:grid; place-items:center; font-size:24px; font-weight:800;}
.brand-name {font-family:Manrope,sans-serif; font-weight:800; letter-spacing:-.04em; font-size:1.05rem; line-height:1.15;}
.brand-sub {font-size:.7rem; letter-spacing:.12em; text-transform:uppercase; color:#a8c5b8 !important; margin-top:4px;}
.eyebrow {color:#78aa99; font-size:.72rem; font-weight:800; letter-spacing:.14em; text-transform:uppercase;}
.hero {padding: .7rem 0 1.6rem;}
.hero h1 {font-size:clamp(2.2rem, 4vw, 3.7rem); line-height:1.06; letter-spacing:-.055em; margin:.65rem 0 .8rem; color:#f1f8f2;}
.hero p {color:#bbcec4; font-size:1.05rem; line-height:1.6; max-width:650px; margin:0;}
.hero-pill {display:inline-block; background:#203a32; border:1px solid #35574a; border-radius:99px; padding:.42rem .8rem; color:#c9edbf; font-size:.7rem; font-weight:800; letter-spacing:.1em; text-transform:uppercase;}
[data-testid="stVerticalBlockBorderWrapper"] > div {background:#172b28; border:1px solid #315047; border-radius:18px; box-shadow:0 12px 36px rgba(0,0,0,.18); padding:1.5rem;}
[data-testid="stMetric"] {background:#203e33; border:1px solid #395c4a; border-radius:14px; padding:1.1rem 1.25rem;}
[data-testid="stMetricValue"] {color:#d0f5b7;}
div.stButton > button {border-radius:10px; font-weight:600; min-height:2.65rem; background:#203834; border-color:#466359; color:#edf6ef;}
div.stButton > button[kind="primary"] {background:#b9ed76; border:1px solid #b9ed76; color:#10291f; min-height:3rem;}
div.stButton > button[kind="primary"]:hover {background:#d1f69d; border-color:#d1f69d; color:#10291f;}
textarea {border-radius:12px !important;}
[data-testid="stCodeBlock"] pre {border-radius:10px;}
.section-kicker {color:#a7cdb8; font-size:.7rem; font-weight:800; letter-spacing:.12em; text-transform:uppercase; margin-bottom:.4rem;}
@media (max-width: 768px) {.block-container {padding:1rem 1rem 3rem;} .hero h1 {font-size:2.35rem;}}
</style>
""", unsafe_allow_html=True)

if "conversation" not in st.session_state:
    st.session_state.conversation = ""
if "analysis" not in st.session_state:
    st.session_state.analysis = None

with st.sidebar:
    st.markdown('<div class="brand"><div class="brand-mark">◈</div><div><div class="brand-name">Customer Failure Detector</div><div class="brand-sub">Quality workspace</div></div></div>', unsafe_allow_html=True)
    st.markdown('<div class="eyebrow">Workspace settings</div>', unsafe_allow_html=True)
    st.subheader("Your connection")
    env_key = os.getenv("GEMINI_API_KEY", "")
    api_key = st.text_input("Gemini API key", type="password", help="Used for this session. Alternatively set GEMINI_API_KEY in your environment.")
    st.caption("An environment key is configured." if env_key else "Get a key from Google AI Studio, or configure GEMINI_API_KEY.")
    st.divider()
    st.subheader("Before you begin")
    st.caption("Remove personal or sensitive information before submitting. The transcript is sent to Google Gemini for analysis.")
    st.caption("AI assessments can be incomplete or mistaken. Review the transcript before acting.")

st.markdown('<div class="hero"><span class="hero-pill">✦ &nbsp; Customer experience intelligence</span><h1>Better conversations<br>start with clarity.</h1><p>Find the moments that matter, understand what went wrong, and give your team a better way forward.</p></div>', unsafe_allow_html=True)

left, right = st.columns([1.05, 1], gap="large")
with left, st.container(border=True):
    st.markdown('<div class="section-kicker">01 / Input</div>', unsafe_allow_html=True)
    st.subheader("The conversation")
    st.caption("Paste a transcript below, or explore an example to get started.")
    sample_cols = st.columns(3)
    for col, (label, sample) in zip(sample_cols, SAMPLES.items()):
        if col.button(label, use_container_width=True):
            st.session_state.conversation = sample
            st.session_state.analysis = None
            st.session_state.pop("review_verdict", None)
            st.session_state.pop("review_notes", None)
    conversation = st.text_area("Support transcript", key="conversation", height=300, max_chars=MAX_CONVERSATION_CHARS, placeholder="Agent: How can I help?\nCustomer: I'm having trouble with…", help="Include both sides of the conversation for the best context.")
    st.caption(f"{len(conversation):,} / {MAX_CONVERSATION_CHARS:,} characters")
    if st.button("Analyze conversation →", type="primary", use_container_width=True):
        st.session_state.analysis = None
        st.session_state.pop("review_verdict", None)
        st.session_state.pop("review_notes", None)
        try:
            with st.spinner("Reviewing the conversation…"):
                result = analyze_conversation(api_key or env_key, conversation)
            st.session_state.analysis = result.to_dict()
            st.session_state.analyzed_conversation = conversation
        except AnalysisError as exc:
            st.error(str(exc))

with right, st.container(border=True):
    st.markdown('<div class="section-kicker">02 / Insights</div>', unsafe_allow_html=True)
    st.subheader("Your analysis")
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
        st.divider()
        st.markdown("#### Reviewer assessment")
        st.caption("Record your decision and any corrections. Your review is included in the downloaded report.")
        verdict = st.selectbox("Review status", ["Not reviewed", "Confirmed", "Needs correction"], key="review_verdict")
        notes = st.text_area("Reviewer notes and corrections", key="review_notes", max_chars=5000, placeholder="Add context, corrections, or a reason for your decision…")
        report = {**result, "review": {"status": verdict, "notes": notes.strip()}}
        st.download_button("Download analysis as JSON", json.dumps(report, indent=2, ensure_ascii=False), file_name="customer-analysis.json", mime="application/json", use_container_width=True, disabled=conversation != st.session_state.get("analyzed_conversation"), help="Reanalyze the current transcript before downloading." if conversation != st.session_state.get("analyzed_conversation") else None)
    else:
        st.markdown("### Your next insight starts here")
        st.caption("Add a conversation and run an analysis to uncover the details behind the customer experience.")
        st.divider()
        st.markdown("**01  ·  Pinpoint the moment**")
        st.caption("Identify the failure point and the evidence behind it.")
        st.markdown("**02  ·  Understand the why**")
        st.caption("Explore likely causes and the customer’s emotional state.")
        st.markdown("**03  ·  Move forward**")
        st.caption("Get a suggested response and practical next actions.")
