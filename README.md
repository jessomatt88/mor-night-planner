# MOR Night Planner

An MVP "plan my night" engine that scrapes NYC event sources, stores them in a lightweight database, analyzes user preferences, and generates a curated night itinerary.

## Features

- **Modular Scraper Framework**: Extensible architecture for adding new event sources
- **Multiple Event Sources**: 
  - Eventbrite
  - Posh
  - House of Yes
  - Slipper Room
  - Instagram (placeholder for future implementation)
- **SQLite Database**: Lightweight storage with indexed fields for fast queries
- **FastAPI Backend**: RESTful API with event filtering and night planning endpoints
- **Web UI**: Simple, elegant interface for planning your night
- **Smart Deduplication**: Automatically removes duplicate events across sources
- **Time-based Filtering**: Events organized by time windows (early evening, prime time, late night, after hours)

## Project Structure

```
mor-night-planner/
├── scraper/              # Event scraper modules
│   ├── base_scraper.py   # Base scraper class
│   ├── eventbrite_scraper.py
│   ├── posh_scraper.py
│   ├── house_of_yes_scraper.py
│   ├── slipper_room_scraper.py
│   └── instagram_scraper.py
├── pipeline/             # Data pipeline
│   └── run_scrape.py     # Main scraper orchestration
├── api/                  # FastAPI backend
│   └── main.py           # API endpoints
├── ui/                   # Frontend
│   └── index.html        # Web interface
├── utils/                # Utilities
│   └── database.py       # Database management
├── tests/                # Test files
├── .env.example          # Environment variables template
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/mor-night-planner.git
cd mor-night-planner
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install Playwright browsers (for web scraping):
```bash
playwright install chromium
```

5. Create environment file:
```bash
cp .env.example .env
```

## Usage

### 1. Run the Scrapers

Collect events from all configured sources:

```bash
python pipeline/run_scrape.py
```

This will:
- Run all scrapers
- Deduplicate events
- Store new events in the database
- Remove expired events

### 2. Launch the API

Start the FastAPI backend server:

```bash
cd api
python main.py
```

Or using uvicorn directly:
```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

### 3. Open the UI

Open the web interface in your browser:

```bash
# On macOS
open ui/index.html

# On Linux
xdg-open ui/index.html

# On Windows
start ui/index.html
```

Or simply open `ui/index.html` in your web browser.

## API Endpoints

### GET /events

Get all events, optionally filtered by date.

**Query Parameters:**
- `date` (optional): Date in YYYY-MM-DD format

**Response:**
```json
{
  "date": "2025-11-15",
  "total_events": 25,
  "time_windows": {
    "early_evening": [...],
    "prime_time": [...],
    "late_night": [...],
    "after_hours": [...]
  }
}
```

### POST /plan-night

Generate a curated night itinerary.

**Request Body:**
```json
{
  "date": "2025-11-15",
  "starting_location": "Brooklyn",
  "walking_radius": 1.0,
  "mood": "threshold"
}
```

**Mood Options:**
- `warm-up`: Early evening, chill vibes
- `threshold`: Prime time energy
- `climax`: Late night peak
- `afterglow`: After hours wind down

**Response:**
```json
{
  "date": "2025-11-15",
  "starting_location": "Brooklyn",
  "mood": "threshold",
  "itinerary": [
    {
      "time": "09:00 PM",
      "title": "Event Name",
      "location": "Venue Address",
      "description": "Event description...",
      "price": "$20",
      "url": "https://...",
      "tags": ["nightlife", "music"]
    }
  ],
  "total_events": 5
}
```

### GET /health

Health check endpoint.

## Architecture Overview

### Scraper Layer

The scraper framework uses an object-oriented design with a base class (`BaseScraper`) that all scrapers inherit from. Each scraper:

1. Implements the `scrape()` method
2. Returns events in a standardized format
3. Handles errors gracefully
4. Validates event data before returning

