"""
Enhanced Market Prediction Sensors v2.2.0
Provides comprehensive progress tracking and current source display
"""
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import MarketPredictionCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Market Prediction sensors."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    entities = [
        # Market prediction sensors
        MarketPredictionSensor(coordinator, "sp500", "S&P 500"),
        MarketPredictionSensor(coordinator, "ftse", "FTSE 100"),
        
        # Enhanced progress tracking sensors  
        MarketProgressSensor(coordinator),
        MarketStatusSensor(coordinator),
        CurrentSourceSensor(coordinator),
        ProcessingTimeSensor(coordinator),
    ]
    
    async_add_entities(entities)

class MarketPredictionSensor(CoordinatorEntity, SensorEntity):
    """Sensor for market predictions with enhanced attributes."""

    def __init__(self, coordinator: MarketPredictionCoordinator, market: str, display_name: str):
        super().__init__(coordinator)
        self.market = market
        self.display_name = display_name
        self._attr_name = f"Market Prediction {display_name}"
        self._attr_unique_id = f"market_prediction_{market}"
        self._attr_icon = "mdi:trending-up"

    @property
    def state(self) -> str:
        """Return the state of the sensor."""
        if not self.coordinator.data or "predictions" not in self.coordinator.data:
            return "No prediction data available"
        
        predictions = self.coordinator.data["predictions"]
        if self.market not in predictions:
            return "No prediction data available"
        
        prediction = predictions[self.market]
        direction = prediction.get("direction", "UNKNOWN")
        magnitude = prediction.get("magnitude", 0)
        
        return f"{direction} {magnitude:.2f}%"

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return additional state attributes."""
        if not self.coordinator.data or "predictions" not in self.coordinator.data:
            return {
                "status": "waiting_for_data",
                "market": self.display_name,
                "last_updated": None
            }
        
        predictions = self.coordinator.data["predictions"]
        if self.market not in predictions:
            return {
                "status": "no_prediction_available",
                "market": self.display_name,
                "last_updated": self.coordinator.data.get("last_updated")
            }
        
        prediction = predictions[self.market]
        sentiment_data = self.coordinator.data.get("sentiment_analysis", {})
        technical_data = self.coordinator.data.get("technical_analysis", {})
        
        # Get top contributing sentiment sources
        sources = sentiment_data.get("sources", [])
        top_sources = sorted(
            sources,
            key=lambda x: abs(x.get("sentiment_score", 0) * x.get("weight", 0)),
            reverse=True
        )[:3]
        
        attributes = {
            "market": self.display_name,
            "direction": prediction.get("direction"),
            "magnitude": round(prediction.get("magnitude", 0), 2),
            "confidence": round(prediction.get("confidence", 0), 1),
            "technical_score": round(prediction.get("technical_score", 0), 4),
            "sentiment_score": round(prediction.get("sentiment_score", 0), 4),
            "combined_score": round(prediction.get("combined_score", 0), 4),
            "last_updated": self.coordinator.data.get("last_updated"),
            "sentiment_sources_processed": sentiment_data.get("total_sources", 0),
            "sentiment_processing_time": round(sentiment_data.get("processing_time", 0), 1),
            "top_sentiment_sources": [
                {
                    "source": s.get("source", "Unknown"),
                    "sentiment": round(s.get("sentiment_score", 0), 3),
                    "weight": s.get("weight", 0),
                    "impact": round(abs(s.get("sentiment_score", 0) * s.get("weight", 0)), 3)
                }
                for s in top_sources
            ]
        }
        
        # Add technical analysis details if available
        if technical_data and self.market in technical_data:
            tech_market_data = technical_data[self.market]
            attributes.update({
                "rsi": round(tech_market_data.get("rsi", 0), 1),
                "moving_average_signal": round(tech_market_data.get("ma_signal", 0), 3),
                "momentum": round(tech_market_data.get("momentum", 0), 3),
                "volatility": round(tech_market_data.get("volatility", 0), 3)
            })
        
        return attributes

    @property
    def icon(self) -> str:
        """Return the icon based on prediction direction."""
        if not self.coordinator.data or "predictions" not in self.coordinator.data:
            return "mdi:help-circle"
        
        predictions = self.coordinator.data["predictions"]
        if self.market not in predictions:
            return "mdi:help-circle"
        
        direction = predictions[self.market].get("direction", "")
        return "mdi:trending-up" if direction == "UP" else "mdi:trending-down"

class MarketProgressSensor(CoordinatorEntity, SensorEntity):
    """Sensor for tracking analysis progress."""

    def __init__(self, coordinator: MarketPredictionCoordinator):
        super().__init__(coordinator)
        self._attr_name = "Market Prediction Progress"
        self._attr_unique_id = "market_prediction_progress"
        self._attr_icon = "mdi:progress-clock"
        self._attr_unit_of_measurement = "%"

    @property
    def state(self) -> float:
        """Return the progress percentage."""
        if hasattr(self.coordinator, 'progress_percentage'):
            return round(self.coordinator.progress_percentage, 1)
        
        # Fallback to data-based progress
        if self.coordinator.data and "progress" in self.coordinator.data:
            return round(self.coordinator.data["progress"].get("percentage", 0), 1)
        
        return 0

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return progress details."""
        attrs = {
            "stage": getattr(self.coordinator, 'current_stage', 'Unknown'),
            "current_source": getattr(self.coordinator, 'current_source', 'Unknown'),
            "eta_seconds": getattr(self.coordinator, 'eta_seconds', 0),
            "processing_start": getattr(self.coordinator, 'processing_start_time', None)
        }
        
        # Add formatted time estimates
        eta = attrs["eta_seconds"]
        if eta > 0:
            if eta > 60:
                attrs["eta_formatted"] = f"{eta/60:.1f} minutes"
            else:
                attrs["eta_formatted"] = f"{eta:.0f} seconds"
        else:
            attrs["eta_formatted"] = "Complete"
        
        # Add processing time if available
        if attrs["processing_start"]:
            elapsed = (datetime.now() - attrs["processing_start"]).total_seconds()
            if elapsed > 60:
                attrs["processing_time"] = f"{elapsed/60:.1f} minutes"
            else:
                attrs["processing_time"] = f"{elapsed:.0f} seconds"
        
        return attrs

