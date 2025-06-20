"""Constants for the Market Prediction integration."""

DOMAIN = "market_prediction"
CONF_ALPHA_VANTAGE_API_KEY = "alpha_vantage_api_key"
CONF_FMP_API_KEY = "fmp_api_key"

# API endpoints
ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co/query"
FMP_BASE_URL = "https://financialmodelingprep.com/api"

# Update intervals
UPDATE_INTERVAL_SECONDS = 21600  # 6 hours
RAPID_UPDATE_INTERVAL_SECONDS = 1800  # 30 minutes

# Sentiment sources configuration
SENTIMENT_SOURCES = [
    {
        "name": "Alpha Vantage News",
        "weight": 5.0,
        "items": 20,
        "api_delay": 1.25,
        "timeout": 30
    },
    {
        "name": "Bloomberg Market",
        "weight": 4.5,
        "items": 10,
        "api_delay": 3.5,
        "timeout": 35
    },
    {
        "name": "Reuters Financial",
        "weight": 4.5,
        "items": 12,
        "api_delay": 1.8,
        "timeout": 22
    },
    {
        "name": "Marketaux Financial",
        "weight": 4.0,
        "items": 15,
        "api_delay": 2.0,
        "timeout": 30
    },
    {
        "name": "Finnhub Sentiment",
        "weight": 4.0,
        "items": 18,
        "api_delay": 1.1,
        "timeout": 20
    },
    {
        "name": "Financial Times",
        "weight": 4.0,
        "items": 8,
        "api_delay": 3.5,
        "timeout": 28
    },
    {
        "name": "Wall Street Journal",
        "weight": 4.0,
        "items": 15,
        "api_delay": 1.3,
        "timeout": 20
    },
    {
        "name": "CNBC Market News",
        "weight": 3.5,
        "items": 22,
        "api_delay": 0.68,
        "timeout": 15
    },
    {
        "name": "Yahoo Finance",
        "weight": 3.0,
        "items": 25,
        "api_delay": 0.6,
        "timeout": 15
    },
    {
        "name": "MarketWatch",
        "weight": 3.0,
        "items": 15,
        "api_delay": 1.2,
        "timeout": 18
    }
]

# Technical analysis settings
RSI_PERIOD = 14
MA_SHORT_PERIOD = 5
MA_LONG_PERIOD = 10
BOLLINGER_PERIOD = 20
VOLATILITY_WINDOW = 5

# Prediction constraints
MAX_PREDICTION_PERCENTAGE = 4.0
MIN_CONFIDENCE_THRESHOLD = 0.3

# Market symbols
SUPPORTED_MARKETS = {
    "S&P 500": "SPX",
    "FTSE 100": "UKX"
}

# API rate limits (calls per minute)
ALPHA_VANTAGE_RATE_LIMIT = 5
FMP_RATE_LIMIT = 4

# Daily API quotas
ALPHA_VANTAGE_DAILY_QUOTA = 500
FMP_DAILY_QUOTA = 250

# Retry settings
MAX_RETRIES = 3
RETRY_DELAY = 5

# Entity unique IDs
UNIQUE_ID_SP500 = "market_prediction_sp500"
UNIQUE_ID_FTSE100 = "market_prediction_ftse100"
UNIQUE_ID_PROGRESS = "market_prediction_progress"
UNIQUE_ID_STATUS = "market_prediction_status"
UNIQUE_ID_CURRENT_SOURCE = "market_prediction_current_source"
UNIQUE_ID_PROCESSING_TIME = "market_prediction_processing_time"