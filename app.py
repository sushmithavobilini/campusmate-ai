import streamlit as st
from src.agent import CampusMateAgent
from src.db import init_db, add_log, get_logs, clear_logs
from src.tools import simulate_seminar_failure, reset_venue_data, confirm_booking
from src.data import VENUES, EVENT_ITEMS, POLICY_CHUNKS, WEATHER

st.set_page_config(page_title="CampusMate AI", page_icon="🎓", layout="wide")
init_db()
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending" not in st.session_state:
    st.session_state.pending = None

st.title("🎓 CampusMate")
st.caption("BBA Department Helpdesk & Event-Planning Agent | No API required")

with st.sidebar:
    st.header("Agent controls")
    st.write("This version runs locally using Python tools and rule-based intent detection. No API key or external AI service is used.")
    if st.button("Simulate Seminar Hall A booking failure", use_container_width=True):
        result = simulate_seminar_failure()
        add_log("SIMULATION", "simulate_seminar_failure", {}, result)
        st.success("Seminar Hall A marked booked on both dates.")
    if st.button("Reset venue availability", use_container_width=True):
        result = reset_venue_data()
        add_log("SIMULATION", "reset_venue_data", {}, result)
        st.success("Original venue availability restored.")
    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending = None
        st.rerun()

chat, data, audit, kb = st.tabs(["💬 Chat with CampusMate", "📊 Event data", "🧾 Audit log", "📘 Knowledge base"])

with chat:
    st.info("Try: 'Plan a fest for 120 students with a budget of 60000', 'How much casual leave can faculty take?', or 'What time is hostel curfew?'")
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
    prompt = st.chat_input("Ask CampusMate...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        agent = CampusMateAgent()
        with st.chat_message("assistant"):
            with st.spinner("CampusMate is processing the request and using its tools..."):
                answer, events, pending = agent.run(prompt)
                st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})
        for e in events:
            add_log(e["status"], e["tool"], e["arguments"], e["result"])
        if pending:
            st.session_state.pending = pending

    if st.session_state.pending:
        p = st.session_state.pending
        st.divider()
        st.subheader("Human approval required")
        st.warning(f"Approve simulated booking request for **{p['venue']}** on **{p['date']}**? Estimated event total: **₹{p['total_cost']:,}**. No booking has been made.")
        note = st.text_input("Approval note (confirm HoD approval, faculty coordinator and deadline compliance)")
        a, b = st.columns(2)
        with a:
            if st.button("Approve simulated booking", type="primary", use_container_width=True):
                if not note.strip():
                    st.error("Enter an approval note.")
                else:
                    result = confirm_booking(p, note)
                    add_log("HUMAN_APPROVED", "confirm_booking", p, result)
                    st.session_state.pending = None
                    st.success(result["message"])
                    st.rerun()
        with b:
            if st.button("Reject request", use_container_width=True):
                add_log("HUMAN_REJECTED", "reject_booking", p, {"message": "Rejected by user."})
                st.session_state.pending = None
                st.info("Request rejected. Nothing was booked.")
                st.rerun()

with data:
    st.subheader("Event data")
    st.write("Assignment request: 120 students, 13 or 14 November 2026, budget ₹60,000.")
    st.dataframe([{"Venue": n, "Capacity": v["capacity"], "Cost/day": v["cost"], "AV included": v["av"],
                   "13 Nov": v["availability"]["2026-11-13"], "14 Nov": v["availability"]["2026-11-14"]}
                  for n,v in VENUES.items()], use_container_width=True, hide_index=True)
    st.dataframe([{"Item": k, "Price": v} for k,v in EVENT_ITEMS.items()], use_container_width=True, hide_index=True)
    st.write("Weather:", WEATHER)

with audit:
    st.subheader("Audit log")
    rows = get_logs()
    if rows:
        st.dataframe(rows, use_container_width=True, hide_index=True)
    else:
        st.caption("No agent actions recorded yet.")
    if st.button("Clear audit log"):
        clear_logs()
        st.rerun()

with kb:
    st.subheader("Policy knowledge base")
    for c in POLICY_CHUNKS:
        with st.expander(c["title"]):
            st.write(c["text"])
    st.caption("Retrieval uses local keyword matching. Unsupported questions receive an explicit 'not found' response.")
