from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import datetime
import json


class BaseScraper(ABC):
    """Base class for all event scrapers"""
    
    def __init__(self, source_name: str):
        self.source_name = source_name
        self.events = []
    
    @abstractmethod
    def scrape(self) -> List[Dict[str, Any]]:
        """
        Scrape events from the source.
        Returns a list of events in standard format.
        """
        pass
    
    def validate_event(self, event: Dict[str, Any]) -> bool:
        """Validate that an event has all required fields"""
        required_fields = ['title', 'start_datetime', 'venue_name', 'source_platform']
        return all(field in event for field in required_fields)
    
    def create_event(self, title: str, description: str, start_datetime: str, 
                    venue_name: str, neighborhood: str = None, city: str = "New York",
                    price_min: float = None, price_max: float = None,
                    url: str = None, raw_tags: List[str] = None,
                    end_datetime: str = None) -> Dict[str, Any]:
        """Create a standardized event dictionary"""
        event = {
            'title': title,
            'description': description,
            'start_datetime': start_datetime,
            'end_datetime': end_datetime,
            'venue_name': venue_name,
            'neighborhood': neighborhood,
            'city': city,
            'price_min': price_min,
            'price_max': price_max,
            'url': url,
            'raw_tags': raw_tags or [],
            'source_platform': self.source_name
        }
        
        if self.validate_event(event):
            return event
        else:
            raise ValueError(f"Invalid event format: {event}")
    
    def get_events(self) -> List[Dict[str, Any]]:
        """Get all scraped events"""
        return self.events
    
    def clear_events(self):
        """Clear the events list"""
        self.events = []