**Standard Event Format:**
```python
{
    "title": str,
    "description": str,
    "datetime": str (ISO format),
    "location": str,
    "price": str,
    "url": str,
    "tags": List[str]
}
```

### Database Layer

SQLite database with the following schema:

**events table:**
- `id`: Primary key
- `title`: Event title
- `description`: Event description
- `datetime`: Event date/time (indexed)
- `location`: Venue location (indexed)
- `price`: Ticket price
- `url`: Event URL
- `tags`: JSON array of tags (indexed)
- `source`: Source name (indexed)
- `raw_payload`: Full JSON payload
- `discovered_at`: Timestamp when scraped

**Indexes:**
- `idx_datetime`: Fast date-based queries
- `idx_location`: Location filtering
- `idx_source`: Source filtering
- `idx_tags`: Tag-based searches

### Pipeline Layer

The pipeline orchestrates the scraping process:

1. **Run Scrapers**: Execute all configured scrapers in sequence
2. **Deduplicate**: Remove duplicate events based on title, datetime, and source
3. **Store Events**: Insert new events into database (using UNIQUE constraint)
4. **Cleanup**: Remove events older than the target date window

### API Layer

FastAPI backend with two main endpoints:

1. **GET /events**: Returns events grouped by time windows
2. **POST /plan-night**: Uses rules-based heuristics to create a night plan

The night planning algorithm:
- Filters events by date
- Maps mood to preferred time windows
- Selects events matching the mood profile
- Sorts by time to create a logical progression
- Returns top 5 events as an itinerary

### UI Layer

Simple HTML/CSS/JavaScript frontend that:
- Provides a form for user input (date, location, mood)
- Calls the API to generate a night plan
- Displays results in an attractive, card-based layout
- Handles errors gracefully

## Development

### Adding a New Scraper

1. Create a new file in `scraper/` directory
2. Inherit from `BaseScraper`
3. Implement the `scrape()` method
4. Add to `scraper/__init__.py`
5. Add to scraper list in `pipeline/run_scrape.py`

Example:
```python
from scraper.base_scraper import BaseScraper

class NewVenueScraper(BaseScraper):
    def __init__(self):
        super().__init__('new_venue')
        self.base_url = 'https://example.com/events'
    
    def scrape(self):
        self.clear_events()
        # Scraping logic here
        return self.events
```

### Running Tests

```bash
pytest tests/
```

## Next Steps

### Immediate Improvements

1. **Enhanced Scrapers**: Implement full scraping logic for each source (currently using placeholders)
2. **Instagram Integration**: Add proper Instagram scraping with authentication
3. **Location-based Filtering**: Implement actual distance calculations using coordinates
4. **Error Handling**: Add retry logic and better error reporting

### AI Integration

1. **Event Ranking Model**: Train ML model to rank events based on user preferences
2. **Personalization**: Learn from user selections to improve recommendations
3. **Natural Language Processing**: Extract better event metadata (genre, vibe, dress code)
4. **Similarity Matching**: Group similar events and suggest alternatives

### Feature Enhancements

1. **User Accounts**: Save preferences and past itineraries
2. **Social Features**: Share night plans with friends
3. **Real-time Updates**: WebSocket support for live event updates
4. **Mobile App**: Native iOS/Android applications
5. **Calendar Integration**: Export itinerary to Google Calendar, iCal
6. **Notifications**: Alerts for new events matching preferences
7. **Reviews & Ratings**: Community feedback on events and venues

### Infrastructure

1. **Scheduled Scraping**: Cron job to run scrapers automatically
2. **Caching**: Redis cache for frequently accessed data
3. **Rate Limiting**: Protect API from abuse
4. **Authentication**: API keys for external access
5. **Deployment**: Docker containers and cloud hosting
6. **Monitoring**: Logging and error tracking (Sentry, DataDog)

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues, questions, or suggestions, please open an issue on GitHub.

## Acknowledgments

Built for the NYC nightlife community. Special thanks to all the venues and event organizers who make the city's nightlife amazing.
