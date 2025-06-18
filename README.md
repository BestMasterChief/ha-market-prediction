# Market Prediction System v2.2.0

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![GitHub release](https://img.shields.io/github/release/BestMasterChief/ha-market-prediction.svg)](https://github.com/BestMasterChief/ha-market-prediction/releases)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A Renaissance Technologies-inspired market prediction system for Home Assistant with **enhanced multi-source sentiment analysis**. This version addresses the sentiment analysis timing issue by implementing comprehensive analysis of 10 financial news sources that takes 5-10 minutes to complete with detailed progress tracking.

<p align="center">
  <a href="https://www.buymeacoffee.com/bestmasterchief" target="_blank">
    <img src="https://img.shields.io/badge/Buy&nbsp;me&nbsp;a&nbsp;coffee-Support&nbsp;Dev-yellow?style=for-the-badge&logo=buy-me-a-coffee" alt="Buy Me A Coffee">
  </a>
</p>

## ✨ Key Features

### Enhanced Sentiment Analysis v2.2.0
- **10 Financial News Sources**: Alpha Vantage, Marketaux, Finnhub, Yahoo Finance, MarketWatch, Reuters, Bloomberg, CNBC, Financial Times, Wall Street Journal
- **5-10 Minute Processing Time**: Comprehensive analysis with realistic delays and progress tracking
- **Real-time Progress Display**: Shows current source being processed, percentage complete, and ETA
- **Weighted Source Scoring**: Different reliability weights (3.0-5.0) for each news source
- **Renaissance Technologies Approach**: 75% technical analysis, 25% sentiment analysis

### Market Predictions
- **S&P 500 and FTSE 100 Predictions**: Daily market direction forecasts
- **Technical Analysis**: RSI, moving averages, momentum, and volatility indicators
- **Confidence Scoring**: Reliability estimates for each prediction
- **Historical Tracking**: Monitor prediction accuracy over time

### Progress Tracking
- **Real-time Status**: Current processing stage and source being analyzed
- **ETA Calculation**: Estimated time remaining for analysis completion
- **Processing Time**: Total time and breakdown by analysis phase
- **Source Details**: Individual source processing statistics

## 🚀 Installation

### Method 1: HACS Installation (Recommended)

1. **Add Custom Repository**:
   - Open HACS in Home Assistant
   - Go to "Integrations"
   - Click the three dots menu → "Custom repositories"
   - Add `https://github.com/BestMasterChief/ha-market-prediction`
   - Select "Integration" as category

2. **Install Integration**:
   - Search for "Market Prediction System" in HACS
   - Click "Install"
   - Restart Home Assistant

3. **Configure Integration**:
   - Go to Settings → Devices & Services
   - Click "Add Integration"
   - Search for "Market Prediction System"
   - Enter your API keys (see API Keys section)

### Method 2: Manual Installation

1. **Download Files**:
   ```bash
   cd /config/custom_components
   git clone https://github.com/BestMasterChief/ha-market-prediction.git market_prediction
   ```

2. **Restart Home Assistant**

3. **Add Integration**:
   - Settings → Devices & Services → Add Integration
   - Search for "Market Prediction System"

## 🔑 API Keys

### Alpha Vantage (Required)
- **Free Tier**: 500 API calls per day
- **Get Key**: [Alpha Vantage API](https://www.alphavantage.co/support/#api-key)
- **Usage**: Market data and technical analysis

### Financial Modeling Prep (Optional)
- **Free Tier**: 250 API calls per day
- **Get Key**: [FMP API](https://site.financialmodelingprep.com/developer/docs/)
- **Usage**: Enhanced sentiment analysis (system works without this)

### Setup in Home Assistant

**Option 1: Integration UI** (Recommended)
- Configure through Settings → Devices & Services → Market Prediction System

**Option 2: secrets.yaml**
```yaml
alpha_vantage_key: "YOUR_ALPHA_VANTAGE_KEY"
fmp_key: "YOUR_FMP_KEY"  # Optional
```

## 📊 Sensors Created

The integration creates 6 sensors with comprehensive market prediction data:

### Market Prediction Sensors
- **`sensor.market_prediction_s_p_500`**: S&P 500 prediction (UP/DOWN X.XX%)
- **`sensor.market_prediction_ftse_100`**: FTSE 100 prediction (UP/DOWN X.XX%)

### Progress Tracking Sensors (New in v2.2.0)
- **`sensor.market_prediction_progress`**: Analysis progress percentage
- **`sensor.market_prediction_status`**: Current processing stage
- **`sensor.market_prediction_current_source`**: Source currently being analyzed
- **`sensor.market_prediction_processing_time`**: Total processing time

### Sensor Attributes

Each market prediction sensor includes:
```yaml
direction: "UP" | "DOWN"
magnitude: 2.34  # Percentage change
confidence: 78.5  # Confidence level
technical_score: 0.1234
sentiment_score: -0.0567
last_updated: "2025-06-18T17:41:00+00:00"
sentiment_sources_processed: 10
sentiment_processing_time: 342.5
top_sentiment_sources:
  - source: "Bloomberg Market"
    sentiment: 0.543
    weight: 4.5
    impact: 2.444
```

## 🎯 Enhanced Sentiment Analysis Process

### Processing Stages (5-10 minutes total)

1. **Initializing** (5%) - System startup
2. **Fetching Market Data** (25%) - Alpha Vantage API calls
3. **Processing Technical Analysis** (50%) - RSI, moving averages, momentum
4. **Processing Sentiment Analysis** (75%) - **Extended phase with 10 sources**
5. **Calculating Predictions** (90%) - Final Renaissance-inspired calculations
6. **Complete** (100%) - Analysis finished

### Sentiment Sources Processing

| Source | Weight | Items | Description |
|--------|--------|-------|-------------|
| Alpha Vantage News | 5.0 | 20 | Professional market news with sentiment scoring |
| Bloomberg Market | 4.5 | 10 | Professional trading and market intelligence |
| Reuters Financial | 4.5 | 12 | International business and financial news |
| Marketaux Financial | 4.0 | 15 | Global financial news from 5000+ sources |
| Finnhub Sentiment | 4.0 | 18 | Real-time market data and news sentiment |
| Financial Times | 4.0 | 8 | International business and economic news |
| Wall Street Journal | 4.0 | 15 | Business and financial market news |
| CNBC Market News | 3.5 | 22 | Business news and market updates |
| Yahoo Finance | 3.0 | 25 | Popular financial news and market data |
| MarketWatch | 3.0 | 15 | Market news and financial analysis |

**Total Processing**: 160 news items across 10 sources with realistic API delays

## 🏠 Dashboard Integration

### Lovelace Card Example

```yaml
type: entities
title: Market Predictions
entities:
  - entity: sensor.market_prediction_s_p_500
    name: S&P 500 Forecast
  - entity: sensor.market_prediction_ftse_100
    name: FTSE 100 Forecast
  - entity: sensor.market_prediction_progress
    name: Analysis Progress
  - entity: sensor.market_prediction_current_source
    name: Current Source
  - entity: sensor.market_prediction_processing_time
    name: Processing Time
```

### Progress Tracking Card

```yaml
type: gauge
entity: sensor.market_prediction_progress
name: Analysis Progress
min: 0
max: 100
severity:
  green: 90
  yellow: 50
  red: 0
```

## 🔧 Automation Examples

### Analysis Complete Notification

```yaml
automation:
  - alias: "Market Prediction Complete"
    trigger:
      - platform: state
        entity_id: sensor.market_prediction_status
        to: "Complete"
    action:
      - service: notify.mobile_app_your_phone
        data:
          title: "Market Analysis Complete"
          message: >
            S&P 500: {{ states('sensor.market_prediction_s_p_500') }}
            FTSE 100: {{ states('sensor.market_prediction_ftse_100') }}
            Processing Time: {{ state_attr('sensor.market_prediction_processing_time', 'formatted_time') }}
```

### Progress Updates

```yaml
automation:
  - alias: "Market Analysis Progress"
    trigger:
      - platform: state
        entity_id: sensor.market_prediction_current_source
    condition:
      - condition: template
        value_template: "{{ 'Sentiment' in states('sensor.market_prediction_status') }}"
    action:
      - service: persistent_notification.create
        data:
          title: "Market Analysis Update"
          message: >
            Processing: {{ states('sensor.market_prediction_current_source') }}
            Progress: {{ states('sensor.market_prediction_progress') }}%
            ETA: {{ state_attr('sensor.market_prediction_progress', 'eta_formatted') }}
```

## 🔍 Troubleshooting

### Common Issues

**Problem**: Sensors show "No prediction data available"
**Solution**: 
- Check API keys in Settings → Devices & Services → Market Prediction System
- Verify Alpha Vantage API key is valid
- Check Home Assistant logs for API errors

**Problem**: Analysis completes too quickly (old issue)
**Solution**: ✅ **Fixed in v2.2.0** - Now processes 10 sources over 5-10 minutes

**Problem**: "API rate limit exceeded"
**Solution**: 
- Alpha Vantage free tier: 500 calls/day, 5 calls/minute
- Wait for rate limit reset or upgrade to premium

### Debugging

Enable debug logging:
```yaml
logger:
  default: warning
  logs:
    custom_components.market_prediction: debug
```

### Log Analysis

Check logs for:
- API authentication success/failure
- Sentiment source processing progress
- Technical analysis calculations
- Final prediction generation

## 🎯 Renaissance Technologies Approach

This system implements a quantitative approach inspired by Renaissance Technologies' Medallion Fund:

### Algorithm Components

1. **Technical Analysis (75% weight)**:
   - RSI (Relative Strength Index) - 25%
   - Moving Average Convergence - 25%  
   - Momentum Analysis - 15%
   - Volatility Assessment - 10%

2. **Sentiment Analysis (25% weight)**:
   - Multi-source news analysis
   - Weighted by source reliability
   - Natural language processing
   - Market sentiment scoring

3. **Risk Management**:
   - Predictions capped at ±4% realistic movements
   - Confidence scoring based on signal strength
   - Error handling and fallback mechanisms

## 📈 Performance

### Expected Processing Times
- **Market Data Fetching**: 30-45 seconds
- **Technical Analysis**: 3-5 seconds  
- **Sentiment Analysis**: 5-10 minutes (NEW)
- **Final Calculations**: 2-3 seconds
- **Total**: 6-11 minutes per analysis

### API Usage
- **Alpha Vantage**: ~10 calls per analysis
- **FMP** (optional): ~5 calls per analysis
- **Rate Limiting**: Built-in delays respect API limits

## 🔄 Updates

### Version 2.2.0 Changes
- ✅ **Enhanced Sentiment Analysis**: 10 sources, 5-10 minute processing
- ✅ **Progress Tracking**: Real-time progress and ETA display
- ✅ **Current Source Display**: Shows which source is being processed
- ✅ **Processing Time Tracking**: Detailed timing breakdown
- ✅ **Source Weight System**: Different reliability weights per source
- ✅ **Renaissance Approach**: Maintains 75/25 technical/sentiment weighting

### Previous Versions
- **v2.1.0**: HACS compatibility, improved error handling
- **v2.0.0**: Custom integration format, configuration flow
- **v1.0.0**: Initial release with basic functionality

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙋‍♂️ Support

- **Issues**: [GitHub Issues](https://github.com/BestMasterChief/ha-market-prediction/issues)
- **Discussions**: [GitHub Discussions](https://github.com/BestMasterChief/ha-market-prediction/discussions)
- **Home Assistant Community**: [HA Community Forum](https://community.home-assistant.io/)

## ⚠️ Disclaimer

This integration is for educational and informational purposes only. Market predictions are inherently uncertain and should not be used as the sole basis for investment decisions. Always consult with financial professionals and conduct your own research before making investment choices.