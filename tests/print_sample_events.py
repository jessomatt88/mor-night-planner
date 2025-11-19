#!/usr/bin/env python3
"""
Sanity-check script to verify database contents.

This script prints:
- Total number of events in the database
- Breakdown by source_platform
- Sample rows showing venue_name, title, start_datetime, source_platform

Usage:
    python tests/print_sample_events.py
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.database import Database


def print_sample_events():
    """Print database statistics and sample events"""
    
    db = Database()
    
    print("=" * 70)
    print("MOR Night Planner - Database Sanity Check")
    print("=" * 70)
    
    total_count = db.get_event_count()
    print(f"\nTotal events in database: {total_count}")
    
    if total_count == 0:
        print("\n⚠️  Database is empty!")
        print("Run: python pipeline/run_scrape.py")
        return
    
    events = db.get_events()
    
    source_counts = {}
    for event in events:
        source = event.get('source_platform', 'unknown')
        source_counts[source] = source_counts.get(source, 0) + 1
    
    print("\nBreakdown by source_platform:")
    for source, count in sorted(source_counts.items()):
        print(f"  {source}: {count} events")
    
    print("\n" + "-" * 70)
    print("Sample Events:")
    print("-" * 70)
    
    for i, event in enumerate(events[:5], 1):
        print(f"\n{i}. {event.get('title', 'Untitled')}")
        print(f"   Venue: {event.get('venue_name', 'TBD')}")
        print(f"   Neighborhood: {event.get('neighborhood', 'N/A')}")
        print(f"   Date/Time: {event.get('start_datetime', 'N/A')}")
        print(f"   Price: ${event.get('price_min', 0)}-${event.get('price_max', 0)}")
        print(f"   Source: {event.get('source_platform', 'unknown')}")
        print(f"   URL: {event.get('url', 'N/A')}")
    
    if len(events) > 5:
        print(f"\n... and {len(events) - 5} more events")
    
    print("\n" + "=" * 70)
    print("Sanity check complete!")
    print("=" * 70)


if __name__ == '__main__':
    try:
        print_sample_events()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
