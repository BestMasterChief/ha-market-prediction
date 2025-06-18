# Market Prediction System - Detailed Installation Guide

This guide provides step-by-step instructions for installing the Market Prediction System in Home Assistant 2025.

## Prerequisites

- Home Assistant 2025.1.0 or later
- Internet connection for API access
- HACS installed (for HACS method)

## Installation Method 1: HACS (Recommended)

### Step 1: Add Custom Repository to HACS

1. **Open HACS**:
   - Go to Home Assistant sidebar
   - Click on "HACS"

2. **Access Integrations**:
   - Click on "Integrations" tab in HACS

3. **Add Custom Repository**:
   - Click the three dots (⋮) in the top right corner
   - Select "Custom repositories"
   - Add the following details:
     - **Repository**: `https://github.com/yourusername/ha-market-prediction`
     - **Category**: Integration
   - Click "ADD"

### Step 2: Install the Integration

1. **Search for Integration**:
   - In HACS Integrations, search for "Market Prediction System"
   - Click on the integration when it appears

2. **Download Integration**:
   - Click "Download" button
   - Wait for download to complete
   - Click "Download" again to confirm

3. **Restart Home Assistant**:
   - Go to Settings → System → Restart
   - Wait for restart to complete

### Step 3: Configure the Integration

1. **Add Integration**:
   - Go to Settings → Devices & Services
   - Click "Add Integration" (+ button)
   - Search for "Market Prediction System"
   - Click on it to start configuration

2. **Enter API Keys**:
   - **Alpha Vantage API Key** (Required): Enter your key
   - **FMP API Key** (Optional): Enter your key or leave blank
   - **Update Interval**: Set to 30 minutes (default) or customize

3. **Complete Setup**:
   - Click "Submit"
   - Assign to an area if desired
   - Click "Finish"

## Installation Method 2: Manual Installation

### Step 1: Download Repository

Choose one of these methods:

**Option A: Using Git**
```bash
cd /config
git clone https://github.com/yourusername/ha-market-prediction.git
```

**Option B: Direct Download**
1. Go to https://github.com/yourusername/ha-market-prediction
2. Click "Code" → "Download ZIP"
3. Extract ZIP file

### Step 2: Copy Files

1. **Copy Integration Files**:
   ```bash
   cp -r ha-market-prediction/custom_components/market_prediction /config/custom_components/
   ```

2. **Verify File Structure**:
   ```
   /config/custom_components/market_prediction/
   ├── __init__.py
   ├── manifest.json
   ├── config_flow.py
   ├── sensor.py
   ├── const.py
   └── coordinator.py
   ```

### Step 3: Restart and Configure

1. **Restart Home Assistant**:
   - Go to Settings → System → Restart

2. **Add Integration**:
   - Go to Settings → Devices & Services
   - Click "Add Integration"
   - Search for "Market Prediction System"
   - Follow configuration steps above

## API Key Setup

### Alpha Vantage API Key (Required)

1. **Create Account**:
   - Visit: https://www.alphavantage.co/support/#api-key
   - Click "Get your free API key today"
   - Fill out the form with your details
   - Choose "Individual" for account type

2. **Get API Key**:
   - Check your email for activation link
   - Log into your account
   - Copy your API key
   - **Example**: `ABCD1234EFGH5678`

3. **Free Tier Limits**:
   - 500 API calls per day
   - 5 API calls per minute
   - Sufficient for 30-minute updates

### Financial Modeling Prep API Key (Optional)

1. **Create Account**:
   - Visit: https://financialmodelingprep.com/developer/docs
   - Click "Get API Key"
   - Sign up for free account

2. **Get API Key**:
   - Log into dashboard
   - Copy your API key from the dashboard
   - **Example**: `xyz789abc456def123`

3. **Free Tier Limits**:
   - 250 API calls per day
   - Used for news sentiment analysis
   - System works without this key (technical analysis only)

## GitHub Repository Setup (For Contributing)

### Step 1: Fork the Repository

1. **Fork on GitHub**:
   - Go to: https://github.com/yourusername/ha-market-prediction
   - Click "Fork" button
   - Select your GitHub account

### Step 2: Clone Your Fork

```bash
git clone https://github.com/YOURUSERNAME/ha-market-prediction.git
cd ha-market-prediction
```

### Step 3: Set Up Development Environment

1. **Add Upstream Remote**:
   ```bash
   git remote add upstream https://github.com/yourusername/ha-market-prediction.git
   ```

2. **Create Development Branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

### Step 4: Make Changes and Contribute

1. **Make Your Changes**
2. **Test Changes**:
   - Install in test Home Assistant instance
   - Verify functionality

