"""
Market Prediction Pyscript Module

This is an optional pyscript module that can work alongside the main integration
for additional calculations or manual triggering of predictions.
"""

import aiohttp
import asyncio
import logging
from datetime import datetime, timedelta

# Configuration - Update these with your API keys
ALPHA_VANTAGE_API_KEY = pyscript.config.get("alpha_vantage_api_key", "")
FMP_API_KEY = pyscript.config.get("fmp_api_key", "")

# API endpoints
ALPHA_VANTAGE_BASE = "https://www.alphavantage.co/query"
FMP_BASE = "https://financialmodelingprep.com/api"

log = logging.getLogger(__name__)


@service
async def update_market_predictions():
    """Service to manually update market predictions."""
    log.info("Starting manual market prediction update")
    
    try:
        # Update progress sensor
        state.set("sensor.market_prediction_progress", 10)
        state.set("sensor.market_prediction_status", "Fetching Data")
        
        # Fetch market data
        market_data = await fetch_market_data()
        
        state.set("sensor.market_prediction_progress", 50)
        state.set("sensor.market_prediction_status", "Processing Technical")
        
        # Process technical analysis
        predictions = await calculate_predictions(market_data)
        
        state.set("sensor.market_prediction_progress", 90)
        state.set("sensor.market_prediction_status", "Updating Sensors")
        
        # Update sensors
        await update_prediction_sensors(predictions)
        
        state.set("sensor.market_prediction_progress", 100)
        state.set("sensor.market_prediction_status", "Complete")
        
        log.info("Market prediction update completed successfully")
        
    except Exception as e:
        log.error(f"Error updating market predictions: {e}")
        state.set("sensor.market_prediction_status", "Error")
        state.set("sensor.market_prediction_progress", 0)


@pyscript_executor
async def fetch_market_data():
    """Fetch market data from Alpha Vantage."""
    if not ALPHA_VANTAGE_API_KEY:
        raise ValueError("Alpha Vantage API key not configured")
    
    symbols = ["SPY", "VTI"]
    market_data = {}
    
    async with aiohttp.ClientSession() as session:
        for symbol in symbols:
            try:
                # Fetch daily prices
                daily_url = f"{ALPHA_VANTAGE_BASE}?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={ALPHA_VANTAGE_API_KEY}"
                
                async with session.get(daily_url) as response:
                    daily_data = await response.json()
                
                # Fetch RSI
                rsi_url = f"{ALPHA_VANTAGE_BASE}?function=RSI&symbol={symbol}&interval=daily&time_period=14&series_type=close&apikey={ALPHA_VANTAGE_API_KEY}"
                
                async with session.get(rsi_url) as response:
                    rsi_data = await response.json()
                
                market_data[symbol] = {
                    "daily": daily_data,
                    "rsi": rsi_data
                }
                
                # Respect API rate limits
                await asyncio.sleep(1)
                
            except Exception as e:
                log.error(f"Error fetching data for {symbol}: {e}")
                
    return market_data


async def calculate_predictions(market_data):
    """Calculate market predictions based on technical analysis."""
    predictions = {}
    
    for symbol, data in market_data.items():
        try:
            # Extract price data
            time_series = data.get("daily", {}).get("Time Series (Daily)", {})
            if not time_series:
                continue
                
            # Get recent prices
            dates = sorted(time_series.keys(), reverse=True)[:10]
            prices = [float(time_series[date]["4. close"]) for date in dates]
            
            # Get RSI
            rsi_data = data.get("rsi", {}).get("Technical Analysis: RSI", {})
            latest_rsi = 50  # Default if no RSI data
            if rsi_data:
                latest_date = max(rsi_data.keys())
                latest_rsi = float(rsi_data[latest_date]["RSI"])
            
            # Calculate indicators
            current_price = prices[0]
            ma_5 = sum(prices[:5]) / 5
            momentum = (prices[0] - prices[4]) / prices[4] * 100 if len(prices) >= 5 else 0
            
            # Technical score calculation
            tech_score = 0
            
            # RSI analysis
            if latest_rsi < 30:
                tech_score += 0.3  # Oversold
            elif latest_rsi > 70:
                tech_score -= 0.3  # Overbought
            
            # Moving average trend
            if current_price > ma_5:
                tech_score += 0.2
            else:
                tech_score -= 0.2
            
            # Momentum
            tech_score += momentum * 0.01
            
            # Convert to prediction
            prediction_pct = min(max(tech_score * 10, -4), 4)  # Cap at ±4%
            direction = "UP" if prediction_pct > 0 else "DOWN" if prediction_pct < 0 else "FLAT"
            confidence = min(abs(tech_score) * 100, 100)
            
            # Generate explanation
            explanation_parts = []
            if latest_rsi < 30:
                explanation_parts.append("oversold RSI")
            elif latest_rsi > 70:
                explanation_parts.append("overbought RSI")
            
            if current_price > ma_5:
                explanation_parts.append("price above MA")
            else:
                explanation_parts.append("price below MA")
            
            if abs(momentum) > 1:
                explanation_parts.append(f"{'positive' if momentum > 0 else 'negative'} momentum")
            
            explanation = f"Based on: {', '.join(explanation_parts)}"
            
            predictions[symbol] = {
                "direction": direction,
                "percentage": abs(prediction_pct),
                "confidence": confidence,
                "explanation": explanation,
                "rsi": latest_rsi,
                "current_price": current_price,
                "ma_5": ma_5,
                "momentum": momentum
            }
            
        except Exception as e:
            log.error(f"Error calculating prediction for {symbol}: {e}")
    
    return predictions


