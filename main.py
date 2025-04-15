import logging
import argparse
import time
import json
from src.data_collection.news_fetcher import NewsFetcher
from src.storage.database import NewsDatabase
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_directories():
    """Create necessary directories"""
    os.makedirs("data/news_data", exist_ok=True)
    os.makedirs("config", exist_ok=True)
    
    # Create config file if it doesn't exist
    if not os.path.exists("config/api_config.json"):
        with open("config/api_config.json", "w") as f:
            json.dump({
                "cryptocompare": {
                    "base_url": "https://min-api.cryptocompare.com/data/v2/news/",
                    "api_key": "YOUR_API_KEY_HERE"
                },
                "cryptopanic": {
                    "base_url": "https://cryptopanic.com/api/v1/posts/",
                    "api_key": "YOUR_API_KEY_HERE"
                },
                "coingecko": {
                    "base_url": "https://api.coingecko.com/api/v3/"
                },
                "data_storage": {
                    "type": "sqlite",
                    "path": "data/crypto_news.db"
                }
            }, f, indent=2)
            logger.info("Created default config file")

def fetch_and_store(continuous=False, interval=3600):
    """Fetch news and store them in the database"""
    fetcher = NewsFetcher()
    db = NewsDatabase()
    
    def single_fetch():
        # Fetch news from all sources
        news_items = fetcher.fetch_all_sources()
        saved_count = db.save_news(news_items)
        logger.info(f"Saved {saved_count} new news items to database")
        
        # Also save to files
        saved_files = db.save_news_to_files(news_items)
        logger.info(f"Saved {saved_files} news items to files")
        
        # Fetch coin-specific updates
        coin_updates = fetcher.fetch_by_coin(["bitcoin", "ethereum", "ripple", "cardano", "solana"])
        if coin_updates:
            saved_coins = db.save_coin_updates(coin_updates)
            logger.info(f"Saved updates for {saved_coins} coins")
    
    if continuous:
        logger.info(f"Starting continuous fetching every {interval} seconds")
        while True:
            try:
                single_fetch()
                logger.info(f"Sleeping for {interval} seconds")
                time.sleep(interval)
            except KeyboardInterrupt:
                logger.info("Fetching stopped by user")
                break
            except Exception as e:
                logger.error(f"Error during fetching: {e}")
                time.sleep(60)  # Wait a minute before retrying
    else:
        single_fetch()

def display_saved_data(limit=10):
    """Display recently saved news data"""
    db = NewsDatabase()
    recent_news = db.get_recent_news(limit)
    
    if recent_news.empty:
        logger.info("No news found in the database")
    else:
        logger.info(f"Found {len(recent_news)} news items:")
        for _, row in recent_news.iterrows():
            logger.info(f"- {row['source']}: {row['title']} ({row['published_at']})")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Crypto News Collector')
    parser.add_argument('--continuous', action='store_true', help='Run in continuous mode')
    parser.add_argument('--interval', type=int, default=3600, help='Interval between fetches in seconds (default: 3600)')
    parser.add_argument('--show-data', action='store_true', help='Display saved news data')
    parser.add_argument('--limit', type=int, default=10, help='Limit of items to display')
    
    args = parser.parse_args()
    
    setup_directories()
    
    if args.show_data:
        display_saved_data(args.limit)
    else:
        fetch_and_store(continuous=args.continuous, interval=args.interval) 