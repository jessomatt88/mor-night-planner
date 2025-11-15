from .base_scraper import BaseScraper
from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re


class SlipperRoomScraper(BaseScraper):
    """Scraper for Slipper Room events"""
    
    def __init__(self):
        super().__init__('slipper_room')
        self.base_url = 'https://www.slipperroom.com/'
    
    def scrape(self) -> List[Dict[str, Any]]:
        """
        Scrape events from Slipper Room website using HTTP + BeautifulSoup.
        """
        self.clear_events()
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(self.base_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            event_items = soup.find_all('li')
            
            for item in event_items:
                event_link = item.find('a', href=lambda x: x and '/event-details/' in x)
                if not event_link:
                    continue
                
                title_elem = event_link
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                if not title:
                    continue
                
                event_url = event_link.get('href', '')
                if event_url and not event_url.startswith('http'):
                    event_url = f"https://www.slipperroom.com{event_url}"
                
                date_elem = item.find('div', string=re.compile(r'\w{3}\s+\d{1,2},\s+\d{4}'))
                date_str = ""
                time_str = ""
                
                if date_elem:
                    date_text = date_elem.get_text(strip=True)
                    
                    date_match = re.search(r'(\w{3}\s+\d{1,2},\s+\d{4})', date_text)
                    if date_match:
                        date_str = date_match.group(1)
                    
                    time_match = re.search(r'(\d{1,2}:\d{2}\s*(?:AM|PM))', date_text)
                    if time_match:
                        time_str = time_match.group(1)
                
                if not date_str:
                    continue
                
                try:
                    datetime_obj = datetime.strptime(f"{date_str} {time_str}", "%b %d, %Y %I:%M %p")
                    datetime_str = datetime_obj.isoformat()
                except:
                    datetime_str = datetime.now().isoformat()
                
                event = self.create_event(
                    title=title,
                    description='Burlesque and variety show at Slipper Room',
                    datetime_str=datetime_str,
                    location='Slipper Room, 167 Orchard St, New York, NY 10002',
                    price='$15-25',
                    url=event_url,
                    tags=['nightlife', 'slipper_room', 'burlesque', 'variety', 'lower_east_side']
                )
                
                self.events.append(event)
            
        except Exception as e:
            print(f"Error scraping Slipper Room: {e}")
        
        return self.events
