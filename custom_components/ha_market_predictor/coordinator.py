"""Data update coordinator for HA Market Predictor."""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict

import requests
import yfinance as yf
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.event import async_track_time_interval, async_track_utc_time_change
from homeassistant.util import dt as dt_util
import pytz

from .const import (
    DOMAIN,
    ALPHAVANTAGE_DAILY_LIMIT,
    FINANCIALMODELPREP_DAILY_LIMIT,
    FTSE_SYMBOL,
    SP500_SYMBOL,
    FTSE_PRE_MARKET_HOUR,
    FTSE_PRE_CLOSE_HOUR,
    SP500_PRE_MARKET_HOUR,
    SP500_PRE_CLOSE_HOUR,
    DEFAULT_UPDATE_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

class APIRateLimiter:
    """Handle API rate limiting."""

    def __init__(self):
        self.call_counts = {}
        self.reset_times = {}

    def can_make_call(self, api_name: str, limit: int) -> bool:
        """Check if we can make an API call."""
        now = datetime.now()

        # Reset counter if it's a new day
        if api_name in self.reset_times:
            if now.date() > self.reset_times[api_name].date():
                self.call_counts[api_name] = 0
                self.reset_times[api_name] = now
        else:
            self.call_counts[api_name] = 0
            self.reset_times[api_name] = now

        return self.call_counts.get(api_name, 0) < limit

    def record_call(self, api_name: str):
        """Record an API call."""
        self.call_counts[api_name] = self.call_counts.get(api_name, 0) + 1

class MarketPredictorCoordinator(DataUpdateCoordinator):
    """Market prediction coordinator."""

    def __init__(self, hass: HomeAssistant, alphavantage_key: str, fmp_key: str):
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=DEFAULT_UPDATE_INTERVAL,
        )

        self.alphavantage_key = alphavantage_key
        self.fmp_key = fmp_key
        self.rate_limiter = APIRateLimiter()
        self.data = {
            "ftse_prediction": None,
            "sp500_prediction": None,
            "api_usage": {"alphavantage": 0, "fmp": 0},
            "last_update": None,
        }

        # Schedule market-specific updates
        self._setup_scheduled_updates()

    def _setup_scheduled_updates(self):
        """Set up scheduled updates for market hours."""
        # FTSE pre-market check (7:00 AM UK time)
        async_track_utc_time_change(
            self.hass,
            self._scheduled_ftse_premarket,
            hour=FTSE_PRE_MARKET_HOUR,
            minute=0,
            second=0,
        )

        # FTSE pre-close check (3:30 PM UK time)
        async_track_utc_time_change(
            self.hass,
            self._scheduled_ftse_preclose,
            hour=FTSE_PRE_CLOSE_HOUR,
            minute=30,
            second=0,
        )

        # S&P 500 pre-market check (8:30 AM ET in UTC)
        async_track_utc_time_change(
            self.hass,
            self._scheduled_sp500_premarket,
            hour=SP500_PRE_MARKET_HOUR,
            minute=30,
            second=0,
        )

        # S&P 500 pre-close check (3:00 PM ET in UTC)
        async_track_utc_time_change(
            self.hass,
            self._scheduled_sp500_preclose,
            hour=SP500_PRE_CLOSE_HOUR,
            minute=0,
            second=0,
        )

    async def _scheduled_ftse_premarket(self, now):
        """Handle scheduled FTSE pre-market update."""
        _LOGGER.info("Running scheduled FTSE pre-market prediction")
        await self._update_market_prediction("FTSE", FTSE_SYMBOL)

    async def _scheduled_ftse_preclose(self, now):
        """Handle scheduled FTSE pre-close update."""
        _LOGGER.info("Running scheduled FTSE pre-close prediction")
        await self._update_market_prediction("FTSE", FTSE_SYMBOL)

    async def _scheduled_sp500_premarket(self, now):
        """Handle scheduled S&P 500 pre-market update."""
        _LOGGER.info("Running scheduled S&P 500 pre-market prediction")
        await self._update_market_prediction("SP500", SP500_SYMBOL)

    async def _scheduled_sp500_preclose(self, now):
        """Handle scheduled S&P 500 pre-close update."""
        _LOGGER.info("Running scheduled S&P 500 pre-close prediction")
        await self._update_market_prediction("SP500", SP500_SYMBOL)

    async def _update_market_prediction(self, market_name: str, symbol: str):
        """Update prediction for a specific market."""
        try:
            # Check rate limits
            if not self.rate_limiter.can_make_call("alphavantage", ALPHAVANTAGE_DAILY_LIMIT):
                _LOGGER.warning("Alpha Vantage API limit reached for today")
                return

            # Get market data using yfinance (free alternative)
            await self.hass.async_add_executor_job(self._fetch_market_data, market_name, symbol)

            # Update the data
            self.data["last_update"] = dt_util.utcnow()
            self.data["api_usage"]["alphavantage"] = self.rate_limiter.call_counts.get("alphavantage", 0)

            # Notify listeners
            self.async_update_listeners()

        except Exception as err:
            _LOGGER.error("Error updating %s prediction: %s", market_name, err)

    def _fetch_market_data(self, market_name: str, symbol: str):
        """Fetch market data and generate prediction."""
        try:
            # Use yfinance to get market data (no API key required)
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="5d")

            if hist.empty:
                _LOGGER.warning("No historical data available for %s", symbol)
                return

            # Simple prediction logic
            recent_close = hist['Close'].iloc[-1]
            previous_close = hist['Close'].iloc[-2] if len(hist) > 1 else recent_close

            # Calculate momentum
            momentum = (recent_close - previous_close) / previous_close * 100

            # Simple prediction based on momentum
            if momentum > 1:
                prediction = "UP"
                confidence = min(90, 50 + abs(momentum) * 10)
            elif momentum < -1:
                prediction = "DOWN"
                confidence = min(90, 50 + abs(momentum) * 10)
            else:
                prediction = "NEUTRAL"
                confidence = 30

            prediction_data = {
                "prediction": prediction,
                "confidence": round(confidence, 1),
                "current_price": round(recent_close, 2),
                "momentum": round(momentum, 2),
                "timestamp": dt_util.utcnow().isoformat(),
            }

            # Store the prediction
            if market_name == "FTSE":
                self.data["ftse_prediction"] = prediction_data
            else:
                self.data["sp500_prediction"] = prediction_data

            _LOGGER.info(
                "%s prediction: %s (%.1f%% confidence)",
                market_name,
                prediction,
                confidence
            )

        except Exception as err:
            _LOGGER.error("Error fetching data for %s: %s", market_name, err)
            raise

    async def async_manual_prediction(self):
        """Run manual prediction for both markets."""
        _LOGGER.info("Running manual prediction for both markets")

        # Check if we have enough API calls left
        av_calls_left = ALPHAVANTAGE_DAILY_LIMIT - self.rate_limiter.call_counts.get("alphavantage", 0)

        if av_calls_left < 2:
            raise UpdateFailed("Not enough API calls remaining for manual prediction")

        # Update both markets
        await self._update_market_prediction("FTSE", FTSE_SYMBOL)
        await self._update_market_prediction("SP500", SP500_SYMBOL)

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from API endpoint."""
        # This is called by the default update interval
        # For our use case, we mainly rely on scheduled updates
        # But we can use this for general status updates

        self.data["api_usage"] = {
            "alphavantage": self.rate_limiter.call_counts.get("alphavantage", 0),
            "fmp": self.rate_limiter.call_counts.get("fmp", 0),
        }

        return self.data
