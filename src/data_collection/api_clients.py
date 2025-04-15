import requests
import json
import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseApiClient:
    def __init__(self, config_path="config/api_config.json"):
        self.config = self._load_config(config_path)
        
    def _load_config(self, config_path):
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}
            
    def make_request(self, url, params=None, headers=None):
        try:
            logger.info(f"Making request to: {url}")
            if headers:
                logger.info(f"With headers: {headers}")
            response = requests.get(url, params=params, headers=headers)
            
            if response.status_code != 200:
                logger.error(f"API request failed with status code {response.status_code}: {response.text}")
                return None
            
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return None
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON response from {url}")
            return None

class CryptoCompareClient(BaseApiClient):
    def __init__(self, config_path="config/api_config.json"):
        super().__init__(config_path)
        self.base_url = self.config.get("cryptocompare", {}).get("base_url")
        self.api_key = self.config.get("cryptocompare", {}).get("api_key")
        
    def get_latest_news(self, categories=None, limit=50):
        """Fetch latest crypto news from CryptoCompare"""
        if not self.base_url:
            logger.error("CryptoCompare base URL not configured")
            return []
            
        params = {'limit': limit}
        if categories:
            params['categories'] = categories
            
        headers = {}
        if self.api_key:
            headers['Authorization'] = f'Apikey {self.api_key}'
            
        data = self.make_request(f"{self.base_url}/?", params=params, headers=headers)
        
        if data and 'Data' in data:
            return data['Data']
        elif data:
            logger.error(f"Unexpected response format from CryptoCompare: {data}")
        return []

class CryptoPanicClient(BaseApiClient):
    def __init__(self, config_path="config/api_config.json"):
        super().__init__(config_path)
        self.base_url = self.config.get("cryptopanic", {}).get("base_url")
        self.api_key = self.config.get("cryptopanic", {}).get("api_key")
        
    def get_news(self, currencies=None, kind=None, limit=50):
        """Fetch news from CryptoPanic"""
        if not self.base_url or not self.api_key:
            logger.error("CryptoPanic configuration incomplete")
            return []
            
        params = {
            'auth_token': self.api_key,
            'public': 'true',
            'limit': limit
        }
        
        if currencies:
            params['currencies'] = currencies
        if kind:
            params['kind'] = kind  # 'news' or 'media'
            
        data = self.make_request(self.base_url, params=params)
        
        if data and 'results' in data:
            return data['results']
        return []

class CoinGeckoClient(BaseApiClient):
    def __init__(self, config_path="config/api_config.json"):
        super().__init__(config_path)
        self.base_url = self.config.get("coingecko", {}).get("base_url")
        
    def get_coin_updates(self, coin_id="bitcoin"):
        """Fetch latest updates about a specific coin from CoinGecko"""
        if not self.base_url:
            logger.error("CoinGecko base URL not configured")
            return {}
            
        endpoint = f"coins/{coin_id}"
        data = self.make_request(f"{self.base_url}{endpoint}")
        
        if data and 'description' in data:
            return {
                'id': data.get('id'),
                'name': data.get('name'),
                'description': data.get('description', {}).get('en', ''),
                'links': data.get('links', {}),
                'last_updated': data.get('last_updated')
            }
        return {} 