# Installation Guide - Market Prediction System v2.2.2

## Prerequisites

Before installing the Market Prediction System, ensure you have:

- **Home Assistant 2024.1.0 or later**
- **HACS (Home Assistant Community Store) installed** (recommended method)
- **Alpha Vantage API key** (required - free tier available)
- **Financial Modeling Prep API key** (optional - enhances sentiment analysis)
- **Stable internet connection** for API calls

## Method 1: HACS Installation (Recommended)

### Step 1: Add Custom Repository

1. **Open HACS**: Navigate to HACS in your Home Assistant sidebar
2. **Access Custom Repositories**: 
   - Click the three dots menu (⋮) in the top right corner
   - Select "Custom repositories"
3. **Add Repository**:
   - Repository URL: `https://github.com/BestMasterChief/ha-market-prediction`
   - Category: `Integration`
   - Click "ADD"

### Step 2: Install Integration

1. **Search Integration**: 
   - Go to HACS → Integrations
   - Click "+ EXPLORE & DOWNLOAD REPOSITORIES"
   - Search for "Market Prediction System"
2. **Download**: 
   - Click on "Market Prediction System"
   - Click "DOWNLOAD"
   - Select the latest version (v2.2.2)
   - Click "DOWNLOAD" again to confirm

### Step 3: Restart Home Assistant

1. **Restart Required**: Go to Settings → System → Restart
2. **Wait for Restart**: Allow Home Assistant to fully restart (typically 1-2 minutes)

### Step 4: Configure Integration

1. **Add Integration**:
   - Go to Settings → Devices & Services
   - Click "+ ADD INTEGRATION" 
   - Search for "Market Prediction System"
   - Click on the result

2. **Enter API Keys**:
   - **Alpha Vantage API Key** (Required): Enter your API key
   - **Financial Modeling Prep API Key** (Optional): Enter if you have one
   - Click "SUBMIT"

3. **Verify Installation**:
   - The integration should appear in Devices & Services
   - Check that sensors are created and updating

## Method 2: Manual Installation

### Step 1: Download Files

#### Option A: Git Clone
```bash
cd /config/custom_components/
git clone https://github.com/BestMasterChief/ha-market-prediction.git
mv ha-market-prediction/custom_components/market_prediction ./
rm -rf ha-market-prediction
```

#### Option B: Manual Download
1. Download the latest release from GitHub
2. Extract the ZIP file
3. Copy the `custom_components/market_prediction` folder to `/config/custom_components/`

### Step 2: Verify File Structure

Ensure your file structure looks like this:
```
/config/custom_components/market_prediction/
├── __init__.py
├── manifest.json
├── const.py
├── config_flow.py
├── coordinator.py
└── sensor.py
```

### Step 3: Restart and Configure

1. **Restart Home Assistant**
2. **Follow Step 4 from HACS method** to configure the integration

## API Keys Setup

### Alpha Vantage (Required)

1. **Visit**: [https://www.alphavantage.co/support/#api-key](https://www.alphavantage.co/support/#api-key)
2. **Register**: Create a free account
3. **Get Key**: Copy your API key
4. **Limitations**: 500 API calls per day (sufficient for normal use)

### Financial Modeling Prep (Optional)

1. **Visit**: [https://financialmodelingprep.com/developer/docs](https://financialmodelingprep.com/developer/docs)
2. **Register**: Create a free account  
3. **Get Key**: Copy your API key
4. **Limitations**: 250 API calls per day
5. **Benefits**: Enhanced sentiment analysis with additional news sources

## Post-Installation Verification

### Check Sensors

Verify these sensors are created and updating:
- `sensor.s_p_500_prediction`
- `sensor.ftse_100_prediction`
- `sensor.market_prediction_progress`
- `sensor.market_prediction_status`
- `sensor.market_prediction_current_source`
- `sensor.market_prediction_processing_time`

### Test Manual Update

1. Go to Developer Tools → Services
2. Search for `homeassistant.update_entity`
3. Select `sensor.s_p_500_prediction` as target
4. Call the service to trigger manual update

### Monitor Logs

Enable debug logging to monitor operation:
```yaml
# Add to configuration.yaml
logger:
  default: warning
  logs:
    custom_components.market_prediction: debug
```

## Dashboard Setup

### Basic Dashboard Card

Add this to your dashboard:
```yaml
type: entities
title: Market Predictions
entities:
  - sensor.s_p_500_prediction
  - sensor.ftse_100_prediction
  - sensor.market_prediction_progress
  - sensor.market_prediction_status
```

### Advanced Dashboard with Progress

```yaml
type: vertical-stack
cards:
  - type: entities
    title: Market Forecasts
    entities:
      - entity: sensor.s_p_500_prediction
        name: S&P 500 Prediction
        icon: mdi:trending-up
      - entity: sensor.ftse_100_prediction
        name: FTSE 100 Prediction
        icon: mdi:trending-up
  
  - type: entities
    title: Analysis Progress
    entities:
      - entity: sensor.market_prediction_progress
        name: Progress
      - entity: sensor.market_prediction_status
        name: Status
      - entity: sensor.market_prediction_current_source
        name: Current Source
      - entity: sensor.market_prediction_processing_time
        name: Processing Time
```

## Troubleshooting

### Common Installation Issues

**Integration not found after installation**
- Clear browser cache and hard refresh (Ctrl+F5)
- Restart Home Assistant completely
- Check file permissions in custom_components folder

**API validation errors during setup**
- Verify API keys are correct (no extra spaces)
- Test API keys manually at respective provider websites
- Check internet connectivity from Home Assistant

**Sensors showing "Unknown" or "Unavailable"**
- Check API rate limits aren't exceeded
- Verify integration is properly loaded in integrations page
- Check Home Assistant logs for errors

### Advanced Troubleshooting

**Enable detailed logging**:
```yaml
logger:
  default: info
  logs:
    custom_components.market_prediction: debug
    custom_components.market_prediction.coordinator: debug
    custom_components.market_prediction.sensor: debug
```

**Check integration status**:
1. Go to Settings → Devices & Services
2. Find "Market Prediction System"
3. Click on it to see detailed status
4. Look for any error messages or warnings

**Manual API testing**:
```bash
# Test Alpha Vantage API
curl "https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=SPY&apikey=YOUR_KEY"

# Test FMP API  
curl "https://financialmodelingprep.com/api/v3/quote/SPY?apikey=YOUR_KEY"
```

## Updates and Maintenance

### HACS Updates

When updates are available:
1. HACS will show update notifications
2. Go to HACS → Integrations
3. Find "Market Prediction System" with "Update" badge
4. Click "Update" and follow prompts
5. Restart Home Assistant

### Manual Updates

1. Download latest release
2. Replace files in `/config/custom_components/market_prediction/`
3. Restart Home Assistant
4. Check changelog for any breaking changes

## Support

- **GitHub Issues**: [Report bugs and feature requests](https://github.com/BestMasterChief/ha-market-prediction/issues)
- **Documentation**: [Full documentation](https://github.com/BestMasterChief/ha-market-prediction)
- **Community**: Home Assistant Community Forum

## Next Steps

After successful installation:
1. **Set up automations** based on market predictions
2. **Create custom dashboards** for monitoring
3. **Configure notifications** for significant market movements
4. **Monitor API usage** to stay within rate limits

---

For detailed usage instructions and advanced configuration, see the main [README.md](README.md) file.