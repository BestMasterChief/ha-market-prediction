"""DataUpdateCoordinator for Market Prediction."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any

import aiohttp
import async_timeout

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    CONF_ALPHA_VANTAGE_API_KEY,
    CONF_FMP_API_KEY,
    ALPHA_VANTAGE_BASE_URL,
    FMP_BASE_URL,
    PROGRESS_IDLE,
    PROGRESS_FETCHING_DATA,
    PROGRESS_PROCESSING_TECHNICAL,
    PROGRESS_PROCESSING_SENTIMENT,
    PROGRESS_CALCULATING,
    PROGRESS_COMPLETE,
    PROGRESS_ERROR,
    ERROR_NO_API_KEY,
    ERROR_API_ERROR,
    MAX_PREDICTION_CHANGE,
)

_LOGGER = logging.getLogger(__name__)


class MarketPredictionDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(
        self,
        hass: HomeAssistant,
        logger: logging.Logger,
        name: str,
        update_interval: timedelta,
        entry: ConfigEntry,
    ) -> None:
        """Initialize."""
        self.entry = entry
        self._alpha_vantage_key = entry.data.get(CONF_ALPHA_VANTAGE_API_KEY)
        self._fmp_key = entry.data.get(CONF_FMP_API_KEY)
        self._progress_state = PROGRESS_IDLE
        self._progress_percentage = 0
        self._eta = None
        
        super().__init__(hass, logger, name=name, update_interval=update_interval)

    @property
    def progress_state(self) -> str:
        """Return current progress state."""
        return self._progress_state

    @property
    def progress_percentage(self) -> int:
        """Return current progress percentage."""
        return self._progress_percentage

    @property
    def eta(self) -> datetime | None:
        """Return estimated time of completion."""
        return self._eta

    def _set_progress(self, state: str, percentage: int = 0, eta_minutes: int = 0) -> None:
        """Set the current progress state."""
        self._progress_state = state
        self._progress_percentage = percentage
        if eta_minutes > 0:
            self._eta = datetime.now() + timedelta(minutes=eta_minutes)
        else:
            self._eta = None

    async def _async_update_data(self) -> dict[str, Any]:
        """Update data via library."""
        if not self._alpha_vantage_key:
            raise UpdateFailed(ERROR_NO_API_KEY)

        try:
            self._set_progress(PROGRESS_FETCHING_DATA, 10, 3)
            
            # Fetch market data
            market_data = await self._fetch_market_data()
            
            self._set_progress(PROGRESS_PROCESSING_TECHNICAL, 40, 2)
            
            # Process technical indicators
            technical_data = await self._process_technical_indicators(market_data)
            
            self._set_progress(PROGRESS_PROCESSING_SENTIMENT, 70, 1)
            
            # Process sentiment data if FMP key available
            sentiment_data = {}
            if self._fmp_key:
                sentiment_data = await self._fetch_sentiment_data()
            
            self._set_progress(PROGRESS_CALCULATING, 90, 0)
            
            # Generate predictions
            predictions = await self._calculate_predictions(technical_data, sentiment_data)
            
            self._set_progress(PROGRESS_COMPLETE, 100, 0)
            
            return {
                "sp500_prediction": predictions.get("sp500", {}),
                "ftse_prediction": predictions.get("ftse", {}),
                "last_update": datetime.now().isoformat(),
                "progress_state": self._progress_state,
                "progress_percentage": self._progress_percentage,
                "eta": self._eta.isoformat() if self._eta else None,
            }
            
        except Exception as exc:
            self._set_progress(PROGRESS_ERROR, 0, 0)
            _LOGGER.exception("Error updating market prediction data")
            raise UpdateFailed(f"Error communicating with API: {exc}") from exc

    async def _fetch_market_data(self) -> dict[str, Any]:
        """Fetch market data from Alpha Vantage."""
        symbols = ["SPY", "VTI"]  # S&P 500 and FTSE 100 proxies
        market_data = {}
        
        async with aiohttp.ClientSession() as session:
            for symbol in symbols:
                try:
                    # Get daily data
                    daily_url = f"{ALPHA_VANTAGE_BASE_URL}?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={self._alpha_vantage_key}"
                    
                    async with async_timeout.timeout(30):
                        async with session.get(daily_url) as response:
                            daily_data = await response.json()
                    
                    # Get RSI
                    rsi_url = f"{ALPHA_VANTAGE_BASE_URL}?function=RSI&symbol={symbol}&interval=daily&time_period=14&series_type=close&apikey={self._alpha_vantage_key}"
                    
                    async with async_timeout.timeout(30):
                        async with session.get(rsi_url) as response:
                            rsi_data = await response.json()
                    
                    market_data[symbol] = {
                        "daily": daily_data,
                        "rsi": rsi_data
                    }
                    
                    # Add delay to respect API limits
                    await asyncio.sleep(1)
                    
                except Exception as exc:
                    _LOGGER.error(f"Error fetching data for {symbol}: {exc}")
                    raise
        
        return market_data

    async def _process_technical_indicators(self, market_data: dict) -> dict[str, Any]:
        """Process technical indicators."""
        technical_data = {}
        
        for symbol, data in market_data.items():
            try:
                # Process daily prices
                daily_series = data.get("daily", {}).get("Time Series (Daily)", {})
                if not daily_series:
                    continue
                
                # Get latest prices
                dates = sorted(daily_series.keys(), reverse=True)[:20]
                prices = [float(daily_series[date]["4. close"]) for date in dates]
                volumes = [float(daily_series[date]["5. volume"]) for date in dates]
                
                # Calculate technical indicators
                rsi_series = data.get("rsi", {}).get("Technical Analysis: RSI", {})
                latest_rsi_date = max(rsi_series.keys()) if rsi_series else None
                latest_rsi = float(rsi_series[latest_rsi_date]["RSI"]) if latest_rsi_date else 50
                
                # Calculate moving averages
                ma_5 = sum(prices[:5]) / 5 if len(prices) >= 5 else prices[0]
                ma_10 = sum(prices[:10]) / 10 if len(prices) >= 10 else prices[0]
                
                # Calculate momentum
                momentum = (prices[0] - prices[4]) / prices[4] * 100 if len(prices) >= 5 else 0
                
                # Calculate volatility
                returns = [(prices[i] - prices[i+1]) / prices[i+1] for i in range(len(prices)-1)]
                volatility = (sum(r**2 for r in returns) / len(returns)) ** 0.5 if returns else 0
                
                technical_data[symbol] = {
                    "current_price": prices[0],
                    "rsi": latest_rsi,
                    "ma_5": ma_5,
                    "ma_10": ma_10,
                    "momentum": momentum,
                    "volatility": volatility,
                    "volume_avg": sum(volumes[:5]) / 5 if len(volumes) >= 5 else volumes[0],
                }
                
            except Exception as exc:
                _LOGGER.error(f"Error processing technical data for {symbol}: {exc}")
                
        return technical_data

    async def _fetch_sentiment_data(self) -> dict[str, Any]:
        """Fetch sentiment data from FMP."""
        if not self._fmp_key:
            return {}
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{FMP_BASE_URL}/v3/stock_news?tickers=SPY,VTI&limit=50&apikey={self._fmp_key}"
                
                async with async_timeout.timeout(30):
                    async with session.get(url) as response:
                        news_data = await response.json()
                
                # Simple sentiment analysis
                positive_words = ["up", "gain", "rise", "bull", "positive", "growth", "strong"]
                negative_words = ["down", "fall", "bear", "negative", "decline", "weak", "loss"]
                
                sentiment_scores = []
                for article in news_data[:20]:  # Analyze recent 20 articles
                    title = article.get("title", "").lower()
                    text = article.get("text", "").lower()
                    content = f"{title} {text}"
                    
                    positive_count = sum(1 for word in positive_words if word in content)
                    negative_count = sum(1 for word in negative_words if word in content)
                    
                    if positive_count + negative_count > 0:
                        score = (positive_count - negative_count) / (positive_count + negative_count)
                    else:
                        score = 0
                    
                    sentiment_scores.append(score)
                
                avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
                
                return {
                    "overall_sentiment": avg_sentiment,
                    "news_count": len(news_data),
                    "analyzed_articles": len(sentiment_scores)
                }
                
        except Exception as exc:
            _LOGGER.error(f"Error fetching sentiment data: {exc}")
            return {}

    async def _calculate_predictions(self, technical_data: dict, sentiment_data: dict) -> dict[str, Any]:
        """Calculate market predictions."""
        predictions = {}
        
        symbol_map = {
            "SPY": "sp500",
            "VTI": "ftse"
        }
        
        for symbol, data in technical_data.items():
            try:
                # Technical analysis score (75% weight)
                tech_score = 0
                
                # RSI analysis (25% of technical)
                rsi = data.get("rsi", 50)
                if rsi < 30:
                    tech_score += 0.25  # Oversold, expect recovery
                elif rsi > 70:
                    tech_score -= 0.25  # Overbought, expect decline
                
                # Moving average analysis (25% of technical)
                current_price = data.get("current_price", 0)
                ma_5 = data.get("ma_5", 0)
                ma_10 = data.get("ma_10", 0)
                
                if current_price > ma_5 > ma_10:
                    tech_score += 0.25  # Uptrend
                elif current_price < ma_5 < ma_10:
                    tech_score -= 0.25  # Downtrend
                
                # Momentum analysis (15% of technical)
                momentum = data.get("momentum", 0)
                tech_score += momentum * 0.0015  # Scale momentum
                
                # Volatility adjustment (10% of technical)
                volatility = data.get("volatility", 0)
                if volatility < 0.02:
                    tech_score += 0.1  # Low volatility = stable growth
                elif volatility > 0.05:
                    tech_score -= 0.1  # High volatility = uncertainty
                
                # Sentiment analysis score (25% weight)
                sentiment_score = 0
                if sentiment_data:
                    overall_sentiment = sentiment_data.get("overall_sentiment", 0)
                    sentiment_score = overall_sentiment * 0.25
                
                # Combine scores
                final_score = (tech_score * 0.75) + (sentiment_score * 0.25)
                
                # Convert to percentage and cap at ±4%
                prediction_pct = min(max(final_score * 100, -MAX_PREDICTION_CHANGE), MAX_PREDICTION_CHANGE)
                
                # Calculate confidence based on signal strength
                confidence = min(abs(final_score) * 200, 100)  # 0-100%
                
                # Determine direction
                direction = "UP" if prediction_pct > 0 else "DOWN" if prediction_pct < 0 else "FLAT"
                
                # Generate explanation
                explanation_parts = []
                if rsi < 30:
                    explanation_parts.append("oversold conditions (RSI)")
                elif rsi > 70:
                    explanation_parts.append("overbought conditions (RSI)")
                
                if current_price > ma_5 > ma_10:
                    explanation_parts.append("bullish moving average trend")
                elif current_price < ma_5 < ma_10:
                    explanation_parts.append("bearish moving average trend")
                
                if momentum > 1:
                    explanation_parts.append("positive momentum")
                elif momentum < -1:
                    explanation_parts.append("negative momentum")
                
                if sentiment_data and abs(overall_sentiment) > 0.1:
                    sentiment_desc = "positive" if overall_sentiment > 0 else "negative"
                    explanation_parts.append(f"{sentiment_desc} news sentiment")
                
                explanation = f"Prediction based on: {', '.join(explanation_parts) if explanation_parts else 'mixed technical signals'}"
                
                prediction_key = symbol_map.get(symbol, symbol.lower())
                predictions[prediction_key] = {
                    "direction": direction,
                    "percentage": round(abs(prediction_pct), 2),
                    "confidence": round(confidence, 1),
                    "explanation": explanation,
                    "technical_score": round(tech_score, 3),
                    "sentiment_score": round(sentiment_score, 3),
                    "final_score": round(final_score, 3),
                }
                
            except Exception as exc:
                _LOGGER.error(f"Error calculating prediction for {symbol}: {exc}")
                
        return predictions