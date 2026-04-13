from datetime import datetime

class ItineraryPlanner:
    def __init__(self, llm_client, db_manager):
        self.llm = llm_client
        self.db = db_manager
    
    async def plan_itinerary(self, telegram_id, destination, days, budget, interests):
        """Generate a travel itinerary based on user preferences."""
        prompt = f"""You are a professional travel planner. Please create a detailed {days}-day travel itinerary for {destination}.

User Preferences:
- Destination: {destination}
- Duration: {days} days
- Budget Level: {self._translate_budget(budget)}
- Interests: {', '.join(interests) if isinstance(interests, list) else interests}

Please format the itinerary as follows:

[Day 1]
Morning: [Activity]
Lunch: [Restaurant Suggestion]
Afternoon: [Activity]
Evening: [Dinner and Night Activity]

[Day 2]
...

Include:
1. Specific attraction names
2. Suggested transportation methods
3. Estimated costs
4. Practical tips
"""
        
        response = self.llm.submit(prompt)
        
        itinerary_data = {
            "destination": destination,
            "days": days,
            "budget": budget,
            "interests": interests,
            "plan": response,
            "created_at": datetime.now().isoformat()
        }
        
        self.db.save_itinerary(
            telegram_id=telegram_id,
            destination=destination,
            days=days,
            budget=budget,
            interests=interests,
            itinerary_data=itinerary_data
        )
        
        return response
    
    def _translate_budget(self, budget):
        """Translate budget codes to readable descriptions."""
        budget_map = {
            "low": "Economy (Low Budget)",
            "medium": "Comfortable (Medium Budget)",
            "high": "Luxury (High Budget)"
        }
        return budget_map.get(budget, "Comfortable (Medium Budget)")
