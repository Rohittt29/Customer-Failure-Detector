# Customer Failure Detector

A Streamlit app for reviewing customer support conversations with Gemini. Paste a transcript to get a likely failure point and root cause, customer emotion, a suggested response, recommended next actions, supporting transcript excerpts, and a 0–10 quality assessment. Excerpts are checked for exact matches in the submitted transcript; a missing excerpt is shown when none can be verified. A matching quote does not guarantee the interpretation is correct. Reviewers can mark the analysis as confirmed or needing correction, add notes, and download the analysis and review together as JSON. Review notes stay in the current session and reset when a new analysis is started.

## Run locally

Requires Python 3.10 or newer and a Gemini API key from [Google AI Studio](https://aistudio.google.com/).

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Enter your API key in the sidebar, or set `GEMINI_API_KEY` in your environment or a local `.env` file. The default model is `gemini-2.5-flash`; set `GEMINI_MODEL` to another compatible model if needed. Never commit API keys.

Transcripts are sent to Google Gemini. Remove sensitive information before submitting and check the provider's terms for your use case. AI output is an estimate and should be reviewed against the source conversation. The app does not persist analyses beyond the active Streamlit session; a downloaded report is saved wherever your browser places downloads.

## Tests

```bash
python -m unittest discover -s tests
```
