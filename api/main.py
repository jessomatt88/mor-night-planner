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


class PlanNightV2Request(BaseModel):
    date: str
    start_time: str
    end_time: str
    home_base: str
    max_travel_minutes: int
    energy_level: str
    dress_code: str = "smart_casual"
    wants_dinner: bool = False
    crowd_preference: str = "no_preference"


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


@app.post("/plan-night-v2")
def plan_night_v2(request: PlanNightV2Request):
    """
    Generate a curated night itinerary with AI-ish planning logic.
    Uses heuristics based on energy level, travel time, crowd preference, and other factors.
    """
    try:
        events = db.get_events(date=request.date)
        
        if not events:
            return {
                "date": request.date,
                "home_base": request.home_base,
                "max_travel_minutes": request.max_travel_minutes,
                "energy_level": request.energy_level,
                "wants_dinner": request.wants_dinner,
                "recommendations": []
            }
        
        neighborhood_distances = {
            'harlem': {'harlem': 0, 'upper west side': 15, 'upper east side': 20, 'midtown': 25, 
                      'chelsea': 35, 'east village': 40, 'lower east side': 45, 'brooklyn': 50, 'bushwick': 60},
            'upper west side': {'upper west side': 0, 'harlem': 15, 'midtown': 15, 'upper east side': 20,
                               'chelsea': 25, 'east village': 35, 'lower east side': 40, 'brooklyn': 45, 'bushwick': 55},
            'upper east side': {'upper east side': 0, 'harlem': 20, 'midtown': 15, 'upper west side': 20,
                               'chelsea': 30, 'east village': 25, 'lower east side': 30, 'brooklyn': 40, 'bushwick': 50},
            'midtown': {'midtown': 0, 'upper west side': 15, 'upper east side': 15, 'chelsea': 10,
                       'east village': 20, 'lower east side': 25, 'brooklyn': 35, 'bushwick': 45, 'harlem': 25},
            'chelsea': {'chelsea': 0, 'midtown': 10, 'east village': 15, 'west village': 10, 'soho': 15,
                       'lower east side': 20, 'brooklyn': 30, 'bushwick': 40, 'harlem': 35},
            'east village': {'east village': 0, 'lower east side': 10, 'chelsea': 15, 'midtown': 20,
                            'brooklyn': 25, 'bushwick': 35, 'williamsburg': 20, 'harlem': 40},
            'lower east side': {'lower east side': 0, 'east village': 10, 'soho': 15, 'brooklyn': 20,
                               'williamsburg': 15, 'bushwick': 30, 'chelsea': 20, 'harlem': 45},
            'brooklyn': {'brooklyn': 0, 'bushwick': 15, 'williamsburg': 10, 'lower east side': 20,
                        'east village': 25, 'chelsea': 30, 'midtown': 35, 'harlem': 50},
            'bushwick': {'bushwick': 0, 'williamsburg': 10, 'brooklyn': 15, 'lower east side': 30,
                        'east village': 35, 'chelsea': 40, 'midtown': 45, 'harlem': 60},
            'williamsburg': {'williamsburg': 0, 'bushwick': 10, 'brooklyn': 10, 'lower east side': 15,
                            'east village': 20, 'chelsea': 30, 'midtown': 35, 'harlem': 50},
        }
        
        venues_30_plus = ['house of yes', 'slipper room', 'jazz standard', 'blue note', 'village vanguard']
        
        intense_keywords = ['edm', 'rave', 'techno', 'bass', 'warehouse', 'club', 'dj']
        seated_keywords = ['dinner', 'show', 'theater', 'burlesque', 'comedy', 'jazz', 'seated']
        
        def calculate_travel_time(home_base_lower, event_neighborhood_lower):
            if not event_neighborhood_lower or event_neighborhood_lower == 'tbd':
                return 30
            
            if home_base_lower in neighborhood_distances and event_neighborhood_lower in neighborhood_distances[home_base_lower]:
                return neighborhood_distances[home_base_lower][event_neighborhood_lower]
            
            return 35
        
        def score_event(event):
            score = 50.0
            reasons = []
            
            event_neighborhood = (event.get('neighborhood') or '').lower()
            home_base_lower = request.home_base.lower()
            
            travel_time = calculate_travel_time(home_base_lower, event_neighborhood)
            
            if travel_time <= request.max_travel_minutes:
                score += 20
                reasons.append(f"within {request.max_travel_minutes} min travel")
            elif travel_time <= request.max_travel_minutes + 15:
                score += 10
                reasons.append(f"slightly outside travel range ({travel_time} min)")
            else:
                score -= 20
                reasons.append(f"far from home base ({travel_time} min)")
            
            title_lower = (event.get('title') or '').lower()
            desc_lower = (event.get('description') or '').lower()
            tags = event.get('raw_tags') or []
            tags_lower = [t.lower() for t in tags]
            
            is_intense = any(kw in title_lower or kw in desc_lower or kw in tags_lower for kw in intense_keywords)
            is_seated = any(kw in title_lower or kw in desc_lower or kw in tags_lower for kw in seated_keywords)
            
            if request.energy_level == 'low':
                if is_seated:
                    score += 25
                    reasons.append("seated/show style (good for low energy)")
                if is_intense:
                    score -= 30
                    reasons.append("too intense for low energy")
                if request.wants_dinner and is_seated:
                    score += 15
                    reasons.append("dinner-friendly")
            elif request.energy_level == 'medium':
                if is_seated:
                    score += 10
                    reasons.append("good mix of seated and standing")
                if is_intense:
                    score -= 10
            elif request.energy_level == 'high':
                if is_intense:
                    score += 25
                    reasons.append("high energy event")
                if is_seated:
                    score -= 15
                    reasons.append("too seated for high energy")
            
            venue_lower = (event.get('venue_name') or '').lower()
            if request.crowd_preference == '30_plus_preferred':
                if any(v in venue_lower for v in venues_30_plus):
                    score += 20
                    reasons.append("known for 30+ crowd")
                elif 'college' in title_lower or 'student' in title_lower:
                    score -= 20
                    reasons.append("younger crowd")
            
            start_time_str = event.get('start_datetime', '')
            try:
                event_dt = datetime.fromisoformat(start_time_str.replace('Z', '+00:00'))
                event_time = event_dt.strftime('%H:%M')
                
                if request.start_time <= event_time <= request.end_time:
                    score += 15
                    reasons.append("within your time window")
                else:
                    score -= 10
            except:
                pass
            
            price_min = event.get('price_min')
            if price_min is not None:
                if price_min == 0:
                    score += 5
                    reasons.append("free event")
                elif price_min < 20:
                    score += 3
            
            return score, reasons
        
        scored_events = []
        for event in events:
            score, reasons = score_event(event)
            scored_events.append((score, event, reasons))
        
        scored_events.sort(key=lambda x: x[0], reverse=True)
        
        recommendations = []
        for score, event, reasons in scored_events[:10]:
            try:
                start_datetime_str = event.get('start_datetime', '')
                event_dt = datetime.fromisoformat(start_datetime_str.replace('Z', '+00:00'))
                
                why_this = "; ".join(reasons[:3]) if reasons else "Matches your preferences"
                
                recommendations.append({
                    "title": event.get('title'),
                    "start_datetime": start_datetime_str,
                    "venue_name": event.get('venue_name'),
                    "neighborhood": event.get('neighborhood'),
                    "city": event.get('city', 'New York'),
                    "price_min": event.get('price_min'),
                    "price_max": event.get('price_max'),
                    "url": event.get('url'),
                    "source_platform": event.get('source_platform'),
                    "why_this": why_this
                })
            except Exception as e:
                continue
        
        return {
            "date": request.date,
            "home_base": request.home_base,
            "max_travel_minutes": request.max_travel_minutes,
            "energy_level": request.energy_level,
            "wants_dinner": request.wants_dinner,
            "recommendations": recommendations
        }
    
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
