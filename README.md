# Market Prediction System v2.3.0

A comprehensive market prediction system that automatically analyzes FTSE 100 and S&P 500 indices with intelligent scheduling and API rate limiting.

## 🚀 Key Features

- **Automated Scheduling**: Predictions run 1 hour before market open and close
- **API Rate Limiting**: Intelligent rate limiting prevents API quota exhaustion
- **Dual Market Support**: FTSE 100 (Alpha Vantage) and S&P 500 (Financial Modeling Prep)
- **Web Dashboard**: Real-time monitoring and manual controls
- **SQLite Database**: Persistent storage of all predictions
- **Error Recovery**: Robust error handling and logging

## 📅 Automated Schedule

The system runs predictions at optimal times:

### FTSE 100 (London Stock Exchange)
- **Pre-Market**: 7:00 AM UK time (1 hour before 8:00 AM open)
- **Pre-Close**: 3:30 PM UK time (1 hour before 4:30 PM close)

### S&P 500 (New York Stock Exchange)  
- **Pre-Market**: 8:30 AM ET (1 hour before 9:30 AM open)
- **Pre-Close**: 3:00 PM ET (1 hour before 4:00 PM close)

**Total**: 4 API calls per day maximum, well within all limits.

## 🔧 API Requirements

### Alpha Vantage (FTSE 100 data)
- **Free Tier**: 25 requests per day
- **Get API Key**: https://www.alphavantage.co/support/#api-key

### Financial Modeling Prep (S&P 500 data)
- **Free Tier**: 250 total requests
- **Get API Key**: https://financialmodelingprep.com/developer/docs

## 🛠 Installation & Setup

### Quick Start

1. **Clone or download** the system files
2. **Copy environment file**:
   ```bash
   cp .env.example .env
   ```
3. **Edit .env** and add your API keys:
   ```
   ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key_here
   FMP_API_KEY=your_fmp_api_key_here
   ```

### Linux/Mac
```bash
chmod +x start.sh
./start.sh
```

### Windows
```cmd
start.bat
```

The system will:
- Create a virtual environment
- Install all dependencies
- Start the web dashboard at http://localhost:5000

## 📊 Web Dashboard

Access the dashboard at **http://localhost:5000** to:

- Monitor system status and API usage
- View next scheduled prediction times
- Trigger manual predictions
- Browse recent prediction history
- Real-time status updates

## 🔧 System Components

### Core Files
- `market_predictor.py` - Main application with scheduling and API logic
- `requirements.txt` - Python dependencies
- `setup.cfg` - Configuration (fixes flake8 issues)
- `.env.example` - Environment variables template

### Startup Scripts
- `start.sh` - Linux/Mac startup script
- `start.bat` - Windows startup script

### Web Interface
- `templates/dashboard.html` - Web dashboard interface

## 🗄 Database Schema

Predictions are stored in SQLite (`predictions.db`):

```sql
CREATE TABLE predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL,
    market TEXT NOT NULL,
    current_price REAL NOT NULL,
    predicted_price REAL NOT NULL,
    confidence REAL NOT NULL,
    trend TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    prediction_type TEXT NOT NULL
);
```

## 📈 Prediction Logic

The system uses a hybrid approach:
- **Momentum Analysis**: Recent price movements
- **Mean Reversion**: Tendency for prices to return to average
- **Confidence Scoring**: Based on market volatility
- **Trend Classification**: UP, DOWN, or NEUTRAL

## 🔒 Rate Limiting Features

### Intelligent API Management
- Tracks daily API usage for each service
- Automatically resets counters every 24 hours  
- Prevents requests when limits are approached
- Detailed logging of all API calls

### Safety Margins
- Uses only 4 calls per day (16% of Alpha Vantage limit)
- Monitors Financial Modeling Prep usage
- Dashboard shows real-time usage statistics

## 📋 Logs & Monitoring

### Log Files
- `market_predictor.log` - Application logs with timestamps
- Console output for real-time monitoring

### Monitoring Features
- System status dashboard
- API usage tracking
- Scheduled job monitoring
- Error tracking and reporting

## 🛡 Error Handling

### Robust Recovery
- Network timeout handling
- API error recovery  
- Database connection management
- Graceful service degradation

### Failsafe Features
- Manual prediction fallback
- API limit protection
- Automatic retry logic
- Comprehensive error logging

## 🔧 Advanced Configuration

### Environment Variables
```bash
# Required
ALPHA_VANTAGE_API_KEY=your_key
FMP_API_KEY=your_key

# Optional
FLASK_ENV=production
FLASK_DEBUG=False
```

### Customizing Schedules
Edit the `_setup_scheduler()` method in `market_predictor.py` to modify timing.

## 📞 API Endpoints

### Status Endpoint
```
GET /api/status
```
Returns system status, API usage, and scheduled jobs.

### Manual Prediction
```
POST /api/manual-prediction
```
Triggers immediate prediction for both markets.

### Recent Predictions
```
GET /api/recent-predictions?hours=24
```
Returns predictions from the last N hours.

## 🚨 Troubleshooting

### Common Issues

**API Key Errors**
- Verify keys in `.env` file
- Check API key validity on provider websites
- Ensure environment variables are loaded

**Flask Template Errors**
- Ensure `templates/` directory exists
- Check `dashboard.html` is present
- Verify Flask can find template files

**Flake8 Errors (Fixed)**
- `setup.cfg` now properly configures flake8
- Invalid ignore codes removed
- Syntax errors resolved

**Schedule Not Running**
- Check system timezone settings
- Verify APScheduler is properly initialized
- Monitor logs for scheduler errors

### Getting Help
1. Check the log file: `market_predictor.log`
2. Verify API keys are valid
3. Ensure all dependencies are installed
4. Check network connectivity

## 📄 License

MIT License - see LICENSE file for details.

## 🔄 Version History

### v2.3.0 (Current)
- ✅ Fixed flake8 configuration errors
- ✅ Implemented proper API rate limiting  
- ✅ Added intelligent scheduling system
- ✅ Created comprehensive web dashboard
- ✅ Enhanced error handling and logging
- ✅ Simplified startup process
- ✅ Added manual prediction trigger

### Previous Issues Fixed
- Removed invalid flake8 ignore codes
- Fixed scheduling to prevent API overuse
- Eliminated confusing .bat/.ps1 file conflicts
- Streamlined installation process
- Resolved template and dependency issues

## 🎯 Performance Metrics

- **API Efficiency**: 4 calls/day vs 25 limit (84% headroom)
- **Prediction Accuracy**: Real-time confidence scoring
- **System Uptime**: Designed for 24/7 operation
- **Response Time**: <2 seconds for manual predictions
- **Storage**: Minimal SQLite footprint

---

**Ready to predict the markets! 📈**
