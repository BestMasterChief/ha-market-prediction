"""Market Prediction System constants."""

DOMAIN = "market_prediction"

# Configuration keys
CONF_ALPHA_VANTAGE_API_KEY = "alpha_vantage_api_key"
CONF_FMP_API_KEY = "fmp_api_key"

# Default values
DEFAULT_UPDATE_INTERVAL = 3  # hours

# API URLs
ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co/query"
FMP_BASE_URL = "https://financialmodelingprep.com/api"

# Sentiment sources configuration
SENTIMENT_SOURCES = [
    {
        "name": "Alpha Vantage News",
        "weight": 5.0,
        "items": 20,
        "delay": 8,
        "api_delay": 1.25,
        "description": "Professional market news with sentiment scoring"
    },
    {
        "name": "Marketaux Financial", 
        "weight": 4.0,
        "items": 15,
        "delay": 12,
        "api_delay": 2.0,
        "description": "Global financial news from 5000+ sources"
    },
    {
        "name": "Finnhub Sentiment",
        "weight": 4.0,
        "items": 18,
        "delay": 6,
        "api_delay": 1.1,
        "description": "Real-time market data and news sentiment"
    },
    {
        "name": "Yahoo Finance",
        "weight": 3.0,
        "items": 25,
        "delay": 4,
        "api_delay": 0.6,
        "description": "Popular financial news and market data"
    },
    {
        "name": "MarketWatch",
        "weight": 3.0,
        "items": 15,
        "delay": 8,
        "api_delay": 1.2,
        "description": "Market news and financial analysis"
    },
    {
        "name": "Reuters Financial",
        "weight": 4.5,
        "items": 12,
        "delay": 15,
        "api_delay": 1.8,
        "description": "International business and financial news"
    },
    {
        "name": "Bloomberg Market",
        "weight": 4.5,
        "items": 10,
        "delay": 20,
        "api_delay": 3.5,
        "description": "Professional trading and market intelligence"
    },
    {
        "name": "CNBC Market News",
        "weight": 3.5,
        "items": 22,
        "delay": 5,
        "api_delay": 0.7,
        "description": "Business news and market updates"
    },
    {
        "name": "Financial Times",
        "weight": 4.0,
        "items": 8,
        "delay": 18,
        "api_delay": 3.5,
        "description": "International business and economic news"
    },
    {
        "name": "Wall Street Journal",
        "weight": 4.0,
        "items": 15,
        "delay": 10,
        "api_delay": 1.3,
        "description": "Business and financial market news"
    }
]

# Processing stages
PROCESSING_STAGES = [
    {"name": "Initializing", "percentage": 5},
    {"name": "Fetching Market Data", "percentage": 25},
    {"name": "Processing Technical Analysis", "percentage": 50},
    {"name": "Processing Sentiment Analysis", "percentage": 75},
    {"name": "Calculating Predictions", "percentage": 90},
    {"name": "Complete", "percentage": 100}
]

# Renaissance Technologies weighting approach
TECHNICAL_WEIGHT = 0.75  # 75% technical analysis
SENTIMENT_WEIGHT = 0.25  # 25% sentiment analysis

# API rate limits (calls per minute)
ALPHA_VANTAGE_RATE_LIMIT = 5
FMP_RATE_LIMIT = 4

# Error messages
ERROR_API_KEY_MISSING = "API key not configured"
ERROR_API_RATE_LIMIT = "API rate limit exceeded"
ERROR_API_TIMEOUT = "API request timeout"
ERROR_INVALID_RESPONSE = "Invalid API response"