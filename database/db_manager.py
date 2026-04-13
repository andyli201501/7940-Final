from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base, User, Itinerary, Favorite, ChatLog
from datetime import datetime
import json
import os

class DatabaseManager:
    def __init__(self, database_url=None):
        """Initialize database connection."""
        self.database_url = database_url or os.getenv('DATABASE_URL', 'sqlite:///travelbot.db')
        self.engine = create_engine(self.database_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
    
    def get_session(self):
        """Get a database session."""
        return self.Session()
    
    def get_or_create_user(self, telegram_id, username=None):
        """Get existing user or create a new one."""
        session = self.get_session()
        user = session.query(User).filter_by(telegram_id=telegram_id).first()
        
        if not user:
            user = User(telegram_id=telegram_id, username=username)
            session.add(user)
            session.commit()
        
        session.close()
        return user
    
    def save_itinerary(self, telegram_id, destination, days, budget, interests, itinerary_data):
        """Save a generated itinerary to the database."""
        session = self.get_session()
        itinerary = Itinerary(
            telegram_id=telegram_id,
            destination=destination,
            days=days,
            budget=budget,
            interests=json.dumps(interests) if isinstance(interests, list) else interests,
            itinerary_data=itinerary_data
        )
        session.add(itinerary)
        session.commit()
        session.close()
        return itinerary
    
    def get_user_itineraries(self, telegram_id):
        """Retrieve all itineraries for a specific user."""
        session = self.get_session()
        itineraries = session.query(Itinerary).filter_by(telegram_id=telegram_id).all()
        session.close()
        return itineraries
    
    def add_favorite(self, telegram_id, place_name, place_type, location, notes=""):
        """Add a place to user's favorites."""
        session = self.get_session()
        favorite = Favorite(
            telegram_id=telegram_id,
            place_name=place_name,
            place_type=place_type,
            location=location,
            notes=notes
        )
        session.add(favorite)
        session.commit()
        session.close()
        return favorite
    
    def get_favorites(self, telegram_id, place_type=None):
        """Retrieve user's favorites, optionally filtered by type."""
        session = self.get_session()
        query = session.query(Favorite).filter_by(telegram_id=telegram_id)
        
        if place_type:
            query = query.filter_by(place_type=place_type)
        
        favorites = query.all()
        session.close()
        return favorites
    
    def log_chat(self, telegram_id, message, response, feature_type=None):
        """Log a conversation exchange."""
        session = self.get_session()
        log = ChatLog(
            telegram_id=telegram_id,
            message=message,
            response=response,
            feature_type=feature_type
        )
        session.add(log)
        session.commit()
        session.close()

    def get_chat_history(self, telegram_id, limit=20):
        """Get recent chat history for a user."""
        session = self.get_session()
        logs = session.query(ChatLog).filter_by(
            telegram_id=telegram_id
        ).order_by(
            ChatLog.timestamp.desc()
        ).limit(limit).all()
        session.close()
        return logs