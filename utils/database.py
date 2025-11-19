import sqlite3
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import os


class Database:
    """SQLite database manager for events"""
    
    def __init__(self, db_path: str = './data/events.db'):
        self.db_path = db_path
        self._ensure_data_directory()
        self.init_database()
    
    def _ensure_data_directory(self):
        """Ensure the data directory exists"""
        data_dir = os.path.dirname(self.db_path)
        if data_dir and not os.path.exists(data_dir):
            os.makedirs(data_dir)
    
    def get_connection(self):
        """Get a database connection"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialize the database schema"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                start_datetime TEXT NOT NULL,
                end_datetime TEXT,
                venue_name TEXT,
                neighborhood TEXT,
                city TEXT,
                price_min REAL,
                price_max REAL,
                url TEXT,
                source_platform TEXT NOT NULL,
                raw_tags TEXT,
                created_at TEXT NOT NULL,
                UNIQUE(title, start_datetime, venue_name)
            )
        ''')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_start_datetime ON events(start_datetime)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_venue_name ON events(venue_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_neighborhood ON events(neighborhood)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_city ON events(city)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_source_platform ON events(source_platform)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_raw_tags ON events(raw_tags)')
        
        conn.commit()
        conn.close()
    
    def insert_event(self, event: Dict[str, Any]) -> bool:
        """Insert a single event into the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO events 
                (title, description, start_datetime, end_datetime, venue_name, neighborhood, 
                 city, price_min, price_max, url, source_platform, raw_tags, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                event.get('title'),
                event.get('description'),
                event.get('start_datetime'),
                event.get('end_datetime'),
                event.get('venue_name'),
                event.get('neighborhood'),
                event.get('city'),
                event.get('price_min'),
                event.get('price_max'),
                event.get('url'),
                event.get('source_platform'),
                json.dumps(event.get('raw_tags', [])),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error inserting event: {e}")
            return False
        finally:
            conn.close()
    
    def insert_events(self, events: List[Dict[str, Any]]) -> int:
        """Insert multiple events into the database"""
        count = 0
        for event in events:
            if self.insert_event(event):
                count += 1
        return count
    
    def get_events(self, date: Optional[str] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get events from the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = 'SELECT * FROM events'
        params = []
        
        if date:
            query += ' WHERE date(start_datetime) = date(?)'
            params.append(date)
        
        query += ' ORDER BY start_datetime'
        
        if limit:
            query += ' LIMIT ?'
            params.append(limit)
        
        cursor.execute(query, params)
        
        columns = [desc[0] for desc in cursor.description]
        events = []
        
        for row in cursor.fetchall():
            event = dict(zip(columns, row))
            if event.get('raw_tags'):
                event['raw_tags'] = json.loads(event['raw_tags'])
            events.append(event)
        
        conn.close()
        return events
    
    def delete_old_events(self, cutoff_date: str) -> int:
        """Delete events older than the cutoff date"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM events WHERE start_datetime < ?', (cutoff_date,))
        deleted_count = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return deleted_count
    
    def get_event_count(self) -> int:
        """Get total number of events in database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM events')
        count = cursor.fetchone()[0]
        
        conn.close()
        return count
    
    def clear_all_events(self):
        """Clear all events from the database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM events')
        
        conn.commit()
        conn.close()
