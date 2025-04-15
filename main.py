import logging
import argparse
import time
import json
from src.data_collection.news_fetcher import NewsFetcher
from src.storage.database import NewsDatabase
from src.analysis.llm_analyzer import LLMAnalyzer
from src.analysis.report_generator import ReportGenerator
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Default interval set to 8 hours (in seconds)
DEFAULT_INTERVAL = 28800

def setup_directories():
    """Create necessary directories"""
    os.makedirs("data/news_data", exist_ok=True)
    os.makedirs("data/reports", exist_ok=True)
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
                "openai": {
                    "api_key": "YOUR_OPENAI_API_KEY_HERE",
                    "model": "gpt-3.5-turbo-16k"
                },
                "data_storage": {
                    "type": "sqlite",
                    "path": "data/crypto_news.db"
                }
            }, f, indent=2)
            logger.info("Created default config file")

def fetch_and_store(continuous=False, interval=DEFAULT_INTERVAL, analyze=True):
    """Fetch news, store them in the database, and optionally analyze them"""
    fetcher = NewsFetcher()
    db = NewsDatabase()
    analyzer = LLMAnalyzer() if analyze else None
    report_generator = ReportGenerator() if analyze else None
    
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
            
        # Analyze news if requested
        if analyze and analyzer:
            logger.info("Analyzing news with LLM...")
            analysis_result = analyzer.analyze_recent_news(db)
            
            if "error" not in analysis_result:
                logger.info("News analysis completed successfully")
                
                # Generate reports
                if report_generator:
                    html_report = report_generator.generate_html_report(analysis_result)
                    text_report = report_generator.generate_text_report(analysis_result)
                    
                    if html_report:
                        logger.info(f"HTML report generated: {html_report}")
                    if text_report:
                        logger.info(f"Text report generated: {text_report}")
            else:
                logger.error(f"News analysis failed: {analysis_result['error']}")
    
    if continuous:
        logger.info(f"Starting continuous fetching every {interval} seconds ({interval/3600:.1f} hours)")
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

def display_latest_analysis():
    """Display the latest analysis result"""
    db = NewsDatabase()
    latest_analysis = db.get_latest_analysis()
    
    if latest_analysis and "analysis" in latest_analysis and latest_analysis["analysis"]:
        logger.info(f"Latest analysis from {latest_analysis.get('created_at', 'unknown time')}:")
        
        # Print summary if available
        analysis = latest_analysis["analysis"]
        if isinstance(analysis, dict) and "summary" in analysis:
            logger.info(f"Summary: {analysis['summary']}")
        else:
            logger.info(f"Analysis: {latest_analysis['analysis']}")
            
        logger.info("For full details, check the reports directory.")
    else:
        logger.info("No analysis results found. Run with --analyze to generate analysis.")

def analyze_latest_news():
    """Analyze the latest news without fetching new data"""
    logger.info("Analyzing latest unanalyzed news...")
    db = NewsDatabase()
    analyzer = LLMAnalyzer()
    report_generator = ReportGenerator()
    
    analysis_result = analyzer.analyze_recent_news(db)
    
    if "error" not in analysis_result:
        logger.info("News analysis completed successfully")
        
        # Generate reports
        html_report = report_generator.generate_html_report(analysis_result)
        text_report = report_generator.generate_text_report(analysis_result)
        
        if html_report:
            logger.info(f"HTML report generated: {html_report}")
        if text_report:
            logger.info(f"Text report generated: {text_report}")
            
        return True
    else:
        logger.error(f"News analysis failed: {analysis_result['error']}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Crypto News Collector and Analyzer')
    parser.add_argument('--continuous', action='store_true', help='Run in continuous mode')
    parser.add_argument('--interval', type=int, default=DEFAULT_INTERVAL, 
                        help=f'Interval between fetches in seconds (default: {DEFAULT_INTERVAL} - 8 hours)')
    parser.add_argument('--show-data', action='store_true', help='Display saved news data')
    parser.add_argument('--limit', type=int, default=10, help='Limit of items to display')
    parser.add_argument('--no-analyze', action='store_true', help='Skip LLM analysis of news')
    parser.add_argument('--analyze-only', action='store_true', help='Only analyze existing news without fetching new data')
    parser.add_argument('--show-analysis', action='store_true', help='Display latest analysis results')
    
    args = parser.parse_args()
    
    setup_directories()
    
    if args.show_data:
        display_saved_data(args.limit)
    elif args.show_analysis:
        display_latest_analysis()
    elif args.analyze_only:
        analyze_latest_news()
    else:
        fetch_and_store(continuous=args.continuous, interval=args.interval, analyze=not args.no_analyze) 