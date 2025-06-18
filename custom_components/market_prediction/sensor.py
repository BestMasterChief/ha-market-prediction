"""Sensor platform for Market Prediction integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    SUPPORTED_SYMBOLS,
    ATTR_CONFIDENCE,
    ATTR_DIRECTION,
    ATTR_PERCENTAGE,
    ATTR_EXPLANATION,
    ATTR_LAST_UPDATE,
    ATTR_API_CALLS_REMAINING,
)
from .coordinator import MarketPredictionCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    
    entities = []
    
    # Create prediction sensors for each supported market
    for market_name in SUPPORTED_SYMBOLS:
        entities.append(MarketPredictionSensor(coordinator, market_name))
    
    # Create progress and status sensors
    entities.extend([
        MarketProgressSensor(coordinator),
        MarketStatusSensor(coordinator),
    ])
    
    async_add_entities(entities, update_before_add=True)


class MarketPredictionSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Market Prediction sensor."""

    def __init__(self, coordinator: MarketPredictionCoordinator, market_name: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._market_name = market_name
        self._symbol = SUPPORTED_SYMBOLS[market_name]
        
        self._attr_name = f"{market_name} Prediction"
        self._attr_unique_id = f"market_prediction_{market_name.lower().replace(' ', '_').replace('&', 'and')}"
        self._attr_icon = "mdi:trending-up"

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        if not self.coordinator.data or "predictions" not in self.coordinator.data:
            return None
        
        predictions = self.coordinator.data["predictions"]
        if self._market_name not in predictions:
            return None
        
        prediction = predictions[self._market_name]
        direction = prediction.get("direction", "UNKNOWN")
        percentage = prediction.get("percentage", 0)
        
        if direction == "NEUTRAL":
            return "NEUTRAL"
        else:
            return f"{direction} {abs(percentage):.1f}%"

    @property
    def icon(self) -> str:
        """Return the icon of the sensor."""
        if not self.coordinator.data or "predictions" not in self.coordinator.data:
            return "mdi:help"
        
        predictions = self.coordinator.data["predictions"]
        if self._market_name not in predictions:
            return "mdi:help"
        
        direction = predictions[self._market_name].get("direction", "UNKNOWN")
        
        if direction == "UP":
            return "mdi:trending-up"
        elif direction == "DOWN":
            return "mdi:trending-down"
        else:
            return "mdi:trending-neutral"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        if not self.coordinator.data or "predictions" not in self.coordinator.data:
            return {}
        
        predictions = self.coordinator.data["predictions"]
        if self._market_name not in predictions:
            return {}
        
        prediction = predictions[self._market_name]
        
        attributes = {
            ATTR_DIRECTION: prediction.get("direction", "UNKNOWN"),
            ATTR_PERCENTAGE: prediction.get("percentage", 0),
            ATTR_CONFIDENCE: prediction.get("confidence", 0),
            ATTR_EXPLANATION: prediction.get("explanation", "No explanation available"),
            ATTR_LAST_UPDATE: self.coordinator.data.get("last_update"),
            "symbol": self._symbol,
            "market": self._market_name,
        }
        
        # Add API calls remaining info
        if "api_calls_remaining" in self.coordinator.data:
            attributes[ATTR_API_CALLS_REMAINING] = self.coordinator.data["api_calls_remaining"]
        
        return attributes

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return (
            self.coordinator.last_update_success
            and self.coordinator.data is not None
            and "predictions" in self.coordinator.data
            and self._market_name in self.coordinator.data["predictions"]
        )


class MarketProgressSensor(CoordinatorEntity, SensorEntity):
    """Sensor showing the current progress of market prediction analysis."""

    def __init__(self, coordinator: MarketPredictionCoordinator) -> None:
        """Initialize the progress sensor."""
        super().__init__(coordinator)
        
        self._attr_name = "Market Prediction Progress"
        self._attr_unique_id = "market_prediction_progress"
        self._attr_icon = "mdi:progress-clock"
        self._attr_native_unit_of_measurement = "%"
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> int | None:
        """Return the current progress percentage."""
        if hasattr(self.coordinator, 'progress_data'):
            return self.coordinator.progress_data.get("progress", 0)
        elif self.coordinator.data and "progress" in self.coordinator.data:
            return self.coordinator.data["progress"].get("progress", 0)
        return 0

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        attributes = {}
        
        if hasattr(self.coordinator, 'progress_data'):
            progress_data = self.coordinator.progress_data
        elif self.coordinator.data and "progress" in self.coordinator.data:
            progress_data = self.coordinator.data["progress"]
        else:
            progress_data = {"stage": "Unknown", "progress": 0, "eta": None}
        
        attributes.update({
            "stage": progress_data.get("stage", "Unknown"),
            "eta": progress_data.get("eta"),
            "last_update": self.coordinator.data.get("last_update") if self.coordinator.data else None,
        })
        
        return attributes


class MarketStatusSensor(CoordinatorEntity, SensorEntity):
    """Sensor showing the current status of market prediction analysis."""

    def __init__(self, coordinator: MarketPredictionCoordinator) -> None:
        """Initialize the status sensor."""
        super().__init__(coordinator)
        
        self._attr_name = "Market Prediction Status"
        self._attr_unique_id = "market_prediction_status"
        self._attr_icon = "mdi:information"

    @property
    def native_value(self) -> str:
        """Return the current status."""
        if not self.coordinator.last_update_success:
            return "Error"
        
        if hasattr(self.coordinator, 'progress_data'):
            stage = self.coordinator.progress_data.get("stage", "Unknown")
            progress = self.coordinator.progress_data.get("progress", 0)
        elif self.coordinator.data and "progress" in self.coordinator.data:
            stage = self.coordinator.data["progress"].get("stage", "Unknown")
            progress = self.coordinator.data["progress"].get("progress", 0)
        else:
            return "Unknown"
        
        if progress == 100:
            return "Ready"
        else:
            return f"{stage} ({progress}%)"

    @property
    def icon(self) -> str:
        """Return the icon based on status."""
        if not self.coordinator.last_update_success:
            return "mdi:alert-circle"
        
        if hasattr(self.coordinator, 'progress_data'):
            progress = self.coordinator.progress_data.get("progress", 0)
        elif self.coordinator.data and "progress" in self.coordinator.data:
            progress = self.coordinator.data["progress"].get("progress", 0)
        else:
            return "mdi:help"
        
        if progress == 100:
            return "mdi:check-circle"
        elif progress > 0:
            return "mdi:loading"
        else:
            return "mdi:information"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        attributes = {}
        
        if self.coordinator.data:
            # Add API call information
            if "api_calls_remaining" in self.coordinator.data:
                api_calls = self.coordinator.data["api_calls_remaining"]
                attributes.update({
                    "alpha_vantage_calls_remaining": api_calls.get("alpha_vantage", 0),
                    "fmp_calls_remaining": api_calls.get("fmp", 0),
                })
            
            attributes["last_update"] = self.coordinator.data.get("last_update")
            
            # Add prediction summary
            if "predictions" in self.coordinator.data:
                predictions = self.coordinator.data["predictions"]
                attributes["markets_analyzed"] = len(predictions)
                
                up_count = sum(1 for p in predictions.values() if p.get("direction") == "UP")
                down_count = sum(1 for p in predictions.values() if p.get("direction") == "DOWN")
                neutral_count = len(predictions) - up_count - down_count
                
                attributes.update({
                    "markets_up": up_count,
                    "markets_down": down_count,
                    "markets_neutral": neutral_count,
                })
        
        return attributes

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self.async_write_ha_state()