import streamlit as st
import google.generativeai as genai
import json
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

# Set Page Config
st.set_page_config(page_title="Customer Failure Detector", layout="wide")

# Get current page from query param
page = st.query_params.get("page", "home").lower()

# Custom CSS for subtle, elegant light theme
st.markdown("""
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
        color: #2D2926 !important;
    }
    
    /* Subtle gradient background for the whole app */
    .stApp {
        background: #F9F8F3 !important;
    }
    
    .stMarkdown, .stText, p, span, li, h1, h2, h3, h4 {
        color: #2D2926 !important;
    }
    
    /* Hide Streamlit elements */
    header {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .block-container {
        padding-top: 0rem;
        padding-bottom: 0rem;
    }

    /* Navbar styling: Pure white to stand out from off-white background */
    .navbar {
        background-color: #ffffff;
        padding: 15px 40px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-left: -5rem;
        margin-right: -5rem;
        margin-bottom: 3rem;
        border-bottom: 1px solid #EFECE6;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
    }
    .navbar-brand {
        font-size: 22px;
        font-weight: 700;
        color: #5E6055 !important;
        letter-spacing: -0.3px;
    }
    .navbar-links {
        display: flex;
        gap: 25px;
    }
    .navbar-links a {
        color: #2D2926 !important;
        text-decoration: none;
        font-size: 15px;
        font-weight: 600;
        transition: color 0.2s;
    }
    .navbar-links a:hover {
        color: #5E6055 !important;
    }
    
    /* Hero section: Clean white card on top of the subtle app background */
    .hero {
        text-align: center;
        padding: 50px 40px;
        background-color: #ffffff;
        border-radius: 16px;
        margin-top: 10px;
        margin-bottom: 30px;
        border: 1px solid #EFECE6;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
    }
    .hero h1 {
        font-size: 40px;
        font-weight: 800;
        color: #5E6055 !important; 
        margin-bottom: 16px;
        letter-spacing: -1px;
    }
    .hero p {
        color: #2D2926 !important;
        font-size: 18px;
        max-width: 700px;
        margin: 0 auto;
        line-height: 1.6;
    }
    
    /* Result Cards */
    .result-card {
        background-color: #ffffff;
        border: 1px solid #EFECE6;
        border-radius: 12px;
        padding: 24px;
        height: 100%;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
    }
    .result-card-header {
        color: #5E6055;
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 700;
        margin-bottom: 12px;
        border-bottom: 1px solid #EFECE6;
        padding-bottom: 8px;
    }
    .result-card-body {
        font-size: 15px;
        color: #2D2926;
        line-height: 1.6;
        font-weight: 500;
    }
    
    /* Progress bar */
    .score-container {
        margin-top: 30px;
        padding: 30px;
        border: 1px solid #EFECE6;
        border-radius: 12px;
        background-color: #ffffff;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    .score-title {
        font-size: 15px;
        color: #5E6055;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 700;
        margin-bottom: 15px;
    }
    .progress-track {
        background-color: #EFECE6;
        border-radius: 10px;
        height: 16px;
        width: 100%;
        overflow: hidden;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 20px 0;
        margin-top: 40px;
        color: #2D2926;
        font-size: 14px;
        border-top: 1px solid #EFECE6;
    }
    
    /* Streamlit overrides */
    div.stButton > button {
        background-color: #5E6055;
        color: white;
        border: none;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        border-radius: 8px;
        transition: background-color 0.2s;
        box-shadow: 0 2px 4px rgba(45, 41, 38, 0.1);
    }
    div.stButton > button:hover {
        background-color: #2D2926;
        color: white;
        border: none;
    }
    div.stButton > button:active {
        background-color: #2D2926;
        color: white;
    }
    
    /* Custom button variants for samples */
    div[data-testid="column"] button {
        background-color: #F9F8F3;
        color: #5E6055;
        border: 1px solid #EFECE6;
        width: 100%;
        border-radius: 8px;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    }
    div[data-testid="column"] button:hover {
        background-color: #EFECE6;
        color: #2D2926;
        border: 1px solid #5E6055;
    }
</style>
""", unsafe_allow_html=True)

# Render Navbar
st.markdown(f"""
<div class="navbar">
    <div class="navbar-brand">Customer Failure Detector</div>
    <div class="navbar-links">
        <a href="?page=home" target="_self" style="{ 'color: #5E6055 !important; font-weight: 700;' if page == 'home' else '' }">Home</a>
        <a href="?page=about" target="_self" style="{ 'color: #5E6055 !important; font-weight: 700;' if page == 'about' else '' }">About</a>
    </div>
</div>
""", unsafe_allow_html=True)

