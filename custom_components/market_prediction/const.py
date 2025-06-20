"""Constants for the Market Prediction System integration."""

DOMAIN = "market_prediction"

# API URLs
ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co/query"
FMP_BASE_URL = "https://financialmodelingprep.com/api/v3"

# Default values
DEFAULT_NAME = "Market Prediction System"
DEFAULT_SCAN_INTERVAL = 3600  # 1 hour
DEFAULT_TIMEOUT = 30

# Update intervals (in seconds)
UPDATE_INTERVAL_SECONDS = 300  # 5 minutes

# Prediction weight distribution
TECHNICAL_WEIGHT = 0.75
SENTIMENT_WEIGHT = 0.25

# Technical analysis weights
RSI_WEIGHT = 0.25
MOMENTUM_WEIGHT = 0.30
MA_WEIGHT = 0.25
BOLLINGER_WEIGHT = 0.15
VOLUME_WEIGHT = 0.15
VOLATILITY_WEIGHT = 0.10

# Sentiment analysis sources with weights and processing times
SENTIMENT_SOURCES = [
    {
        "name": "Alpha Vantage News",
        "weight": 5.0,
        "items": 20,
        "api_delay": 1.25
    },
    {
        "name": "Bloomberg Market",
        "weight": 4.5,
        "items": 10,
        "api_delay": 3.5
    },
    {
        "name": "Reuters Financial",
        "weight": 4.5,
        "items": 12,
        "api_delay": 1.8
    },
    {
        "name": "Marketaux Financial",
        "weight": 4.0,
        "items": 15,
        "api_delay": 2.0
    },
    {
        "name": "Finnhub Sentiment",
        "weight": 4.0,
        "items": 18,
        "api_delay": 1.1
    },
    {
        "name": "Financial Times",
        "weight": 4.0,
        "items": 8,
        "api_delay": 3.5
    },
    {
        "name": "Wall Street Journal",
        "weight": 4.0,
        "items": 15,
        "api_delay": 1.3
    },
    {
        "name": "CNBC Market News",
        "weight": 3.5,
        "items": 22,
        "api_delay": 0.7
    },
    {
        "name": "Yahoo Finance",
        "weight": 3.0,
        "items": 25,
        "api_delay": 0.6
    },
    {
        "name": "MarketWatch",
        "weight": 3.0,
        "items": 15,
        "api_delay": 1.2
    }
]

# Symbols to track
SYMBOLS = {
    "SP500": "SPY",
    "FTSE100": "ISF.L"
}

# Sensor types
SENSOR_TYPES = [
    "s_p_500_prediction",
    "ftse_100_prediction",
    "market_prediction_progress",
    "market_prediction_status",
    "market_prediction_current_source",
    "market_prediction_processing_time"
]

# Prediction states
PREDICTION_STATES = {
    "up": "UP",
    "down": "DOWN",
    "flat": "FLAT"
}

# Progress stages
PROGRESS_STAGES = {
    "initializing": {"progress": 5, "description": "Initializing"},
    "fetching_data": {"progress": 25, "description": "Fetching Market Data"},
    "processing_technical": {"progress": 50, "description": "Processing Technical Analysis"},
    "processing_sentiment": {"progress": 75, "description": "Processing Sentiment Analysis"},
    "calculating": {"progress": 90, "description": "Calculating Predictions"},
    "complete": {"progress": 100, "description": "Complete"}
}

# API rate limits
ALPHA_VANTAGE_RATE_LIMIT = 5  # calls per minute
FMP_RATE_LIMIT = 4  # calls per minute

# API quotas (daily)
ALPHA_VANTAGE_DAILY_QUOTA = 500
FMP_DAILY_QUOTA = 250

# Prediction limits
MAX_PREDICTION_CHANGE = 4.0  # Maximum percentage change
MIN_CONFIDENCE = 0.0
MAX_CONFIDENCE = 100.0