VENUES = {
    "Main Auditorium": {"capacity": 400, "cost": 35000, "av": True,
        "availability": {"2026-11-13": "booked", "2026-11-14": "free"}},
    "Seminar Hall A": {"capacity": 150, "cost": 10000, "av": True,
        "availability": {"2026-11-13": "free", "2026-11-14": "free"}},
    "Open-air Quadrangle": {"capacity": 300, "cost": 5000, "av": False,
        "availability": {"2026-11-13": "free", "2026-11-14": "free"}},
    "Classroom Block": {"capacity": 150, "cost": 0, "av": False,
        "availability": {"2026-11-13": "free", "2026-11-14": "booked"}, "rooms": 3}
}
ORIGINAL_AVAILABILITY = {
    "Main Auditorium": {"2026-11-13": "booked", "2026-11-14": "free"},
    "Seminar Hall A": {"2026-11-13": "free", "2026-11-14": "free"},
    "Open-air Quadrangle": {"2026-11-13": "free", "2026-11-14": "free"},
    "Classroom Block": {"2026-11-13": "free", "2026-11-14": "booked"}
}
EVENT_ITEMS = {
    "lunch_per_person": 180, "snacks_per_person": 60,
    "guest_speaker": 10000, "printing": 3000, "prizes": 7500,
    "sound_system": 8000, "outdoor_tent": 12000
}
WEATHER = {"2026-11-13": "Clear", "2026-11-14": "70% chance of rain"}
POLICY_CHUNKS = [
    {"title": "Faculty leave policy", "text": "Faculty members are entitled to 12 days of casual leave per academic year effective 2025, replacing the 2022 limit of 10 days. Faculty earn 15 days of earned leave per year, and up to 30 days may be carried forward. Leave applications must be submitted through the HR portal at least 3 working days in advance."},
    {"title": "Student attendance policy", "text": "Students need 75% attendance. Up to 10% may be condoned for medical reasons if a certificate is submitted within 7 days of returning."},
    {"title": "Event approval and venue policy", "text": "Any student event with more than 100 participants needs Head of Department approval and a named faculty coordinator. Venue requests must be made 10 days ahead. Food at university events must come from approved caterers only."},
    {"title": "Library timings", "text": "The library is open 8 AM to 10 PM on weekdays and 9 AM to 5 PM on Saturdays."}
]
