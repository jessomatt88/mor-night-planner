from .base_scraper import BaseScraper
from typing import List, Dict, Any
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re


class ShotgunScraper(BaseScraper):
    """Scraper for Shotgun.live NYC events"""
    
    def __init__(self):
        super().__init__('shotgun')
        self.base_url = 'https://shotgun.live/en-us/events/new-york'
    
    def _extract_neighborhood(self, location_text: str) -> str:
        """Extract neighborhood from location text"""
        neighborhoods = {
            'brooklyn': 'Brooklyn',
            'bushwick': 'Bushwick',
            'williamsburg': 'Williamsburg',
            'greenpoint': 'Greenpoint',
            'lower east side': 'Lower East Side',
            'east village': 'East Village',
            'west village': 'West Village',
            'soho': 'SoHo',
            'tribeca': 'Tribeca',
            'chelsea': 'Chelsea',
            'harlem': 'Harlem',
            'upper west side': 'Upper West Side',
            'upper east side': 'Upper East Side',
            'midtown': 'Midtown',
            'queens': 'Queens',
            'astoria': 'Astoria',
            'long island city': 'Long Island City',
        }
        
        location_lower = location_text.lower()
        for key, value in neighborhoods.items():
            if key in location_lower:
                return value
        
        return 'Manhattan'
    
    def _parse_price(self, price_text: str) -> tuple:
        """Parse price text to extract min and max prices"""
        if not price_text or 'free' in price_text.lower():
            return 0.0, 0.0
        
        prices = re.findall(r'\d+(?:\.\d+)?', price_text)
        if len(prices) >= 2:
            return float(prices[0]), float(prices[1])
        elif len(prices) == 1:
            price = float(prices[0])
            return price, price
        
        return None, None
    
    def scrape(self) -> List[Dict[str, Any]]:
        """
        Scrape events from Shotgun.live NYC.
        Limited to first 2 pages for MVP to be respectful of the platform.
        """
        self.clear_events()
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
            }
            
            today = datetime.now()
            end_date = today + timedelta(days=14)
            
            for page in range(1, 3):
                try:
                    url = f"{self.base_url}?page={page}" if page > 1 else self.base_url
                    response = requests.get(url, headers=headers, timeout=15)
                    
                    if response.status_code != 200:
                        print(f"  Shotgun returned status {response.status_code}")
                        break
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    event_cards = (soup.find_all('div', class_='event-card') or 
                                  soup.find_all('article', class_='event') or
                                  soup.find_all('a', class_='event-link') or
                                  soup.find_all('div', attrs={'data-testid': 'event-item'}))
                    
                    if not event_cards:
                        print(f"  No event cards found on page {page}")
                        break
                    
                    for card in event_cards:
                        try:
                            title_elem = (card.find('h2') or card.find('h3') or 
                                        card.find('div', class_='event-title') or
                                        card.find('span', class_='title'))
                            if not title_elem:
                                continue
                            title = title_elem.get_text(strip=True)
                            
                            desc_elem = (card.find('p', class_='event-description') or 
                                       card.find('div', class_='description'))
                            description = desc_elem.get_text(strip=True)[:500] if desc_elem else f"Event in New York City"
                            
                            time_elem = card.find('time')
                            start_datetime = None
                            if time_elem and time_elem.get('datetime'):
                                start_datetime = time_elem.get('datetime')
                            else:
                                date_elem = (card.find('div', class_='event-date') or
                                           card.find('span', class_='date'))
                                if date_elem:
                                    start_datetime = datetime.now().isoformat()
                            
                            if not start_datetime:
                                continue
                            
                            location_elem = (card.find('div', class_='event-location') or 
                                           card.find('span', class_='location') or
                                           card.find('p', class_='venue'))
                            location_text = location_elem.get_text(strip=True) if location_elem else 'New York, NY'
                            
                            venue_name = location_text.split(',')[0].strip() if ',' in location_text else location_text.strip()
                            if not venue_name or venue_name == 'New York':
                                venue_name = 'TBD'
                            neighborhood = self._extract_neighborhood(location_text)
                            
                            price_elem = (card.find('div', class_='event-price') or 
                                        card.find('span', class_='price'))
                            price_text = price_elem.get_text(strip=True) if price_elem else 'Free'
                            price_min, price_max = self._parse_price(price_text)
                            
                            link_elem = card if card.name == 'a' else card.find('a', href=True)
                            url = link_elem.get('href') if link_elem else None
                            if url and not url.startswith('http'):
                                url = f"https://shotgun.live{url}"
                            
                            raw_tags = ['nightlife', 'shotgun', 'nyc']
                            title_lower = title.lower()
                            if 'music' in title_lower or 'concert' in title_lower or 'dj' in title_lower:
                                raw_tags.append('music')
                            if 'dance' in title_lower or 'party' in title_lower or 'club' in title_lower:
                                raw_tags.append('dance')
                            if 'techno' in title_lower or 'house' in title_lower:
                                raw_tags.append('electronic')
                            if 'art' in title_lower or 'gallery' in title_lower:
                                raw_tags.append('art')
                            
                            event = self.create_event(
                                title=title,
                                description=description,
                                start_datetime=start_datetime,
                                venue_name=venue_name,
                                neighborhood=neighborhood,
                                city='New York',
                                price_min=price_min,
                                price_max=price_max,
                                url=url,
                                raw_tags=raw_tags
                            )
                            self.events.append(event)
                            
                        except Exception as e:
                            print(f"  Error parsing Shotgun event card: {e}")
                            continue
                    
                    print(f"  Scraped page {page}, found {len(event_cards)} cards")
                    
                except Exception as e:
                    print(f"  Error scraping Shotgun page {page}: {e}")
                    continue
            
        except Exception as e:
            print(f"Error scraping Shotgun: {e}")
        
        return self.events
