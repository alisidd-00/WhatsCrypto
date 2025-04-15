import logging
from datetime import datetime
from .api_clients import CryptoCompareClient, CryptoPanicClient, CoinGeckoClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsFetcher:
    def __init__(self, config_path="config/api_config.json"):
        self.cryptocompare = CryptoCompareClient(config_path)
        self.cryptopanic = CryptoPanicClient(config_path)
        self.coingecko = CoinGeckoClient(config_path)
        
    def fetch_all_sources(self, limit=50):
        """Fetch news from all configured sources"""
        logger.info("Fetching news from multiple sources...")
        
        all_news = []
        
        # Get news from CryptoCompare
        logger.info("Fetching news from CryptoCompare...")
        cc_news = self.cryptocompare.get_latest_news(limit=limit)
        logger.info(f"Retrieved {len(cc_news)} news items from CryptoCompare")
        
        for item in cc_news:
            all_news.append({
                'source': 'cryptocompare',
                'title': item.get('title', ''),
                'body': item.get('body', ''),
                'published_at': item.get('published_on'),
                'url': item.get('url', ''),
                'source_name': item.get('source', ''),
                'categories': item.get('categories', ''),
                'collected_at': datetime.now().isoformat()
            })
        
        # Get news from CryptoPanic
        logger.info("Fetching news from CryptoPanic...")
        cp_news = self.cryptopanic.get_news(limit=limit)
        logger.info(f"Retrieved {len(cp_news)} news items from CryptoPanic")
        
        for item in cp_news:
            # Extract currency codes properly from the currencies list of dictionaries
            currencies = []
            for currency in item.get('currencies', []):
                if isinstance(currency, dict) and 'code' in currency:
                    currencies.append(currency['code'])
                elif isinstance(currency, str):
                    currencies.append(currency)
            
            all_news.append({
                'source': 'cryptopanic',
                'title': item.get('title', ''),
                'body': '',  # CryptoPanic doesn't provide full body in free tier
                'published_at': item.get('published_at'),
                'url': item.get('url', ''),
                'source_name': item.get('source', {}).get('title', ''),
                'categories': ', '.join(currencies),  # Now using our properly processed currencies list
                'collected_at': datetime.now().isoformat()
            })
            
        logger.info(f"Collected {len(all_news)} news items in total")
        return all_news
    
    def fetch_by_coin(self, coin_ids=None):
        """Fetch news specific to certain coins"""
        if not coin_ids:
            coin_ids = ["bitcoin", "ethereum", "ripple"]
            
        coin_updates = {}
        for coin_id in coin_ids:
            update = self.coingecko.get_coin_updates(coin_id)
            if update:
                coin_updates[coin_id] = update
                
        return coin_updates 