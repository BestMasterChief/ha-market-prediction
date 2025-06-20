# HA Market Predictor

A Home Assistant custom integration that provides intelligent market predictions for FTSE 100 and S&P 500 indices.

## Features

- **Scheduled Predictions**: Automatically runs predictions 1 hour before market open and close
- **Rate Limiting**: Respects API limits (25 calls/day for Alpha Vantage, 250 for Financial Modeling Prep)
- **Manual Triggers**: On-demand predictions via Home Assistant service
- **Real-time Monitoring**: Track API usage and prediction confidence
- **Market Intelligence**: Momentum-based prediction algorithm with confidence scoring

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to "Integrations" 
3. Click the 3 dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL and select "Integration" as the category
6. Click "Download"
7. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/ha_market_predictor` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant
3. Go to Settings → Devices & Services → Add Integration
4. Search for "HA Market Predictor"

## Configuration

1. Go to Settings → Devices & Services → Add Integration
2. Search for "HA Market Predictor"
3. Enter your API keys:
   - **Alpha Vantage API Key**: Get free key from [Alpha Vantage](https://www.alphavantage.co/support/#api-key)
   - **Financial Modeling Prep API Key**: Get free key from [Financial Modeling Prep](https://financialmodelingprep.com/developer/docs)

## Usage

### Automatic Predictions

The integration automatically runs predictions at optimal times:

- **FTSE 100**: 7:00 AM and 3:30 PM UK time
- **S&P 500**: 8:30 AM and 3:00 PM ET

### Manual Predictions

Use the `ha_market_predictor.manual_prediction` service to trigger predictions on-demand:

```yaml
service: ha_market_predictor.manual_prediction
```

### Sensors

The integration creates three sensors:

1. **FTSE Prediction** (`sensor.ftse_prediction`)
   - State: UP/DOWN/NEUTRAL
   - Attributes: confidence, current_price, momentum, last_updated

2. **S&P 500 Prediction** (`sensor.s_p_500_prediction`)
   - State: UP/DOWN/NEUTRAL  
   - Attributes: confidence, current_price, momentum, last_updated

3. **API Usage Today** (`sensor.api_usage_today`)
   - State: Number of API calls made today
   - Attributes: Detailed usage for each API service

## Scheduling

The integration uses intelligent scheduling to minimize API usage:

- **Maximum 4 API calls per day** (well below the 25-call Alpha Vantage limit)
- **Market-aware timing** (only checks during relevant market hours)
- **Rate limiting protection** (prevents quota exhaustion)

## Troubleshooting

### API Limits

If you see "API limit reached" messages:

1. Check the API Usage sensor to see current consumption
2. Wait for the daily reset (midnight UTC)
3. Consider upgrading to paid API plans for higher limits

### No Predictions

If predictions aren't appearing:

1. Check your API keys are valid
2. Ensure your internet connection is stable
3. Check Home Assistant logs for error messages
4. Try running a manual prediction

## Support

- [Issues](https://github.com/your-username/ha-market-predictor/issues)
- [Discussions](https://github.com/your-username/ha-market-predictor/discussions)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
