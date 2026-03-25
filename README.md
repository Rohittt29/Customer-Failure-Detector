# Customer Failure Detector (AI Support QA)

**Customer Failure Detector** is an enterprise-grade AI analytics platform designed to audit, evaluate, and coach customer support interactions at scale. By leveraging Google's state-of-the-art Gemini LLMs, the application automatically reads full support transcripts and pinpoints exactly where communication broke down, reducing churn and saving QA analysts hours of manual review.

---

### 🚀 Live Demo
*(Insert your Streamlit deployment link here once deployed!)*

### 🔍 Features
- **Instant QA at Scale:** Capable of processing complex customer transcripts in seconds to identify pain points.
- **Root Cause & Emotion Analysis:** Uses semantic reasoning to determine the exact emotional trigger causing a customer failure and clearly identifies the underlying business logic that broke down (e.g., policy constraints, server issues).
- **Ideal Conversational Pathways:** Generates an "Ideal Response" to serve as automated, realistic agent coaching material.
- **Custom Native Dashboard UI:** Built with an elegant, completely custom styling aesthetic (unlike generic templates) utilizing dynamically rendered CSS SVGs and complex Flexbox layouts via native Python rendering mechanisms.
- **Gemini Engine Integration:** Implements asynchronous logic and robust LLM generation fallback loops to guarantee valid, clean JSON payload outputs from models (`gemini-2.5-flash`, `gemini-1.5-pro`, etc.).

### 💻 Technology Stack
- **Frontend & App State:** Python 3, Streamlit
- **AI Core Engine:** Google Generative AI (Gemini SDK)
- **Data Engineering:** Pandas, JSON Processing
- **Styling:** Custom Embedded CSS & Dynamic SVGs (HTML injection)

---

### 🛠️ Local Development Setup

To run this application locally, you will need a Google Gemini API Key.

**1. Clone the repository**
```bash
git clone https://github.com/your-username/CustomerFailureDetector.git
cd CustomerFailureDetector
```

**2. Create a virtual environment**
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

**3. Install Dependencies**
```bash
pip install -r requirements.txt
```

**4. Set up your Environment Variable**
Create a `.env` file in the root directory and add your Google Gemini API key:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

**5. Launch the Application**
```bash
streamlit run app.py
```

---

### 📈 Future Roadmap
- Integration with third-party ticketing platforms (Zendesk / Intercom API integrations).
- Mass-bulk JSON upload parsing to evaluate hundreds of transcripts at a time.
- Time-series graphing for CX Quality Score drift over time.

*Built by [Rohit Kumbhar]*
