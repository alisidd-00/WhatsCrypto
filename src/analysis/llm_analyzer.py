import logging
import json
import os
import requests
from datetime import datetime, timedelta
import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMAnalyzer:
    """Analyzes crypto news using OpenAI's LLM capabilities."""
    
    def __init__(self, config_path="config/api_config.json"):
        self.config = self._load_config(config_path)
        self.openai_config = self.config.get("openai", {})
        # self.api_key = self.openai_config.get("api_key", os.environ.get("OPENAI_API_KEY"))
        self.api_key = self.openai_config.get("api_key", '')
        self.model = self.openai_config.get("model", "gpt-4o-mini")
        
        if not self.api_key:
            logger.warning("No OpenAI API key found. LLM analysis will not be available.")
    
    def _load_config(self, config_path):
        """Load configuration from the specified path."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}
            
    def analyze_recent_news(self, db_instance, hours=8, limit=100):
        """
        Analyze news from the last specified hours.
        
        Args:
            db_instance: Database instance to fetch news from
            hours: Hours to look back for news
            limit: Maximum number of news items to analyze
            
        Returns:
            Dictionary containing analysis results
        """
        if not self.api_key:
            logger.error("Cannot perform analysis: No OpenAI API key provided")
            return {"error": "No OpenAI API key provided"}
            
        # Get recent news
        recent_news = self._get_news_for_analysis(db_instance, hours, limit)
        
        if recent_news.empty:
            logger.info("No news to analyze")
            return {"analysis": "No recent news available for analysis"}
            
        # Prepare news for analysis
        news_for_prompt = self._prepare_news_for_prompt(recent_news)
        
        # Analyze with OpenAI
        analysis_result = self._analyze_with_openai(news_for_prompt)
        
        # Save analysis results to database
        self._save_analysis_results(db_instance, analysis_result)
        
        return analysis_result
    
    def _get_news_for_analysis(self, db_instance, hours, limit):
        """Get recent news that hasn't been analyzed yet."""
        conn = db_instance._get_connection()
        lookback_time = (datetime.now() - timedelta(hours=hours)).isoformat()
        
        query = f"""
        SELECT * FROM news 
        WHERE analyzed = 0 
        AND published_at > '{lookback_time}'
        ORDER BY published_at DESC
        LIMIT {limit}
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        logger.info(f"Retrieved {len(df)} news items for analysis")
        return df
    
    def _prepare_news_for_prompt(self, news_df):
        """Prepare news dataframe for inclusion in LLM prompt."""
        news_items = []
        
        for _, row in news_df.iterrows():
            item = {
                'title': row['title'],
                'source': row['source_name'],
                'published_at': row['published_at'],
                'categories': row['categories'],
                'url': row['url']
            }
            
            # Only include body if it's not too long
            if row['body'] and len(row['body']) < 1000:
                item['body'] = row['body']
            
            news_items.append(item)
            
        return news_items
    
    def _analyze_with_openai(self, news_items):
        """Send news to OpenAI for analysis and return results."""
        logger.info("Analyzing news with OpenAI...")
        
        # Construct the prompt
        system_prompt = """
        You are a cryptocurrency market analyst expert. Analyze the provided crypto news and extract:
        1. Key market indicators and signals
        2. Significant events and their potential impact
        3. Overall market sentiment
        4. Important trends across various cryptocurrencies
        5. Potential investment opportunities or risks
        
        Format your analysis as a JSON with these sections:
        - summary: A concise summary of the most important insights
        - market_indicators: List of key market indicators found in the news
        - significant_events: List of significant events and their potential impact
        - sentiment: Overall market sentiment (positive, neutral, negative) with reasoning
        - trends: Important trends identified
        - opportunities_and_risks: Potential investment opportunities or risks
        - key_coins: Analysis of specific cryptocurrencies mentioned
        
        Be objective, fact-based, and avoid speculation where possible.
        """
        
        user_prompt = f"Here are the latest cryptocurrency news items to analyze:\n\n{json.dumps(news_items, indent=2)}"
        
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 2000
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                analysis_text = result['choices'][0]['message']['content']
                
                # Try to parse as JSON if it's in JSON format
                try:
                    analysis_json = json.loads(analysis_text)
                    return analysis_json
                except json.JSONDecodeError:
                    # If it's not valid JSON, return as text
                    return {"analysis": analysis_text}
            else:
                logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
                return {"error": f"API error: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Error during OpenAI analysis: {e}")
            return {"error": str(e)}
    
    def _save_analysis_results(self, db_instance, analysis_result):
        """Save analysis results to the database and mark analyzed news."""
        conn = db_instance._get_connection()
        cursor = conn.cursor()
        
        # Save the analysis
        timestamp = datetime.now().isoformat()
        
        try:
            # Insert the analysis into an analysis table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS news_analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                analysis_data TEXT,
                created_at TEXT
            )
            ''')
            
            cursor.execute('''
            INSERT INTO news_analysis (analysis_data, created_at)
            VALUES (?, ?)
            ''', (json.dumps(analysis_result), timestamp))
            
            # Mark the news items as analyzed
            cursor.execute('''
            UPDATE news
            SET analyzed = 1
            WHERE analyzed = 0
            ''')
            
            conn.commit()
            logger.info("Analysis results saved to database")
            
        except Exception as e:
            logger.error(f"Error saving analysis results: {e}")
        finally:
            conn.close() 