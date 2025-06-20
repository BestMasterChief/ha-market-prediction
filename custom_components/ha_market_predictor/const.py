"""Constants for the HA Market Predictor integration."""
from datetime import timedelta

DOMAIN = "ha_market_predictor"

# Configuration keys
CONF_ALPHAVANTAGE_API_KEY = "alphavantage_api_key"
CONF_FINANCIALMODELPREP_API_KEY = "financialmodelprep_api_key"

# API Limits
ALPHAVANTAGE_DAILY_LIMIT = 25
FINANCIALMODELPREP_DAILY_LIMIT = 250

# Update intervals
DEFAULT_UPDATE_INTERVAL = timedelta(hours=1)

# Market symbols
FTSE_SYMBOL = "^FTSE"
SP500_SYMBOL = "^GSPC"

# Market timings (in UTC for consistency)
FTSE_PRE_MARKET_HOUR = 7  # 7:00 AM UK time (1 hour before 8:00 AM open)
FTSE_PRE_CLOSE_HOUR = 15  # 3:30 PM UK time (1 hour before 4:30 PM close)
SP500_PRE_MARKET_HOUR = 13  # 8:30 AM ET in UTC (1 hour before 9:30 AM open)
SP500_PRE_CLOSE_HOUR = 20  # 3:00 PM ET in UTC (1 hour before 4:00 PM close)

# Entity names
FTSE_PREDICTION_ENTITY = "ftse_prediction"
SP500_PREDICTION_ENTITY = "sp500_prediction"
API_USAGE_ENTITY = "api_usage_today"
