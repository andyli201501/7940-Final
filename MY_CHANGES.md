# GU Yuxian (25418513) Contribution: Bot Development

**Date:** April 11, 2026
**Role:** Backend Bot Logic & Feature Implementation

## Files Added/Modified

### New Modules Created:
1.  `database/` (Database Models & Manager)
    *   `models.py`: Defines User, Itinerary, Favorite, and ChatLog tables.
    *   `db_manager.py`: Handles all SQL operations (CRUD).
2.  `features/` (Bot Features)
    *   `itinerary.py`: Logic for generating travel plans via LLM.
    *   `recommendation.py`: Logic for suggesting places.
    *   `favorites.py`: Logic for saving/viewing favorites.

### Main File Updated:
*   `chatbot.py`:
    *   Integrated DatabaseManager.
    *   Added command handlers: `/plan`, `/recommend`, `/favorites`, `/history`, `/save`.
    *   Implemented smart argument parsing for `/plan` (e.g., "Tokyo 5 days medium").
    *   Fixed async/sync handling for the `ChatGPT` class (using `.submit()`).
    *   Added message chunking for long responses.

## Features Implemented

1.  **Travel Planning (`/plan`)**
    *   Users can specify destination, days, budget (low/med/high), and interests.
    *   Plans are automatically saved to the database.
2.  **Recommendations (`/recommend`)**
    *   Users can ask for specific types of places (attractions, restaurants).
3.  **Favorites (`/save`, `/favorites`)**
    *   Users can save specific places from recommendations.
    *   View saved places using `/favorites`.
4.  **History (`/history`)**
    *   View a list of past generated itineraries.
    *   View full details using `/history <index>`.
5.  **Database Integration**
    *   Full persistence using SQLAlchemy.
    *   Supports SQLite (local) and PostgreSQL (via URL env var).

## Testing Results
*   Bot starts successfully.
*   `/start` creates a user record.
*   `/plan` generates and saves an itinerary.
*   `/history` retrieves saved data.
*   `/recommend` calls the LLM and formats results.

## Notes for Member 3
*   Ensure `requirements.txt` includes `sqlalchemy` and `psycopg2-binary`.
*   The `ChatGPT` class uses a synchronous `submit()` method, so do not add `await` before it.
