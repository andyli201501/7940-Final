import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from ChatGPT_HKBU import ChatGPT
from database.db_manager import DatabaseManager
from features.itinerary import ItineraryPlanner
from features.recommendation import RecommendationEngine
from features.favorites import FavoritesManager
import configparser
import os
import re
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TravelBot:
    def __init__(self, config_path='config.ini'):
        self.config = configparser.ConfigParser()
        self.config.read(config_path)
        
        # Initialize database
        db_url = os.getenv('DATABASE_URL', 'sqlite:///travelbot.db')
        self.db = DatabaseManager(db_url)
        
        # Initialize LLM
        self.llm = ChatGPT(self.config)
        
        # Initialize features
        self.itinerary_planner = ItineraryPlanner(self.llm, self.db)
        self.recommendation = RecommendationEngine(self.llm, self.db)
        self.favorites = FavoritesManager(self.db)
        
        # Create bot application
        token = self.config['TELEGRAM']['ACCESS_TOKEN']
        self.app = Application.builder().token(token).build()
        
        # Setup handlers
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup command and message handlers."""
        self.app.add_handler(CommandHandler("start", self.start))
        self.app.add_handler(CommandHandler("help", self.help))
        self.app.add_handler(CommandHandler("plan", self.plan_itinerary))
        self.app.add_handler(CommandHandler("recommend", self.recommend))
        self.app.add_handler(CommandHandler("favorites", self.show_favorites))
        self.app.add_handler(CommandHandler("history", self.show_history))
        self.app.add_handler(CommandHandler("save", self.save_place))  # ✅ ADDED
        self.app.add_handler(CommandHandler("chathistory", self.chat_history))
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        user = update.effective_user
        self.db.get_or_create_user(user.id, user.username)
        
        welcome_message = """
👋 Welcome to the Travel Itinerary Assistant!

I can help you:
✈️ Plan travel itineraries
🏛️ Recommend attractions, restaurants, and hotels
⭐ Save your favorite places
📋 View your history

Commands:
/plan - Plan an itinerary
/recommend - Get recommendations
/favorites - View saved favorites
/history - View past itineraries
/save - Save a place to favorites
/help - Show this help message