SAMPLE_1 = '''Agent: Thank you for calling TechBox support. How can I help?
Customer: Hi, I ordered a package two weeks ago and it still hasn't arrived.
Agent: Okay, let me check. What's your order number?
Customer: It's 99482.
Agent: It looks like it was lost in transit. You'll need to contact the courier company to file a claim.
Customer: Wait, what? Can't you guys do that? I bought it from you!
Agent: Sorry, once it leaves our warehouse, it's out of our hands. Is there anything else I can help with?
Customer: No, this is ridiculous. Cancel my account.'''

SAMPLE_2 = '''Agent: Welcome to CloudHost. How may I assist you today?
Customer: Hey, my website has been down for 3 hours. I'm losing sales. What's going on?
Agent: We're experiencing a minor outage on server block B. It will be fixed soon.
Customer: 'Soon'? I need a timeframe. This is a business account.
Agent: I don't have an exact timeframe, but our engineers are on it. Please be patient.
Customer: I've been patient for 3 hours! Can you at least migrate me to another server?
Agent: That's a premium feature. You're on the basic plan, so you have to wait.
Customer: Are you kidding me? We're losing thousands.
Agent: I understand, but those are our policies. Have a good day.'''

SAMPLE_3 = '''Agent: Hi, this is Billing Support.
Customer: Hi, I just got my credit card statement and I was charged $150 instead of my usual $50 subscription.
Agent: Let me see. Ah, you were switched to the Annual Pro plan yesterday.
Customer: I didn't authorize that! I've been on the monthly plan for two years.
Agent: You must have clicked the upgrade button on the dashboard. It's non-refundable.
Customer: I haven't even logged into the dashboard this month! This is fraud.
Agent: We don't commit fraud, sir. The system shows it was clicked from your account. You can downgrade next year.
Customer: I want a manager right now.'''


def analyze_conversation(api_key, conversation):
    errors = {}
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=api_key)
        
        prompt = f"""You are a Customer Experience Quality Analyst. Analyze the following customer support conversation. Identify: 1) The exact failure point where the experience broke down, 2) The root cause of that failure, 3) The emotional state of the customer at the worst moment, 4) The ideal response the agent should have given, 5) An overall CX quality score out of 10. Return your response as clean JSON ONLY with keys: failure_point, root_cause, customer_emotion, ideal_response, cx_score. Do not include markdown formatting or backticks around the json, just return the raw JSON string starting with {{ and ending with }}.

Conversation:
{conversation}"""
        
        # Comprehensive list of universally available models, in order of preference
        models_to_try = [
            'gemini-2.5-flash',
            'gemini-2.0-flash',
            'gemini-1.5-flash',
            'gemini-1.5-pro',
            'gemini-1.0-pro'
        ]
        
        response = None
        
        for model_name in models_to_try:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                )
                break # If successful, break out of loop
            except Exception as e:
                errors[model_name] = str(e)
                # Only fallback if it's a 404/not found error
                if "404" in str(e) or "NOT_FOUND" in str(e).upper():
                    continue
                else:
                    raise Exception(f"Model {model_name} failed with an unrecoverable error: {str(e)}")
                    
        if response is None:
            error_details = "\\n".join([f" - {m}: {e}" for m, e in errors.items()])
            raise Exception(f"Your API Key does not have access to any known text generation models. Details:\\n{error_details}\\nPlease check if your API key is valid and has access to Gemini models.")
                
        text = response.text.strip()
        
    except ImportError:
        import google.generativeai as genai_old
        genai_old.configure(api_key=api_key)
        prompt = f"""You are a Customer Experience Quality Analyst. Analyze the following customer support conversation. Identify: 1) The exact failure point where the experience broke down, 2) The root cause of that failure, 3) The emotional state of the customer at the worst moment, 4) The ideal response the agent should have given, 5) An overall CX quality score out of 10. Return your response as clean JSON ONLY with keys: failure_point, root_cause, customer_emotion, ideal_response, cx_score. Do not include markdown formatting or backticks around the json, just return the raw JSON string starting with {{ and ending with }}.

Conversation:
{conversation}"""
        
        models_to_try = ['gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-1.0-pro']
        response = None
        for model_name in models_to_try:
            try:
                model = genai_old.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                break
            except Exception as e:
                errors[model_name] = str(e)
                continue
                
        if not response:
            error_details = "\\n".join([f" - {m}: {e}" for m, e in errors.items()])
            raise Exception(f"No available models found for your API key. Details:\\n{error_details}\\nPlease verify your Google API key privileges.")
            
        text = response.text.strip()
        
    if text.startswith('```json'):
        text = text[7:]
    if text.startswith('```'):
        text = text[3:]
    if text.endswith('```'):
        text = text[:-3]
        
    return json.loads(text.strip())

