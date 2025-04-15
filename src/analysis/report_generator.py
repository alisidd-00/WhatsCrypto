import json
import logging
from datetime import datetime
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ReportGenerator:
    """Generates human-readable reports from LLM analysis data."""
    
    def __init__(self, output_dir="data/reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_html_report(self, analysis_data):
        """
        Generate an HTML report from the analysis data.
        
        Args:
            analysis_data: Dictionary containing analysis results
            
        Returns:
            str: Path to the generated HTML report
        """
        if not analysis_data or "error" in analysis_data:
            logger.error(f"Cannot generate report: Invalid analysis data")
            return None
            
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        report_path = os.path.join(self.output_dir, f"crypto_analysis_{timestamp}.html")
        
        try:
            html_content = self._create_html_content(analysis_data)
            
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(html_content)
                
            logger.info(f"HTML report generated: {report_path}")
            return report_path
        except Exception as e:
            logger.error(f"Error generating HTML report: {e}")
            return None
    
    def generate_text_report(self, analysis_data):
        """
        Generate a plain text report from the analysis data.
        
        Args:
            analysis_data: Dictionary containing analysis results
            
        Returns:
            str: Path to the generated text report
        """
        if not analysis_data or "error" in analysis_data:
            logger.error(f"Cannot generate report: Invalid analysis data")
            return None
            
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        report_path = os.path.join(self.output_dir, f"crypto_analysis_{timestamp}.txt")
        
        try:
            text_content = self._create_text_content(analysis_data)
            
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(text_content)
                
            logger.info(f"Text report generated: {report_path}")
            return report_path
        except Exception as e:
            logger.error(f"Error generating text report: {e}")
            return None
    
    def _create_html_content(self, analysis_data):
        """Create HTML content from the analysis data."""
        # Extract the analysis if it's nested
        if isinstance(analysis_data, dict) and "analysis" in analysis_data:
            if isinstance(analysis_data["analysis"], dict):
                analysis = analysis_data["analysis"]
            else:
                # Handle case where analysis is a string
                return f"""
                <html>
                <head>
                    <title>Cryptocurrency Market Analysis</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; line-height: 1.6; max-width: 1000px; margin: 0 auto; padding: 20px; }}
                        h1, h2 {{ color: #2c3e50; }}
                        .timestamp {{ color: #7f8c8d; font-style: italic; margin-bottom: 20px; }}
                        pre {{ background-color: #f9f9f9; padding: 10px; border-radius: 5px; white-space: pre-wrap; }}
                    </style>
                </head>
                <body>
                    <h1>Cryptocurrency Market Analysis</h1>
                    <div class="timestamp">Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>
                    <pre>{analysis_data["analysis"]}</pre>
                </body>
                </html>
                """
        else:
            analysis = analysis_data
        
        # Build the HTML content
        html = f"""
        <html>
        <head>
            <title>Cryptocurrency Market Analysis</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; max-width: 1000px; margin: 0 auto; padding: 20px; }}
                h1, h2, h3 {{ color: #2c3e50; }}
                .timestamp {{ color: #7f8c8d; font-style: italic; margin-bottom: 20px; }}
                .section {{ margin-bottom: 30px; }}
                .positive {{ color: #27ae60; }}
                .negative {{ color: #c0392b; }}
                .neutral {{ color: #7f8c8d; }}
                ul {{ padding-left: 20px; }}
                li {{ margin-bottom: 5px; }}
            </style>
        </head>
        <body>
            <h1>Cryptocurrency Market Analysis</h1>
            <div class="timestamp">Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>
        """
        
        # Summary section
        if "summary" in analysis:
            html += f"""
            <div class="section">
                <h2>Summary</h2>
                <p>{analysis["summary"]}</p>
            </div>
            """
        
        # Market indicators section
        if "market_indicators" in analysis:
            html += f"""
            <div class="section">
                <h2>Key Market Indicators</h2>
                <ul>
            """
            if isinstance(analysis["market_indicators"], list):
                for indicator in analysis["market_indicators"]:
                    html += f"<li>{indicator}</li>"
            else:
                html += f"<li>{analysis['market_indicators']}</li>"
            html += """
                </ul>
            </div>
            """
        
        # Significant events section
        if "significant_events" in analysis:
            html += f"""
            <div class="section">
                <h2>Significant Events</h2>
                <ul>
            """
            if isinstance(analysis["significant_events"], list):
                for event in analysis["significant_events"]:
                    html += f"<li>{event}</li>"
            else:
                html += f"<li>{analysis['significant_events']}</li>"
            html += """
                </ul>
            </div>
            """
        
        # Sentiment section
        if "sentiment" in analysis:
            sentiment_class = "neutral"
            sentiment_value = analysis["sentiment"]
            if isinstance(sentiment_value, dict) and "sentiment" in sentiment_value:
                sentiment_text = sentiment_value["sentiment"].lower()
                if "positive" in sentiment_text:
                    sentiment_class = "positive"
                elif "negative" in sentiment_text:
                    sentiment_class = "negative"
                sentiment_display = str(sentiment_value)
            else:
                sentiment_text = str(sentiment_value).lower()
                if "positive" in sentiment_text:
                    sentiment_class = "positive"
                elif "negative" in sentiment_text:
                    sentiment_class = "negative"
                sentiment_display = sentiment_value
                
            html += f"""
            <div class="section">
                <h2>Market Sentiment</h2>
                <p class="{sentiment_class}">{sentiment_display}</p>
            </div>
            """
        
        # Trends section
        if "trends" in analysis:
            html += f"""
            <div class="section">
                <h2>Important Trends</h2>
                <ul>
            """
            if isinstance(analysis["trends"], list):
                for trend in analysis["trends"]:
                    html += f"<li>{trend}</li>"
            else:
                html += f"<li>{analysis['trends']}</li>"
            html += """
                </ul>
            </div>
            """
        
        # Opportunities and risks section
        if "opportunities_and_risks" in analysis:
            html += f"""
            <div class="section">
                <h2>Opportunities and Risks</h2>
            """
            if isinstance(analysis["opportunities_and_risks"], dict):
                if "opportunities" in analysis["opportunities_and_risks"]:
                    html += "<h3>Opportunities</h3><ul>"
                    opportunities = analysis["opportunities_and_risks"]["opportunities"]
                    if isinstance(opportunities, list):
                        for opportunity in opportunities:
                            html += f"<li>{opportunity}</li>"
                    else:
                        html += f"<li>{opportunities}</li>"
                    html += "</ul>"
                    
                if "risks" in analysis["opportunities_and_risks"]:
                    html += "<h3>Risks</h3><ul>"
                    risks = analysis["opportunities_and_risks"]["risks"]
                    if isinstance(risks, list):
                        for risk in risks:
                            html += f"<li>{risk}</li>"
                    else:
                        html += f"<li>{risks}</li>"
                    html += "</ul>"
            else:
                html += f"<p>{analysis['opportunities_and_risks']}</p>"
            html += """
            </div>
            """
        
        # Key coins section
        if "key_coins" in analysis:
            html += f"""
            <div class="section">
                <h2>Key Cryptocurrencies</h2>
            """
            if isinstance(analysis["key_coins"], dict):
                for coin, analysis_text in analysis["key_coins"].items():
                    html += f"<h3>{coin}</h3><p>{analysis_text}</p>"
            elif isinstance(analysis["key_coins"], list):
                html += "<ul>"
                for coin_item in analysis["key_coins"]:
                    html += f"<li>{coin_item}</li>"
                html += "</ul>"
            else:
                html += f"<p>{analysis['key_coins']}</p>"
            html += """
            </div>
            """
        
        # Close HTML tags
        html += """
        </body>
        </html>
        """
        
        return html
    
    def _create_text_content(self, analysis_data):
        """Create plain text content from the analysis data."""
        # Extract the analysis if it's nested
        if isinstance(analysis_data, dict) and "analysis" in analysis_data:
            if isinstance(analysis_data["analysis"], dict):
                analysis = analysis_data["analysis"]
            else:
                # Handle case where analysis is a string
                return f"""
CRYPTOCURRENCY MARKET ANALYSIS
Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

{analysis_data["analysis"]}
                """
        else:
            analysis = analysis_data
        
        # Build the text content
        text = f"""CRYPTOCURRENCY MARKET ANALYSIS
Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

"""
        
        # Summary section
        if "summary" in analysis:
            text += f"""SUMMARY
-------
{analysis["summary"]}

"""
        
        # Market indicators section
        if "market_indicators" in analysis:
            text += f"""KEY MARKET INDICATORS
--------------------
"""
            if isinstance(analysis["market_indicators"], list):
                for indicator in analysis["market_indicators"]:
                    text += f"- {indicator}\n"
            else:
                text += f"- {analysis['market_indicators']}\n"
            text += "\n"
        
        # Significant events section
        if "significant_events" in analysis:
            text += f"""SIGNIFICANT EVENTS
-----------------
"""
            if isinstance(analysis["significant_events"], list):
                for event in analysis["significant_events"]:
                    text += f"- {event}\n"
            else:
                text += f"- {analysis['significant_events']}\n"
            text += "\n"
        
        # Sentiment section
        if "sentiment" in analysis:
            text += f"""MARKET SENTIMENT
---------------
{analysis["sentiment"]}

"""
        
        # Trends section
        if "trends" in analysis:
            text += f"""IMPORTANT TRENDS
---------------
"""
            if isinstance(analysis["trends"], list):
                for trend in analysis["trends"]:
                    text += f"- {trend}\n"
            else:
                text += f"- {analysis['trends']}\n"
            text += "\n"
        
        # Opportunities and risks section
        if "opportunities_and_risks" in analysis:
            text += f"""OPPORTUNITIES AND RISKS
----------------------
"""
            if isinstance(analysis["opportunities_and_risks"], dict):
                if "opportunities" in analysis["opportunities_and_risks"]:
                    text += "Opportunities:\n"
                    opportunities = analysis["opportunities_and_risks"]["opportunities"]
                    if isinstance(opportunities, list):
                        for opportunity in opportunities:
                            text += f"- {opportunity}\n"
                    else:
                        text += f"- {opportunities}\n"
                    text += "\n"
                    
                if "risks" in analysis["opportunities_and_risks"]:
                    text += "Risks:\n"
                    risks = analysis["opportunities_and_risks"]["risks"]
                    if isinstance(risks, list):
                        for risk in risks:
                            text += f"- {risk}\n"
                    else:
                        text += f"- {risks}\n"
                    text += "\n"
            else:
                text += f"{analysis['opportunities_and_risks']}\n\n"
        
        # Key coins section
        if "key_coins" in analysis:
            text += f"""KEY CRYPTOCURRENCIES
-------------------
"""
            if isinstance(analysis["key_coins"], dict):
                for coin, analysis_text in analysis["key_coins"].items():
                    text += f"{coin}:\n{analysis_text}\n\n"
            elif isinstance(analysis["key_coins"], list):
                for coin_item in analysis["key_coins"]:
                    text += f"- {coin_item}\n"
            else:
                text += f"{analysis['key_coins']}\n"
        
        return text 