Tell me where you want to travel!
"""
        await update.message.reply_text(welcome_message)
    
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Display help information."""
        help_text = """
📖 User Guide:

1️⃣ Plan an Itinerary:
   /plan Tokyo 5 days medium food,shopping
   
2️⃣ Get Recommendations:
   /recommend Paris attractions
   
3️⃣ Save a Place:
   /save Eiffel Tower attractions
   
4️⃣ View Favorites:
   /favorites
   
5️⃣ View History:
   /history
   /history 1 (view details of #1)

💡 Tips:
- Budget levels: low, medium, high
- Recommendation types: attractions, restaurants, hotels, activities
"""
        await update.message.reply_text(help_text)
    
    async def plan_itinerary(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle itinerary planning request."""
        try:
            args = context.args
            
            if len(args) < 4:
                await update.message.reply_text(
                    "❌ Usage: /plan <destination> <days> <budget> [interests]\n\n"
                    "Example: /plan Tokyo 5 days medium food,shopping"
                )
                return
            
            full_text = ' '.join(args)
            match = re.search(r'(\d+)\s*(?:days?)?\s*(low|medium|high)', full_text, re.IGNORECASE)
            
            if not match:
                await update.message.reply_text(
                    "❌ Could not parse days and budget. Example: /plan Tokyo 5 days medium food"
                )
                return
            
            days_num = int(match.group(1))
            budget_val = match.group(2).lower()
            
            parts = full_text.split(match.group(0))
            destination = parts[0].strip()
            interests_part = parts[1].strip() if len(parts) > 1 else ""
            interests_val = [i.strip() for i in interests_part.split(',') if i.strip()] if interests_part else []
            
            await update.message.reply_text("🤔 Planning your itinerary, please wait...")
            
            user_id = update.effective_user.id
            itinerary = await self.itinerary_planner.plan_itinerary(
                telegram_id=user_id,
                destination=destination,
                days=days_num,
                budget=budget_val,
                interests=interests_val
            )
            
            self.db.log_chat(
                telegram_id=user_id,
                message=f"/plan {destination} {days_num} days {budget_val}",
                response=itinerary[:500],
                feature_type='plan'
            )
            
            for i in range(0, len(itinerary), 4000):
                await update.message.reply_text(itinerary[i:i+4000])
        
        except ValueError as e:
            logger.error(f"Value error: {e}")
            await update.message.reply_text("❌ Days must be a number")
        except Exception as e:
            logger.error(f"Itinerary planning error: {e}")
            await update.message.reply_text("❌ An error occurred, please try again later")
    
    async def recommend(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle recommendation request."""
        try:
            args = context.args
            
            if len(args) < 2:
                await update.message.reply_text(
                    "❌ Usage: /recommend <destination> <type> [preferences]\n\n"
                    "Example: /recommend Paris attractions romantic,photo"
                )
                return
            
            destination = args[0]
            place_type = args[1].lower()
            preferences = args[2] if len(args) > 2 else None
            
            await update.message.reply_text("🔍 Searching for recommendations...")
            
            user_id = update.effective_user.id
            response = await self.recommendation.recommend_places(
                telegram_id=user_id,
                destination=destination,
                place_type=place_type,
                preferences=preferences
            )
            
            self.db.log_chat(
                telegram_id=user_id,
                message=f"/recommend {destination} {place_type}",
                response=response[:500],
                feature_type='recommend'
            )

            for i in range(0, len(response), 4000):
                await update.message.reply_text(response[i:i+4000])
        
        except Exception as e:
            logger.error(f"Recommendation error: {e}")
            await update.message.reply_text("❌ An error occurred, please try again later")
    
    async def show_favorites(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Display user favorites."""
        try:
            args = context.args
            place_type = args[0] if args else None
            
            user_id = update.effective_user.id
            response = await self.favorites.view_favorites(user_id, place_type)
            
            await update.message.reply_text(response)
        
        except Exception as e:
            logger.error(f"Show favorites error: {e}")
            await update.message.reply_text("❌ An error occurred")
    
    async def show_history(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Display itinerary history or details of a specific one."""
        user_id = update.effective_user.id
        itineraries = self.db.get_user_itineraries(user_id)
        
        if not itineraries:
            await update.message.reply_text("📋 You have no saved itineraries yet. Use /plan to start!")
            return
        
        args = context.args
        if args and args[0].isdigit():
            # View specific itinerary
            idx = int(args[0]) - 1
            if 0 <= idx < len(itineraries):
                selected = itineraries[idx]
                plan_text = selected.itinerary_data
                if isinstance(plan_text, dict):
                    plan_text = plan_text.get("plan", "No detailed plan available.")
                else:
                    plan_text = str(plan_text)
                
                header = f"📅 Itinerary #{idx+1}: {selected.destination}\n\n"
                
                # Send in chunks if too long
                for i in range(0, len(plan_text), 4000):
                    chunk = plan_text[i:i+4000]
                    if i == 0:
                        await update.message.reply_text(header + chunk)
                    else:
                        await update.message.reply_text(chunk)
            else:
                await update.message.reply_text(
                    f"❌ Index {args[0]} out of range. You have {len(itineraries)} itineraries."
                )
        else:
            # Show list view
            result = "📋 Your Itinerary History (use `/history 1` to view details):\n\n"
            for i, itin in enumerate(itineraries[-5:], 1):
                result += f"{i}. {itin.destination} ({itin.days} days) - {itin.created_at.strftime('%Y-%m-%d')}\n"
            await update.message.reply_text(result)
    
    async def save_place(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Save a place to favorites."""
        try:
            args = context.args
            
            if len(args) < 1:
                await update.message.reply_text(
                    "❌ Usage: /save <place_name> [type]\n\n"
                    "Example: /save Eiffel Tower attractions"
                )
                return
            
            # Last word is type, rest is name
            place_type = args[-1].lower() if len(args) > 1 else "attraction"
            place_name = ' '.join(args[:-1]) if len(args) > 1 else args[0]
            
            user_id = update.effective_user.id
            
            await self.favorites.add_to_favorites(
                telegram_id=user_id,
                place_name=place_name,
                place_type=place_type,
                location="",
                notes="Saved from recommendation"
            )
            
            await update.message.reply_text(f"✅ Saved \"{place_name}\" to your favorites!")
        
        except Exception as e:
            logger.error(f"Save error: {e}")
            await update.message.reply_text("❌ Could not save this place.")
    
    async def chat_history(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Display user's chat history."""
        user_id = update.effective_user.id
        logs = self.db.get_chat_history(user_id, limit=15)
        
        if not logs:
            await update.message.reply_text("📭 You have no chat history yet.")
            return
        
        result = "📜 Your recent conversations:\n\n"
        for i, log in enumerate(logs, 1):
            result += f"{i}. 🗣 You: {log.message[:50]}\n"
            result += f"   🤖 Bot: {log.response[:50]}\n"
            if log.feature_type:
                result += f"   🏷️ Type: {log.feature_type}\n"
            result += f"   🕒 {log.timestamp.strftime('%Y-%m-%d %H:%M')}\n\n"
            
            # Telegram limits a single message to 4096 characters and allows for batch sending
            if len(result) > 3500:
                await update.message.reply_text(result)
                result = ""
        
        if result:
            await update.message.reply_text(result)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages."""
        user_id = update.effective_user.id
        message = update.message.text
        
        try:
            response = self.llm.submit(f"User said: {message}")
            # ordinary conversation，feature_type=None
            self.db.log_chat(user_id, message, response, feature_type=None)
            await update.message.reply_text(response)
        except Exception as e:
            logger.error(f"Message handling error: {e}")
            await update.message.reply_text("Sorry, I encountered an issue. Please try again later.")
    
    def run(self):
        """Start the bot."""
        logger.info("🤖 Travel Assistant starting...")
        self.app.run_polling(drop_pending_updates=True)

def main():
    bot = TravelBot()
    bot.run()

if __name__ == '__main__':
    main()