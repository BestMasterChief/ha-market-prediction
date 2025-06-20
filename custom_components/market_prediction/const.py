"""Constants for the Market Prediction System integration."""
from datetime import timedelta

DOMAIN = "market_prediction"
UPDATE_INTERVAL = timedelta(hours=3)

# API Configuration
ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co/query"
FMP_BASE_URL = "https://financialmodelingprep.com/api/v3"

# Default configuration
DEFAULT_UPDATE_INTERVAL = 3
DEFAULT_PREDICTION_TIMES = "06:30,12:00,17:30"
DEFAULT_CONFIDENCE_THRESHOLD = 50
DEFAULT_MAX_PREDICTION_CHANGE = 4.0

# API Limits
ALPHA_VANTAGE_DAILY_LIMIT = 500
FMP_DAILY_LIMIT = 250

# Sentiment Analysis Sources
SENTIMENT_SOURCES = [
    {
        "name": "Alpha Vantage News",
        "weight": 5.0,
        "items": 20,
        "api_delay": 1.2,
        "reliability": "high"
    },
    {
        "name": "Bloomberg Market", 
        "weight": 4.5,
        "items": 10,
        "api_delay": 1.8,
        "reliability": "high"
    },
    {
        "name": "Reuters Financial",
        "weight": 4.5,
        "items": 12,
        "api_delay": 1.1,
        "reliability": "high"
    },
    {
        "name": "Marketaux Financial",
        "weight": 4.0,
        "items": 15,
        "api_delay": 1.5,
        "reliability": "medium"
    },
    {
        "name": "Finnhub Sentiment",
        "weight": 4.0,
        "items": 18,
        "api_delay": 1.0,
        "reliability": "medium"
    },
    {
        "name": "Financial Times",
        "weight": 4.0,
        "items": 8,
        "api_delay": 1.4,
        "reliability": "high"
    },
    {
        "name": "Wall Street Journal",
        "weight": 4.0,
        "items": 15,
        "api_delay": 1.0,
        "reliability": "high"
    },
    {
        "name": "CNBC Market News",
        "weight": 3.5,
        "items": 22,
        "api_delay": 0.7,
        "reliability": "medium"
    },
    {
        "name": "Yahoo Finance",
        "weight": 3.0,
        "items": 25,
        "api_delay": 0.6,
        "reliability": "medium"
    },
    {
        "name": "MarketWatch",
        "weight": 3.0,
        "items": 15,
        "api_delay": 0.9,
        "reliability": "medium"
    },
]

# Technical Analysis Weights (Renaissance Technologies inspired)
TECHNICAL_WEIGHTS = {
    "rsi_analysis": 0.25,      # RSI overbought/oversold conditions
    "momentum_analysis": 0.30,  # 5-day price momentum
    "moving_average": 0.25,     # 5-day vs 10-day MA convergence
    "volume_analysis": 0.15,    # Volume confirmation
    "volatility": 0.05,         # Volatility impact on confidence
}

# Sentiment Analysis Weight
SENTIMENT_WEIGHT = 0.25
TECHNICAL_WEIGHT = 0.75

# Market Symbols
MARKET_SYMBOLS = {
    "sp500": {"symbol": "SPY", "name": "S&P 500"},
    "ftse100": {"symbol": "VTI", "name": "FTSE 100"},  # Using VTI as proxy
}

# Prediction Limits
MAX_PREDICTION_PERCENTAGE = 4.0
MIN_PREDICTION_PERCENTAGE = 0.1
MAX_CONFIDENCE = 95
MIN_CONFIDENCE = 10