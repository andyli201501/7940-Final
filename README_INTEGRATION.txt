=========================================
INTEGRATION INSTRUCTIONS FOR MEMBER 3
=========================================

Hi! Here are the files for the Bot Development (done by GU Yuxian).

1. COPY FILES
   - Copy the `database/` folder to the root of your repository.
   - Copy the `features/` folder to the root of your repository.
   - REPLACE the existing `chatbot.py` with the one in this package.

2. UPDATE DEPENDENCIES
   Add these lines to your `requirements.txt`:
   - sqlalchemy==2.0.25
   - psycopg2-binary==2.9.9
   - python-dotenv==1.0.0
   Then run: pip install -r requirements.txt

3. CONFIGURATION
   - Ensure your `config.ini` has [TELEGRAM] and [CHATGPT] sections.
   - The bot defaults to a local SQLite database (`travelbot.db`).
   - If you want to use the AWS RDS database, set the `DATABASE_URL` environment variable.

4. TESTING
   - Run: python chatbot.py
   - Test commands:
     /start
     /plan Tokyo 5 days medium food,shopping
     /recommend Paris attractions
     /favorites
     /history

All code is written in English.
Let me know if you encounter any merge conflicts!
