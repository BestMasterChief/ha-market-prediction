"""Sensor platform for Market Prediction System."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import MarketPredictionCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Market Prediction sensors from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        MarketPredictionSensor(
            coordinator, "s_p_500_prediction", "S&P 500 Prediction"
        ),
        MarketPredictionSensor(
            coordinator, "ftse_100_prediction", "FTSE 100 Prediction"
        ),
        MarketProgressSensor(coordinator),
        MarketStatusSensor(coordinator),
        MarketCurrentSourceSensor(coordinator),
        MarketProcessingTimeSensor(coordinator),
    ]

    async_add_entities(entities)


class MarketPredictionSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Market Prediction sensor."""

    def __init__(
        self,
        coordinator: MarketPredictionCoordinator,
        prediction_type: str,
        name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._prediction_type = prediction_type
        self._attr_name = name
        self._attr_unique_id = f"{DOMAIN}_{prediction_type}"
        self._attr_icon = "mdi:trending-up"

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return "No prediction data available"

        prediction_data = self.coordinator.data.get(self._prediction_type, {})
        
        if not prediction_data:
            return "No prediction data available"

        direction = prediction_data.get("direction", "FLAT")
        change = prediction_data.get("predicted_change", 0)

        if direction == "FLAT":
            return "FLAT 0.0%"
        else:
            return f"{direction} {abs(change):.1f}%"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        if not self.coordinator.data:
            return {}

        prediction_data = self.coordinator.data.get(self._prediction_type, {})
        
        if not prediction_data:
            return {}

        return {
            "symbol": prediction_data.get("symbol", ""),
            "direction": prediction_data.get("direction", "FLAT"),
            "predicted_change": prediction_data.get("predicted_change", 0),
            "confidence": prediction_data.get("confidence", 0),
            "technical_score": prediction_data.get("technical_score", 0),
            "sentiment_score": prediction_data.get("sentiment_score", 0),
            "final_score": prediction_data.get("final_score", 0),
            "last_update": self.coordinator.data.get("last_update", ""),
        }

    @property
    def icon(self) -> str:
        """Return the icon for the sensor."""
        if not self.coordinator.data:
            return "mdi:help-circle"

        prediction_data = self.coordinator.data.get(self._prediction_type, {})
        direction = prediction_data.get("direction", "FLAT")

        if direction == "UP":
            return "mdi:trending-up"
        elif direction == "DOWN":
            return "mdi:trending-down"
        else:
            return "mdi:trending-neutral"

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            self.coordinator.last_update_success and
            self.coordinator.data is not None and
            self._prediction_type in self.coordinator.data
        )


class MarketProgressSensor(CoordinatorEntity, SensorEntity):
    """Sensor for market prediction progress."""

    def __init__(self, coordinator: MarketPredictionCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "Market Prediction Progress"
        self._attr_unique_id = f"{DOMAIN}_progress"
        self._attr_native_unit_of_measurement = "%"
        self._attr_device_class = SensorDeviceClass.POWER_FACTOR
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_icon = "mdi:progress-clock"

    @property
    def native_value(self) -> float | None:
        """Return the progress value."""
        if hasattr(self.coordinator, 'progress'):
            return round(self.coordinator.progress, 1)
        
        if self.coordinator.data:
            return self.coordinator.data.get("progress", 0)
        
        return 0

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        return {
            "status": getattr(self.coordinator, '_status', 'Unknown'),
            "current_source": getattr(
                self.coordinator, '_current_source', ''
            ),
        }


class MarketStatusSensor(CoordinatorEntity, SensorEntity):
    """Sensor for market prediction status."""

    def __init__(self, coordinator: MarketPredictionCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "Market Prediction Status"
        self._attr_unique_id = f"{DOMAIN}_status"
        self._attr_icon = "mdi:information"

    @property
    def native_value(self) -> str:
        """Return the status value."""
        if hasattr(self.coordinator, 'status'):
            return self.coordinator.status
        
        if self.coordinator.data:
            return self.coordinator.data.get("status", "Unknown")
        
        return "Idle"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        return {
            "progress": getattr(self.coordinator, '_progress', 0),
            "processing_time": getattr(
                self.coordinator, '_processing_time', 0
            ),
        }


class MarketCurrentSourceSensor(CoordinatorEntity, SensorEntity):
    """Sensor for current source being processed."""

    def __init__(self, coordinator: MarketPredictionCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "Market Prediction Current Source"
        self._attr_unique_id = f"{DOMAIN}_current_source"
        self._attr_icon = "mdi:newspaper"

    @property
    def native_value(self) -> str:
        """Return the current source being processed."""
        if hasattr(self.coordinator, 'current_source'):
            return self.coordinator.current_source or "None"
        
        if self.coordinator.data:
            return self.coordinator.data.get("current_source", "None")
        
        return "None"


class MarketProcessingTimeSensor(CoordinatorEntity, SensorEntity):
    """Sensor for processing time."""

    def __init__(self, coordinator: MarketPredictionCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "Market Prediction Processing Time"
        self._attr_unique_id = f"{DOMAIN}_processing_time"
        self._attr_native_unit_of_measurement = "s"
        self._attr_device_class = SensorDeviceClass.DURATION
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_icon = "mdi:timer"

    @property
    def native_value(self) -> float | None:
        """Return the processing time in seconds."""
        if hasattr(self.coordinator, 'processing_time'):
            return round(self.coordinator.processing_time, 1)
        
        if self.coordinator.data:
            return self.coordinator.data.get("processing_time", 0)
        
        return 0