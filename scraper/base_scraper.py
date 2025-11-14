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
        required_fields = ['title', 'description', 'datetime', 'location', 'price', 'url', 'tags']
        return all(field in event for field in required_fields)
    
    def create_event(self, title: str, description: str, datetime_str: str, 
                    location: str, price: str, url: str, tags: List[str]) -> Dict[str, Any]:
        """Create a standardized event dictionary"""
        event = {
            'title': title,
            'description': description,
            'datetime': datetime_str,
            'location': location,
            'price': price,
            'url': url,
            'tags': tags,
            'source': self.source_name
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
