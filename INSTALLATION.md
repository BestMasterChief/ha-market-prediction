# Installation Guide - Market Prediction System v2.2.2

## Quick Start

This guide covers two installation methods for the Market Prediction System integration.

## Method 1: HACS Installation (Recommended)

### Prerequisites
- Home Assistant 2024.1.0 or later
- HACS (Home Assistant Community Store) installed

### Step-by-Step Installation

1. **Add Custom Repository**
   - Open HACS in Home Assistant
   - Go to "Integrations" tab
   - Click the 3-dot menu (⋮) in the top right
   - Select "Custom repositories"
   - Add repository URL: `https://github.com/BestMasterChief/ha-market-prediction`
   - Select "Integration" as category
   - Click "Add"

2. **Install Integration**
   - Search for "Market Prediction System" in HACS
   - Click "Install"
   - Restart Home Assistant

3. **Configure Integration**
   - Go to Settings → Devices & Services
   - Click "Add Integration"
   - Search for "Market Prediction System"
   - Click to add
   - Enter your API keys when prompted

## Method 2: Manual Installation

### Step-by-Step Installation

1. **Download Files**
   - Download the latest release from GitHub
   - Extract the files

2. **Copy Files**
   - Copy the entire `custom_components/market_prediction` folder
   - Paste into your Home Assistant `config/custom_components/` directory
   - Final structure should be: `config/custom_components/market_prediction/`

3. **Restart Home Assistant**
   - Restart Home Assistant completely

4. **Add Integration**
   - Go to Settings → Devices & Services
   - Click "Add Integration"
   - Search for "Market Prediction System"
   - Follow the configuration steps

## API Key Setup

### Alpha Vantage (Required)
1. Visit: https://www.alphavantage.co/support/#api-key
2. Sign up for a free account
3. Copy your API key
4. Enter during integration setup

### Financial Modeling Prep (Optional)
1. Visit: https://financialmodelingprep.com/developer/docs
2. Sign up for a free account
3. Copy your API key
4. Enter during integration setup (or leave blank)

## Verification

After installation, verify these sensors appear:
- `sensor.market_prediction_s_p_500`
- `sensor.market_prediction_ftse_100`
- `sensor.market_prediction_progress`
- `sensor.market_prediction_status`
- `sensor.market_prediction_current_source`
- `sensor.market_prediction_processing_time`

## Troubleshooting

### Integration Not Found
- Ensure you've restarted Home Assistant after installation
- Check that files are in the correct directory structure

### API Key Errors
- Verify API keys are correct and active
- Check API usage limits haven't been exceeded

### Sensors Unavailable
- Wait for the first analysis to complete (5-10 minutes)
- Check Home Assistant logs for error messages
- Verify internet connectivity

## Support

For issues or questions:
- GitHub Issues: https://github.com/BestMasterChief/ha-market-prediction/issues
- Home Assistant Community: https://community.home-assistant.io/