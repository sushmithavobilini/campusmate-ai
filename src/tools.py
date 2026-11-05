from src.data import VENUES, EVENT_ITEMS, WEATHER, ORIGINAL_AVAILABILITY, POLICY_CHUNKS

def calculate_budget(n, venue=None):
    fixed = n*EVENT_ITEMS["lunch_per_person"] + n*EVENT_ITEMS["snacks_per_person"] + EVENT_ITEMS["guest_speaker"] + EVENT_ITEMS["printing"] + EVENT_ITEMS["prizes"]
    venue_extra = 0
    extras = []
    if venue:
        venue_extra = VENUES[venue]["cost"]
        if not VENUES[venue]["av"]:
            venue_extra += EVENT_ITEMS["sound_system"]; extras.append("Sound system")
        if venue == "Open-air Quadrangle":
            venue_extra += EVENT_ITEMS["outdoor_tent"]; extras.append("Outdoor tent")
    total = fixed + venue_extra
    return {"fixed_cost":fixed,"venue_extra":venue_extra,"extras":extras,"total":total,"remaining":60000-total}

def find_policy(question):
    q=question.lower()
    groups=[(["casual leave","earned leave","faculty leave","faculty members","leave"],0),(["attendance","medical","sick","condoned"],1),(["event","hod","venue","caterer","coordinator","approval","10 days"],2),(["library","close","opening","timing","saturday"],3)]
    for words,idx in groups:
        if any(w in q for w in words):
            return {"found":True,"chunk":POLICY_CHUNKS[idx]["title"],"text":POLICY_CHUNKS[idx]["text"]}
    return {"found":False,"text":"The knowledge base does not contain this information."}

def compare_venues(n=120,budget=60000,dates=None):
    dates=dates or ["2026-11-13","2026-11-14"]
    out=[]
    for date in dates:
        for name,v in VENUES.items():
            cost=calculate_budget(n,name)["total"]
            available=v["availability"][date]=="free"
            capacity=v["capacity"]>=n
            within=cost<=budget
            status="Conditional" if available and capacity and within else "Impossible"
            reasons=[]
            if not available: reasons.append("Already booked")
            if not capacity: reasons.append("Insufficient capacity")
            if not within: reasons.append("Over budget")
            if date=="2026-11-14" and name=="Open-air Quadrangle": reasons.append("70% rain risk")
            if name=="Classroom Block": reasons.append("Three separate rooms; common-session coordination needed")
            reasons.append("10-day venue request deadline has passed as of 5 November 2026; authorised exception required")
            out.append({"venue":name,"date":date,"cost":cost,"available":available,"capacity":v["capacity"],"av":v["av"],"status":status,"reasons":reasons})
    return out

def simulate_seminar_failure():
    VENUES["Seminar Hall A"]["availability"]["2026-11-13"]="booked"
    VENUES["Seminar Hall A"]["availability"]["2026-11-14"]="booked"
    return {"message":"Seminar Hall A marked booked on both dates."}

def reset_venue_data():
    for name,dates in ORIGINAL_AVAILABILITY.items(): VENUES[name]["availability"]=dates.copy()
    return {"message":"Original venue availability restored."}

# Backward-compatible alias for earlier project versions.
def reset_venues():
    return reset_venue_data()

def request_booking(venue,date,n=120,budget=60000):
    v=VENUES[venue]; cost=calculate_budget(n,venue)["total"]
    if v["availability"][date]!="free": return {"ok":False,"reason":"Venue unavailable"}
    if v["capacity"]<n: return {"ok":False,"reason":"Insufficient capacity"}
    if cost>budget: return {"ok":False,"reason":"Over budget"}
    return {"approval_required":True,"venue":venue,"date":date,"total_cost":cost,"participants":n}

def confirm_booking(pending,note):
    v=VENUES[pending["venue"]]
    if v["availability"][pending["date"]]!="free": return {"success":False,"message":"Venue availability changed. Booking not confirmed."}
    v["availability"][pending["date"]]="booked"
    return {"success":True,"message":"Simulated booking confirmed. This is not a real university reservation.","approval_note":note}