if page == "about":
    st.title("About Customer Failure Detector")
    
    st.markdown("""
    **Customer Failure Detector** is an enterprise platform designed specifically for Quality Assurance (QA) and Customer Support teams. 
    It leverages state-of-the-art AI to automatically analyze customer interactions and identify the exact moment a conversation broke down.
    """)
    
    st.header("How It Helps Your Business", divider="gray")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background-color: #ffffff; padding: 24px; border-radius: 12px; border: 1px solid #EFECE6; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
            <div style="font-weight: 700; font-size: 16px; color: #5E6055; margin-bottom: 8px;">Reduce Churn</div>
            <div style="color: #2D2926; font-size: 15px; line-height: 1.5;">Identify the root causes of customer frustration before they result in canceled subscriptions or lost sales.</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div style="background-color: #ffffff; padding: 24px; border-radius: 12px; border: 1px solid #EFECE6; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
            <div style="font-weight: 700; font-size: 16px; color: #5E6055; margin-bottom: 8px;">Instant QA at Scale</div>
            <div style="color: #2D2926; font-size: 15px; line-height: 1.5;">Traditional QA sampling covers less than 2% of tickets. Our tool can evaluate 100% of your interactions instantly.</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div style="background-color: #ffffff; padding: 24px; border-radius: 12px; border: 1px solid #EFECE6; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
            <div style="font-weight: 700; font-size: 16px; color: #5E6055; margin-bottom: 8px;">Agent Coaching</div>
            <div style="color: #2D2926; font-size: 15px; line-height: 1.5;">By providing an 'Ideal Response' for every failure, you can train your support agents with real-world, personalized feedback.</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div style="background-color: #ffffff; padding: 24px; border-radius: 12px; border: 1px solid #EFECE6; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
            <div style="font-weight: 700; font-size: 16px; color: #5E6055; margin-bottom: 8px;">Discover Systemic Issues</div>
            <div style="color: #2D2926; font-size: 15px; line-height: 1.5;">Find out if your policies, server outages, or confusing UI are the underlying reasons for bad CX, not just isolated agent errors.</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.header("How It Works", divider="gray")
    st.markdown("""
    1. **Input:** You paste a conversation transcript (from Zendesk, Intercom, or phone logs) into the tool.
    2. **Analysis:** The AI reads the entire context, understanding sentiment and business logic.
    3. **Actionable Output:** It pinpoints exactly what went wrong, scores the interaction, and tells you what should have been said instead.
    """)
    
    # (Tech Stack removed per user request)