3. **Commit and Push**:
   ```bash
   git add .
   git commit -m "Description of changes"
   git push origin feature/your-feature-name
   ```

4. **Create Pull Request**:
   - Go to your fork on GitHub
   - Click "New Pull Request"
   - Add description of changes

## Configuration Validation

### Step 1: Check Integration Status

1. **Verify Installation**:
   - Go to Settings → Devices & Services
   - Look for "Market Prediction System"
   - Status should be "Configured"

2. **Check Sensors**:
   - Go to Developer Tools → States
   - Look for these entities:
     - `sensor.s_p_500_prediction`
     - `sensor.ftse_100_prediction`
     - `sensor.market_prediction_progress`
     - `sensor.market_prediction_status`

### Step 2: Test API Connections

1. **Check Logs**:
   - Go to Settings → System → Logs
   - Look for "custom_components.market_prediction"
   - Should show successful API connections

2. **Manual Update**:
   - Go to Developer Tools → Services
   - Call service: `homeassistant.update_entity`
   - Target: `sensor.s_p_500_prediction`

### Step 3: Verify Data Updates

1. **Check Sensor States**:
   - Sensors should update within 30 minutes
   - Progress sensor should show processing stages
   - Prediction sensors should show "UP X%" or "DOWN X%"

2. **Check Attributes**:
   - Each prediction sensor should have:
     - `direction`: UP/DOWN/FLAT
     - `percentage`: 0.0-4.0
     - `confidence`: 0-100
     - `explanation`: Text description

## Troubleshooting Common Issues

### Issue: "Integration not found"

**Cause**: Files not copied correctly or HA not restarted

**Solution**:
1. Verify file structure in `/config/custom_components/`
2. Restart Home Assistant
3. Clear browser cache (Ctrl+F5)

### Issue: "Invalid API key"

**Cause**: Incorrect API key or expired key

**Solution**:
1. Double-check API key from provider
2. Ensure no extra spaces in key
3. Reconfigure integration with correct key

### Issue: "Sensors show unavailable"

**Cause**: API connection problems or rate limits

**Solution**:
1. Check internet connection
2. Verify API usage limits not exceeded
3. Wait 24 hours for rate limits to reset
4. Check Home Assistant logs for specific errors

### Issue: "No prediction data available"

**Cause**: API data processing failed

**Solution**:
1. Check logs for specific error messages
2. Verify both API services are accessible
3. Try manual sensor update
4. Restart integration if needed

## Advanced Configuration

### Custom Update Intervals

Edit integration configuration:
- Minimum: 15 minutes (to respect API limits)
- Maximum: 120 minutes
- Recommended: 30 minutes for good balance

### Dashboard Integration

Add to dashboard:
```yaml
type: grid
columns: 2
cards:
  - type: sensor
    entity: sensor.s_p_500_prediction
    name: S&P 500
  - type: sensor
    entity: sensor.ftse_100_prediction
    name: FTSE 100
  - type: sensor
    entity: sensor.market_prediction_progress
    name: Processing
  - type: sensor
    entity: sensor.market_prediction_status
    name: Status
```

### Automation Examples

**Daily Alert Automation**:
```yaml
alias: Market Prediction Alert
triggers:
  - trigger: time
    at: "09:30:00"
conditions:
  - condition: time
    weekday: ["mon", "tue", "wed", "thu", "fri"]
actions:
  - action: notify.persistent_notification
    data:
      title: "📈 Daily Market Prediction"
      message: |
        S&P 500: {{ states('sensor.s_p_500_prediction') }}
        FTSE 100: {{ states('sensor.ftse_100_prediction') }}
```

## Support and Resources

- **Issues**: https://github.com/yourusername/ha-market-prediction/issues
- **Discussions**: https://github.com/yourusername/ha-market-prediction/discussions
- **Home Assistant Community**: https://community.home-assistant.io
- **Documentation**: This repository's wiki

## Security Notes

1. **API Keys**:
   - Never share API keys publicly
   - Store in Home Assistant secrets if needed
   - Regenerate keys if compromised

2. **Repository**:
   - Don't commit API keys to version control
   - Use `.gitignore` for sensitive files
   - Keep personal forks private if needed

## Next Steps

After successful installation:

1. **Monitor Performance**: Check daily predictions and accuracy
2. **Customize Dashboards**: Create personalized market views
3. **Set Up Automations**: Create alerts and notifications
4. **Contribute**: Report issues and suggest improvements
5. **Explore**: Try different update intervals and configurations

## Conclusion

You should now have a fully functional Market Prediction System running in Home Assistant 2025. The system will provide daily market predictions with progress tracking and detailed explanations of the analysis.

For questions or issues, please check the troubleshooting section or create an issue on GitHub.