# Market Prediction System for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![GitHub release](https://img.shields.io/github/release/BestMasterChief/ha-market-prediction.svg)](https://github.com/BestMasterChief/ha-market-prediction/releases)
[![Validate](https://github.com/BestMasterChief/ha-market-prediction/workflows/Validate/badge.svg)](https://github.com/BestMasterChief/ha-market-prediction/actions)

A Renaissance Technologies-inspired market prediction system for Home Assistant that provides intelligent forecasts for S&P 500 and FTSE 100 indices.

## ✨ Features

- 🎯 **Renaissance Technologies-Inspired Algorithm**: Multi-factor quantitative analysis combining technical indicators and sentiment analysis
- 📊 **Real-time Progress Tracking**: See exactly what stage the analysis is in with ETA estimates
- 🔄 **Smart API Management**: Automatic rate limiting and daily quota tracking
- 🚨 **Intelligent Error Handling**: Clear error messages for API issues with automatic recovery
- 📱 **HACS Compatible**: Easy installation and updates through HACS
- 🌐 **Home Assistant 2025 Ready**: Full compatibility with the latest HA versions

## 📈 Sensors Created

| Sensor | Description | Example State |
|--------|-------------|---------------|
| `sensor.s_p_500_prediction` | S&P 500 market direction prediction | `UP 2.3%` |
| `sensor.ftse_100_prediction` | FTSE 100 market direction prediction | `DOWN 1.5%` |
| `sensor.market_prediction_progress` | Real-time analysis progress | `75%` |
| `sensor.market_prediction_status` | Current processing stage | `Processing Technical (75%)` |

## 🔧 Prerequisites

- Home Assistant 2024.1.0 or newer
- Alpha Vantage API key (free - 500 calls/day)
- Financial Modeling Prep API key (optional - 250 total calls)

### Getting API Keys

1. **Alpha Vantage** (Required):
   - Visit: https://www.alphavantage.co/support/#api-key
   - Sign up for free account
   - Get your API key (500 requests/day)

2. **Financial Modeling Prep** (Optional):
   - Visit: https://financialmodelingprep.com/developer/docs
   - Sign up for free account
   - Get your API key (250 total requests)

## 🚀 Installation

### Method 1: HACS Installation (Recommended)

1. **Add Custom Repository**:
   - Open HACS in Home Assistant
   - Click the three dots (⋮) in the top right
   - Select "Custom repositories"
   - Add repository URL: `https://github.com/BestMasterChief/ha-market-prediction`
   - Select category: "Integration"
   - Click "ADD"

2. **Install Integration**:
   - Search for "Market Prediction System" in HACS
   - Click "Download"
   - Restart Home Assistant

3. **Configure Integration**:
   - Go to Settings → Devices & Services
   - Click "Add Integration"
   - Search for "Market Prediction System"
   - Enter your API keys
   - Click "Submit"

### Method 2: Manual Installation

1. **Download Files**:
   - Download the latest release from GitHub
   - Extract to `/config/custom_components/market_prediction/`

2. **Restart Home Assistant**

3. **Add Integration**:
   - Go to Settings → Devices & Services
   - Click "Add Integration"
   - Search for "Market Prediction System"

## 📊 Algorithm Details

### Technical Analysis (75% Weight)
- **RSI Analysis (25%)**: 14-day Relative Strength Index for overbought/oversold conditions
- **Momentum Analysis (25%)**: Short-term price momentum evaluation
- **Moving Average Analysis (15%)**: 5-day and 10-day trend analysis
- **Volatility Assessment (10%)**: Price volatility impact on confidence

### Sentiment Analysis (25% Weight)
- **News Processing**: Analyzes recent financial news headlines
- **Keyword Scoring**: Positive/negative sentiment calculation
- **Weighted Integration**: Combines technical and sentiment signals

### Progress Tracking
1. **Initializing** (5%) - Setting up analysis
2. **Fetching Market Data** (25%) - Retrieving price data from Alpha Vantage
3. **Processing Technical Analysis** (50%) - Computing technical indicators
4. **Processing Sentiment Analysis** (75%) - Analyzing news sentiment (if FMP key provided)
5. **Calculating Predictions** (90%) - Generating final predictions
6. **Complete** (100%) - Analysis finished

## 🔍 Troubleshooting

### Common Issues

**Sensors show "Unavailable"**:
- Check API keys in integration configuration
- Verify network connectivity
- Check Home Assistant logs for specific errors

**Progress jumps to 100% immediately**:
- Usually indicates API authentication failure
- Check that API keys are valid and have remaining quota

**"Cannot connect" error**:
- Verify internet connectivity
- Check if APIs are experiencing downtime
- Review firewall settings

### API Limits

- **Alpha Vantage**: 500 requests per day (resets at midnight UTC)
- **Financial Modeling Prep**: 250 total requests (lifetime limit for free accounts)

### Log Analysis

Enable debug logging to see detailed information:

```yaml
logger:
  default: warning
  logs:
    custom_components.market_prediction: debug
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This integration is for educational and informational purposes only. Market predictions are inherently uncertain and should not be used as the sole basis for investment decisions. Past performance does not guarantee future results.

## 🙏 Acknowledgments

- Inspired by Renaissance Technologies' quantitative approach
- Thanks to the Home Assistant community
- API providers: Alpha Vantage and Financial Modeling Prep

---

**Star ⭐ this repository if you find it useful!**