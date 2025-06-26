# Installation Guide - Market Prediction System v2.2.3

## Quick Installation (HACS)

### Prerequisites
- Home Assistant 2024.1.0 or later
- HACS installed and configured
- Alpha Vantage API key (free)
- Financial Modeling Prep API key (optional)

### Step 1: Add Custom Repository
1. Open HACS in Home Assistant
2. Click the three dots menu (⋮) in the top right
3. Select "Custom repositories"
4. Add repository URL: `https://github.com/BestMasterChief/ha-market-prediction`
5. Select category: "Integration"
6. Click "ADD"

### Step 2: Install Integration
1. Search for "Market Prediction System" in HACS
2. Click the integration card
3. Click "Download" button
4. Restart Home Assistant when prompted

### Step 3: Configure Integration
1. Go to Settings → Devices & Services
2. Click "Add Integration" (+)
3. Search for "Market Prediction System"
4. Enter your Alpha Vantage API key
5. Optionally enter Financial Modeling Prep API key
6. Configure update intervals and prediction times
7. Click "Submit"

## Manual Installation

### Step 1: Download Files
```bash
# Navigate to custom_components directory
cd /config/custom_components/

# Clone repository
git clone https://github.com/BestMasterChief/ha-market-prediction.git

# Move integration files
mv ha-market-prediction/custom_components/market_prediction ./

# Clean up
rm -rf ha-market-prediction
```

### Step 2: File Verification
Ensure your directory structure looks like this:
```
/config/custom_components/market_prediction/
├── __init__.py
├── config_flow.py
├── const.py
├── coordinator.py
├── manifest.json
└── sensor.py
```

### Step 3: Restart and Configure
1. Restart Home Assistant
2. Follow "Step 3" from HACS installation above

## API Keys Setup

### Alpha Vantage (Required)
1. Visit [https://www.alphavantage.co/support/#api-key](https://www.alphavantage.co/support/#api-key)
2. Enter your email address
3. Check your email for the API key
4. **Free tier provides 500 API calls per day**

### Financial Modeling Prep (Optional)
1. Visit [https://financialmodelingprep.com/developer/docs](https://financialmodelingprep.com/developer/docs)
2. Sign up for a free account
3. Navigate to your dashboard to get the API key
4. **Free tier provides 250 API calls per day**

## Configuration Options

### Initial Setup Options
- **Alpha Vantage API Key**: Required for market data
- **FMP API Key**: Optional, enhances sentiment analysis
- **Update Interval**: How often to refresh predictions (1-24 hours)
- **Prediction Times**: When to run analysis (comma-separated times like "06:30,12:00,17:30")

### Advanced Options (Available After Setup)
Access via Settings → Devices & Services → Market Prediction System → "Options"

- **Update Interval**: Change prediction frequency
- **Prediction Times**: Modify analysis schedule
- **Weekend Analysis**: Enable/disable weekend market analysis
- **Confidence Threshold**: Minimum confidence for predictions (10-95%)
- **Max Prediction Change**: Cap predictions at realistic levels (1-10%)

### Reconfiguration
Access via Settings → Devices & Services → Market Prediction System → "Configure"

- Change API keys
- Modify basic settings
- Validate new API connections

## Verification

### 1. Check Integration Status
- Go to Settings → Devices & Services
- Find "Market Prediction System"
- Status should show "✓ Configured"

### 2. Verify Sensor Entities
Go to Developer Tools → States and look for:
- `sensor.s_p_500_prediction`
- `sensor.ftse_100_prediction`
- `sensor.market_prediction_progress`
- `sensor.market_prediction_status`
- `sensor.market_prediction_current_source`
- `sensor.market_prediction_processing_time`

### 3. Test Functionality
- Trigger a manual update from the integration page
- Monitor the progress sensor for activity
- Check that predictions appear within 5-10 minutes

## Troubleshooting

### Common Installation Issues

**Integration not found in HACS**
- Ensure custom repository was added correctly
- Check that the URL is exactly: `https://github.com/BestMasterChief/ha-market-prediction`
- Try refreshing HACS or restarting Home Assistant

**Sensors showing "unavailable"**
- Check API keys are correctly configured
- Verify internet connectivity
- Check Home Assistant logs for errors
- Ensure API quotas haven't been exceeded

**"No prediction data available"**
- Wait 5-10 minutes for initial analysis to complete
- Check that your API keys are valid
- Monitor the progress sensor for updates

### Error Messages

**"Cannot connect to Alpha Vantage"**
- Check internet connectivity
- Verify API key is correct
- Try again later (may be temporary API issue)

**"Invalid API key"**
- Double-check your Alpha Vantage API key
- Ensure no extra spaces or characters
- Get a new API key if needed

**"API rate limit exceeded"**
- You've used your daily API quota
- Wait until the next day or upgrade your API plan
- Reduce update frequency in options

### Debug Logging

Add to `configuration.yaml` for detailed logs:
```yaml
logger:
  default: warning
  logs:
    custom_components.market_prediction: debug
```

Then restart Home Assistant and check the logs.

## Uninstallation

### HACS Method
1. Go to HACS → Integrations
2. Find "Market Prediction System"
3. Click the three dots menu
4. Select "Remove"
5. Restart Home Assistant

### Manual Method
1. Remove integration from Settings → Devices & Services
2. Delete `/config/custom_components/market_prediction/` directory
3. Restart Home Assistant

## Support

If you encounter issues:
1. Check this installation guide
2. Review the troubleshooting section
3. Check [GitHub Issues](https://github.com/BestMasterChief/ha-market-prediction/issues)
4. Create a new issue with detailed error information