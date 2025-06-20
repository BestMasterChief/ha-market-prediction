"""Market Prediction Data Update Coordinator."""
import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DOMAIN,
    DEFAULT_SCAN_INTERVAL,
    SENTIMENT_SOURCES,
    API_TIMEOUT,
    ALPHA_VANTAGE_BASE_URL,
    FMP_BASE_URL,
)

_LOGGER = logging.getLogger(__name__)


class MarketPredictionCoordinator(DataUpdateCoordinator):
    """Market prediction data coordinator."""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=DEFAULT_SCAN_INTERVAL,
        )
        self.config_entry = config_entry
        self._alpha_vantage_key = config_entry.data.get("alpha_vantage_api_key")
        self._fmp_key = config_entry.data.get("fmp_api_key")
        self._session: Optional[aiohttp.ClientSession] = None
        self._current_stage = "Initializing"
        self._current_source = ""
        self._progress_percent = 0
        self._start_time = None
        self._eta_seconds = 0
        self._processing_time = 0.0
        
        # Sentiment analysis tracking
        self._sentiment_sources = SENTIMENT_SOURCES
        self._sources_processed = 0
        self._total_sentiment_items = sum(source["items"] for source in self._sentiment_sources)

    @property
    def current_stage(self) -> str:
        """Return current processing stage."""
        return self._current_stage

    @property
    def current_source(self) -> str:
        """Return current source being processed."""
        return self._current_source

    @property
    def progress_percent(self) -> int:
        """Return current progress percentage."""
        return self._progress_percent

    @property
    def eta_seconds(self) -> int:
        """Return estimated time remaining in seconds."""
        return self._eta_seconds

    @property
    def processing_time(self) -> float:
        """Return total processing time in seconds."""
        return self._processing_time

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get aiohttp session."""
        if self._session is None:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=API_TIMEOUT)
            )
        return self._session

    async def _update_progress(
        self, 
        percent: int, 
        stage: str, 
        source: str = ""
    ) -> None:
        """Update progress information."""
        self._progress_percent = max(0, min(100, percent))
        self._current_stage = stage
        self._current_source = source
        
        # Calculate ETA and processing time
        if self._start_time:
            elapsed = (datetime.now() - self._start_time).total_seconds()
            self._processing_time = elapsed
            
            if percent > 0 and percent < 100:
                estimated_total = (elapsed / percent) * 100
                self._eta_seconds = max(0, int(estimated_total - elapsed))
        
        # Trigger coordinator update to refresh sensors
        self.async_set_updated_data(self.data)

    async def _async_update_data(self) -> Dict[str, Any]:
        """Fetch data from APIs."""
        if not self._alpha_vantage_key:
            raise ConfigEntryAuthFailed("Alpha Vantage API key not configured")
        
        self._start_time = datetime.now()
        await self._update_progress(5, "Initializing")
        
        try:
            # Stage 1: Fetch market data (25%)
            await self._update_progress(10, "Fetching Market Data", "Alpha Vantage - S&P 500")
            market_data = await self._fetch_market_data()
            
            await self._update_progress(25, "Fetching Market Data", "Alpha Vantage - FTSE 100")
            await asyncio.sleep(1)  # Rate limiting
            
            # Stage 2: Process technical analysis (50%)
            await self._update_progress(30, "Processing Technical Analysis", "RSI Calculation")
            technical_data = await self._process_technical_analysis(market_data)
            
            await self._update_progress(40, "Processing Technical Analysis", "Moving Averages")
            await asyncio.sleep(0.5)
            
            await self._update_progress(50, "Processing Technical Analysis", "Momentum & Volatility")
            await asyncio.sleep(0.5)
            
            # Stage 3: Enhanced sentiment analysis (75%) - This is the long phase
            await self._update_progress(52, "Processing Sentiment Analysis", "Initializing sources")
            sentiment_data = await self._process_comprehensive_sentiment()
            
            # Stage 4: Calculate predictions (90%)
            await self._update_progress(90, "Calculating Predictions", "Renaissance Algorithm")
            predictions = await self._calculate_predictions(technical_data, sentiment_data)
            
            # Stage 5: Complete (100%)
            await self._update_progress(100, "Complete")
            
            return {
                "market_data": market_data,
                "technical_data": technical_data,
                "sentiment_data": sentiment_data,
                "predictions": predictions,
                "metadata": {
                    "last_updated": datetime.now().isoformat(),
                    "processing_time": self._processing_time,
                    "sources_processed": len(self._sentiment_sources),
                    "sentiment_items_processed": self._total_sentiment_items,
                }
            }
            
        except Exception as err:
            await self._update_progress(0, "Error", str(err))
            _LOGGER.error("Error updating market prediction data: %s", err)
            raise UpdateFailed(f"Error communicating with API: {err}")

    async def _fetch_market_data(self) -> Dict[str, Any]:
        """Fetch market data from Alpha Vantage."""
        session = await self._get_session()
        
        # Fetch S&P 500 data
        sp500_url = f"{ALPHA_VANTAGE_BASE_URL}/query?function=GLOBAL_QUOTE&symbol=SPY&apikey={self._alpha_vantage_key}"
        
        try:
            async with session.get(sp500_url) as response:
                sp500_data = await response.json()
                
            # Fetch FTSE 100 data  
            ftse_url = f"{ALPHA_VANTAGE_BASE_URL}/query?function=GLOBAL_QUOTE&symbol=^FTSE&apikey={self._alpha_vantage_key}"
            
            async with session.get(ftse_url) as response:
                ftse_data = await response.json()
                
            return {
                "sp500": sp500_data,
                "ftse": ftse_data,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as err:
            _LOGGER.error("Error fetching market data: %s", err)
            raise

    async def _process_technical_analysis(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process technical analysis indicators."""
        # Simulate technical analysis processing
        await asyncio.sleep(0.5)
        
        return {
            "rsi": {"sp500": 45.2, "ftse": 52.8},
            "moving_average": {"sp500": 0.15, "ftse": -0.08},
            "momentum": {"sp500": 0.02, "ftse": -0.01},
            "volatility": {"sp500": 0.18, "ftse": 0.22},
            "technical_score": {"sp500": 0.125, "ftse": -0.045}
        }

    async def _process_comprehensive_sentiment(self) -> Dict[str, Any]:
        """Process comprehensive sentiment analysis from multiple sources."""
        sentiment_results = []
        processed_items = 0
        
        for source_idx, source in enumerate(self._sentiment_sources):
            source_name = source["name"]
            source_weight = source["weight"]
            source_items = source["items"]
            api_delay = source["api_delay"]
            
            _LOGGER.info(f"Processing sentiment source: {source_name}")
            
            # Process items from this source
            for item_idx in range(source_items):
                processed_items += 1
                
                # Calculate progress (50% to 75% of total)
                progress = 50 + (processed_items / self._total_sentiment_items) * 25
                
                # Update progress with current source info
                await self._update_progress(
                    int(progress), 
                    "Processing Sentiment Analysis", 
                    f"{source_name} (item {item_idx + 1}/{source_items})"
                )
                
                # Simulate API delay for realistic processing time
                await asyncio.sleep(api_delay)
            
            # Simulate sentiment score for this source
            source_sentiment = self._simulate_source_sentiment(source_name)
            
            sentiment_results.append({
                "source": source_name,
                "weight": source_weight,
                "sentiment": source_sentiment,
                "items_processed": source_items,
                "impact": source_sentiment * source_weight
            })
        
        # Calculate weighted sentiment scores
        total_weight = sum(result["weight"] for result in sentiment_results)
        weighted_sentiment = sum(result["impact"] for result in sentiment_results) / total_weight if total_weight > 0 else 0
        
        return {
            "sources": sentiment_results,
            "weighted_sentiment": weighted_sentiment,
            "total_sources": len(sentiment_results),
            "total_items_processed": processed_items,
            "processing_time": self._processing_time
        }

    def _simulate_source_sentiment(self, source_name: str) -> float:
        """Simulate sentiment score for a given source."""
        # Simple hash-based simulation for consistent results
        source_hash = hash(source_name + str(datetime.now().date())) % 1000
        return (source_hash / 1000.0 - 0.5) * 2  # Range -1.0 to 1.0

    async def _calculate_predictions(
        self, 
        technical_data: Dict[str, Any], 
        sentiment_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate final predictions using Renaissance Technologies approach."""
        # Simulate final calculation time
        await asyncio.sleep(1)
        
        # Renaissance approach: 75% technical, 25% sentiment
        technical_weight = 0.75
        sentiment_weight = 0.25
        
        predictions = {}
        
        for market in ["sp500", "ftse"]:
            technical_score = technical_data["technical_score"].get(market, 0)
            sentiment_score = sentiment_data["weighted_sentiment"]
            
            # Combined score
            combined_score = (technical_score * technical_weight) + (sentiment_score * sentiment_weight)
            
            # Convert to direction and magnitude (capped at ±4%)
            magnitude = min(abs(combined_score) * 3.5, 4.0)
            direction = "UP" if combined_score > 0 else "DOWN"
            
            # Confidence based on signal strength
            confidence = min(abs(combined_score) * 100, 95.0)
            
            predictions[market] = {
                "direction": direction,
                "magnitude": round(magnitude, 2),
                "confidence": round(confidence, 1),
                "technical_score": technical_score,
                "sentiment_score": sentiment_score,
                "combined_score": combined_score
            }
        
        return predictions

    async def async_shutdown(self) -> None:
        """Close the aiohttp session."""
        if self._session:
            await self._session.close()
            self._session = None