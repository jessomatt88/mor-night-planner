from .base_scraper import BaseScraper
from typing import List, Dict, Any
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import re
from zoneinfo import ZoneInfo


class HouseOfYesScraper(BaseScraper):
    """Scraper for House of Yes events - parses event info from calendar HTML"""
    
    def __init__(self):
        super().__init__('house_of_yes')
        self.base_url = 'https://www.houseofyes.org/calendar'
    
    def scrape(self) -> List[Dict[str, Any]]:
        """
        Scrape events from House of Yes calendar page.
        Extracts event titles, dates, and links directly from the HTML.
        """
        self.clear_events()
        
        try:
            print("Fetching House of Yes calendar page...")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(self.base_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            shotgun_links = soup.select('a[href*="shotgun.live/events/"]')
            
            event_urls = list(set([link.get('href') for link in shotgun_links if link.get('href')]))
            print(f"Found {len(event_urls)} unique Shotgun event URLs")
            
            if len(event_urls) == 0:
                print("No Shotgun events found, using default events")
                return self._get_default_events()
            
            for url in event_urls[:10]:
                try:
                    event_data = self._parse_event_from_url(url)
                    if event_data:
                        self.events.append(event_data)
                        print(f"  ✓ Parsed: {event_data['title']} on {event_data['datetime'][:10]}")
                except Exception as e:
                    print(f"  ✗ Failed to parse {url}: {e}")
                    continue
            
            if len(self.events) == 0:
                print("No events successfully parsed, using default events")
                return self._get_default_events()
            
            print(f"Successfully scraped {len(self.events)} House of Yes events")
            
        except Exception as e:
            print(f"Error scraping House of Yes: {e}")
            return self._get_default_events()
        
        return self.events
    
    def _parse_event_from_url(self, url: str) -> Dict[str, Any]:
        """Parse event details from Shotgun URL slug"""
        if '/events/' not in url:
            return None
        
        slug = url.split('/events/')[-1].split('?')[0]
        
        date_match = re.search(
            r'(january|february|march|april|may|june|july|august|september|october|november|december)-(\d{1,2})-(\d{4})$',
            slug,
            re.IGNORECASE
        )
        
        if not date_match:
            return None
        
        month_name = date_match.group(1).capitalize()
        day = date_match.group(2)
        year = date_match.group(3)
        
        title_slug = slug[:date_match.start()].rstrip('-')
        title = title_slug.replace('-', ' ').title()
        
        date_str = f"{month_name} {day}, {year} 9:00 PM"
        dt = datetime.strptime(date_str, "%B %d, %Y %I:%M %p")
        eastern = dt.replace(tzinfo=ZoneInfo('America/New_York'))
        
        return self.create_event(
            title=title,
            description=f'Live event at House of Yes. Get tickets at Shotgun.',
            datetime_str=eastern.isoformat(),
            location='House of Yes, 2 Wyckoff Ave, Brooklyn, NY 11237',
            price='Varies',
            url=url,
            tags=['nightlife', 'house_of_yes', 'live_music', 'performance', 'brooklyn']
        )
    
    def _get_default_events(self) -> List[Dict[str, Any]]:
        """Return default recurring House of Yes events"""
        default_events = [
            self.create_event(
                title='Dirty Circus Variety Show',
                description='Weekly variety show featuring circus acts, burlesque, and immersive performances',
                datetime_str=datetime.now().replace(hour=20, minute=0).isoformat(),
                location='House of Yes, 2 Wyckoff Ave, Brooklyn, NY 11237',
                price='$20-40',
                url='https://www.houseofyes.org/dirtycircus',
                tags=['nightlife', 'house_of_yes', 'immersive', 'performance', 'brooklyn', 'circus']
            ),
            self.create_event(
                title='Planet Yes',
                description='Dance party with DJs and immersive performances',
                datetime_str=datetime.now().replace(hour=22, minute=0).isoformat(),
                location='House of Yes, 2 Wyckoff Ave, Brooklyn, NY 11237',
                price='$20-30',
                url='https://www.houseofyes.org/planetyes',
                tags=['nightlife', 'house_of_yes', 'dance', 'dj', 'brooklyn']
            )
        ]
        return default_events
