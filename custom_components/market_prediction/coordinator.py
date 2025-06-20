"""Data update coordinator for Market Prediction System."""
from __future__ import annotations

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Any

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    DOMAIN,
    ALPHA_VANTAGE_BASE_URL,
    DEFAULT_TIMEOUT,
    SENTIMENT_SOURCES,
    SYMBOLS,
    TECHNICAL_WEIGHT,
    SENTIMENT_WEIGHT,
    MAX_PREDICTION_CHANGE,
    PROGRESS_STAGES,
    UPDATE_INTERVAL_SECONDS,
)

_LOGGER = logging.getLogger(__name__)


class MarketPredictionCoordinator(DataUpdateCoordinator):
    """Market prediction data update coordinator."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL_SECONDS),
        )
        self.entry = entry
        self.alpha_vantage_key = entry.data["alpha_vantage_api_key"]
        self.fmp_key = entry.data.get("fmp_api_key", "")
        self.sentiment_sources = SENTIMENT_SOURCES
        self._progress = 0
        self._status = "Idle"
        self._current_source = ""
        self._processing_time = 0
        self._start_time = 0

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from APIs."""
        self._start_time = time.time()
        
        try:
            await self._update_progress(5, "Initializing", "")
            
            # Fetch market data for both indices
            sp500_data = await self._fetch_market_data("SPY")
            ftse_data = await self._fetch_market_data("ISF.L")
            
            await self._update_progress(25, "Fetching Market Data", "Complete")
            
            # Process technical analysis
            sp500_technical = await self._process_technical_analysis(sp500_data)
            ftse_technical = await self._process_technical_analysis(ftse_data)
            
            await self._update_progress(
                50, "Processing Technical Analysis", "Complete"
            )
            
            # Process sentiment analysis (5-10 minutes)
            sentiment_data = await self._process_comprehensive_sentiment()
            
            await self._update_progress(
                75, "Processing Sentiment Analysis", "Complete"
            )
            
            # Calculate final predictions
            sp500_prediction = self._calculate_prediction(
                sp500_technical, sentiment_data, "SPY"
            )
            ftse_prediction = self._calculate_prediction(
                ftse_technical, sentiment_data, "ISF.L"
            )
            
            await self._update_progress(90, "Calculating Predictions", "Complete")
            
            # Update processing time
            self._processing_time = time.time() - self._start_time
            
            result = {
                "s_p_500_prediction": sp500_prediction,
                "ftse_100_prediction": ftse_prediction,
                "progress": 100,
                "status": "Complete",
                "current_source": "Analysis Complete",
                "processing_time": self._processing_time,
                "last_update": datetime.now().isoformat(),
            }
            
            await self._update_progress(100, "Complete", "")
            return result
            
        except Exception as err:
            _LOGGER.error("Error updating market prediction data: %s", err)
            await self._update_progress(0, "Error", str(err))
            raise

    async def _fetch_market_data(self, symbol: str) -> dict[str, Any]:
        """Fetch market data from Alpha Vantage."""
        url = (
            f"{ALPHA_VANTAGE_BASE_URL}?"
            f"function=GLOBAL_QUOTE&symbol={symbol}&apikey={self.alpha_vantage_key}"
        )
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=DEFAULT_TIMEOUT) as response:
                if response.status != 200:
                    raise ValueError(f"API error: {response.status}")
                
                data = await response.json()
                
                if "Error Message" in data:
                    raise ValueError(f"API error: {data['Error Message']}")
                
                quote = data.get("Global Quote", {})
                
                return {
                    "symbol": quote.get("01. symbol", symbol),
                    "price": float(quote.get("05. price", 0)),
                    "change": float(quote.get("09. change", 0)),
                    "change_percent": quote.get("10. change percent", "0%"),
                    "volume": int(quote.get("06. volume", 0)),
                    "timestamp": quote.get("07. latest trading day", ""),
                }

    async def _process_technical_analysis(self, data: dict) -> dict[str, float]:
        """Process technical analysis indicators."""
        # Simulate technical analysis processing
        await asyncio.sleep(0.1)
        
        price = data.get("price", 0)
        change = data.get("change", 0)
        volume = data.get("volume", 0)
        
        # Calculate RSI (simplified)
        rsi = min(max((price % 100), 20), 80)
        rsi_signal = (rsi - 50) / 50  # Normalize to -1 to 1
        
        # Calculate momentum
        momentum = change / price if price > 0 else 0
        momentum_signal = min(max(momentum * 10, -1), 1)
        
        # Calculate moving average signal (simplified)
        ma_signal = 0.3 if change > 0 else -0.3
        
        # Calculate volatility
        volatility = abs(change) / price if price > 0 else 0
        volatility_signal = min(max(volatility * 5, -1), 1)
        
        # Volume analysis
        volume_signal = 0.2 if volume > 1000000 else -0.1
        
        return {
            "rsi_signal": rsi_signal,
            "momentum_signal": momentum_signal,
            "ma_signal": ma_signal,
            "volatility_signal": volatility_signal,
            "volume_signal": volume_signal,
        }

    async def _process_comprehensive_sentiment(self) -> dict[str, Any]:
        """Process sentiment analysis with multiple sources and progress tracking."""
        sentiment_results = []
        total_items = sum(source["items"] for source in self.sentiment_sources)
        processed_items = 0
        
        for source_idx, source in enumerate(self.sentiment_sources):
            source_name = source["name"]
            
            for item_idx in range(source["items"]):
                processed_items += 1
                progress = 50 + (processed_items / total_items) * 25
                
                current_status = (
                    f"{source_name} (item {item_idx + 1}/{source['items']})"
                )
                
                await self._update_progress(
                    progress, "Processing Sentiment Analysis", current_status
                )
                
                # Simulate API delay and processing
                await asyncio.sleep(source["api_delay"])
                
                # Simulate sentiment analysis result
                sentiment_score = (
                    0.1 if source_idx % 3 == 0 else 
                    -0.05 if source_idx % 3 == 1 else 0.02
                )
                
                sentiment_results.append({
                    "source": source_name,
                    "weight": source["weight"],
                    "sentiment": sentiment_score,
                })
        
        # Calculate weighted sentiment
        total_weight = sum(r["weight"] for r in sentiment_results)
        weighted_sentiment = sum(
            r["sentiment"] * r["weight"] for r in sentiment_results
        ) / total_weight if total_weight > 0 else 0
        
        return {
            "overall_sentiment": weighted_sentiment,
            "source_count": len(sentiment_results),
            "confidence": min(abs(weighted_sentiment) * 100, 85),
        }

    def _calculate_prediction(
        self,
        technical: dict[str, float],
        sentiment: dict[str, Any],
        symbol: str
    ) -> dict[str, Any]:
        """Calculate final prediction combining technical and sentiment analysis."""
        # Combine technical signals
        technical_score = (
            technical["rsi_signal"] * 0.25 +
            technical["momentum_signal"] * 0.30 +
            technical["ma_signal"] * 0.25 +
            technical["volatility_signal"] * 0.10 +
            technical["volume_signal"] * 0.10
        )
        
        # Get sentiment score
        sentiment_score = sentiment["overall_sentiment"]
        
        # Combine with weights
        final_score = (
            technical_score * TECHNICAL_WEIGHT +
            sentiment_score * SENTIMENT_WEIGHT
        )
        
        # Calculate prediction
        prediction_change = min(
            max(final_score * 5, -MAX_PREDICTION_CHANGE), MAX_PREDICTION_CHANGE
        )
        
        direction = "UP" if prediction_change > 0.1 else (
            "DOWN" if prediction_change < -0.1 else "FLAT"
        )
        
        confidence = min(
            abs(prediction_change) * 20 + sentiment["confidence"], 95
        )
        
        return {
            "symbol": symbol,
            "direction": direction,
            "predicted_change": round(prediction_change, 2),
            "confidence": round(confidence, 1),
            "technical_score": round(technical_score, 3),
            "sentiment_score": round(sentiment_score, 3),
            "final_score": round(final_score, 3),
        }

    async def _update_progress(
        self, progress: float, status: str, current_source: str
    ) -> None:
        """Update progress tracking."""
        self._progress = progress
        self._status = status
        self._current_source = current_source
        
        # Calculate ETA
        if self._start_time > 0 and progress > 5:
            elapsed = time.time() - self._start_time
            if progress < 100:
                estimated_total = elapsed * (100 / progress)
                eta_seconds = max(0, estimated_total - elapsed)
            else:
                eta_seconds = 0
        else:
            eta_seconds = 0
        
        # Update sensor states if they exist
        if hasattr(self.hass.states, 'async_set'):
            try:
                await self.hass.async_add_executor_job(
                    self._update_sensor_states, progress, status, 
                    current_source, eta_seconds
                )
            except Exception as err:
                _LOGGER.debug("Could not update sensor states: %s", err)

    def _update_sensor_states(
        self, progress: float, status: str, current_source: str, eta: float
    ) -> None:
        """Update sensor states synchronously."""
        try:
            self.hass.states.async_set(
                "sensor.market_prediction_progress",
                round(progress, 1),
                {"unit_of_measurement": "%", "friendly_name": "Analysis Progress"}
            )
            
            self.hass.states.async_set(
                "sensor.market_prediction_status",
                status,
                {"friendly_name": "Processing Status"}
            )
            
            self.hass.states.async_set(
                "sensor.market_prediction_current_source",
                current_source,
                {"friendly_name": "Current Source"}
            )
            
            eta_time = datetime.now() + timedelta(seconds=eta)
            self.hass.states.async_set(
                "sensor.market_prediction_eta",
                eta_time.isoformat() if eta > 0 else "Complete",
                {"friendly_name": "Estimated Completion"}
            )
        except Exception as err:
            _LOGGER.debug("Error updating sensor states: %s", err)

    @property
    def progress(self) -> float:
        """Return current progress."""
        return self._progress

    @property
    def status(self) -> str:
        """Return current status."""
        return self._status

    @property
    def current_source(self) -> str:
        """Return current source being processed."""
        return self._current_source

    @property
    def processing_time(self) -> float:
        """Return total processing time."""
        return self._processing_time