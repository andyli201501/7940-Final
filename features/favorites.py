class FavoritesManager:
    def __init__(self, db_manager):
        self.db = db_manager
    
    async def add_to_favorites(self, telegram_id, place_name, place_type, location, notes=""):
        """Add a place to user favorites."""
        self.db.add_favorite(
            telegram_id=telegram_id,
            place_name=place_name,
            place_type=place_type,
            location=location,
            notes=notes
        )
        return f"✅ Successfully added \"{place_name}\" to your favorites!"
    
    async def view_favorites(self, telegram_id, place_type=None):
        """Display user's saved favorites."""
        favorites = self.db.get_favorites(telegram_id, place_type)
        
        if not favorites:
            return "⭐ You have no saved favorites yet."
        
        result = "⭐ My Favorites:\n\n"
        for fav in favorites:
            result += f"📍 {fav.place_name}\n"
            result += f"   Type: {fav.place_type}\n"
            if fav.location:
                result += f"   Location: {fav.location}\n"
            result += "\n"
        
        return result
