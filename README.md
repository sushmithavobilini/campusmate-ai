# CampusMate (No-API version)

A Streamlit application that runs without API keys, paid AI services or external model connections.

## What it does
- Rule-based intent routing for the assignment's common requests.
- Python tools for calculations, venue comparison, policy retrieval and simulated booking requests.
- Multi-step event evaluation and alternative venue checks.
- Human approval before simulated booking confirmation.
- SQLite audit log.

## Important limitation
This is an agentic workflow prototype, not an LLM-powered generative AI system. It uses rules and Python functions, so it understands a limited set of phrasings. Do not describe it as a Claude/Gemini-powered AI. It demonstrates tool use, planning, constraints, failure recovery and human-in-the-loop control.

## Run on Streamlit Community Cloud
1. Upload all files and folders to a public GitHub repository.
2. Open https://share.streamlit.io/
3. Click **Create app**.
4. Select the repository, branch `main`, and main file path `app.py`.
5. Click **Deploy**.

No secrets or API keys are required.

## Local run
Install Python, then run:
`pip install -r requirements.txt`
`streamlit run app.py`

## Tests
- "Plan a one-day Agentic AI Fest for 120 students on 13 or 14 November with a budget of 60000."
- "How much casual leave can faculty take?"
- "What time is the hostel curfew?"
- Click the failure simulation button, then ask CampusMate to replan the fest.
- "Book the recommended venue" to generate a pending request; approve or reject in the UI.
