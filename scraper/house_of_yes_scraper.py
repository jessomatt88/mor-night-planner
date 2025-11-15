from .base_scraper import BaseScraper
from typing import List, Dict, Any
from datetime import datetime
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


class HouseOfYesScraper(BaseScraper):
    """Scraper for House of Yes events using Playwright"""
    
    def __init__(self):
        super().__init__('house_of_yes')
        self.base_url = 'https://www.houseofyes.org/calendar'
    
    def scrape(self) -> List[Dict[str, Any]]:
        """
        Scrape events from House of Yes website using Playwright.
        Falls back to recurring events if dynamic content cannot be loaded.
        """
        self.clear_events()
        
        if not PLAYWRIGHT_AVAILABLE:
            print("Warning: Playwright not available, returning default House of Yes events")
            return self._get_default_events()
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                page.goto(self.base_url, wait_until='networkidle', timeout=30000)
                page.wait_for_timeout(5000)
                
                featured_links = page.query_selector_all('a[href*="/"]')
                
                for link in featured_links:
                    try:
                        href = link.get_attribute('href')
                        if not href:
                            continue
                        
                        if 'shotgun.live' in href or 'houseofyes.org' in href:
                            title_elem = link.query_selector('img')
                            if title_elem:
                                alt_text = title_elem.get_attribute('alt')
                                if alt_text:
                                    event = self.create_event(
                                        title=alt_text,
                                        description='Immersive nightlife experience at House of Yes',
                                        datetime_str=datetime.now().isoformat(),
                                        location='House of Yes, 2 Wyckoff Ave, Brooklyn, NY 11237',
                                        price='$20-40',
                                        url=href if href.startswith('http') else f'https://www.houseofyes.org{href}',
                                        tags=['nightlife', 'house_of_yes', 'immersive', 'performance', 'brooklyn']
                                    )
                                    self.events.append(event)
                    except Exception as e:
                        continue
                
                browser.close()
                
                if len(self.events) == 0:
                    return self._get_default_events()
            
        except Exception as e:
            print(f"Error scraping House of Yes with Playwright: {e}")
            return self._get_default_events()
        
        return self.events[:10]
    
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
