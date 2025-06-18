"""Constants for the Market Prediction integration."""
from homeassistant.const import Platform

DOMAIN = "market_prediction"

PLATFORMS: list[Platform] = [Platform.SENSOR]

# Configuration Keys
CONF_ALPHA_VANTAGE_API_KEY = "alpha_vantage_api_key"
CONF_FMP_API_KEY = "fmp_api_key"
CONF_UPDATE_INTERVAL = "update_interval"

# Default Values
DEFAULT_UPDATE_INTERVAL = 30  # minutes
DEFAULT_SYMBOLS = ["SPY", "VTI"]  # S&P 500 and FTSE 100 ETFs

# API Endpoints
ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co/query"
FMP_BASE_URL = "https://financialmodelingprep.com/api"

# Sensor Names
SENSOR_PREDICTION_SP500 = "S&P 500 Prediction"
SENSOR_PREDICTION_FTSE = "FTSE 100 Prediction"
SENSOR_PROGRESS = "Market Prediction Progress"
SENSOR_STATUS = "Market Prediction Status"

# Progress States
PROGRESS_IDLE = "idle"
PROGRESS_FETCHING_DATA = "fetching_data"
PROGRESS_PROCESSING_TECHNICAL = "processing_technical"
PROGRESS_PROCESSING_SENTIMENT = "processing_sentiment"
PROGRESS_CALCULATING = "calculating_prediction"
PROGRESS_COMPLETE = "complete"
PROGRESS_ERROR = "error"

# Error Messages
ERROR_NO_API_KEY = "API key not configured"
ERROR_API_LIMIT = "API rate limit exceeded"
ERROR_API_ERROR = "API request failed"
ERROR_PROCESSING = "Data processing failed"

# Prediction Limits
MAX_PREDICTION_CHANGE = 4.0  # Maximum ±4% prediction
MIN_CONFIDENCE = 0.0
MAX_CONFIDENCE = 100.0