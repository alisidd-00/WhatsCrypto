import json
import sqlite3
import os
import logging
from datetime import datetime
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsDatabase:
    def __init__(self, config_path="config/api_config.json"):
        self.config = self._load_config(config_path)
        self.db_type = self.config.get("data_storage", {}).get("type", "sqlite")
        self.db_path = self.config.get("data_storage", {}).get("path", "data/crypto_news.db")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        if self.db_type == "sqlite":
            self._init_sqlite()
            
    def _load_config(self, config_path):
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}
    
    def _get_connection(self):
        """Get a database connection."""
        if self.db_type == "sqlite":
            return sqlite3.connect(self.db_path)
        else:
            logger.error(f"Unsupported database type: {self.db_type}")
            return None
            
    def _init_sqlite(self):
        """Initialize SQLite database with necessary tables"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Create news table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,
            title TEXT,
            body TEXT,
            published_at TEXT,
            url TEXT UNIQUE,
            source_name TEXT,
            categories TEXT,
            collected_at TEXT,
            analyzed BOOLEAN DEFAULT 0
        )
        ''')
        
        # Create coin_updates table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS coin_updates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            coin_id TEXT,
            name TEXT,
            description TEXT,
            links TEXT,
            last_updated TEXT,
            collected_at TEXT
        )
        ''')
        
        conn.commit()
        conn.close()
        
    def save_news(self, news_items):
        """Save news items to the database"""
        if not news_items:
            logger.warning("No news items to save")
            return 0
            
        if self.db_type == "sqlite":
            return self._save_news_sqlite(news_items)
        else:
            logger.error(f"Unsupported database type: {self.db_type}")
            return 0
            
    def _save_news_sqlite(self, news_items):
        """Save news items to SQLite database"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        saved_count = 0
        for item in news_items:
            try:
                cursor.execute('''
                INSERT OR IGNORE INTO news 
                (source, title, body, published_at, url, source_name, categories, collected_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    item.get('source', ''),
                    item.get('title', ''),
                    item.get('body', ''),
                    item.get('published_at', ''),
                    item.get('url', ''),
                    item.get('source_name', ''),
                    item.get('categories', ''),
                    item.get('collected_at', datetime.now().isoformat())
                ))
                if cursor.rowcount > 0:
                    saved_count += 1
            except Exception as e:
                logger.error(f"Error saving news item: {e}")
                
        conn.commit()
        conn.close()
        
        logger.info(f"Saved {saved_count} new news items to database")
        return saved_count
        
    def save_coin_updates(self, coin_updates):
        """Save coin updates to the database"""
        if not coin_updates:
            return 0
            
        if self.db_type == "sqlite":
            return self._save_coin_updates_sqlite(coin_updates)
        else:
            logger.error(f"Unsupported database type: {self.db_type}")
            return 0
            
    def _save_coin_updates_sqlite(self, coin_updates):
        """Save coin updates to SQLite database"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        saved_count = 0
        for coin_id, update in coin_updates.items():
            try:
                cursor.execute('''
                INSERT INTO coin_updates 
                (coin_id, name, description, links, last_updated, collected_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    coin_id,
                    update.get('name', ''),
                    update.get('description', ''),
                    json.dumps(update.get('links', {})),
                    update.get('last_updated', ''),
                    datetime.now().isoformat()
                ))
                saved_count += 1
            except Exception as e:
                logger.error(f"Error saving coin update: {e}")
                
        conn.commit()
        conn.close()
        
        logger.info(f"Saved {saved_count} coin updates to database")
        return saved_count
        
    def get_recent_news(self, limit=100):
        """Get the most recent news items from the database"""
        if self.db_type == "sqlite":
            conn = self._get_connection()
            df = pd.read_sql_query(f"SELECT * FROM news ORDER BY published_at DESC LIMIT {limit}", conn)
            conn.close()
            return df
        else:
            logger.error(f"Unsupported database type: {self.db_type}")
            return pd.DataFrame()
    
    def get_latest_analysis(self):
        """Get the most recent analysis from the database"""
        if self.db_type == "sqlite":
            conn = self._get_connection()
            cursor = conn.cursor()
            
            try:
                cursor.execute('''
                SELECT analysis_data, created_at FROM news_analysis
                ORDER BY created_at DESC
                LIMIT 1
                ''')
                
                result = cursor.fetchone()
                if result:
                    analysis_data, created_at = result
                    return {"analysis": json.loads(analysis_data), "created_at": created_at}
                else:
                    return {"analysis": None, "message": "No analysis found"}
            except Exception as e:
                logger.error(f"Error retrieving latest analysis: {e}")
                return {"error": str(e)}
            finally:
                conn.close()
        else:
            logger.error(f"Unsupported database type: {self.db_type}")
            return {"error": "Unsupported database type"}
        
    def save_news_to_files(self, news_items):
        """Save news items as JSON files in the news_data directory"""
        if not news_items:
            return 0
        
        save_path = 'data/news_data'
        os.makedirs(save_path, exist_ok=True)
        
        saved_count = 0
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        for i, item in enumerate(news_items):
            try:
                filename = f"{save_path}/{item['source']}_{timestamp}_{i}.json"
                with open(filename, 'w') as f:
                    json.dump(item, f, indent=2)
                saved_count += 1
            except Exception as e:
                logger.error(f"Error saving news item to file: {e}")
        
        logger.info(f"Saved {saved_count} news items to files")
        return saved_count 