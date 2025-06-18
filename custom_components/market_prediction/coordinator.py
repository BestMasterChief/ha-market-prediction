"""Data update coordinator for Market Prediction."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any

import aiohttp
from asyncio_throttle import Throttler

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    CONF_ALPHA_VANTAGE_API_KEY,
    CONF_FMP_API_KEY,
    ALPHA_VANTAGE_BASE_URL,
    FMP_BASE_URL,
    DEFAULT_UPDATE_INTERVAL,
    DEFAULT_TIMEOUT,
    SUPPORTED_SYMBOLS,
    PROGRESS_STAGES,
    ALPHA_VANTAGE_DAILY_LIMIT,
    FMP_DAILY_LIMIT,
)

_LOGGER = logging.getLogger(__name__)


class MarketPredictionCoordinator(DataUpdateCoordinator):
    """Class to manage fetching market prediction data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        self.entry = entry
        self.alpha_vantage_api_key = entry.data[CONF_ALPHA_VANTAGE_API_KEY]
        self.fmp_api_key = entry.data.get(CONF_FMP_API_KEY)
        
        # Progress tracking
        self._current_stage = "initializing"
        self._current_progress = 0
        self._eta = None
        self._stage_start_time = None
        
        # API call tracking
        self._alpha_vantage_calls_today = 0
        self._fmp_calls_today = 0
        self._last_reset_date = datetime.now().date()
        
        # Throttling to prevent API abuse
        self._av_throttler = Throttler(rate_limit=5, period=60)  # 5 calls per minute
        self._fmp_throttler = Throttler(rate_limit=4, period=60)  # 4 calls per minute
        
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=DEFAULT_UPDATE_INTERVAL,
        )

    async def _async_setup(self) -> None:
        """Set up the coordinator."""
        self._update_progress("initializing")
        _LOGGER.info("Market Prediction coordinator setup complete")

    def _update_progress(self, stage: str) -> None:
        """Update the current progress stage."""
        if stage in PROGRESS_STAGES:
            self._current_stage = stage
            self._current_progress = PROGRESS_STAGES[stage]["progress"]
            self._stage_start_time = datetime.now()
            
            # Calculate ETA based on typical stage durations
            stage_durations = {
                "initializing": 10,
                "fetching_data": 30,
                "processing_technical": 20,
                "processing_sentiment": 15,
                "calculating": 10,
            }
            
            if stage != "complete":
                remaining_time = stage_durations.get(stage, 30)
                self._eta = datetime.now() + timedelta(seconds=remaining_time)
            else:
                self._eta = None
                
            _LOGGER.debug(f"Progress updated: {stage} ({self._current_progress}%)")

    def _reset_daily_counters(self) -> None:
        """Reset daily API call counters if needed."""
        today = datetime.now().date()
        if today != self._last_reset_date:
            self._alpha_vantage_calls_today = 0
            self._fmp_calls_today = 0
            self._last_reset_date = today
            _LOGGER.info("API call counters reset for new day")

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from APIs with proper progress tracking."""
        self._reset_daily_counters()
        
        try:
            self._update_progress("fetching_data")
            
            # Check API limits
            if self._alpha_vantage_calls_today >= ALPHA_VANTAGE_DAILY_LIMIT:
                raise UpdateFailed("Alpha Vantage daily API limit exceeded")
            
            # Fetch market data
            market_data = await self._fetch_market_data()
            
            self._update_progress("processing_technical")
            
            # Process technical analysis
            technical_analysis = await self._process_technical_analysis(market_data)
            
            sentiment_data = {}
            if self.fmp_api_key and self._fmp_calls_today < FMP_DAILY_LIMIT:
                self._update_progress("processing_sentiment")
                sentiment_data = await self._fetch_sentiment_data()
            else:
                _LOGGER.info("Skipping sentiment analysis - no FMP API key or limit exceeded")
            
            self._update_progress("calculating")
            
            # Generate predictions
            predictions = await self._generate_predictions(technical_analysis, sentiment_data)
            
            self._update_progress("complete")
            
            return {
                "predictions": predictions,
                "technical_analysis": technical_analysis,
                "sentiment_data": sentiment_data,
                "last_update": datetime.now().isoformat(),
                "api_calls_remaining": {
                    "alpha_vantage": ALPHA_VANTAGE_DAILY_LIMIT - self._alpha_vantage_calls_today,
                    "fmp": FMP_DAILY_LIMIT - self._fmp_calls_today if self.fmp_api_key else 0,
                },
                "progress": {
                    "stage": PROGRESS_STAGES[self._current_stage]["stage"],
                    "progress": self._current_progress,
                    "eta": self._eta.isoformat() if self._eta else None,
                }
            }
            
        except Exception as err:
            _LOGGER.error(f"Error updating market prediction data: {err}")
            self._update_progress("complete")  # Reset progress on error
            if "Invalid API call" in str(err) or "API key" in str(err):
                raise ConfigEntryAuthFailed(f"API authentication failed: {err}") from err
            raise UpdateFailed(f"Error communicating with API: {err}") from err

    async def _fetch_market_data(self) -> dict[str, Any]:
        """Fetch market data from Alpha Vantage."""
        market_data = {}
        
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT)
        ) as session:
            for market_name, symbol in SUPPORTED_SYMBOLS.items():
                try:
                    async with self._av_throttler:
                        url = (
                            f"{ALPHA_VANTAGE_BASE_URL}?"
                            f"function=GLOBAL_QUOTE&symbol={symbol}&apikey={self.alpha_vantage_api_key}"
                        )
                        
                        async with session.get(url) as response:
                            if response.status != 200:
                                raise UpdateFailed(f"Alpha Vantage API returned status {response.status}")
                            
                            data = await response.json()
                            self._alpha_vantage_calls_today += 1
                            
                            if "Error Message" in data:
                                raise UpdateFailed(f"Alpha Vantage error: {data['Error Message']}")
                            
                            if "Note" in data:
                                raise UpdateFailed("Alpha Vantage API rate limit exceeded")
                            
                            if "Global Quote" not in data:
                                raise UpdateFailed(f"Invalid Alpha Vantage response for {symbol}")
                            
                            quote_data = data["Global Quote"]
                            market_data[market_name] = {
                                "symbol": quote_data.get("01. symbol"),
                                "price": float(quote_data.get("05. price", 0)),
                                "change": float(quote_data.get("09. change", 0)),
                                "change_percent": quote_data.get("10. change percent", "0%").replace("%", ""),
                                "volume": int(quote_data.get("06. volume", 0)),
                                "previous_close": float(quote_data.get("08. previous close", 0)),
                            }
                            
                except (asyncio.TimeoutError, aiohttp.ClientError) as err:
                    _LOGGER.error(f"Error fetching data for {market_name}: {err}")
                    raise UpdateFailed(f"Network error fetching {market_name} data") from err
                
                # Small delay between requests
                await asyncio.sleep(0.5)
        
        return market_data

    async def _fetch_sentiment_data(self) -> dict[str, Any]:
        """Fetch sentiment data from Financial Modeling Prep (optional)."""
        if not self.fmp_api_key:
            return {}
        
        sentiment_data = {}
        
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT)
        ) as session:
            try:
                async with self._fmp_throttler:
                    url = f"{FMP_BASE_URL}/stock_news?tickers=SPY&limit=10&apikey={self.fmp_api_key}"
                    
                    async with session.get(url) as response:
                        if response.status != 200:
                            _LOGGER.warning(f"FMP API returned status {response.status}")
                            return {}
                        
                        data = await response.json()
                        self._fmp_calls_today += 1
                        
                        if isinstance(data, dict) and "Error Message" in data:
                            _LOGGER.warning(f"FMP API error: {data['Error Message']}")
                            return {}
                        
                        # Basic sentiment analysis
                        positive_words = ["good", "great", "positive", "up", "rise", "gain", "bull", "strong"]
                        negative_words = ["bad", "down", "fall", "drop", "bear", "weak", "decline", "loss"]
                        
                        sentiment_score = 0
                        news_count = 0
                        
                        for article in data[:10]:  # Process up to 10 articles
                            title = article.get("title", "").lower()
                            content = article.get("text", "").lower()
                            combined_text = f"{title} {content}"
                            
                            positive_count = sum(1 for word in positive_words if word in combined_text)
                            negative_count = sum(1 for word in negative_words if word in combined_text)
                            
                            if positive_count > negative_count:
                                sentiment_score += 1
                            elif negative_count > positive_count:
                                sentiment_score -= 1
                            
                            news_count += 1
                        
                        if news_count > 0:
                            sentiment_data = {
                                "sentiment_score": sentiment_score / news_count,
                                "news_processed": news_count,
                                "sentiment_direction": "positive" if sentiment_score > 0 else "negative" if sentiment_score < 0 else "neutral",
                            }
                        
            except (asyncio.TimeoutError, aiohttp.ClientError) as err:
                _LOGGER.warning(f"Error fetching sentiment data: {err}")
                return {}
        
        return sentiment_data

    async def _process_technical_analysis(self, market_data: dict[str, Any]) -> dict[str, Any]:
        """Process technical analysis indicators."""
        technical_data = {}
        
        for market_name, data in market_data.items():
            price = data["price"]
            change_percent = float(data["change_percent"])
            
            # Simple technical indicators
            rsi_signal = 0
            if abs(change_percent) > 2:
                rsi_signal = -1 if change_percent < -2 else 1
            
            momentum_signal = 1 if change_percent > 0 else -1 if change_percent < 0 else 0
            
            # Combine signals
            technical_score = (rsi_signal * 0.4) + (momentum_signal * 0.6)
            
            technical_data[market_name] = {
                "rsi_signal": rsi_signal,
                "momentum_signal": momentum_signal,
                "technical_score": technical_score,
                "volatility": abs(change_percent),
            }
        
        return technical_data

    async def _generate_predictions(
        self, technical_analysis: dict[str, Any], sentiment_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Generate market predictions based on analysis."""
        predictions = {}
        
        sentiment_weight = 0.25 if sentiment_data else 0
        technical_weight = 1.0 - sentiment_weight
        
        for market_name in SUPPORTED_SYMBOLS:
            if market_name not in technical_analysis:
                continue
            
            technical_score = technical_analysis[market_name]["technical_score"]
            sentiment_score = sentiment_data.get("sentiment_score", 0) if sentiment_data else 0
            
            # Combine scores
            combined_score = (technical_score * technical_weight) + (sentiment_score * sentiment_weight)
            
            # Determine direction and confidence
            if combined_score > 0.3:
                direction = "UP"
                confidence = min(abs(combined_score) * 100, 95)
            elif combined_score < -0.3:
                direction = "DOWN"
                confidence = min(abs(combined_score) * 100, 95)
            else:
                direction = "NEUTRAL"
                confidence = 50
            
            # Calculate percentage prediction (capped at ±4%)
            percentage = min(max(combined_score * 2.5, -4.0), 4.0)
            
            # Generate explanation
            explanation_parts = []
            if technical_analysis[market_name]["technical_score"] != 0:
                explanation_parts.append("Technical indicators suggest market momentum")
            if sentiment_data and sentiment_score != 0:
                explanation_parts.append(f"News sentiment is {sentiment_data['sentiment_direction']}")
            
            explanation = ". ".join(explanation_parts) if explanation_parts else "Based on current market conditions"
            
            predictions[market_name] = {
                "direction": direction,
                "percentage": round(percentage, 1),
                "confidence": round(confidence),
                "explanation": explanation,
                "combined_score": round(combined_score, 3),
            }
        
        return predictions

    @property
    def progress_data(self) -> dict[str, Any]:
        """Return current progress information."""
        return {
            "stage": PROGRESS_STAGES[self._current_stage]["stage"],
            "progress": self._current_progress,
            "eta": self._eta.isoformat() if self._eta else None,
        }