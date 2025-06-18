# Installation Guide - Market Prediction System

This guide provides detailed installation instructions for the Market Prediction System integration for Home Assistant.

## 🔧 Prerequisites

Before starting, ensure you have:

- Home Assistant 2024.1.0 or newer
- HACS installed and configured
- Internet connection for API access
- API keys (see section below)

## 🗝️ API Key Requirements

### Alpha Vantage (Required)
- **Free Tier**: 500 API calls per day
- **Sign Up**: https://www.alphavantage.co/support/#api-key
- **Cost**: Free
- **Usage**: Market data and technical analysis

### Financial Modeling Prep (Optional)
- **Free Tier**: 250 total API calls (lifetime)
- **Sign Up**: https://financialmodelingprep.com/developer/docs
- **Cost**: Free (limited) or paid plans available
- **Usage**: News sentiment analysis

**Note**: The integration works with just the Alpha Vantage API key. FMP is optional for enhanced sentiment analysis.

## 📦 Installation Methods

### Method A: HACS Installation (Recommended)

#### Step 1: Add Custom Repository
1. Open Home Assistant
2. Navigate to **HACS** → **Integrations**
3. Click the **three dots (⋮)** in the top right corner
4. Select **"Custom repositories"**
5. Add the following details:
   - **Repository**: `https://github.com/BestMasterChief/ha-market-prediction`
   - **Category**: `Integration`
6. Click **"ADD"**

#### Step 2: Install Integration
1. In HACS, search for **"Market Prediction System"**
2. Click on the integration
3. Click **"Download"**
4. Wait for download to complete
5. **Restart Home Assistant**

#### Step 3: Configure Integration
1. Go to **Settings** → **Devices & Services**
2. Click **"Add Integration"** (+ button)
3. Search for **"Market Prediction System"**
4. Enter your API keys:
   - **Alpha Vantage API Key**: [Your key] (Required)
   - **FMP API Key**: [Your key] (Optional)
5. Click **"Submit"**

### Method B: Manual Installation

#### Step 1: Download Files
1. Download the latest release from: https://github.com/BestMasterChief/ha-market-prediction/releases
2. Extract the ZIP file
3. Copy the `custom_components/market_prediction/` folder to your Home Assistant `custom_components` directory

**Expected Directory Structure:**
```
/config/
├── custom_components/
│   └── market_prediction/
│       ├── __init__.py
│       ├── manifest.json
│       ├── const.py
│       ├── config_flow.py
│       ├── coordinator.py
│       └── sensor.py
```

#### Step 2: Restart Home Assistant
1. Restart Home Assistant completely
2. Wait for restart to complete

#### Step 3: Add Integration
1. Go to **Settings** → **Devices & Services**
2. Click **"Add Integration"** (+ button)
3. Search for **"Market Prediction System"**
4. Configure with your API keys

## 🌐 GitHub Repository Setup (For Contributors)

### Critical Branch Configuration

**⚠️ Important**: HACS requires the default branch to be named `main` or `master`, not `ha-market-prediction`.

#### Fix Branch Name Issue:
```bash
# If your current default branch is "ha-market-prediction"
git checkout ha-market-prediction
git branch -m ha-market-prediction main
git push -u origin main

# Update GitHub default branch
# Go to GitHub → Settings → Branches → Change default branch to "main"

# Update local references
git branch --unset-upstream
git push --set-upstream origin main
```

### Repository File Structure
```
ha-market-prediction/
├── custom_components/
│   └── market_prediction/
│       ├── __init__.py
│       ├── manifest.json
│       ├── const.py
│       ├── config_flow.py
│       ├── coordinator.py
│       └── sensor.py
├── .github/
│   └── workflows/
│       └── validate.yaml
├── README.md
├── INSTALLATION.md
├── hacs.json
└── LICENSE
```

## ✅ Verification Steps

### 1. Check Integration Status
- Go to **Settings** → **Devices & Services**
- Look for **"Market Prediction System"**
- Status should show **"✓ Configured"**

### 2. Verify Sensors
Navigate to **Developer Tools** → **States** and check for:
- `sensor.s_p_500_prediction`
- `sensor.ftse_100_prediction`
- `sensor.market_prediction_progress`
- `sensor.market_prediction_status`

### 3. Test Progress Tracking
1. Go to **Developer Tools** → **Services**
2. Call service: `homeassistant.update_entity`
3. Target: `sensor.market_prediction_progress`
4. Watch the progress sensor update through stages

### 4. Check Logs
- Go to **Settings** → **System** → **Logs**
- Look for any errors related to `market_prediction`
- Normal operation should show minimal warnings

## 🚨 Troubleshooting

### Common Issues and Solutions

#### "Integration not found"
**Cause**: Files not properly placed or Home Assistant not restarted.

**Solution**:
1. Verify file placement in `/config/custom_components/market_prediction/`
2. Restart Home Assistant completely
3. Clear browser cache

#### "Invalid API key" Error
**Cause**: Incorrect or expired API keys.

**Solution**:
1. Verify API keys are copied correctly (no extra spaces)
2. Test API keys manually:
   ```bash
   # Test Alpha Vantage
   curl "https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=SPY&apikey=YOUR_KEY"
   
   # Test FMP (if using)
   curl "https://financialmodelingprep.com/api/v3/quote/SPY?apikey=YOUR_KEY"
   ```

#### "Sensors Unavailable"
**Cause**: API calls failing or rate limits exceeded.

**Solution**:
1. Check API quota usage
2. Wait for rate limit reset (usually 24 hours)
3. Enable debug logging:
   ```yaml
   logger:
     default: warning
     logs:
       custom_components.market_prediction: debug
   ```

#### "Progress jumps to 100%"
**Cause**: Coordinator error during data fetching.

**Solution**:
1. Check Home Assistant logs for specific errors
2. Verify API keys are valid
3. Check network connectivity
4. Restart integration:
   - Settings → Devices & Services → Market Prediction System → ... → Reload

### Log Analysis

#### Enable Detailed Logging
Add to `configuration.yaml`:
```yaml
logger:
  default: warning
  logs:
    custom_components.market_prediction: debug
    custom_components.market_prediction.coordinator: debug
```

#### Log Locations
- **Main Logs**: Settings → System → Logs
- **Integration Logs**: Filter by "market_prediction"

### API Quota Management

#### Check Remaining Calls
The status sensor shows remaining API calls:
- Check attributes of `sensor.market_prediction_status`
- Look for `alpha_vantage_calls_remaining` and `fmp_calls_remaining`

#### Rate Limit Best Practices
- Alpha Vantage: 5 calls per minute maximum
- FMP: 4 calls per minute maximum
- Daily limits reset at midnight UTC

## 🔄 Updates and Maintenance

### HACS Updates
1. HACS will automatically notify of updates
2. Click "Update" when available
3. Restart Home Assistant

### Manual Updates
1. Download new release from GitHub
2. Replace files in `custom_components/market_prediction/`
3. Restart Home Assistant

### Configuration Changes
- Most settings can be changed via the integration UI
- Go to Settings → Devices & Services → Market Prediction System → Configure

## 📞 Support

### Getting Help
1. **Check Logs**: Always check logs first for specific error messages
2. **GitHub Issues**: Report bugs at https://github.com/BestMasterChief/ha-market-prediction/issues
3. **Home Assistant Community**: Post in the custom components section

### Reporting Issues
When reporting issues, please include:
- Home Assistant version
- Integration version
- Complete error logs
- Steps to reproduce the problem
- API provider (Alpha Vantage, FMP, or both)

---

**Need more help?** Check the [README.md](README.md) for additional information or open an issue on GitHub.