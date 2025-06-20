# Market Prediction System for Home Assistant

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)
[![hacs][hacsbadge]][hacs]

A Renaissance Technologies-inspired market prediction integration for Home Assistant that provides daily forecasts for S&P 500 and FTSE 100 indices using sophisticated quantitative analysis.

<p align="center">
  <a href="https://www.buymeacoffee.com/bestmasterchief" target="_blank">
    <img src="https://img.shields.io/badge/Buy&nbsp;me&nbsp;a&nbsp;coffee-Support&nbsp;Dev-yellow?style=for-the-badge&logo=buy-me-a-coffee" alt="Buy Me A Coffee">
  </a>
</p>

## Features

- **Multi-Factor Analysis**: Combines technical analysis (75% weight) with sentiment analysis (25% weight)
- **Real-Time Progress Tracking**: Visual progress indicators showing analysis stages
- **Renaissance Technologies Methodology**: Inspired by the legendary Medallion Fund's approach
- **Multiple Data Sources**: Processes 10 different financial news sources for sentiment analysis
- **Professional APIs**: Uses Alpha Vantage and Financial Modeling Prep for market data
- **HACS Compatible**: Easy installation through Home Assistant Community Store

## Sensors Created

The integration creates 6 sensor entities:

1. **S&P 500 Prediction** - Daily market direction forecast (UP/DOWN X.X%)
2. **FTSE 100 Prediction** - Daily market direction forecast (UP/DOWN X.X%)
3. **Analysis Progress** - Real-time progress percentage (0-100%)
4. **Analysis Status** - Current processing stage
5. **Current Source** - Data source being processed
6. **Processing Time** - Time taken for analysis

## Installation

### HACS (Recommended)

1. Open HACS in Home Assistant
2. Go to "Integrations"
3. Click the 3-dot menu and select "Custom repositories"
4. Add repository URL: `https://github.com/BestMasterChief/ha-market-prediction`
5. Select "Integration" as category
6. Install "Market Prediction System"
7. Restart Home Assistant
8. Go to Settings → Devices & Services
9. Click "Add Integration" and search for "Market Prediction System"
10. Enter your API keys when prompted

### Manual Installation

1. Download the latest release
2. Copy `custom_components/market_prediction` to your Home Assistant config directory
3. Restart Home Assistant
4. Add the integration via Settings → Devices & Services

## API Keys Required

### Alpha Vantage (Required)
- Free tier: 500 API calls per day
- Sign up at: https://www.alphavantage.co/support/#api-key
- Used for market data and technical analysis

### Financial Modeling Prep (Optional)
- Free tier: 250 API calls per day  
- Sign up at: https://financialmodelingprep.com/developer/docs
- Enhances sentiment analysis capabilities
- System works without this key

## Algorithm Details

### Technical Analysis (75% Weight)
- **RSI Analysis (25%)**: 14-day Relative Strength Index for overbought/oversold conditions
- **Moving Average Analysis (25%)**: 5-day and 10-day trend evaluation
- **Momentum Analysis (15%)**: 5-day price momentum calculation
- **Volatility Assessment (10%)**: Price volatility impact on confidence

### Sentiment Analysis (25% Weight)
- **Multi-Source Processing**: Analyzes news from 10 different financial sources
- **Weighted Scoring**: Each source has reliability weight (3.0-5.0)
- **Natural Language Processing**: Keyword-based sentiment scoring
- **Real-Time Progress**: Shows which source is currently being processed

## Dashboard Example

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
```

## Configuration

The integration is configured through the Home Assistant UI. No YAML configuration required.

### Options Available
- Update interval (1-24 hours)
- Enable/disable notifications
- API timeout settings

## Troubleshooting

### Common Issues

**"API key not configured"**
- Verify API keys are entered correctly
- Check API key quotas haven't been exceeded

**"No prediction data available"**
- Ensure internet connectivity
- Verify API services are operational
- Check Home Assistant logs for detailed errors

**Sensors show "unavailable"**
- Restart the integration via Settings → Devices & Services
- Check API key validity
- Monitor for rate limiting

### Debug Logging

Enable debug logging in `configuration.yaml`:

```yaml
logger:
  default: warning
  logs:
    custom_components.market_prediction: debug
```

## Disclaimer

This integration provides market predictions for informational purposes only. All predictions involve uncertainty and should not be used as the sole basis for investment decisions. Past performance does not guarantee future results.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- [GitHub Issues](https://github.com/BestMasterChief/ha-market-prediction/issues)
- [Home Assistant Community Forum](https://community.home-assistant.io/)

---

**Inspired by Renaissance Technologies' quantitative approach to market analysis**

[commits-shield]: https://img.shields.io/github/commit-activity/y/BestMasterChief/ha-market-prediction.svg?style=for-the-badge
[commits]: https://github.com/BestMasterChief/ha-market-prediction/commits/main
[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[license-shield]: https://img.shields.io/github/license/BestMasterChief/ha-market-prediction.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/BestMasterChief/ha-market-prediction.svg?style=for-the-badge
[releases]: https://github.com/BestMasterChief/ha-market-prediction/releases