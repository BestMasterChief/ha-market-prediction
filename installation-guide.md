# HA Market Predictor - Installation Guide

## Overview

The HA Market Predictor is now properly configured as a Home Assistant custom integration that can be installed via HACS. This replaces the previous standalone application approach.

## What Changed

Previously, you had a standalone Flask application that ran separately from Home Assistant. Now, the market prediction functionality is integrated directly into Home Assistant as a custom integration, providing:

- Native Home Assistant sensor entities
- Automatic scheduling without external dependencies
- Configuration through Home Assistant UI
- Service calls for manual predictions
- Proper rate limiting and error handling

## Installation Steps

### 1. Organize Files for GitHub

Run the provided batch script to organize files:

```bash
organize_files.bat
```

This creates a `Full/` directory with the proper GitHub structure.

### 2. Upload to GitHub

1. Create a new GitHub repository (e.g., `ha-market-predictor`)
2. Upload all contents from the `Full/` directory to your repository
3. Update the repository URLs in:
   - `custom_components/ha_market_predictor/manifest.json`
   - `README.md`

### 3. Add to HACS

1. Open HACS in Home Assistant
2. Go to "Integrations"
3. Click the 3 dots menu → "Custom repositories"
4. Add your GitHub repository URL
5. Select "Integration" as the category
6. Click "Download"

### 4. Install the Integration

1. Restart Home Assistant
2. Go to Settings → Devices & Services → Add Integration
3. Search for "HA Market Predictor"
4. Enter your API keys:
   - Alpha Vantage API Key
   - Financial Modeling Prep API Key

## Available Entities

After installation, you'll have these entities:

### Sensors

1. **sensor.ftse_prediction**
   - State: UP/DOWN/NEUTRAL
   - Attributes: confidence, current_price, momentum, last_updated

2. **sensor.s_p_500_prediction**
   - State: UP/DOWN/NEUTRAL
   - Attributes: confidence, current_price, momentum, last_updated

3. **sensor.api_usage_today**
   - State: Number of API calls used today
   - Attributes: Detailed usage for each API service

### Services

- **ha_market_predictor.manual_prediction**: Trigger manual predictions for both markets

## Scheduling

The integration automatically runs predictions at:

- **FTSE 100**: 7:00 AM and 3:30 PM UK time (1 hour before open/close)
- **S&P 500**: 8:30 AM and 3:00 PM ET (1 hour before open/close)

Maximum of 4 API calls per day, well under the 25-call Alpha Vantage limit.

## Usage Examples

### Dashboard Card

Add this to your Lovelace dashboard:

```yaml
type: entities
title: Market Predictions
entities:
  - sensor.ftse_prediction
  - sensor.s_p_500_prediction
  - sensor.api_usage_today
```

### Automation Example

Trigger actions based on predictions:

```yaml
automation:
  - alias: "Market Alert - FTSE Bullish"
    trigger:
      - platform: state
        entity_id: sensor.ftse_prediction
        to: "UP"
    condition:
      - condition: numeric_state
        entity_id: sensor.ftse_prediction
        attribute: confidence
        above: 70
    action:
      - service: notify.mobile_app
        data:
          title: "FTSE Bullish Signal"
          message: "FTSE prediction: UP with {{ state_attr('sensor.ftse_prediction', 'confidence') }}% confidence"
```

### Manual Prediction Script

```yaml
script:
  manual_market_check:
    alias: "Manual Market Check"
    sequence:
      - service: ha_market_predictor.manual_prediction
      - delay: "00:00:30"
      - service: notify.home_assistant
        data:
          message: >
            Market Update:
            FTSE: {{ states('sensor.ftse_prediction') }}
            S&P 500: {{ states('sensor.s_p_500_prediction') }}
```

## Troubleshooting

### Common Issues

1. **Integration not appearing**: Ensure you've restarted Home Assistant after adding to HACS
2. **API errors**: Check your API keys in the integration configuration
3. **No predictions**: Check the API usage sensor to ensure you haven't hit rate limits

### Log Monitoring

Enable debug logging for troubleshooting:

```yaml
logger:
  default: warning
  logs:
    custom_components.ha_market_predictor: debug
```

## Migration from Previous Version

If you were using the standalone Flask application:

1. Stop the old application
2. Remove any related automations or scripts
3. Install this Home Assistant integration
4. Update any automations to use the new sensor entities

The new integration provides the same functionality but integrated directly into Home Assistant with better scheduling and rate limiting.