async def update_prediction_sensors(predictions):
    """Update Home Assistant sensors with predictions."""
    try:
        # Update S&P 500 prediction (SPY)
        if "SPY" in predictions:
            spy_pred = predictions["SPY"]
            direction = spy_pred["direction"]
            percentage = spy_pred["percentage"]
            
            state_value = f"{direction} {percentage:.1f}%"
            
            state.set("sensor.s_p_500_prediction", state_value, {
                "direction": direction,
                "percentage": percentage,
                "confidence": spy_pred["confidence"],
                "explanation": spy_pred["explanation"],
                "rsi": spy_pred["rsi"],
                "current_price": spy_pred["current_price"],
                "last_update": datetime.now().isoformat()
            })
        
        # Update FTSE prediction (VTI as proxy)
        if "VTI" in predictions:
            vti_pred = predictions["VTI"]
            direction = vti_pred["direction"]
            percentage = vti_pred["percentage"]
            
            state_value = f"{direction} {percentage:.1f}%"
            
            state.set("sensor.ftse_100_prediction", state_value, {
                "direction": direction,
                "percentage": percentage,
                "confidence": vti_pred["confidence"],
                "explanation": vti_pred["explanation"],
                "rsi": vti_pred["rsi"],
                "current_price": vti_pred["current_price"],
                "last_update": datetime.now().isoformat()
            })
            
    except Exception as e:
        log.error(f"Error updating sensors: {e}")


@time_trigger("cron(0 8,12,17 * * 1-5)")
async def scheduled_update():
    """Scheduled update during market hours."""
    log.info("Running scheduled market prediction update")
    await update_market_predictions()


@state_trigger("input_button.update_market_predictions == 'on'")
async def manual_update_trigger():
    """Trigger update when input button is pressed."""
    log.info("Manual update triggered")
    await update_market_predictions()


# Helper functions for other automations
@service
def get_market_sentiment():
    """Get current market sentiment from predictions."""
    try:
        sp500_state = state.get("sensor.s_p_500_prediction")
        ftse_state = state.get("sensor.ftse_100_prediction")
        
        sp500_direction = state.getattr("sensor.s_p_500_prediction").get("direction", "FLAT")
        ftse_direction = state.getattr("sensor.ftse_100_prediction").get("direction", "FLAT")
        
        if sp500_direction == "UP" and ftse_direction == "UP":
            return "bullish"
        elif sp500_direction == "DOWN" and ftse_direction == "DOWN":
            return "bearish"
        else:
            return "mixed"
            
    except Exception as e:
        log.error(f"Error getting market sentiment: {e}")
        return "unknown"


@service
def get_prediction_confidence():
    """Get average confidence of predictions."""
    try:
        sp500_conf = state.getattr("sensor.s_p_500_prediction").get("confidence", 0)
        ftse_conf = state.getattr("sensor.ftse_100_prediction").get("confidence", 0)
        
        return (sp500_conf + ftse_conf) / 2
        
    except Exception as e:
        log.error(f"Error getting prediction confidence: {e}")
        return 0


# Initialization
log.info("Market Prediction Pyscript module loaded")

# Check configuration
if not ALPHA_VANTAGE_API_KEY:
    log.warning("Alpha Vantage API key not configured in pyscript config")

if not FMP_API_KEY:
    log.info("FMP API key not configured - sentiment analysis will be disabled")