else:
    # Home Page
    st.markdown("""
    <div class="hero">
        <div style="display: inline-block; padding: 6px 16px; background-color: #EFECE6; color: #5E6055; border-radius: 20px; font-weight: 600; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 20px; border: 1px solid #EFECE6;">AI Support Analysis</div>
        <h1>Customer Failure Detector</h1>
        <p>Paste a customer support conversation below. Our AI will analyze the sentiment, pinpoint exactly where the interaction failed, and generate the perfect response strategy.</p>
    </div>
    """, unsafe_allow_html=True)
    
    container = st.container()
    
    with container:
        # Settings
        api_key = os.getenv("GEMINI_API_KEY")
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("**Load a Sample Conversation:**")
        
        # Session state for textarea
        if 'conversation' not in st.session_state:
            st.session_state.conversation = ""
            
        c1, c2, c3 = st.columns(3)
        if c1.button("Sample 1: Lost Package (Retail)"):
            st.session_state.conversation = SAMPLE_1
            st.rerun()
        if c2.button("Sample 2: Server Outage (SaaS)"):
            st.session_state.conversation = SAMPLE_2
            st.rerun()
        if c3.button("Sample 3: Billing Dispute (Sub)"):
            st.session_state.conversation = SAMPLE_3
            st.rerun()
            
        conversation = st.text_area(
            "Customer Conversation / Ticket details",
            value=st.session_state.conversation,
            height=250,
            placeholder="Agent: Thank you for calling... \nCustomer: I have a problem..."
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Analyze CTA
        col_btn, _ = st.columns([1, 4])
        with col_btn:
            analyze_clicked = st.button("Analyze", use_container_width=True)

        if analyze_clicked:
            if not api_key:
                st.error("API Key not found. Please set the GEMINI_API_KEY environment variable in your .env file.")
            elif not conversation.strip():
                st.warning("Please enter or select a conversation to analyze.")
            else:
                try:
                    with st.spinner("Analyzing conversation with Gemini..."):
                        results = analyze_conversation(api_key, conversation)
                        
                        st.markdown("<hr style='margin: 30px 0; border: none; border-top: 1px solid #EFECE6;'>", unsafe_allow_html=True)
                        st.markdown("<h3 style='color:#5E6055; font-weight:700; margin-bottom: 24px;'>Analysis Results</h3>", unsafe_allow_html=True)
                        
                        # Score Component
                        score = float(results.get('cx_score', 0))
                        
                        if score < 5:
                            color = "#ef4444" # Red
                            bg_color = "#fee2e2"
                        elif score <= 7:
                            color = "#f59e0b" # Orange
                            bg_color = "#fef3c7"
                        else:
                            color = "#10b981" # Green
                            bg_color = "#d1fae5"
                            
                        # SVG donut chart math
                        dash_array = 283 # roughly 2 * pi * 45
                        dash_offset = dash_array - (dash_array * (score / 10))
                        
                        st.markdown(f"""
                        <div style="display: flex; justify-content: center; align-items: center; padding: 30px; background: #ffffff; border: 1px solid #EFECE6; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); margin-bottom: 30px;">
                            <div style="text-align: right; margin-right: 40px;">
                                <h3 style="color: #5E6055; font-size: 18px; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 5px;">Overall Quality Score</h3>
                                <p style="color: #2D2926; font-size: 14px; margin-top: 0;">Interaction Performance out of 10</p>
                            </div>
                            <div style="position: relative; width: 120px; height: 120px;">
                                <svg width="120" height="120" viewBox="0 0 100 100">
                                    <circle cx="50" cy="50" r="45" fill="none" stroke="{bg_color}" stroke-width="10" />
                                    <circle cx="50" cy="50" r="45" fill="none" stroke="{color}" stroke-width="10" 
                                        stroke-dasharray="{dash_array}" stroke-dashoffset="{dash_offset}" 
                                        stroke-linecap="round" transform="rotate(-90 50 50)" 
                                        style="transition: stroke-dashoffset 1.5s ease-in-out;" />
                                </svg>
                                <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; display: flex; align-items: center; justify-content: center;">
                                    <span style="font-size: 26px; font-weight: 800; color: {color};">{score}</span>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Layout textual chunks in diagnostic flow
                        colA, colB = st.columns(2)
                        
                        with colA:
                            st.markdown(f"""
                            <div style="background: #ffffff; border: 1px solid #EFECE6; border-left: 6px solid #ef4444; border-radius: 12px; padding: 24px; margin-bottom: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); height: 100%;">
                                <div style="font-size: 12px; color: #5E6055; text-transform: uppercase; font-weight: 800; letter-spacing: 1px; margin-bottom: 12px;">1. Failure Point</div>
                                <div style="font-size: 15px; color: #2D2926; line-height: 1.6; font-weight: 500;">{results.get('failure_point', 'N/A')}</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            st.markdown(f"""
                            <div style="background: #ffffff; border: 1px solid #EFECE6; border-left: 6px solid #6366f1; border-radius: 12px; padding: 24px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); height: 100%;">
                                <div style="font-size: 12px; color: #5E6055; text-transform: uppercase; font-weight: 800; letter-spacing: 1px; margin-bottom: 12px;">2. Customer Emotion</div>
                                <div style="font-size: 15px; color: #2D2926; line-height: 1.6; font-weight: 500;">{results.get('customer_emotion', 'N/A')}</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                        with colB:
                            st.markdown(f"""
                            <div style="background: #ffffff; border: 1px solid #EFECE6; border-left: 6px solid #f59e0b; border-radius: 12px; padding: 24px; margin-bottom: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); height: 100%;">
                                <div style="font-size: 12px; color: #5E6055; text-transform: uppercase; font-weight: 800; letter-spacing: 1px; margin-bottom: 12px;">3. Root Cause</div>
                                <div style="font-size: 15px; color: #2D2926; line-height: 1.6; font-weight: 500;">{results.get('root_cause', 'N/A')}</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            st.markdown(f"""
                            <div style="background: #ffffff; border: 1px solid #EFECE6; border-left: 6px solid #10b981; border-radius: 12px; padding: 24px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); height: 100%;">
                                <div style="font-size: 12px; color: #5E6055; text-transform: uppercase; font-weight: 800; letter-spacing: 1px; margin-bottom: 12px;">4. Ideal Response</div>
                                <div style="font-size: 15px; color: #2D2926; line-height: 1.6; font-weight: 500;">{results.get('ideal_response', 'N/A')}</div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                except json.JSONDecodeError as e:
                    st.error("Failed to parse the response from the AI. The AI didn't return valid JSON. Please try again.")
                    st.write(str(e))
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")

# Footer
st.markdown("""
<div class="footer">
    Built by Rohit Kumbhar
</div>
""", unsafe_allow_html=True)
