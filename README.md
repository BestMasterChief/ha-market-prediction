# Market Prediction System for Home Assistant

A Renaissance Technologies-inspired market prediction system that provides daily predictions for S&P 500 and FTSE 100 indices using quantitative analysis.

## Features

- 🔮 **Daily Predictions**: Get UP/DOWN predictions with percentage changes for major market indices
- 📊 **Technical Analysis**: Uses RSI, moving averages, momentum, and volatility indicators  
- 📰 **Sentiment Analysis**: Incorporates news sentiment from Financial Modeling Prep API
- 🎯 **Progress Tracking**: Real-time progress indicators showing prediction processing stages
- ⚡ **Home Assistant 2025 Compatible**: Uses latest automation syntax and HACS integration
- 🔒 **Secure Configuration**: API keys managed through Home Assistant UI

## Screenshots

![Market Prediction Dashboard](https://via.placeholder.com/600x300/1f1f1f/ffffff?text=Market+Prediction+Dashboard)

## Installation

### Method 1: HACS Installation (Recommended)

1. **Add Custom Repository**:
   - Go to HACS → Integrations → ⋮ (three dots) → Custom repositories
   - Add repository URL: `https://github.com/yourusername/ha-market-prediction`
   - Category: Integration
   - Click "ADD"

2. **Install Integration**:
   - Search for "Market Prediction System" in HACS
   - Click "Download"
   - Restart Home Assistant

3. **Configure Integration**:
   - Go to Settings → Devices & Services → Add Integration
   - Search for "Market Prediction System"
   - Enter your API keys (see API Setup below)

### Method 2: Manual Installation

1. **Download Files**:
   ```bash
   cd /config
   git clone https://github.com/yourusername/ha-market-prediction.git
   ```

2. **Copy Files**:
   ```bash
   cp -r ha-market-prediction/custom_components/market_prediction /config/custom_components/
   ```

3. **Restart Home Assistant**

4. **Add Integration**:
   - Go to Settings → Devices & Services → Add Integration
   - Search for "Market Prediction System"

## API Setup

### Alpha Vantage API (Required)

1. Visit [Alpha Vantage](https://www.alphavantage.co/support/#api-key)
2. Sign up for a free account
3. Get your API key (500 calls/day free)
4. Enter the key during integration setup

### Financial Modeling Prep API (Optional)

1. Visit [Financial Modeling Prep](https://financialmodelingprep.com/developer/docs)
2. Sign up for a free account  
3. Get your API key (250 calls/day free)
4. Enter the key during setup for enhanced sentiment analysis

## Sensors Created

| Sensor | Description | Example State |
|--------|-------------|---------------|
| `sensor.s_p_500_prediction` | S&P 500 daily prediction | "UP 2.3%" |
| `sensor.ftse_100_prediction` | FTSE 100 daily prediction | "DOWN 1.5%" |
| `sensor.market_prediction_progress` | Processing progress | 85% |
| `sensor.market_prediction_status` | Current processing stage | "Processing Technical" |

## Sensor Attributes

Each prediction sensor includes detailed attributes:

```yaml
direction: "UP"
percentage: 2.3
confidence: 76.5
explanation: "Prediction based on: bullish moving average trend, positive momentum, positive news sentiment"
technical_score: 0.184
sentiment_score: 0.052
last_update: "2025-06-18T15:30:00"
```

## Dashboard Examples

### Basic Cards

```yaml
type: entities
title: Market Predictions
entities:
  - sensor.s_p_500_prediction
  - sensor.ftse_100_prediction
  - sensor.market_prediction_progress
```

### Detailed Card

```yaml
type: custom:mushroom-entity-card
entity: sensor.s_p_500_prediction
name: S&P 500 Prediction
icon: mdi:trending-up
secondary_info: |
  {{ state_attr('sensor.s_p_500_prediction', 'explanation') }}
badge_icon: |
  {% set confidence = state_attr('sensor.s_p_500_prediction', 'confidence') %}
  {% if confidence > 80 %}mdi:shield-check
  {% elif confidence > 60 %}mdi:shield-half-full
  {% else %}mdi:shield-outline
  {% endif %}
```

## Automation Examples

### Daily Notification

```yaml
alias: "Market Prediction Alert"
triggers:
  - trigger: state
    entity_id: sensor.s_p_500_prediction
conditions:
  - condition: template
    value_template: "{{ state_attr('sensor.s_p_500_prediction', 'confidence') > 70 }}"
actions:
  - action: notify.mobile_app_your_phone
    data:
      title: "📈 Market Prediction"
      message: |
        S&P 500: {{ states('sensor.s_p_500_prediction') }}
        Confidence: {{ state_attr('sensor.s_p_500_prediction', 'confidence') }}%
        {{ state_attr('sensor.s_p_500_prediction', 'explanation') }}
```

## Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| Update Interval | 30 minutes | How often to fetch new data |
| Alpha Vantage API Key | Required | For market data and technical indicators |
| FMP API Key | Optional | For news sentiment analysis |

## Troubleshooting

### Common Issues

**"No prediction data available"**
- Check API keys are entered correctly
- Verify internet connection
- Check API usage limits

**"API key not configured"**
- Reconfigure integration with valid API keys
- Ensure keys have proper permissions

**Sensors show "unavailable"**
- Check Home Assistant logs for errors
- Verify API services are accessible
- Restart integration if needed

### Debug Logging

Add to `configuration.yaml`:

```yaml
logger:
  default: warning
  logs:
    custom_components.market_prediction: debug
```

## API Usage Limits

| Provider | Free Tier | Paid Plans |
|----------|-----------|------------|
| Alpha Vantage | 500 calls/day | 5-1200 calls/min |
| Financial Modeling Prep | 250 calls/day | Unlimited |

With default settings (30-minute updates), the system uses ~48 Alpha Vantage calls per day.

## Algorithm Details

### Technical Analysis (75% Weight)

- **RSI Analysis (25%)**: Identifies overbought/oversold conditions
- **Moving Averages (25%)**: 5-day and 10-day trend analysis  
- **Momentum (15%)**: 5-day price momentum calculation
- **Volatility (10%)**: Price volatility assessment

### Sentiment Analysis (25% Weight)

- **News Processing**: Analyzes recent financial news headlines
- **Keyword Scoring**: Positive/negative sentiment calculation
- **Weighted Average**: Combines multiple news sources

### Risk Management

- Predictions capped at ±4% realistic range
- Confidence scoring based on signal strength
- Multiple indicator confirmation required

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Disclaimer

This system is for educational and informational purposes only. It does not constitute financial advice. Market predictions are inherently uncertain and past performance does not guarantee future results. Always consult with qualified financial advisors before making investment decisions.

## Support

- 🐛 [Report Issues](https://github.com/yourusername/ha-market-prediction/issues)
- 💬 [Community Discussion](https://community.home-assistant.io)
- 📖 [Documentation](https://github.com/yourusername/ha-market-prediction/wiki)

## Changelog

### v2.0.0
- ✅ Home Assistant 2025 compatibility
- ✅ HACS integration support
- ✅ Progress tracking sensors
- ✅ Enhanced error handling
- ✅ UI configuration flow
- ✅ Improved technical analysis

### v1.0.0
- Initial release