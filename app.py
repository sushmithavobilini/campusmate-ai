import streamlit as st
import pandas as pd
from src.agent import CampusMateAgent
from src.db import init_db, add_log, get_logs, clear_logs
from src.tools import simulate_seminar_failure, reset_venue_data, confirm_booking, calculate_budget, compare_venues
from src.data import VENUES, EVENT_ITEMS, POLICY_CHUNKS, WEATHER

st.set_page_config(page_title="CampusMate | BBA Fest", page_icon="🎓", layout="wide", initial_sidebar_state="expanded")
init_db()

# ---------- Session state ----------
for key, default in {
    "messages": [], "pending": None, "approval": {"hod": False, "coordinator": "", "exception": False, "proposal": False, "spending": False},
    "selected_date": "2026-11-13", "planner_participants": 120, "planner_budget": 60000,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ---------- Styling ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap');
html, body, [class*="css"] {font-family:'DM Sans',sans-serif;}
.block-container {padding-top:1.5rem; padding-bottom:3rem; max-width:1450px;}
[data-testid="stSidebar"] {background:#101a2b; border-right:1px solid #26354b;}
[data-testid="stSidebar"] * {color:#e8eef8 !important;}
[data-testid="stSidebar"] [data-testid="stRadio"] label {padding:8px 10px; border-radius:9px;}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {background:#20304a;}
.hero {background:linear-gradient(120deg,#172943 0%,#244b70 58%,#316b82 100%); padding:28px 32px; border-radius:18px; color:white; margin-bottom:20px;}
.hero h1 {font-family:'Manrope',sans-serif; color:white; font-size:2.2rem; margin:0 0 6px 0;}
.hero p {color:#dce9f5; margin:0; font-size:1rem;}
.eyebrow {letter-spacing:.12em; text-transform:uppercase; font-size:.72rem; color:#b7cde0; font-weight:700; margin-bottom:8px;}
.metric {background:#f7f9fc; border:1px solid #e4eaf1; border-radius:14px; padding:17px 18px; min-height:105px;}
.metric .k {font-size:.82rem; color:#637287; margin-bottom:8px;}
.metric .v {font-family:'Manrope',sans-serif; font-size:1.8rem; font-weight:800; color:#172943;}
.metric .s {font-size:.78rem; color:#718096; margin-top:2px;}
.section-title {font-family:'Manrope',sans-serif; font-size:1.22rem; font-weight:800; color:#1c2e45; margin:14px 0 10px 0;}
.info-card {border:1px solid #e3eaf1; border-radius:13px; padding:16px 18px; background:white;}
.good {background:#eaf8f0; border:1px solid #c9ead7; color:#17643b; padding:13px 16px; border-radius:11px;}
.warn {background:#fff7e6; border:1px solid #f2dfae; color:#805a12; padding:13px 16px; border-radius:11px;}
.bad {background:#fff0ef; border:1px solid #f3c9c5; color:#943c36; padding:13px 16px; border-radius:11px;}
.small-muted {color:#718096; font-size:.84rem;}
div.stButton > button {border-radius:10px; font-weight:600;}
[data-testid="stChatMessage"] {border-radius:13px;}
</style>
""", unsafe_allow_html=True)

# ---------- Helpers ----------
def metric(label, value, sub=""):
    st.markdown(f'<div class="metric"><div class="k">{label}</div><div class="v">{value}</div><div class="s">{sub}</div></div>', unsafe_allow_html=True)

def hero(kicker, title, subtitle):
    st.markdown(f'<div class="hero"><div class="eyebrow">{kicker}</div><h1>{title}</h1><p>{subtitle}</p></div>', unsafe_allow_html=True)

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("<div style='font-size:1.55rem;font-weight:800;font-family:Manrope,sans-serif;margin:10px 0 2px'>🎓 CampusMate</div><div style='color:#aab9cc;font-size:.88rem'>BBA Department · Agentic AI Fest</div>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color:#314158;margin:22px 0 14px'>", unsafe_allow_html=True)
    pages = ["Dashboard", "AI Helpdesk", "Fest Planner", "Approvals & Audit", "Knowledge Base"]
    jump_to = st.session_state.pop("_page_jump", "Dashboard")
    page = st.radio("WORKSPACE", pages, index=pages.index(jump_to) if jump_to in pages else 0, label_visibility="visible")
    st.markdown("<hr style='border-color:#314158;margin:18px 0'>", unsafe_allow_html=True)
    st.caption("EVENT SNAPSHOT")
    st.markdown("<div style='font-size:.82rem;color:#aab9cc'>Approved planning budget</div><div style='font-size:1.8rem;font-weight:800'>₹60,000</div><div style='font-size:.82rem;color:#aab9cc;margin-top:14px'>Expected participants</div><div style='font-size:1.8rem;font-weight:800'>120</div>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color:#314158;margin:18px 0'>", unsafe_allow_html=True)
    st.caption("Academic prototype · bookings and approvals are simulated only")
    with st.expander("Demo controls"):
        if st.button("Simulate Seminar Hall A failure", use_container_width=True):
            result = simulate_seminar_failure(); add_log("SIMULATION", "simulate_seminar_failure", {}, result); st.success("Hall A marked booked on both dates.")
        if st.button("Reset venue availability", use_container_width=True):
            result = reset_venue_data(); add_log("SIMULATION", "reset_venue_data", {}, result); st.success("Availability reset.")
        if st.button("Clear chat", use_container_width=True):
            st.session_state.messages = []; st.session_state.pending = None; st.rerun()

# ---------- Dashboard ----------
if page == "Dashboard":
    hero("BBA DEPARTMENT · EVENT COMMAND CENTRE", "Agentic AI Fest 2026", "Plan the one-day fest, check university rules, compare venues and move approvals forward.")
    fixed = calculate_budget(120)["fixed_cost"]
    c1,c2,c3,c4 = st.columns(4)
    with c1: metric("PARTICIPANTS", "120", "Expected attendance")
    with c2: metric("TOTAL BUDGET", "₹60,000", "Approved event limit")
    with c3: metric("FIXED COSTS", f"₹{fixed:,}", "Food, speaker, printing, prizes")
    with c4: metric("BALANCE", f"₹{60000-fixed:,}", "Available for venue and extras")
    st.markdown("<div class='section-title'>Your event at a glance</div>", unsafe_allow_html=True)
    left,right = st.columns([1.15, .85])
    with left:
        st.markdown("<div class='info-card'><b>📅 Proposed dates</b><br>13 or 14 November 2026<br><br><b>📍 Venue shortlist</b><br>Seminar Hall A · Classroom Block · Open-air Quadrangle<br><br><b>🎤 Event essentials</b><br>Guest speaker, lunch, snacks, printing and prizes</div>", unsafe_allow_html=True)
    with right:
        st.markdown("<div class='warn'><b>Deadline alert</b><br>Venue requests must be submitted 10 days in advance. As planning is on 5 November, an authorised exception is required for either proposed date.</div>", unsafe_allow_html=True)
        st.markdown("<div style='height:10px'></div><div class='good'><b>Best initial fit</b><br>Seminar Hall A on 13 November: estimated total ₹59,300, AV included, ₹700 remaining. This is conditional on approvals and deadline exception.</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Quick actions</div>", unsafe_allow_html=True)
    q1,q2,q3 = st.columns(3)
    with q1:
        if st.button("💬 Ask about a policy", use_container_width=True): st.session_state.quick_prompt = "How many days of casual leave can faculty take?"; st.session_state._page_jump = "AI Helpdesk"; st.rerun()
    with q2:
        if st.button("📊 Compare venues", use_container_width=True): st.session_state._page_jump = "Fest Planner"; st.rerun()
    with q3:
        if st.button("✅ Review approvals", use_container_width=True): st.session_state._page_jump = "Approvals & Audit"; st.rerun()

# ---------- AI Helpdesk ----------
elif page == "AI Helpdesk":
    hero("POLICY + CALCULATION ASSISTANT", "CampusMate Helpdesk", "Ask about the supplied university policies or run a quick calculation.")
    st.markdown("<div class='small-muted'>This prototype uses local policy retrieval and Python tools. It does not use an external AI model or invent answers outside the assignment data.</div>", unsafe_allow_html=True)
    with st.expander("Try an example question", expanded=not bool(st.session_state.messages)):
        examples = ["How many days of casual leave can faculty take?", "What time does the library close on Saturday?", "Can medical absence be condoned?", "Do we need HoD approval for the fest?", "Multiply 12 and 8.", "What is the venue request deadline?"]
        cols = st.columns(2)
        for i,ex in enumerate(examples):
            with cols[i%2]:
                if st.button(ex, key=f"ex_{i}", use_container_width=True): st.session_state.quick_prompt = ex
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])
    prompt = st.chat_input("Ask CampusMate about policies, the fest or a calculation...")
    if "quick_prompt" in st.session_state:
        prompt = st.session_state.pop("quick_prompt")
    if prompt:
        st.session_state.messages.append({"role":"user","content":prompt})
        agent = CampusMateAgent()
        answer, events, pending = agent.run(prompt)
        st.session_state.messages.append({"role":"assistant","content":answer})
        for e in events: add_log(e["status"],e["tool"],e["arguments"],e["result"])
        if pending: st.session_state.pending = pending
        st.rerun()
    if st.session_state.pending:
        p = st.session_state.pending
        st.warning(f"Simulated booking request: **{p['venue']}**, **{p['date']}**, estimated total **₹{p['total_cost']:,}**. No real booking has been made.")
        note = st.text_input("Approval note", key="chat_approval_note")
        a,b = st.columns(2)
        with a:
            if st.button("Approve simulated booking", type="primary", use_container_width=True):
                if note.strip():
                    result=confirm_booking(p,note); add_log("HUMAN_APPROVED","confirm_booking",p,result); st.session_state.pending=None; st.success(result["message"]); st.rerun()
                else: st.error("Add an approval note first.")
        with b:
            if st.button("Reject request", use_container_width=True):
                add_log("HUMAN_REJECTED","reject_booking",p,{"message":"Rejected by user"}); st.session_state.pending=None; st.rerun()

# ---------- Fest Planner ----------
elif page == "Fest Planner":
    hero("EVENT OPERATIONS", "Agentic Fest Planner", "A transparent plan with cost calculations, venue checks, policy constraints and fallback options.")
    a,b,c = st.columns(3)
    with a: metric("PARTICIPANTS", "120", "Assignment requirement")
    with b: metric("BUDGET", "₹60,000", "Maximum spend")
    with c: metric("FIXED COSTS", "₹49,300", "Before venue and extras")
    st.markdown("<div class='section-title'>1 · Fixed cost calculation</div>", unsafe_allow_html=True)
    fixed_rows = [
        {"Expense":"Lunch (120 × ₹180)","Working":"120 × ₹180","Cost":"₹21,600"},
        {"Expense":"Snacks (120 × ₹60)","Working":"120 × ₹60","Cost":"₹7,200"},
        {"Expense":"Guest speaker honorarium","Working":"Given amount","Cost":"₹10,000"},
        {"Expense":"Printing","Working":"Given amount","Cost":"₹3,000"},
        {"Expense":"Prizes","Working":"Given amount","Cost":"₹7,500"},
    ]
    st.dataframe(pd.DataFrame(fixed_rows), hide_index=True, use_container_width=True)
    st.markdown("<div class='good'>Fixed costs = <b>₹49,300</b> · Remaining for venue and extras = <b>₹10,700</b></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>2 · Venue comparison</div>", unsafe_allow_html=True)
    date_label = st.selectbox("Compare date", ["13 November 2026", "14 November 2026"], index=0)
    date = "2026-11-13" if date_label.startswith("13") else "2026-11-14"
    rows = []
    for r in compare_venues(120,60000,[date]):
        rows.append({"Venue":r["venue"],"Capacity":r["capacity"],"Venue + extras":f"₹{r['cost']-49300:,}","Total":f"₹{r['cost']:,}","Availability":"Free" if r["available"] else "Booked","AV":"Included" if r["av"] else "Not included","Weather":WEATHER[date],"Assessment":r["status"],"Reason":"; ".join(r["reasons"][:3])})
    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
    st.markdown("<div class='warn'><b>Mandatory deadline check:</b> Venue requests must be made 10 days ahead. For 13 November, the normal deadline was 3 November; for 14 November, it was 4 November. Both have passed as of 5 November. An authorised exception is needed before booking.</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>3 · Recommendation and recovery</div>", unsafe_allow_html=True)
    if date == "2026-11-13":
        st.markdown("<div class='good'><b>Initial recommendation: Seminar Hall A</b><br>Estimated total ₹59,300 · AV included · capacity 150 · clear forecast · ₹700 remaining. Recommendation is conditional on HoD approval, named faculty coordinator and authorised deadline exception.</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='warn'><b>14 November:</b> Seminar Hall A is within budget at ₹59,300 and indoors. The outdoor venue has a 70% rain risk and costs ₹74,300 with tent and sound. Main Auditorium exceeds budget.</div>", unsafe_allow_html=True)
    st.caption("Fallback: if Seminar Hall A becomes unavailable, Classroom Block on 13 November is estimated at ₹57,300, but consists of three separate rooms and needs a common-session feasibility check.")
    st.markdown("<div class='section-title'>4 · Prepare approval proposal</div>", unsafe_allow_html=True)
    coordinator = st.text_input("Named faculty coordinator", value=st.session_state.approval["coordinator"])
    if st.button("Simulate Seminar Hall A becoming unavailable", key="planner_failure"):
        result = simulate_seminar_failure(); add_log("SIMULATION", "simulate_seminar_failure", {}, result); st.warning("Seminar Hall A is now unavailable on both dates. Recheck the comparison."); st.rerun()
    if st.button("Prepare approval proposal", type="primary"):
        st.session_state.approval["coordinator"] = coordinator
        st.session_state.approval["proposal"] = bool(coordinator.strip())
        if not coordinator.strip(): st.error("A named faculty coordinator is required.")
        else:
            add_log("PROPOSAL_PREPARED","prepare_approval_proposal",{"coordinator":coordinator,"date":date_label},{"status":"Draft prepared; no booking made"})
            st.success("Proposal draft prepared. Complete the approval checklist before submitting a simulated booking request.")

# ---------- Approvals & Audit ----------
elif page == "Approvals & Audit":
    hero("CONTROL + TRACEABILITY", "Approvals & Audit Trail", "Track the approvals that must happen before any venue booking or spending commitment.")
    st.markdown("<div class='warn'><b>Prototype notice:</b> These are simulated approval records only. No university officer, venue team or supplier is contacted.</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Approval checklist</div>", unsafe_allow_html=True)
    ap = st.session_state.approval
    ap["hod"] = st.checkbox("HoD approval received", value=ap["hod"])
    ap["coordinator"] = st.text_input("Named faculty coordinator", value=ap["coordinator"])
    ap["exception"] = st.checkbox("Authorised exception for missed 10-day venue deadline received", value=ap["exception"])
    ap["proposal"] = st.checkbox("Final proposal and budget approved", value=ap["proposal"])
    ap["spending"] = st.checkbox("Spending approval received", value=ap["spending"])
    complete = ap["hod"] and bool(ap["coordinator"].strip()) and ap["exception"] and ap["proposal"] and ap["spending"]
    if complete: st.success("All required approval checks are marked complete.")
    else: st.info("Booking gate locked: complete all five requirements above.")
    st.markdown("<div class='section-title'>Booking gate</div>", unsafe_allow_html=True)
    st.write("Status:", "Ready for simulated request" if complete else "Not ready — approvals incomplete")
    if st.button("Submit simulated Seminar Hall A booking request", disabled=not complete):
        p={"venue":"Seminar Hall A","date":"2026-11-13","participants":120,"total_cost":59300}
        st.session_state.pending=p
        add_log("BOOKING_REQUEST_SUBMITTED","request_booking",p,{"status":"Pending simulated confirmation"})
        st.success("Simulated request submitted. This does not reserve the actual venue.")
    st.markdown("<div class='section-title'>Audit log</div>", unsafe_allow_html=True)
    logs=get_logs()
    if logs: st.dataframe(pd.DataFrame(logs),hide_index=True,use_container_width=True)
    else: st.caption("No actions recorded yet.")
    if logs:
        csv=pd.DataFrame(logs).to_csv(index=False).encode("utf-8")
        st.download_button("⬇ Download audit log CSV",csv,"campusmate_audit_log.csv","text/csv")
    if st.button("Clear audit log"):
        clear_logs(); st.rerun()

# ---------- Knowledge Base ----------
elif page == "Knowledge Base":
    hero("POLICY REFERENCE", "BBA Knowledge Base", "The policy facts supplied with the assignment, grouped for quick retrieval.")
    search=st.text_input("Search policies", placeholder="Try: attendance, leave, venue deadline, library...")
    filtered=[x for x in POLICY_CHUNKS if not search or search.lower() in (x["title"]+" "+x["text"]).lower()]
    for i,chunk in enumerate(filtered,1):
        with st.expander(f"{i:02d}  ·  {chunk['title']}",expanded=bool(search)):
            st.write(chunk["text"])
    st.markdown("<div class='info-card'><b>Knowledge limitation</b><br>The hostel curfew is not provided in the assignment data. CampusMate should say it cannot verify the timing rather than invent an answer. The 2025 casual-leave rule replaces the older 2022 limit.</div>",unsafe_allow_html=True)

st.markdown("<div style='margin-top:34px;padding-top:14px;border-top:1px solid #e6ebf1;color:#8995a5;font-size:.78rem'>CampusMate · BBA Department Agentic AI Fest · Academic prototype · All approvals and bookings are simulated</div>",unsafe_allow_html=True)
