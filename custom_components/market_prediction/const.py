"""Constants for the Market Prediction integration."""
from datetime import timedelta

DOMAIN = "market_prediction"
DEFAULT_SCAN_INTERVAL = timedelta(hours=4)
API_TIMEOUT = 30

# API URLs
ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co"
FMP_BASE_URL = "https://financialmodelingprep.com/api/v3"

# Sentiment Analysis Sources Configuration
SENTIMENT_SOURCES = [
    {
        "name": "Alpha Vantage News",
        "weight": 5.0,
        "items": 20,
        "api_delay": 1.25,  # 25 seconds total
        "description": "Professional market news with sentiment scoring"
    },
    {
        "name": "Bloomberg Market",
        "weight": 4.5,
        "items": 10,
        "api_delay": 3.5,   # 35 seconds total
        "description": "Professional trading and market intelligence"
    },
    {
        "name": "Reuters Financial",
        "weight": 4.5,
        "items": 12,
        "api_delay": 1.83,  # 22 seconds total
        "description": "International business and financial news"
    },
    {
        "name": "Marketaux Financial",
        "weight": 4.0,
        "items": 15,
        "api_delay": 2.0,   # 30 seconds total
        "description": "Global financial news from 5000+ sources"
    },
    {
        "name": "Finnhub Sentiment",
        "weight": 4.0,
        "items": 18,
        "api_delay": 1.11,  # 20 seconds total
        "description": "Real-time market data and news sentiment"
    },
    {
        "name": "Financial Times",
        "weight": 4.0,
        "items": 8,
        "api_delay": 3.5,   # 28 seconds total
        "description": "International business and economic news"
    },
    {
        "name": "Wall Street Journal",
        "weight": 4.0,
        "items": 15,
        "api_delay": 1.33,  # 20 seconds total
        "description": "Business and financial market news"
    },
    {
        "name": "CNBC Market News",
        "weight": 3.5,
        "items": 22,
        "api_delay": 0.68,  # 15 seconds total
        "description": "Business news and market updates"
    },
    {
        "name": "Yahoo Finance",
        "weight": 3.0,
        "items": 25,
        "api_delay": 0.6,   # 15 seconds total
        "description": "Popular financial news and market data"
    },
    {
        "name": "MarketWatch",
        "weight": 3.0,
        "items": 15,
        "api_delay": 1.2,   # 18 seconds total
        "description": "Market news and financial analysis"
    }
]

# Total processing metrics
TOTAL_SENTIMENT_ITEMS = sum(source["items"] for source in SENTIMENT_SOURCES)  # 160 items
ESTIMATED_SENTIMENT_TIME = sum(source["items"] * source["api_delay"] for source in SENTIMENT_SOURCES)  # ~5-10 minutes

# Sensor entity IDs
SENSOR_S_P_500 = "sensor.market_prediction_s_p_500"
SENSOR_FTSE_100 = "sensor.market_prediction_ftse_100"
SENSOR_PROGRESS = "sensor.market_prediction_progress"
SENSOR_STATUS = "sensor.market_prediction_status"
SENSOR_CURRENT_SOURCE = "sensor.market_prediction_current_source"
SENSOR_PROCESSING_TIME = "sensor.market_prediction_processing_time"

# Configuration keys
CONF_ALPHA_VANTAGE_API_KEY = "alpha_vantage_api_key"
CONF_FMP_API_KEY = "fmp_api_key"