class MarketStatusSensor(CoordinatorEntity, SensorEntity):
    """Sensor for current processing status."""

    def __init__(self, coordinator: MarketPredictionCoordinator):
        super().__init__(coordinator)
        self._attr_name = "Market Prediction Status"
        self._attr_unique_id = "market_prediction_status"
        self._attr_icon = "mdi:information"

    @property
    def state(self) -> str:
        """Return the current processing stage."""
        return getattr(self.coordinator, 'current_stage', 'Unknown')

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return status details."""
        return {
            "current_source": getattr(self.coordinator, 'current_source', 'Unknown'),
            "progress": getattr(self.coordinator, 'progress_percentage', 0),
            "stage_detail": f"{getattr(self.coordinator, 'current_stage', 'Unknown')} - {getattr(self.coordinator, 'current_source', 'Unknown')}"
        }

class CurrentSourceSensor(CoordinatorEntity, SensorEntity):
    """Sensor specifically for tracking the current source being processed."""

    def __init__(self, coordinator: MarketPredictionCoordinator):
        super().__init__(coordinator)
        self._attr_name = "Market Prediction Current Source"
        self._attr_unique_id = "market_prediction_current_source"
        self._attr_icon = "mdi:web"

    @property
    def state(self) -> str:
        """Return the current source being processed."""
        current_source = getattr(self.coordinator, 'current_source', 'Unknown')
        
        # If we're in sentiment analysis, show more detail
        if hasattr(self.coordinator, 'current_stage'):
            stage = self.coordinator.current_stage
            if "Sentiment" in stage and current_source != "Unknown":
                return current_source
        
        return current_source

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return source processing details."""
        attrs = {
            "processing_stage": getattr(self.coordinator, 'current_stage', 'Unknown'),
            "progress_percentage": getattr(self.coordinator, 'progress_percentage', 0)
        }
        
        # Add sentiment source details if available
        if hasattr(self.coordinator, 'sentiment_sources'):
            current_source = getattr(self.coordinator, 'current_source', '')
            
            for source in self.coordinator.sentiment_sources:
                if source["name"] == current_source:
                    attrs.update({
                        "source_weight": source["weight"],
                        "source_items": source["items"],
                        "source_api_delay": source["api_delay"]
                    })
                    break
        
        return attrs

class ProcessingTimeSensor(CoordinatorEntity, SensorEntity):
    """Sensor for tracking total processing time."""

    def __init__(self, coordinator: MarketPredictionCoordinator):
        super().__init__(coordinator)
        self._attr_name = "Market Prediction Processing Time"
        self._attr_unique_id = "market_prediction_processing_time"
        self._attr_icon = "mdi:clock"
        self._attr_unit_of_measurement = "s"

    @property
    def state(self) -> float:
        """Return the processing time in seconds."""
        if self.coordinator.data and "progress" in self.coordinator.data:
            return round(self.coordinator.data["progress"].get("processing_time", 0), 1)
        
        if hasattr(self.coordinator, 'processing_start_time') and self.coordinator.processing_start_time:
            elapsed = (datetime.now() - self.coordinator.processing_start_time).total_seconds()
            return round(elapsed, 1)
        
        return 0

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return processing time details."""
        processing_time = self.state
        
        attrs = {
            "processing_time_seconds": processing_time,
            "processing_time_minutes": round(processing_time / 60, 2),
            "start_time": getattr(self.coordinator, 'processing_start_time', None)
        }
        
        # Add formatted time
        if processing_time > 60:
            attrs["formatted_time"] = f"{processing_time/60:.1f} minutes"
        else:
            attrs["formatted_time"] = f"{processing_time:.0f} seconds"
        
        # Add sentiment processing breakdown if available
        if self.coordinator.data and "sentiment_analysis" in self.coordinator.data:
            sentiment_time = self.coordinator.data["sentiment_analysis"].get("processing_time", 0)
            attrs.update({
                "sentiment_processing_time": round(sentiment_time, 1),
                "sentiment_time_percentage": round((sentiment_time / processing_time * 100), 1) if processing_time > 0 else 0
            })
        
        return attrs