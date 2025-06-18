# Complete Installation and GitHub Setup Guide

## GitHub Repository Setup Instructions

### Step 1: Fix Repository Default Branch

⚠️ **CRITICAL**: Your repository's default branch "ha-market-prediction" must be changed to "main" for HACS compatibility.

1. **Change Default Branch**:
   - Go to your repository: https://github.com/BestMasterChief/ha-market-prediction
   - Click Settings → Branches
   - Under "Default branch", click the edit icon
   - Change from "ha-market-prediction" to "main"
   - Confirm the change

2. **Update Local Repository** (if you have local files):
   ```bash
   git branch -m ha-market-prediction main
   git push origin main
   git push origin --delete ha-market-prediction
   ```

### Step 2: Create Proper Directory Structure

Create this exact folder structure in your repository:

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
├── hacs.json
└── INSTALLATION.md
```

### Step 3: Upload All Files

Upload these files to your GitHub repository in the correct locations:

1. **Root Directory Files**:
   - `README.md` (main documentation)
   - `hacs.json` (HACS configuration)
   - `INSTALLATION.md` (this file)

2. **custom_components/market_prediction/ Files**:
   - `__init__.py` (integration entry point)
   - `manifest.json` (integration metadata)
   - `const.py` (constants and configuration)
   - `config_flow.py` (UI configuration)
   - `coordinator.py` (main processing logic)
   - `sensor.py` (sensor entities)

3. **GitHub Actions File** (optional but recommended):
   ```yaml
   # .github/workflows/validate.yaml
   name: Validate
   on:
     push:
     pull_request:
   jobs:
     validate:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         - name: HACS Validation
           uses: hacs/action@main
           with:
             category: integration
   ```

### Step 4: Create GitHub Release

1. **Go to Releases**:
   - Navigate to https://github.com/BestMasterChief/ha-market-prediction/releases
   - Click "Create a new release"

2. **Release Configuration**:
   - **Tag version**: `v2.2.0`
   - **Release title**: `Market Prediction System v2.2.0 - Enhanced Sentiment Analysis`
   - **Description**:
     ```markdown
     ## Enhanced Multi-Source Sentiment Analysis
     
     ### 🎯 Fixes
     - ✅ Sentiment analysis now takes 5-10 minutes instead of completing instantly
     - ✅ Added 10 financial news sources with weighted scoring
     - ✅ Real-time progress tracking with current source display
     - ✅ Comprehensive processing time breakdown
     
     ### 🚀 New Features
     - Multi-source sentiment analysis (Alpha Vantage, Marketaux, Finnhub, etc.)
     - Progress tracking sensors with ETA calculation
     - Current source display sensor
     - Processing time monitoring
     - Renaissance Technologies-inspired 75/25 weighting
     
     ### 📊 Sentiment Sources
     - Alpha Vantage News (weight: 5.0, 20 items)
     - Bloomberg Market (weight: 4.5, 10 items)
     - Reuters Financial (weight: 4.5, 12 items)
     - Marketaux Financial (weight: 4.0, 15 items)
     - Finnhub Sentiment (weight: 4.0, 18 items)
     - And 5 more sources for comprehensive coverage
     
     ### 🔧 Installation
     1. Add repository to HACS custom repositories
     2. Install "Market Prediction System" integration
     3. Configure with Alpha Vantage API key (required)
     4. Optionally add FMP API key for enhanced features
     ```

3. **Attach Files** (optional):
   - You can attach a ZIP file of the integration for manual installation

4. **Publish Release**

## HACS Installation for Users

### Method 1: Add as Custom Repository

1. **Open HACS**:
   - Home Assistant → HACS → Integrations

2. **Add Custom Repository**:
   - Click three dots menu (⋮) → Custom repositories
   - Repository: `https://github.com/BestMasterChief/ha-market-prediction`
   - Category: `Integration`
   - Click "Add"

3. **Install Integration**:
   - Search for "Market Prediction System"
   - Click "Download"
   - Restart Home Assistant

4. **Configure Integration**:
   - Settings → Devices & Services
   - Click "Add Integration"
   - Search "Market Prediction System"
   - Enter API keys

### Method 2: Manual Installation

1. **Download Files**:
   - Download from: https://github.com/BestMasterChief/ha-market-prediction/releases
   - Extract the ZIP file

2. **Copy Files**:
   ```bash
   # Copy to Home Assistant config directory
   cp -r custom_components/market_prediction /config/custom_components/
   ```

3. **Restart Home Assistant**

4. **Add Integration**: Settings → Devices & Services → Add Integration

## API Keys Setup

### Alpha Vantage (Required)

1. **Get Free API Key**:
   - Visit: https://www.alphavantage.co/support/#api-key
   - Fill out the form (name, email, etc.)
   - Copy your API key

2. **Test API Key**:
   ```bash
   curl "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=SPY&apikey=YOUR_KEY"
   ```

