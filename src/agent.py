import re
from src.tools import calculate_budget, find_policy, compare_venues, request_booking

class CampusMateAgent:
    """Rule-based agent loop: detects intent, invokes Python tools, evaluates constraints, and requests approval."""
    def run(self, prompt):
        q = prompt.lower()
        events, pending = [], None

        # Policy question route (retrieval tool)
        policy_terms = ["leave", "attendance", "medical", "library", "hostel", "curfew", "caterer", "hod", "faculty", "policy"]
        if any(t in q for t in policy_terms) and not any(t in q for t in ["plan", "fest", "event", "venue", "budget"]):
            result = find_policy(prompt)
            events.append({"status":"TOOL_EXECUTED","tool":"retrieve_policy","arguments":{"question":prompt},"result":result})
            if not result["found"]:
                return "I couldn't find this information in the CampusMate knowledge base. I won't guess the answer.", events, None
            return f"**Retrieved from: {result['chunk']}**\n\n{result['text']}", events, None

        # Calculator route
        if any(t in q for t in ["calculate", "what is", "multiply", "budget"]) and not any(t in q for t in ["plan", "fest", "event", "venue"]):
            nums = [int(x.replace(",", "")) for x in re.findall(r"\d[\d,]*", prompt)]
            if len(nums) >= 2 and ("multiply" in q or "percent" in q or "%" in q):
                if "multiply" in q:
                    result = {"calculation": f"{nums[0]} × {nums[1]}", "answer": nums[0]*nums[1]}
                else:
                    result = {"calculation": f"{nums[0]}% of {nums[1]}", "answer": nums[0]*nums[1]/100}
                events.append({"status":"TOOL_EXECUTED","tool":"calculator","arguments":{"numbers":nums},"result":result})
                return f"**Calculation:** {result['calculation']} = **{result['answer']:,.2f}**", events, None

        # Event planning route
        if any(t in q for t in ["plan", "fest", "event", "venue", "booking"]):
            nums = [int(x.replace(",", "")) for x in re.findall(r"\d[\d,]*", prompt)]
            participants = 120
            budget = 60000
            if nums:
                if any(word in q for word in ["students", "participants", "people"]):
                    participants = nums[0]
                if "budget" in q and len(nums) > 1:
                    budget = nums[-1]
            comparison = compare_venues(participants, budget)
            events.append({"status":"TOOL_EXECUTED","tool":"compare_venues","arguments":{"participants":participants,"budget":budget},"result":comparison})
            fixed = calculate_budget(participants)["fixed_cost"]
            viable = [x for x in comparison if x["available"] and x["capacity"] >= participants and x["cost"] <= budget]
            lines = [
                f"## Event plan for {participants} students",
                f"**Budget:** ₹{budget:,}",
                f"**Fixed event costs:** ₹{fixed:,} (lunch, snacks, speaker, printing and prizes)",
                "",
                "| Venue | Date | Total | Status |",
                "|---|---|---:|---|"
            ]
            for x in comparison:
                lines.append(f"| {x['venue']} | {x['date']} | ₹{x['cost']:,} | {x['status']} |")
            lines += ["", "**Policy check:** Events above 100 participants need HoD approval and a named faculty coordinator. Venue requests must be made 10 days ahead. As the planning date is 5 November 2026, neither 13 nor 14 November meets the 10-day requirement without an approved exception."]
            if viable:
                preferred = sorted(viable, key=lambda x: (not x["av"], x["cost"]))[0]
                lines += ["", f"**Recommended option:** {preferred['venue']} on {preferred['date']}.",
                          f"Total estimated cost: ₹{preferred['cost']:,}; remaining budget: ₹{budget-preferred['cost']:,}.",
                          "This is a conditional recommendation. Confirm the faculty coordinator, HoD approval, venue deadline and operational suitability before booking."]
            else:
                lines += ["", "**Recommendation:** No option currently satisfies all constraints. Revise the date, budget or requirements."]
            if "book" in q:
                if viable:
                    preferred = sorted(viable, key=lambda x: (not x["av"], x["cost"]))[0]
                    pending = request_booking(preferred["venue"], preferred["date"], participants, budget)
                    events.append({"status":"TOOL_EXECUTED","tool":"request_booking","arguments":{"venue":preferred["venue"],"date":preferred["date"],"participants":participants,"budget":budget},"result":pending})
                    lines += ["", "A simulated booking request is ready, but no booking has been made. Human approval is required."]
            return "\n".join(lines), events, pending

        return ("I can help with event planning, venue comparison, budget calculations and the supplied faculty/student policies. "
                "Try asking me to plan the Agentic AI Fest or ask a policy question."), events, None
