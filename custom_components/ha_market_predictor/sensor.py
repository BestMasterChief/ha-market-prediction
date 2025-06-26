"""Market prediction sensor platform."""
from __future__ import annotations

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


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Market Prediction sensors from a config entry."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = [
        MarketPredictionSensor(
            coordinator,
            "s_p_500_prediction",
            "S&P 500 Prediction",
            "mdi:trending-up",
        ),
        MarketPredictionSensor(
            coordinator,
            "ftse_100_prediction", 
            "FTSE 100 Prediction",
            "mdi:trending-down",
        ),
        MarketProgressSensor(
            coordinator,
            "market_prediction_progress",
            "Market Prediction Progress",
            "mdi:progress-clock",
        ),
        MarketStatusSensor(
            coordinator,
            "market_prediction_status",
            "Market Prediction Status",
            "mdi:information",
        ),
        MarketCurrentSourceSensor(
            coordinator,
            "market_prediction_current_source",
            "Market Prediction Current Source",
            "mdi:newspaper",
        ),
        MarketProcessingTimeSensor(
            coordinator,
            "market_prediction_processing_time",
            "Market Prediction Processing Time",
            "mdi:timer",
        ),
    ]

    async_add_entities(entities)


class MarketPredictionSensor(CoordinatorEntity, SensorEntity):
    """Representation of a market prediction sensor."""

    def __init__(
        self,
        coordinator: MarketPredictionCoordinator,
        sensor_type: str,
        name: str,
        icon: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._attr_name = name
        self._attr_icon = icon
        self._attr_unique_id = f"{DOMAIN}_{sensor_type}"
        self._attr_device_info = coordinator.device_info

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None
        
        prediction_data = self.coordinator.data.get(self._sensor_type)
        if not prediction_data:
            return "No prediction data available"
        
        direction = prediction_data.get("direction", "FLAT")
        percentage = prediction_data.get("percentage", 0.0)
        
        if direction == "FLAT":
            return "FLAT 0.0%"
        return f"{direction} {percentage:.1f}%"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        if not self.coordinator.data:
            return {}
        
        prediction_data = self.coordinator.data.get(self._sensor_type, {})
        return {
            "direction": prediction_data.get("direction", "FLAT"),
            "percentage": prediction_data.get("percentage", 0.0),
            "confidence": prediction_data.get("confidence", 0),
            "explanation": prediction_data.get("explanation", ""),
            "last_updated": prediction_data.get("last_updated"),
            "technical_score": prediction_data.get("technical_score", 0),
            "sentiment_score": prediction_data.get("sentiment_score", 0),
        }

    @property
    def icon(self) -> str:
        """Return the icon based on prediction direction."""
        if not self.coordinator.data:
            return "mdi:help-circle"
        
        prediction_data = self.coordinator.data.get(self._sensor_type, {})
        direction = prediction_data.get("direction", "FLAT")
        
        if direction == "UP":
            return "mdi:trending-up"
        elif direction == "DOWN":
            return "mdi:trending-down"
        return "mdi:trending-neutral"


class MarketProgressSensor(CoordinatorEntity, SensorEntity):
    """Sensor for market prediction progress tracking."""

    def __init__(
        self,
        coordinator: MarketPredictionCoordinator,
        sensor_type: str,
        name: str,
        icon: str,
    ) -> None:
        """Initialize the progress sensor."""
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._attr_name = name
        self._attr_icon = icon
        self._attr_unique_id = f"{DOMAIN}_{sensor_type}"
        self._attr_device_info = coordinator.device_info
        self._attr_native_unit_of_measurement = "%"
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> int | None:
        """Return the progress percentage."""
        if not self.coordinator.data:
            return 0
        return self.coordinator.data.get("progress", 0)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional progress attributes."""
        if not self.coordinator.data:
            return {}
        
        return {
            "status": self.coordinator.data.get("status", "Idle"),
            "eta": self.coordinator.data.get("eta"),
            "current_stage": self.coordinator.data.get("current_stage", ""),
            "last_updated": self.coordinator.data.get("last_updated"),
        }


class MarketStatusSensor(CoordinatorEntity, SensorEntity):
    """Sensor for market prediction status."""

    def __init__(
        self,
        coordinator: MarketPredictionCoordinator,
        sensor_type: str,
        name: str,
        icon: str,
    ) -> None:
        """Initialize the status sensor."""
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._attr_name = name
        self._attr_icon = icon
        self._attr_unique_id = f"{DOMAIN}_{sensor_type}"
        self._attr_device_info = coordinator.device_info

    @property
    def native_value(self) -> str | None:
        """Return the current status."""
        if not self.coordinator.data:
            return "Idle"
        return self.coordinator.data.get("status", "Idle")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional status attributes."""
        if not self.coordinator.data:
            return {}
        
        return {
            "progress": self.coordinator.data.get("progress", 0),
            "current_stage": self.coordinator.data.get("current_stage", ""),
            "last_error": self.coordinator.data.get("last_error"),
            "last_updated": self.coordinator.data.get("last_updated"),
        }


class MarketCurrentSourceSensor(CoordinatorEntity, SensorEntity):
    """Sensor for current source being analyzed."""

    def __init__(
        self,
        coordinator: MarketPredictionCoordinator,
        sensor_type: str,
        name: str,
        icon: str,
    ) -> None:
        """Initialize the current source sensor."""
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._attr_name = name
        self._attr_icon = icon
        self._attr_unique_id = f"{DOMAIN}_{sensor_type}"
        self._attr_device_info = coordinator.device_info

    @property
    def native_value(self) -> str | None:
        """Return the current source being processed."""
        if not self.coordinator.data:
            return "None"
        return self.coordinator.data.get("current_source", "None")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional source attributes."""
        if not self.coordinator.data:
            return {}
        
        return {
            "source_progress": self.coordinator.data.get("source_progress", ""),
            "sources_processed": self.coordinator.data.get(
                "sources_processed", 0
            ),
            "total_sources": self.coordinator.data.get("total_sources", 0),
            "last_updated": self.coordinator.data.get("last_updated"),
        }


class MarketProcessingTimeSensor(CoordinatorEntity, SensorEntity):
    """Sensor for total processing time."""

    def __init__(
        self,
        coordinator: MarketPredictionCoordinator,
        sensor_type: str,
        name: str,
        icon: str,
    ) -> None:
        """Initialize the processing time sensor."""
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._attr_name = name
        self._attr_icon = icon
        self._attr_unique_id = f"{DOMAIN}_{sensor_type}"
        self._attr_device_info = coordinator.device_info
        self._attr_native_unit_of_measurement = "minutes"
        self._attr_device_class = SensorDeviceClass.DURATION
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> float | None:
        """Return the processing time in minutes."""
        if not self.coordinator.data:
            return 0.0
        
        processing_time = self.coordinator.data.get("processing_time", 0.0)
        if isinstance(processing_time, (int, float)):
            return round(processing_time, 1)
        return 0.0

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional processing time attributes."""
        if not self.coordinator.data:
            return {}
        
        return {
            "eta": self.coordinator.data.get("eta"),
            "start_time": self.coordinator.data.get("start_time"),
            "end_time": self.coordinator.data.get("end_time"),
            "last_updated": self.coordinator.data.get("last_updated"),
        }