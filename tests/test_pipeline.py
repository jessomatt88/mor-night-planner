#!/usr/bin/env python3
"""
Test script to verify the pipeline works with mock data
"""

import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.database import Database


def create_mock_events():
    """Create mock events for testing"""
    db = Database()
    
    base_date = datetime.now()
    
    mock_events = [
        {
            'title': 'House of Yes: Cosmic Disco',
            'description': 'An immersive disco experience with live performers and cosmic vibes',
            'datetime': (base_date.replace(hour=22, minute=0)).isoformat(),
            'location': 'House of Yes, 2 Wyckoff Ave, Brooklyn, NY 11237',
            'price': '$25',
            'url': 'https://www.houseofyes.org/events/cosmic-disco',
            'tags': ['nightlife', 'house_of_yes', 'disco', 'immersive'],
            'source': 'house_of_yes'
        },
        {
            'title': 'Slipper Room: Burlesque Extravaganza',
            'description': 'Classic burlesque show with variety acts',
            'datetime': (base_date.replace(hour=21, minute=30)).isoformat(),
            'location': 'Slipper Room, 167 Orchard St, New York, NY 10002',
            'price': '$20',
            'url': 'https://www.slipperroom.com/shows',
            'tags': ['nightlife', 'slipper_room', 'burlesque', 'variety'],
            'source': 'slipper_room'
        },
        {
            'title': 'Brooklyn Warehouse Party',
            'description': 'Underground techno party in Bushwick warehouse',
            'datetime': (base_date.replace(hour=23, minute=0)).isoformat(),
            'location': 'Secret Location, Brooklyn, NY',
            'price': '$15',
            'url': 'https://www.eventbrite.com/e/warehouse-party',
            'tags': ['nightlife', 'techno', 'warehouse', 'brooklyn'],
            'source': 'eventbrite'
        },
        {
            'title': 'Posh Rooftop Experience',
            'description': 'Exclusive rooftop party with skyline views',
            'datetime': (base_date.replace(hour=20, minute=0)).isoformat(),
            'location': 'Manhattan, NY',
            'price': '$40',
            'url': 'https://www.posh.vip/events/rooftop',
            'tags': ['nightlife', 'posh', 'rooftop', 'exclusive'],
            'source': 'posh'
        },
        {
            'title': 'Late Night Jazz Session',
            'description': 'Intimate jazz performance in the Village',
            'datetime': (base_date.replace(hour=1, minute=0) + timedelta(days=1)).isoformat(),
            'location': 'Village Vanguard, New York, NY',
            'price': '$30',
            'url': 'https://www.eventbrite.com/e/jazz-session',
            'tags': ['nightlife', 'jazz', 'live_music', 'village'],
            'source': 'eventbrite'
        }
    ]
    
    print("Adding mock events to database...")
    inserted = db.insert_events(mock_events)
    print(f"Inserted {inserted} mock events")
    
    print(f"\nTotal events in database: {db.get_event_count()}")
    
    print("\nRetrieving events...")
    events = db.get_events()
    for event in events:
        print(f"  - {event['title']} at {event['datetime']}")
    
    return db


if __name__ == '__main__':
    create_mock_events()
    print("\nMock data created successfully!")