### Financial Modeling Prep (Optional)

1. **Get Free API Key**:
   - Visit: https://site.financialmodelingprep.com/developer/docs/
   - Sign up for free account
   - Copy API key from dashboard

2. **Test API Key**:
   ```bash
   curl "https://financialmodelingprep.com/api/v3/quote/SPY?apikey=YOUR_KEY"
   ```

## Configuration Methods

### Option 1: Integration UI (Recommended)

1. **Add Integration**:
   - Settings → Devices & Services
   - Click "Add Integration"
   - Search "Market Prediction System"

2. **Enter API Keys**:
   - Alpha Vantage API Key: `YOUR_ALPHA_VANTAGE_KEY` (required)
   - FMP API Key: `YOUR_FMP_KEY` (optional)

3. **Complete Setup**:
   - Integration will validate keys
   - Creates 6 sensors automatically

### Option 2: secrets.yaml (Alternative)

If you prefer file-based configuration:

```yaml
# secrets.yaml
alpha_vantage_key: "YOUR_ALPHA_VANTAGE_KEY_HERE"
fmp_key: "YOUR_FMP_KEY_HERE"
```

## Sensors Created

The integration creates these sensors:

### Market Predictions
- `sensor.market_prediction_s_p_500`: S&P 500 forecast
- `sensor.market_prediction_ftse_100`: FTSE 100 forecast

### Progress Tracking (New in v2.2.0)
- `sensor.market_prediction_progress`: Analysis progress %
- `sensor.market_prediction_status`: Current processing stage
- `sensor.market_prediction_current_source`: Source being processed
- `sensor.market_prediction_processing_time`: Total processing time

## Expected Behavior

### Normal Analysis Flow (5-10 minutes total)

1. **Initializing** (5%) - 2 seconds
2. **Fetching Market Data** (25%) - 30-45 seconds
3. **Processing Technical Analysis** (50%) - 3-5 seconds
4. **Processing Sentiment Analysis** (75%) - **5-10 minutes** ⏱️
   - Alpha Vantage News (20 items, ~25 seconds)
   - Marketaux Financial (15 items, ~30 seconds)
   - Finnhub Sentiment (18 items, ~20 seconds)
   - Yahoo Finance (25 items, ~15 seconds)
   - MarketWatch (15 items, ~18 seconds)
   - Reuters Financial (12 items, ~22 seconds)
   - Bloomberg Market (10 items, ~35 seconds)
   - CNBC Market News (22 items, ~15 seconds)
   - Financial Times (8 items, ~28 seconds)
   - Wall Street Journal (15 items, ~20 seconds)
5. **Calculating Predictions** (90%) - 2-3 seconds
6. **Complete** (100%) - Done!

### Progress Display

Watch these sensors during analysis:
- `sensor.market_prediction_status`: Shows current stage
- `sensor.market_prediction_current_source`: Shows "Bloomberg Market", "Reuters Financial", etc.
- `sensor.market_prediction_progress`: Shows percentage (0-100%)

## Troubleshooting

### Issue 1: Analysis Too Fast (Fixed)
- ✅ **Fixed in v2.2.0**: Now takes 5-10 minutes with visible progress

### Issue 2: Sensors Unavailable
- Check API keys in Settings → Devices & Services
- Verify internet connection
- Check Home Assistant logs

### Issue 3: "Duplicate key" errors
- Ensure you're using the integration, not manual YAML
- Remove any old configuration from configuration.yaml

### Issue 4: HACS not finding repository
- Ensure default branch is "main" (not "ha-market-prediction")
- Check repository is public
- Verify hacs.json file is in root directory

## Debugging

Enable debug logging:

```yaml
logger:
  default: warning
  logs:
    custom_components.market_prediction: debug
```

Check logs at: Settings → System → Logs

## Support

- **GitHub Issues**: https://github.com/BestMasterChief/ha-market-prediction/issues
- **GitHub Discussions**: https://github.com/BestMasterChief/ha-market-prediction/discussions
- **Home Assistant Community**: Search for "Market Prediction System"

## Success Verification

After installation, you should see:

1. **Integration**: Settings → Devices & Services → "Market Prediction System" ✅
2. **6 Sensors**: Developer Tools → States → search "market_prediction" ✅
3. **Progress Updates**: Watch `sensor.market_prediction_current_source` change ✅
4. **5-10 Minute Analysis**: Time the full sentiment analysis phase ✅

## Repository Checklist

Before publishing, ensure:

- [ ] Default branch is "main" (not "ha-market-prediction")
- [ ] All files uploaded to correct directories
- [ ] hacs.json in root directory
- [ ] manifest.json has correct version (2.2.0)
- [ ] README.md includes installation instructions
- [ ] GitHub release created with proper tag
- [ ] Repository is public
- [ ] All Python files have proper imports

Your repository is now ready for HACS distribution! 🎉