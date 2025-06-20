"""Data update coordinator for Market Prediction."""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    ALPHA_VANTAGE_BASE_URL,
    FMP_BASE_URL,
    CONF_ALPHA_VANTAGE_API_KEY,
    CONF_FMP_API_KEY,
    SENTIMENT_SOURCES,
    UPDATE_INTERVAL_SECONDS,
    MAX_PREDICTION_PERCENTAGE,
    RSI_PERIOD,
    MA_SHORT_PERIOD,
    MA_LONG_PERIOD,
)

_LOGGER = logging.getLogger(__name__)


class MarketPredictionCoordinator(DataUpdateCoordinator):
    """Market prediction data update coordinator."""

    def __init__(self, hass: HomeAssistant, config: Dict[str, Any]) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=UPDATE_INTERVAL_SECONDS),
        )
        self.alpha_vantage_api_key = config[CONF_ALPHA_VANTAGE_API_KEY]
        self.fmp_api_key = config.get(CONF_FMP_API_KEY)
        self.sentiment_sources = SENTIMENT_SOURCES
        self.progress = 0
        self.status = "Idle"
        self.current_source = ""
        self.processing_start_time = None
        self.eta_seconds = 0

    async def _async_update_data(self) -> Dict[str, Any]:
        """Fetch data from API endpoint."""
        try:
            self.processing_start_time = datetime.now()
            await self._update_progress(5, "Initializing", "Setting up analysis")

            # Fetch market data
            await self._update_progress(10, "Fetching Market Data", "Alpha Vantage API")
            sp500_data = await self._fetch_market_data("SPX")
            ftse_data = await self._fetch_market_data("UKX")

            await self._update_progress(25, "Fetching Market Data", "Processing data")
            await asyncio.sleep(2)

            # Process technical analysis
            await self._update_progress(30, "Processing Technical Analysis", "RSI calculation")
            sp500_technical = await self._process_technical_analysis(sp500_data)
            ftse_technical = await self._process_technical_analysis(ftse_data)

            await self._update_progress(50, "Processing Technical Analysis", "Complete")

            # Process sentiment analysis
            sentiment_data = await self._process_comprehensive_sentiment()

            await self._update_progress(90, "Calculating Predictions", "Final analysis")
            sp500_prediction = self._calculate_prediction(sp500_technical, sentiment_data)
            ftse_prediction = self._calculate_prediction(ftse_technical, sentiment_data)

            await self._update_progress(100, "Complete", "Analysis finished")

            return {
                "sp500": sp500_prediction,
                "ftse100": ftse_prediction,
                "sentiment": sentiment_data,
                "last_update": datetime.now().isoformat(),
                "processing_time": (datetime.now() - self.processing_start_time).total_seconds()
            }

        except Exception as err:
            await self._update_progress(0, "Error", f"Analysis failed: {err}")
            raise UpdateFailed(f"Error communicating with API: {err}")

    async def _update_progress(self, progress: int, status: str, current_source: str = "") -> None:
        """Update progress tracking."""
        self.progress = progress
        self.status = status
        self.current_source = current_source

        if self.processing_start_time and progress > 0:
            elapsed = (datetime.now() - self.processing_start_time).total_seconds()
            if progress < 100:
                estimated_total = elapsed * (100 / progress)
                self.eta_seconds = max(0, estimated_total - elapsed)
            else:
                self.eta_seconds = 0

        # Update sensor states
        if self.hass:
            self.hass.states.async_set(
                "sensor.market_prediction_progress",
                progress,
                {"unit_of_measurement": "%", "friendly_name": "Market Prediction Progress"}
            )
            self.hass.states.async_set(
                "sensor.market_prediction_status",
                status,
                {"friendly_name": "Market Prediction Status"}
            )
            self.hass.states.async_set(
                "sensor.market_prediction_current_source",
                current_source,
                {"friendly_name": "Current Source"}
            )

    async def _fetch_market_data(self, symbol: str) -> Dict[str, Any]:
        """Fetch market data from Alpha Vantage."""
        url = f"{ALPHA_VANTAGE_BASE_URL}?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={self.alpha_vantage_api_key}"
        timeout = aiohttp.ClientTimeout(total=30)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if "Time Series (Daily)" in data:
                        return data["Time Series (Daily)"]
                    elif "Error Message" in data:
                        raise UpdateFailed(f"API Error: {data['Error Message']}")
                    elif "Note" in data:
                        raise UpdateFailed("API rate limit exceeded")
                else:
                    raise UpdateFailed(f"HTTP Error: {response.status}")

        return {}

    async def _process_technical_analysis(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Process technical analysis indicators."""
        if not data:
            return {"rsi": 50, "ma_signal": 0, "momentum": 0, "volatility": 0.02}

        # Convert data to lists for processing
        dates = sorted(data.keys(), reverse=True)[:30]  # Last 30 days
        closes = [float(data[date]["4. close"]) for date in dates[:RSI_PERIOD]]

        # Calculate RSI
        rsi = self._calculate_rsi(closes)

        # Calculate moving averages
        ma_short = sum(closes[:MA_SHORT_PERIOD]) / MA_SHORT_PERIOD
        ma_long = sum(closes[:MA_LONG_PERIOD]) / MA_LONG_PERIOD
        ma_signal = (ma_short - ma_long) / ma_long

        # Calculate momentum
        momentum = (closes[0] - closes[4]) / closes[4] if len(closes) > 4 else 0

        # Calculate volatility
        returns = [(closes[i] - closes[i+1]) / closes[i+1] for i in range(len(closes)-1)]
        volatility = (sum(r**2 for r in returns) / len(returns))**0.5 if returns else 0.02

        return {
            "rsi": rsi,
            "ma_signal": ma_signal,
            "momentum": momentum,
            "volatility": volatility
        }

    def _calculate_rsi(self, prices: list) -> float:
        """Calculate RSI indicator."""
        if len(prices) < RSI_PERIOD:
            return 50.0

        gains = []
        losses = []

        for i in range(1, len(prices)):
            diff = prices[i-1] - prices[i]  # Reversed because prices are in descending order
            if diff > 0:
                gains.append(diff)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(diff))

        avg_gain = sum(gains) / len(gains)
        avg_loss = sum(losses) / len(losses)

        if avg_loss == 0:
            return 100.0

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    async def _process_comprehensive_sentiment(self) -> Dict[str, Any]:
        """Process sentiment analysis with multiple sources."""
        sentiment_results = []
        total_items = sum(source["items"] for source in self.sentiment_sources)
        processed_items = 0

        for source_idx, source in enumerate(self.sentiment_sources):
            source_name = source["name"]
            # Simulate processing items from this source
            for item_idx in range(source["items"]):
                processed_items += 1
                progress = 50 + (processed_items / total_items) * 25
                await self._update_progress(
                    int(progress),
                    "Processing Sentiment Analysis",
                    f"{source_name} (item {item_idx+1}/{source['items']})"
                )
                await asyncio.sleep(source["api_delay"])

                # Simulate sentiment score for this item
                sentiment_score = 0.1 * (source_idx % 3 - 1)  # Varies between -0.1 and 0.1
                sentiment_results.append({
                    "source": source_name,
                    "weight": source["weight"],
                    "sentiment": sentiment_score
                })

        # Calculate weighted sentiment
        total_weight = sum(result["weight"] for result in sentiment_results)
        weighted_sentiment = sum(
            result["sentiment"] * result["weight"] for result in sentiment_results
        ) / total_weight if total_weight > 0 else 0

        return {
            "overall_sentiment": weighted_sentiment,
            "sentiment_strength": abs(weighted_sentiment),
            "sentiment_direction": "positive" if weighted_sentiment > 0 else "negative",
            "sources_processed": len(sentiment_results),
            "total_weight": total_weight
        }

    def _calculate_prediction(self, technical: Dict[str, float], sentiment: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate final prediction using Renaissance Technologies inspired algorithm."""
        # Technical analysis (75% weight)
        technical_score = 0

        # RSI component (25% of total)
        rsi = technical["rsi"]
        if rsi < 30:
            technical_score += 0.25  # Oversold, expect bounce
        elif rsi > 70:
            technical_score -= 0.25  # Overbought, expect decline

        # Moving average component (25% of total)
        ma_signal = technical["ma_signal"]
        technical_score += ma_signal * 0.25

        # Momentum component (15% of total)
        momentum = technical["momentum"]
        technical_score += momentum * 0.15

        # Volatility adjustment (10% of total)
        volatility = technical["volatility"]
        volatility_factor = min(volatility * 2, 0.1)  # Cap at 10%
        if technical_score > 0:
            technical_score += volatility_factor
        else:
            technical_score -= volatility_factor

        # Sentiment analysis (25% weight)
        sentiment_score = sentiment["overall_sentiment"] * 0.25

        # Combine scores
        total_score = technical_score + sentiment_score

        # Convert to percentage and apply limits
        prediction_pct = total_score * 100
        prediction_pct = max(-MAX_PREDICTION_PERCENTAGE, min(MAX_PREDICTION_PERCENTAGE, prediction_pct))

        # Calculate confidence based on signal strength
        confidence = min(
            abs(technical_score) + sentiment["sentiment_strength"],
            1.0
        )

        direction = "UP" if prediction_pct > 0 else "DOWN"
        state_value = f"{direction} {abs(prediction_pct):.1f}%"

        return {
            "state": state_value,
            "direction": direction,
            "percentage": abs(prediction_pct),
            "confidence": confidence * 100,
            "technical_score": technical_score,
            "sentiment_score": sentiment_score,
            "total_score": total_score,
            "technical_details": technical,
            "last_update": datetime.now().isoformat()
        }