class RecommendationEngine:
    def __init__(self, llm_client, db_manager):
        self.llm = llm_client
        self.db = db_manager
    
    async def recommend_places(self, telegram_id, destination, place_type, preferences=None):
        """Recommend attractions, restaurants, or hotels."""
        type_map = {
            "attractions": "attractions",
            "restaurants": "restaurants",
            "hotels": "hotels",
            "activities": "activities"
        }
        
        prompt = f"""Please recommend {type_map.get(place_type, place_type)} in {destination}.

Requirements:
- Destination: {destination}
- Type: {type_map.get(place_type, place_type)}
- Preferences: {preferences if preferences else 'No specific preferences'}

Please provide 5-10 recommendations, each including:
1. Name
2. Brief description
3. Highlights/Special features
4. Price range ($/$$/$$$)
5. Location/Area

Keep the format clear and easy to read.
"""
        
        response = self.llm.submit(prompt)
        return response
