# CampusMate — BBA Agentic AI Fest Planner

A Streamlit academic prototype focused only on the BBA Department's one-day Agentic AI Fest assignment.

## Features
- Dashboard with event budget, participants, fixed costs and planning alerts.
- Helpdesk for the supplied university policies and simple calculations.
- Fest planner with fixed-cost calculation, venue/date comparison, weather notes, deadline checks and fallback planning.
- Approval checklist, simulated booking gate and SQLite audit log with CSV export.
- Searchable policy knowledge base.
- Failure simulation for Seminar Hall A and reset control.

## Important limitation
This version does **not** use an API or external language model. It is a rule-based agentic workflow prototype: Python functions perform calculations, retrieve policy text, compare constraints and record simulated actions. It is not an unrestricted generative AI chatbot. All bookings and approvals are simulations; no real university office, venue or supplier is contacted.

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud
1. Upload all files and folders to the root of your GitHub repository, preserving the `src/` folder.
2. Set the app entry point to `app.py`.
3. Streamlit installs packages from `requirements.txt`.

## Assignment data
The app uses the assignment's 120 participants, ₹60,000 budget, 13/14 November 2026 dates, venue capacities and rates, fixed costs, weather notes and four supplied policy areas. It flags that the 10-day venue-request deadline has passed as of 5 November 2026.
