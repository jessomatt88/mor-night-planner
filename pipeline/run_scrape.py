#!/usr/bin/env python3
"""
Pipeline script to run all scrapers, deduplicate events, and store in database.
"""

import sys
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from scraper import (
    EventbriteScraper,
    PoshScraper,
    HouseOfYesScraper,
    SlipperRoomScraper,
    InstagramScraper,
    ShotgunScraper,
    ViewcyScraper
)
from utils.database import Database


def deduplicate_events(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Deduplicate events based on title, start_datetime, and venue_name.
    This allows cross-platform deduplication when the same event appears on multiple sources.
    """
    seen = set()
    unique_events = []
    
    for event in events:
        title_normalized = event.get('title', '').lower().strip()
        
        start_datetime = event.get('start_datetime', '')
        date_part = start_datetime.split('T')[0] if 'T' in start_datetime else start_datetime[:10]
        
        venue_normalized = event.get('venue_name', '').lower().strip()
        
        key = (title_normalized, date_part, venue_normalized)
        
        if key not in seen:
            seen.add(key)
            unique_events.append(event)
        else:
            print(f"  Skipping duplicate: {event.get('title')} at {event.get('venue_name')} on {date_part}")
    
    return unique_events


def run_all_scrapers() -> List[Dict[str, Any]]:
    """
    Run all scrapers and collect events.
    """
    print("Starting scraper pipeline...")
    print("-" * 50)
    
    all_events = []
    
    scrapers = [
        HouseOfYesScraper(),
        SlipperRoomScraper(),
        EventbriteScraper(),
        ShotgunScraper(),
        ViewcyScraper(),
        PoshScraper(),
        InstagramScraper()
    ]
    
    for scraper in scrapers:
        print(f"\nRunning {scraper.source_name} scraper...")
        try:
            events = scraper.scrape()
            print(f"  Found {len(events)} events from {scraper.source_name}")
            all_events.extend(events)
        except Exception as e:
            print(f"  Error running {scraper.source_name} scraper: {e}")
    
    print(f"\nTotal events collected: {len(all_events)}")
    
    unique_events = deduplicate_events(all_events)
    print(f"Unique events after deduplication: {len(unique_events)}")
    
    return unique_events


def cleanup_old_events(db: Database, days_back: int = 1):
    """
    Remove events older than the specified number of days.
    """
    cutoff_date = (datetime.now() - timedelta(days=days_back)).isoformat()
    deleted_count = db.delete_old_events(cutoff_date)
    print(f"Deleted {deleted_count} expired events (older than {days_back} days)")


def main():
    """
    Main pipeline execution.
    """
    print("=" * 50)
    print("MOR Night Planner - Scraper Pipeline")
    print("=" * 50)
    
    db = Database()
    
    print(f"\nCurrent events in database: {db.get_event_count()}")
    
    events = run_all_scrapers()
    
    print("\n" + "-" * 50)
    print("Storing events in database...")
    
    inserted_count = db.insert_events(events)
    print(f"Inserted {inserted_count} new events into database")
    
    print("\n" + "-" * 50)
    print("Cleaning up old events...")
    cleanup_old_events(db, days_back=1)
    
    print("\n" + "-" * 50)
    print(f"Final event count in database: {db.get_event_count()}")
    
    print("\n" + "=" * 50)
    print("Pipeline completed successfully!")
    print("=" * 50)


if __name__ == '__main__':
    main()
