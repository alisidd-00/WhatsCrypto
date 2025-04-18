# WhatsCrypto

A cryptocurrency news analysis system that uses LLM (Large Language Models) to analyze crypto news, extract key indicators, and provide valuable insights to users.

## Features

- Collects cryptocurrency news from multiple sources (CryptoCompare, CryptoPanic, CoinGecko)
- Runs on a schedule (default: every 8 hours)
- Uses OpenAI's API to analyze news data and extract key insights
- Generates both HTML and plain text reports with market analysis
- Identifies market indicators, significant events, sentiment, trends, and opportunities/risks
- Stores all data in a SQLite database for easy access and historical analysis

## Requirements

- Python 3.7+
- OpenAI API key
- CryptoCompare API key (free tier available)
- CryptoPanic API key (free tier available) 

## Installation

1. Clone the repository:
```
git clone https://github.com/yourusername/WhatsCrypto.git
cd WhatsCrypto
```

2. Create a virtual environment and install dependencies:
```
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Set up your API keys:
- Edit `config/api_config.json` with your API keys
- Alternatively, set environment variables:
  - `OPENAI_API_KEY`
  - `CRYPTOCOMPARE_API_KEY`
  - `CRYPTOPANIC_API_KEY`

## Usage

### Data Collection and Analysis

Run with default settings (collect data and analyze):
```
python main.py
```

Run in continuous mode (collect data every 8 hours):
```
python main.py --continuous
```

Adjust the update interval (e.g., every 4 hours):
```
python main.py --continuous --interval 14400
```

Skip the analysis step:
```
python main.py --no-analyze
```

### Viewing Data and Analysis Results

Show recent news items:
```
python main.py --show-data --limit 20
```

Show the most recent analysis:
```
python main.py --show-analysis
```

Only run analysis on existing data without fetching new data:
```
python main.py --analyze-only
```

### Report Access

Reports are saved in the `data/reports` directory in both HTML and text formats. The HTML reports provide a more visual representation with color-coded sentiment analysis.

## Technical Details

- Data is collected from multiple cryptocurrency news sources
- News data is stored in a SQLite database (default: `data/crypto_news.db`)
- OpenAI's API is used to analyze the data and extract key insights
- Analysis results are also stored in the database for future reference
- Reports are generated in both HTML and text formats for easy access

## Future Development

- Integration with trading platforms for automated decision-making
- Web interface for viewing reports and insights
- Support for more news sources and data points
- Custom model training for more specialized crypto analysis

## License

MIT
