import re
from src.tools import calculate_budget, find_policy, compare_venues, request_booking

class CampusMateAgent:
    """Local rule-based agent workflow: routes requests to policy, calculator and event-planning tools."""
    def run(self, prompt):
        q = prompt.lower().strip()
        events, pending = [], None

        policy_terms = ["leave", "attendance", "medical", "sick", "library", "hostel", "curfew", "caterer", "hod", "faculty", "policy", "coordinator", "venue request", "10 days"]
        event_terms = ["plan", "fest", "event", "venue", "booking", "budget", "participant", "students"]
        is_event = any(t in q for t in event_terms)

        # Handle direct arithmetic without confusing the numbers in policy/event prompts.
        if any(t in q for t in ["multiply", "calculate", "percent of", "what is"]):
            nums = [int(x.replace(",", "")) for x in re.findall(r"\d[\d,]*", prompt)]
            if len(nums) >= 2 and ("multiply" in q or "percent" in q or "%" in q):
                if "multiply" in q:
                    value = nums[0] * nums[1]
                    result = {"calculation": f"{nums[0]} × {nums[1]}", "answer": value}
                else:
                    value = nums[0] * nums[1] / 100
                    result = {"calculation": f"{nums[0]}% of {nums[1]}", "answer": value}
                events.append({"status":"TOOL_EXECUTED","tool":"calculator","arguments":{"numbers":nums[:2]},"result":result})
                return f"**Calculation:** {result['calculation']} = **{result['answer']:,.2f}**", events, None

        # Event planning takes priority when the query is about the fest.
        if is_event:
            nums = [int(x.replace(",", "")) for x in re.findall(r"\d[\d,]*", prompt)]
            participants, budget = 120, 60000
            if any(w in q for w in ["students", "participants", "people"]):
                if nums: participants = nums[0]
            if "budget" in q and nums:
                budget = nums[-1]
            comparison = compare_venues(participants, budget)
            events.append({"status":"TOOL_EXECUTED","tool":"compare_venues","arguments":{"participants":participants,"budget":budget},"result":comparison})
            fixed = calculate_budget(participants)["fixed_cost"]
            lines = [f"## Event plan for {participants} students", f"**Budget:** ₹{budget:,}", f"**Fixed costs:** ₹{fixed:,}", "", "| Venue | Date | Estimated total | Availability | Assessment |", "|---|---|---:|---|---|"]
            for x in comparison:
                lines.append(f"| {x['venue']} | {x['date']} | ₹{x['cost']:,} | {'Free' if x['available'] else 'Booked'} | {x['status']} |")
            lines += ["", "**Policy checks:** More than 100 participants requires HoD approval and a named faculty coordinator. Venue requests must be made 10 days ahead. As planning is on 5 November 2026, the normal deadlines for 13 and 14 November have passed; an authorised exception is required."]
            viable = [x for x in comparison if x["available"] and x["capacity"] >= participants and x["cost"] <= budget]
            if viable:
                preferred = sorted(viable, key=lambda x: (not x["av"], x["cost"]))[0]
                lines += ["", f"**Initial recommendation:** {preferred['venue']} on {preferred['date']}. Total ₹{preferred['cost']:,}; remaining ₹{budget-preferred['cost']:,}.", "This is conditional. Confirm approvals, the deadline exception and operational suitability before booking."]
                if "book" in q:
                    pending = request_booking(preferred["venue"], preferred["date"], participants, budget)
                    events.append({"status":"TOOL_EXECUTED","tool":"request_booking","arguments":{"venue":preferred["venue"],"date":preferred["date"],"participants":participants,"budget":budget},"result":pending})
                    lines.append("A simulated booking request is pending human approval. No actual venue has been booked.")
            else:
                lines += ["", "**Recommendation:** No venue currently satisfies all the selected constraints. Change the date, budget or requirements."]
            return "\n".join(lines), events, pending

        if any(t in q for t in policy_terms):
            result = find_policy(prompt)
            events.append({"status":"TOOL_EXECUTED","tool":"retrieve_policy","arguments":{"question":prompt},"result":result})
            if not result["found"]:
                return "I couldn't verify this from the supplied BBA assignment policies, so I won't guess. The hostel curfew, for example, is not included in the knowledge base.", events, None
            return f"**Source: {result['chunk']}**\n\n{result['text']}", events, None

        return ("I can help with the Agentic AI Fest plan, venue and budget comparisons, approval requirements, faculty leave, student attendance and library timings. Try one of the example questions.", events, None)
