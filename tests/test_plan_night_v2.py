#!/usr/bin/env python3
"""
Test script for /plan-night-v2 endpoint
"""

import sys
import os
import requests
import json
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.database import Database

def seed_test_data():
    """Seed the database with test events"""
    db = Database()
    
    test_events = [
        {
            'title': 'Jazz Night at Blue Note',
            'description': 'Intimate jazz performance with dinner service',
            'start_datetime': '2025-11-20T20:00:00',
            'end_datetime': '2025-11-20T23:00:00',
            'venue_name': 'Blue Note',
            'neighborhood': 'West Village',
            'city': 'New York',
            'price_min': 35.0,
            'price_max': 50.0,
            'url': 'https://example.com/blue-note',
            'source_platform': 'test',
            'raw_tags': ['jazz', 'music', 'seated', 'dinner']
        },
        {
            'title': 'Techno Warehouse Party',
            'description': 'All night techno rave with international DJs',
            'start_datetime': '2025-11-20T23:00:00',
            'end_datetime': '2025-11-21T06:00:00',
            'venue_name': 'Warehouse NYC',
            'neighborhood': 'Bushwick',
            'city': 'New York',
            'price_min': 25.0,
            'price_max': 40.0,
            'url': 'https://example.com/warehouse',
            'source_platform': 'test',
            'raw_tags': ['techno', 'edm', 'rave', 'club', 'dance']
        },
        {
            'title': 'Burlesque Show at House of Yes',
            'description': 'Immersive burlesque performance with circus acts',
            'start_datetime': '2025-11-20T21:00:00',
            'end_datetime': '2025-11-20T23:30:00',
            'venue_name': 'House of Yes',
            'neighborhood': 'Bushwick',
            'city': 'New York',
            'price_min': 20.0,
            'price_max': 40.0,
            'url': 'https://example.com/hoy',
            'source_platform': 'test',
            'raw_tags': ['burlesque', 'performance', 'immersive', 'show']
        },
        {
            'title': 'Comedy Show at Comedy Cellar',
            'description': 'Stand-up comedy with surprise guests',
            'start_datetime': '2025-11-20T20:30:00',
            'end_datetime': '2025-11-20T22:30:00',
            'venue_name': 'Comedy Cellar',
            'neighborhood': 'West Village',
            'city': 'New York',
            'price_min': 15.0,
            'price_max': 25.0,
            'url': 'https://example.com/comedy',
            'source_platform': 'test',
            'raw_tags': ['comedy', 'stand-up', 'seated']
        },
        {
            'title': 'Live Music at Harlem Jazz Club',
            'description': 'Local jazz band with soul food menu',
            'start_datetime': '2025-11-20T19:00:00',
            'end_datetime': '2025-11-20T22:00:00',
            'venue_name': 'Harlem Jazz Club',
            'neighborhood': 'Harlem',
            'city': 'New York',
            'price_min': 20.0,
            'price_max': 35.0,
            'url': 'https://example.com/harlem-jazz',
            'source_platform': 'test',
            'raw_tags': ['jazz', 'music', 'seated', 'dinner']
        }
    ]
    
    print("Seeding test data...")
    for event in test_events:
        db.insert_event(event)
    
    print(f"Seeded {len(test_events)} test events")
    return len(test_events)

def test_plan_night_v2():
    """Test the /plan-night-v2 endpoint"""
    
    api_url = "http://localhost:8000/plan-night-v2"
    
    test_cases = [
        {
            "name": "Low energy, wants dinner, from Harlem",
            "payload": {
                "date": "2025-11-20",
                "start_time": "19:00",
                "end_time": "23:00",
                "home_base": "Harlem",
                "max_travel_minutes": 30,
                "energy_level": "low",
                "dress_code": "smart_casual",
                "wants_dinner": True,
                "crowd_preference": "30_plus_preferred"
            }
        },
        {
            "name": "High energy, from Bushwick",
            "payload": {
                "date": "2025-11-20",
                "start_time": "22:00",
                "end_time": "04:00",
                "home_base": "Bushwick",
                "max_travel_minutes": 20,
                "energy_level": "high",
                "dress_code": "very_casual",
                "wants_dinner": False,
                "crowd_preference": "mixed_ok"
            }
        },
        {
            "name": "Medium energy, from West Village",
            "payload": {
                "date": "2025-11-20",
                "start_time": "20:00",
                "end_time": "23:30",
                "home_base": "West Village",
                "max_travel_minutes": 45,
                "energy_level": "medium",
                "dress_code": "smart_casual",
                "wants_dinner": False,
                "crowd_preference": "no_preference"
            }
        }
    ]
    
    print("\n" + "="*60)
    print("Testing /plan-night-v2 endpoint")
    print("="*60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i}: {test_case['name']} ---")
        print(f"Payload: {json.dumps(test_case['payload'], indent=2)}")
        
        try:
            response = requests.post(api_url, json=test_case['payload'])
            
            if response.status_code == 200:
                result = response.json()
                print(f"\n✓ Success! Got {len(result.get('recommendations', []))} recommendations")
                
                for j, rec in enumerate(result.get('recommendations', [])[:3], 1):
                    print(f"\n  Recommendation {j}:")
                    print(f"    Title: {rec.get('title')}")
                    print(f"    Venue: {rec.get('venue_name')} ({rec.get('neighborhood')})")
                    print(f"    Price: ${rec.get('price_min')}-${rec.get('price_max')}")
                    print(f"    Why: {rec.get('why_this')}")
            else:
                print(f"\n✗ Error: Status {response.status_code}")
                print(f"  Response: {response.text}")
        
        except Exception as e:
            print(f"\n✗ Exception: {e}")
    
    print("\n" + "="*60)
    print("Testing complete!")
    print("="*60)

if __name__ == '__main__':
    print("MOR Night Planner - /plan-night-v2 Test Script")
    print("="*60)
    
    seed_count = seed_test_data()
    
    print("\nWaiting for API server to be ready...")
    print("Make sure the API server is running on http://localhost:8000")
    print("\nPress Enter to continue with tests...")
    input()
    
    test_plan_night_v2()
