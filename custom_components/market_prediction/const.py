"""Constants for the Market Prediction integration."""
from datetime import timedelta

DOMAIN = "market_prediction"

# Configuration
CONF_ALPHA_VANTAGE_API_KEY = "alpha_vantage_api_key"
CONF_FMP_API_KEY = "fmp_api_key"

# Defaults
DEFAULT_UPDATE_INTERVAL = timedelta(hours=1)
DEFAULT_NAME = "Market Prediction"
DEFAULT_TIMEOUT = 30

# API URLs
ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co/query"
FMP_BASE_URL = "https://financialmodelingprep.com/api/v3"

# Supported symbols
SUPPORTED_SYMBOLS = {
    "S&P 500": "SPY",
    "FTSE 100": "EWU",
}

# Progress stages
PROGRESS_STAGES = {
    "initializing": {"stage": "Initializing", "progress": 5},
    "fetching_data": {"stage": "Fetching Market Data", "progress": 25},
    "processing_technical": {"stage": "Processing Technical Analysis", "progress": 50},
    "processing_sentiment": {"stage": "Processing Sentiment Analysis", "progress": 75},
    "calculating": {"stage": "Calculating Predictions", "progress": 90},
    "complete": {"stage": "Complete", "progress": 100},
}

# API Limits
ALPHA_VANTAGE_DAILY_LIMIT = 500
FMP_DAILY_LIMIT = 250

# Sensor attributes
ATTR_CONFIDENCE = "confidence"
ATTR_DIRECTION = "direction"
ATTR_PERCENTAGE = "percentage"
ATTR_EXPLANATION = "explanation"
ATTR_LAST_UPDATE = "last_update"
ATTR_API_CALLS_REMAINING = "api_calls_remaining"