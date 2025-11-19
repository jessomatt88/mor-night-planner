"""
Fallback sample events for local testing and demos.

This module provides curated sample events that are inserted into the database
when all scrapers fail to return events. This ensures the UI always has something
to recommend during development and testing.

TODO: Remove or disable this fallback once real scrapers are working reliably.
Set environment variable MOR_ENABLE_FALLBACK=0 to disable.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any
import os


def get_sample_events() -> List[Dict[str, Any]]:
    """
    Returns 10 curated sample events for NYC nightlife.
    
    These events are set to near-future dates (today + 1-7 days) to ensure
    they appear in the planner UI regardless of when the pipeline runs.
    
    Returns:
        List of event dictionaries matching the normalized schema
    """
    
    today = datetime.now()
    dates = [today + timedelta(days=i) for i in range(1, 8)]
    
    sample_events = [
        {
            'title': 'Jazz Night at Blue Note',
            'description': 'Intimate jazz performance featuring Grammy-nominated artists. Dinner service available with reservations. Dress code: smart casual.',
            'start_datetime': f'{dates[0].strftime("%Y-%m-%d")}T20:00:00',
            'end_datetime': f'{dates[0].strftime("%Y-%m-%d")}T23:00:00',
            'venue_name': 'Blue Note Jazz Club',
            'neighborhood': 'West Village',
            'city': 'New York',
            'price_min': 35.0,
            'price_max': 50.0,
            'url': 'https://www.bluenote.net/newyork/',
            'source_platform': 'fallback_sample',
            'raw_tags': ['jazz', 'music', 'seated', 'dinner', '30_plus']
        },
        {
            'title': 'Burlesque Extravaganza',
            'description': 'Immersive burlesque show with circus acts, aerial performances, and live music. Full bar and light bites available.',
            'start_datetime': f'{dates[1].strftime("%Y-%m-%d")}T21:00:00',
            'end_datetime': f'{dates[1].strftime("%Y-%m-%d")}T23:30:00',
            'venue_name': 'House of Yes',
            'neighborhood': 'Bushwick',
            'city': 'New York',
            'price_min': 20.0,
            'price_max': 40.0,
            'url': 'https://www.houseofyes.org/',
            'source_platform': 'fallback_sample',
            'raw_tags': ['burlesque', 'performance', 'immersive', 'show', '30_plus', 'dance']
        },
        {
            'title': 'Underground Techno Night',
            'description': 'All-night techno party with international DJs. Warehouse vibes, serious sound system, and a dedicated dance floor.',
            'start_datetime': f'{dates[2].strftime("%Y-%m-%d")}T23:00:00',
            'end_datetime': f'{dates[3].strftime("%Y-%m-%d")}T06:00:00',
            'venue_name': 'Elsewhere',
            'neighborhood': 'Bushwick',
            'city': 'New York',
            'price_min': 25.0,
            'price_max': 40.0,
            'url': 'https://www.elsewherebrooklyn.com/',
            'source_platform': 'fallback_sample',
            'raw_tags': ['techno', 'edm', 'rave', 'club', 'dance', 'electronic']
        },
        {
            'title': 'Comedy Cellar Late Show',
            'description': 'Stand-up comedy with surprise celebrity drop-ins. Two-drink minimum. Shows often sell out.',
            'start_datetime': f'{dates[2].strftime("%Y-%m-%d")}T20:30:00',
            'end_datetime': f'{dates[2].strftime("%Y-%m-%d")}T22:30:00',
            'venue_name': 'Comedy Cellar',
            'neighborhood': 'West Village',
            'city': 'New York',
            'price_min': 15.0,
            'price_max': 25.0,
            'url': 'https://www.comedycellar.com/',
            'source_platform': 'fallback_sample',
            'raw_tags': ['comedy', 'stand-up', 'seated', '30_plus']
        },
        {
            'title': 'Salsa Dancing Social',
            'description': 'Beginner-friendly salsa night with free lesson at 8pm, then social dancing until late. Live band performs from 10pm.',
            'start_datetime': f'{dates[3].strftime("%Y-%m-%d")}T20:00:00',
            'end_datetime': f'{dates[4].strftime("%Y-%m-%d")}T01:00:00',
            'venue_name': 'SOB\'s',
            'neighborhood': 'SoHo',
            'city': 'New York',
            'price_min': 20.0,
            'price_max': 30.0,
            'url': 'https://www.sobs.com/',
            'source_platform': 'fallback_sample',
            'raw_tags': ['salsa', 'dance', 'latin', 'music', 'social']
        },
        {
            'title': 'Rooftop Cocktails & DJ Set',
            'description': 'Sunset cocktails with panoramic city views. Resident DJ spins house and disco. Dress code enforced.',
            'start_datetime': f'{dates[4].strftime("%Y-%m-%d")}T19:00:00',
            'end_datetime': f'{dates[4].strftime("%Y-%m-%d")}T23:00:00',
            'venue_name': 'Le Bain',
            'neighborhood': 'Chelsea',
            'city': 'New York',
            'price_min': 30.0,
            'price_max': 50.0,
            'url': 'https://www.standardhotels.com/new-york/properties/high-line',
            'source_platform': 'fallback_sample',
            'raw_tags': ['rooftop', 'cocktails', 'dj', 'house', 'disco', '30_plus']
        },
        {
            'title': 'Live Soul Music Dinner Show',
            'description': 'Three-course dinner with live soul and R&B performances. Intimate venue with excellent acoustics.',
            'start_datetime': f'{dates[5].strftime("%Y-%m-%d")}T19:30:00',
            'end_datetime': f'{dates[5].strftime("%Y-%m-%d")}T22:00:00',
            'venue_name': 'Minton\'s Playhouse',
            'neighborhood': 'Harlem',
            'city': 'New York',
            'price_min': 40.0,
            'price_max': 60.0,
            'url': 'https://www.mintonsharlem.com/',
            'source_platform': 'fallback_sample',
            'raw_tags': ['soul', 'rnb', 'music', 'dinner', 'seated', '30_plus']
        },
        {
            'title': 'Indie Rock Concert',
            'description': 'Local indie bands and touring acts. Standing room, full bar, and a killer sound system.',
            'start_datetime': f'{dates[5].strftime("%Y-%m-%d")}T21:00:00',
            'end_datetime': f'{dates[6].strftime("%Y-%m-%d")}T00:00:00',
            'venue_name': 'Bowery Ballroom',
            'neighborhood': 'Lower East Side',
            'city': 'New York',
            'price_min': 25.0,
            'price_max': 35.0,
            'url': 'https://www.boweryballroom.com/',
            'source_platform': 'fallback_sample',
            'raw_tags': ['indie', 'rock', 'concert', 'music', 'live']
        },
        {
            'title': 'Karaoke Night',
            'description': 'Private karaoke rooms and open mic stage. Full menu and extensive drink selection. No cover charge.',
            'start_datetime': f'{dates[6].strftime("%Y-%m-%d")}T20:00:00',
            'end_datetime': f'{dates[6].strftime("%Y-%m-%d")}T02:00:00',
            'venue_name': 'Karaoke Duet',
            'neighborhood': 'Koreatown',
            'city': 'New York',
            'price_min': 0.0,
            'price_max': 0.0,
            'url': 'https://www.karaokeduet.com/',
            'source_platform': 'fallback_sample',
            'raw_tags': ['karaoke', 'social', 'singing', 'fun']
        },
        {
            'title': 'Deep House Warehouse Party',
            'description': 'Underground deep house and minimal techno. Secret location revealed 24h before. BYOB friendly.',
            'start_datetime': f'{dates[6].strftime("%Y-%m-%d")}T23:30:00',
            'end_datetime': f'{dates[0].strftime("%Y-%m-%d")}T05:00:00',
            'venue_name': 'Secret Warehouse',
            'neighborhood': 'Williamsburg',
            'city': 'New York',
            'price_min': 20.0,
            'price_max': 30.0,
            'url': 'https://www.residentadvisor.net/events/us/newyork',
            'source_platform': 'fallback_sample',
            'raw_tags': ['deep house', 'techno', 'warehouse', 'underground', 'dance', 'electronic']
        }
    ]
    
    return sample_events


def is_fallback_enabled() -> bool:
    """
    Check if fallback events are enabled via environment variable.
    
    Returns:
        True if fallback is enabled (default), False otherwise
    """
    return os.getenv('MOR_ENABLE_FALLBACK', '1') == '1'
