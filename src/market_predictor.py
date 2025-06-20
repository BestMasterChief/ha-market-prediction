"""
Market Prediction System v2.3.0
Fixed version with proper scheduling and API rate limiting
"""

import os
import time
import json
import logging
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import threading
from flask import Flask, render_template, jsonify, request
from dataclasses import dataclass
from typing import Dict, List, Optional
import sqlite3

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('market_predictor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class PredictionResult:
    """Data class for prediction results"""
    symbol: str
    current_price: float
    predicted_price: float
    confidence: float
    trend: str  # 'UP', 'DOWN', 'NEUTRAL'
    timestamp: datetime
    market: str  # 'FTSE' or 'SP500'

class APIRateLimiter:
    """Rate limiter for API calls"""

    def __init__(self):
        self.call_counts = {}
        self.reset_times = {}

    def can_make_call(self, api_name: str, limit: int, period_hours: int = 24) -> bool:
        """Check if API call is allowed"""
        now = datetime.now()

        # Reset counter if period has passed
        if api_name in self.reset_times:
            if now >= self.reset_times[api_name]:
                self.call_counts[api_name] = 0
                self.reset_times[api_name] = now + timedelta(hours=period_hours)
        else:
            self.call_counts[api_name] = 0
            self.reset_times[api_name] = now + timedelta(hours=period_hours)

        return self.call_counts.get(api_name, 0) < limit

    def record_call(self, api_name: str):
        """Record an API call"""
        self.call_counts[api_name] = self.call_counts.get(api_name, 0) + 1
        logger.info(f"API call recorded for {api_name}. Count: {self.call_counts[api_name]}")

class MarketDataProvider:
    """Handles market data retrieval with rate limiting"""

    def __init__(self, alpha_vantage_key: str, fmp_key: str):
        self.alpha_vantage_key = alpha_vantage_key
        self.fmp_key = fmp_key
        self.rate_limiter = APIRateLimiter()

    def get_ftse_data(self) -> Optional[Dict]:
        """Get FTSE 100 data from Alpha Vantage"""
        if not self.rate_limiter.can_make_call('alpha_vantage', 25):
            logger.warning("Alpha Vantage rate limit reached")
            return None

        try:
            url = f"https://www.alphavantage.co/query"
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': 'UKX',  # FTSE 100 symbol
                'apikey': self.alpha_vantage_key
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            self.rate_limiter.record_call('alpha_vantage')

            data = response.json()
            if 'Global Quote' in data:
                return data['Global Quote']
            else:
                logger.error(f"Unexpected Alpha Vantage response: {data}")
                return None

        except requests.RequestException as e:
            logger.error(f"Error fetching FTSE data: {e}")
            return None

    def get_sp500_data(self) -> Optional[Dict]:
        """Get S&P 500 data from Financial Modeling Prep"""
        if not self.rate_limiter.can_make_call('fmp', 250):
            logger.warning("Financial Modeling Prep rate limit reached")
            return None

        try:
            url = f"https://financialmodelingprep.com/api/v3/quote/SPY"
            params = {'apikey': self.fmp_key}

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            self.rate_limiter.record_call('fmp')

            data = response.json()
            if data and len(data) > 0:
                return data[0]
            else:
                logger.error(f"Unexpected FMP response: {data}")
                return None

        except requests.RequestException as e:
            logger.error(f"Error fetching S&P 500 data: {e}")
            return None

class PredictionEngine:
    """Simple prediction engine using technical analysis"""

    def __init__(self):
        self.historical_data = {}

    def predict_price(self, symbol: str, current_data: Dict, market: str) -> PredictionResult:
        """Generate price prediction"""
        try:
            if market == 'FTSE':
                current_price = float(current_data.get('05. price', 0))
                prev_close = float(current_data.get('08. previous close', 0))
                change_percent = float(current_data.get('10. change percent', '0%').replace('%', ''))
            else:  # SP500
                current_price = float(current_data.get('price', 0))
                prev_close = float(current_data.get('previousClose', 0))
                change_percent = float(current_data.get('changesPercentage', 0))

            # Simple prediction logic based on momentum and mean reversion
            momentum_factor = min(max(change_percent / 100, -0.05), 0.05)
            mean_reversion_factor = -0.3 * momentum_factor  # Partial mean reversion

            prediction_change = momentum_factor + mean_reversion_factor
            predicted_price = current_price * (1 + prediction_change)

            # Determine trend
            if prediction_change > 0.01:
                trend = 'UP'
            elif prediction_change < -0.01:
                trend = 'DOWN'
            else:
                trend = 'NEUTRAL'

            # Simple confidence calculation
            confidence = max(0.3, min(0.9, 0.7 - abs(change_percent) / 100))

            return PredictionResult(
                symbol=symbol,
                current_price=current_price,
                predicted_price=predicted_price,
                confidence=confidence,
                trend=trend,
                timestamp=datetime.now(),
                market=market
            )

        except (KeyError, ValueError, TypeError) as e:
            logger.error(f"Error creating prediction for {symbol}: {e}")
            return None

class DatabaseManager:
    """Handles SQLite database operations"""

    def __init__(self, db_path: str = 'predictions.db'):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(\
            """CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                market TEXT NOT NULL,
                current_price REAL NOT NULL,
                predicted_price REAL NOT NULL,
                confidence REAL NOT NULL,
                trend TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                prediction_type TEXT NOT NULL
            )""")

        conn.commit()
        conn.close()

    def save_prediction(self, prediction: PredictionResult, prediction_type: str):
        """Save prediction to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(\
            """INSERT INTO predictions 
            (symbol, market, current_price, predicted_price, confidence, trend, timestamp, prediction_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", (
            prediction.symbol,
            prediction.market,
            prediction.current_price,
            prediction.predicted_price,
            prediction.confidence,
            prediction.trend,
            prediction.timestamp.isoformat(),
            prediction_type
        ))

        conn.commit()
        conn.close()

    def get_recent_predictions(self, hours: int = 24) -> List[Dict]:
        """Get recent predictions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        since_time = (datetime.now() - timedelta(hours=hours)).isoformat()

        cursor.execute(\
            """SELECT * FROM predictions 
            WHERE timestamp > ? 
            ORDER BY timestamp DESC""", (since_time,))

        columns = [description[0] for description in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]

        conn.close()
        return results

class MarketPredictor:
    """Main market prediction system"""

    def __init__(self, alpha_vantage_key: str, fmp_key: str):
        self.data_provider = MarketDataProvider(alpha_vantage_key, fmp_key)
        self.prediction_engine = PredictionEngine()
        self.db_manager = DatabaseManager()
        self.scheduler = BackgroundScheduler()
        self.is_running = False

        # Market timezones
        self.uk_tz = pytz.timezone('Europe/London')
        self.us_tz = pytz.timezone('US/Eastern')

        self._setup_scheduler()

    def _setup_scheduler(self):
        """Setup scheduled tasks"""
        # FTSE pre-market check (7:00 AM UK time - 1 hour before 8:00 AM open)
        self.scheduler.add_job(
            func=self._scheduled_ftse_check,
            trigger=CronTrigger(hour=7, minute=0, timezone=self.uk_tz),
            id='ftse_premarket',
            max_instances=1,
            coalesce=True
        )

        # FTSE pre-close check (3:30 PM UK time - 1 hour before 4:30 PM close)
        self.scheduler.add_job(
            func=self._scheduled_ftse_check,
            trigger=CronTrigger(hour=15, minute=30, timezone=self.uk_tz),
            id='ftse_preclose',
            max_instances=1,
            coalesce=True
        )

        # S&P 500 pre-market check (8:30 AM ET - 1 hour before 9:30 AM open)
        self.scheduler.add_job(
            func=self._scheduled_sp500_check,
            trigger=CronTrigger(hour=8, minute=30, timezone=self.us_tz),
            id='sp500_premarket',
            max_instances=1,
            coalesce=True
        )

        # S&P 500 pre-close check (3:00 PM ET - 1 hour before 4:00 PM close)
        self.scheduler.add_job(
            func=self._scheduled_sp500_check,
            trigger=CronTrigger(hour=15, minute=0, timezone=self.us_tz),
            id='sp500_preclose',
            max_instances=1,
            coalesce=True
        )

    def _scheduled_ftse_check(self):
        """Scheduled FTSE check"""
        logger.info("Running scheduled FTSE check")
        prediction = self.predict_ftse()
        if prediction:
            current_time = datetime.now(self.uk_tz)
            if current_time.hour == 7:
                self.db_manager.save_prediction(prediction, 'pre_market')
            else:
                self.db_manager.save_prediction(prediction, 'pre_close')

    def _scheduled_sp500_check(self):
        """Scheduled S&P 500 check"""
        logger.info("Running scheduled S&P 500 check")
        prediction = self.predict_sp500()
        if prediction:
            current_time = datetime.now(self.us_tz)
            if current_time.hour == 8:
                self.db_manager.save_prediction(prediction, 'pre_market')
            else:
                self.db_manager.save_prediction(prediction, 'pre_close')

    def predict_ftse(self) -> Optional[PredictionResult]:
        """Predict FTSE 100"""
        data = self.data_provider.get_ftse_data()
        if data:
            return self.prediction_engine.predict_price('FTSE100', data, 'FTSE')
        return None

    def predict_sp500(self) -> Optional[PredictionResult]:
        """Predict S&P 500"""
        data = self.data_provider.get_sp500_data()
        if data:
            return self.prediction_engine.predict_price('SPY', data, 'SP500')
        return None

    def manual_prediction(self) -> Dict:
        """Manual prediction for both markets"""
        results = {}

        ftse_prediction = self.predict_ftse()
        if ftse_prediction:
            results['FTSE'] = {
                'symbol': ftse_prediction.symbol,
                'current_price': ftse_prediction.current_price,
                'predicted_price': ftse_prediction.predicted_price,
                'confidence': ftse_prediction.confidence,
                'trend': ftse_prediction.trend,
                'timestamp': ftse_prediction.timestamp.isoformat()
            }
            self.db_manager.save_prediction(ftse_prediction, 'manual')

        sp500_prediction = self.predict_sp500()
        if sp500_prediction:
            results['SP500'] = {
                'symbol': sp500_prediction.symbol,
                'current_price': sp500_prediction.current_price,
                'predicted_price': sp500_prediction.predicted_price,
                'confidence': sp500_prediction.confidence,
                'trend': sp500_prediction.trend,
                'timestamp': sp500_prediction.timestamp.isoformat()
            }
            self.db_manager.save_prediction(sp500_prediction, 'manual')

        return results

    def start(self):
        """Start the prediction system"""
        if not self.is_running:
            self.scheduler.start()
            self.is_running = True
            logger.info("Market Prediction System started")

    def stop(self):
        """Stop the prediction system"""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("Market Prediction System stopped")

    def get_status(self) -> Dict:
        """Get system status"""
        jobs = []
        if self.scheduler.running:
            for job in self.scheduler.get_jobs():
                next_run = job.next_run_time
                jobs.append({
                    'id': job.id,
                    'next_run': next_run.isoformat() if next_run else None
                })

        return {
            'running': self.is_running,
            'scheduled_jobs': jobs,
            'api_calls_today': {
                'alpha_vantage': self.data_provider.rate_limiter.call_counts.get('alpha_vantage', 0),
                'fmp': self.data_provider.rate_limiter.call_counts.get('fmp', 0)
            }
        }

# Flask Web Interface
app = Flask(__name__)
predictor = None

@app.route('/')
def index():
    """Main dashboard"""
    return render_template('dashboard.html')

@app.route('/api/status')
def api_status():
    """Get system status"""
    if predictor:
        return jsonify(predictor.get_status())
    return jsonify({'error': 'System not initialized'}), 503

@app.route('/api/manual-prediction', methods=['POST'])
def api_manual_prediction():
    """Trigger manual prediction"""
    if predictor:
        results = predictor.manual_prediction()
        return jsonify(results)
    return jsonify({'error': 'System not initialized'}), 503

@app.route('/api/recent-predictions')
def api_recent_predictions():
    """Get recent predictions"""
    if predictor:
        hours = request.args.get('hours', 24, type=int)
        predictions = predictor.db_manager.get_recent_predictions(hours)
        return jsonify(predictions)
    return jsonify({'error': 'System not initialized'}), 503

def main():
    """Main function"""
    global predictor

    # Get API keys from environment
    alpha_vantage_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    fmp_key = os.getenv('FMP_API_KEY')

    if not alpha_vantage_key or not fmp_key:
        logger.error("API keys not found in environment variables")
        logger.info("Please set ALPHA_VANTAGE_API_KEY and FMP_API_KEY environment variables")
        return

    # Initialize predictor
    predictor = MarketPredictor(alpha_vantage_key, fmp_key)
    predictor.start()

    try:
        # Start Flask app
        app.run(host='0.0.0.0', port=5000, debug=False)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        if predictor:
            predictor.stop()

if __name__ == '__main__':
    main()
