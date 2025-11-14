#!/usr/bin/env python3
"""
FastAPI backend for MOR Night Planner
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.database import Database

app = FastAPI(title="MOR Night Planner API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db = Database()


class PlanNightRequest(BaseModel):
    date: str
    starting_location: str
    walking_radius: float = 1.0
    mood: str = "threshold"


class Event(BaseModel):
    id: int
    title: str
    description: Optional[str]
    datetime: str
    location: Optional[str]
    price: Optional[str]
    url: Optional[str]
    tags: List[str]
    source: str


class NightPlan(BaseModel):
    date: str
    starting_location: str
    mood: str
    itinerary: List[dict]
    total_events: int


@app.get("/")
def read_root():
    """Root endpoint"""
    return {
        "message": "MOR Night Planner API",
        "version": "1.0.0",
        "endpoints": [
            "/events",
            "/plan-night"
        ]
    }


@app.get("/events")
def get_events(date: Optional[str] = Query(None, description="Date in YYYY-MM-DD format")):
    """
    Get events, optionally filtered by date.
    Returns events grouped by time window.
    """
    try:
        events = db.get_events(date=date)
        
        time_windows = {
            "early_evening": [],
            "prime_time": [],
            "late_night": [],
            "after_hours": []
        }
        
        for event in events:
            try:
                event_dt = datetime.fromisoformat(event['datetime'].replace('Z', '+00:00'))
                hour = event_dt.hour
                
                if 18 <= hour < 21:
                    time_windows["early_evening"].append(event)
                elif 21 <= hour < 24:
                    time_windows["prime_time"].append(event)
                elif 0 <= hour < 3:
                    time_windows["late_night"].append(event)
                else:
                    time_windows["after_hours"].append(event)
            except:
                time_windows["prime_time"].append(event)
        
        return {
            "date": date,
            "total_events": len(events),
            "time_windows": time_windows
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/plan-night")
def plan_night(request: PlanNightRequest):
    """
    Generate a curated night itinerary based on user preferences.
    Uses rules-based heuristics to create a progression through the night.
    """
    try:
        events = db.get_events(date=request.date)
        
        if not events:
            raise HTTPException(
                status_code=404,
                detail=f"No events found for date {request.date}"
            )
        
        mood_mapping = {
            "warm-up": ["early_evening", "prime_time"],
            "threshold": ["prime_time", "late_night"],
            "climax": ["late_night", "after_hours"],
            "afterglow": ["after_hours", "late_night"]
        }
        
        preferred_windows = mood_mapping.get(request.mood, ["prime_time", "late_night"])
        
        itinerary = []
        
        for event in events[:10]:
            try:
                event_dt = datetime.fromisoformat(event['datetime'].replace('Z', '+00:00'))
                hour = event_dt.hour
                
                time_category = None
                if 18 <= hour < 21:
                    time_category = "early_evening"
                elif 21 <= hour < 24:
                    time_category = "prime_time"
                elif 0 <= hour < 3:
                    time_category = "late_night"
                else:
                    time_category = "after_hours"
                
                if time_category in preferred_windows:
                    itinerary.append({
                        "time": event_dt.strftime("%I:%M %p"),
                        "title": event['title'],
                        "location": event.get('location', 'TBD'),
                        "description": event.get('description', '')[:200],
                        "price": event.get('price', 'See website'),
                        "url": event.get('url', ''),
                        "tags": event.get('tags', []),
                        "time_category": time_category
                    })
            except:
                continue
        
        itinerary.sort(key=lambda x: x['time'])
        
        return {
            "date": request.date,
            "starting_location": request.starting_location,
            "mood": request.mood,
            "itinerary": itinerary[:5],
            "total_events": len(itinerary),
            "message": f"Your {request.mood} night plan for {request.date}"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database_events": db.get_event_count()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
