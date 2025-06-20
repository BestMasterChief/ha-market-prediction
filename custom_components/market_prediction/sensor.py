"""Sensor platform for Market Prediction integration."""
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    UNIQUE_ID_SP500,
    UNIQUE_ID_FTSE100,
    UNIQUE_ID_PROGRESS,
    UNIQUE_ID_STATUS,
    UNIQUE_ID_CURRENT_SOURCE,
    UNIQUE_ID_PROCESSING_TIME,
)
from .coordinator import MarketPredictionCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator: MarketPredictionCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = [
        MarketPredictionSensor(coordinator, "sp500", "S&P 500", UNIQUE_ID_SP500),
        MarketPredictionSensor(coordinator, "ftse100", "FTSE 100", UNIQUE_ID_FTSE100),
        MarketPredictionProgressSensor(coordinator),
        MarketPredictionStatusSensor(coordinator),
        MarketPredictionCurrentSourceSensor(coordinator),
        MarketPredictionProcessingTimeSensor(coordinator),
    ]

    async_add_entities(entities)


class MarketPredictionSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Market Prediction sensor."""

    def __init__(
        self,
        coordinator: MarketPredictionCoordinator,
        market_key: str,
        market_name: str,
        unique_id: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._market_key = market_key
        self._market_name = market_name
        self._attr_unique_id = unique_id
        self._attr_name = f"Market Prediction {market_name}"
        self._attr_icon = "mdi:chart-line"

    @property
    def native_value(self) -> Optional[str]:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return "No prediction data available"

        market_data = self.coordinator.data.get(self._market_key)
        if not market_data:
            return "No prediction data available"

        return market_data.get("state", "Unknown")

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            self.coordinator.last_update_success
            and self.coordinator.data is not None
            and self._market_key in self.coordinator.data
        )

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return the state attributes."""
        if not self.coordinator.data or self._market_key not in self.coordinator.data:
            return {}

        market_data = self.coordinator.data[self._market_key]
        attrs = {
            "direction": market_data.get("direction", "FLAT"),
            "percentage": market_data.get("percentage", 0),
            "confidence": f"{market_data.get('confidence', 0):.1f}%",
            "technical_score": f"{market_data.get('technical_score', 0):.3f}",
            "sentiment_score": f"{market_data.get('sentiment_score', 0):.3f}",
            "last_update": market_data.get("last_update"),
            "market": self._market_name,
        }

        # Add technical details if available
        technical_details = market_data.get("technical_details", {})
        if technical_details:
            attrs.update({
                "rsi": f"{technical_details.get('rsi', 50):.1f}",
                "moving_average_signal": f"{technical_details.get('ma_signal', 0):.3f}",
                "momentum": f"{technical_details.get('momentum', 0):.3f}",
                "volatility": f"{technical_details.get('volatility', 0):.3f}",
            })

        return attrs

    @property
    def icon(self) -> str:
        """Return the icon of the sensor."""
        if not self.coordinator.data or self._market_key not in self.coordinator.data:
            return "mdi:chart-line"

        market_data = self.coordinator.data[self._market_key]
        direction = market_data.get("direction", "FLAT")

        if direction == "UP":
            return "mdi:trending-up"
        elif direction == "DOWN":
            return "mdi:trending-down"
        else:
            return "mdi:chart-line"


class MarketPredictionProgressSensor(CoordinatorEntity, SensorEntity):
    """Sensor for tracking prediction analysis progress."""

    def __init__(self, coordinator: MarketPredictionCoordinator) -> None:
        """Initialize the progress sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = UNIQUE_ID_PROGRESS
        self._attr_name = "Market Prediction Progress"
        self._attr_icon = "mdi:progress-check"
        self._attr_native_unit_of_measurement = "%"

    @property
    def native_value(self) -> int:
        """Return the progress percentage."""
        return self.coordinator.progress

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return progress attributes."""
        return {
            "status": self.coordinator.status,
            "current_source": self.coordinator.current_source,
            "eta_seconds": self.coordinator.eta_seconds,
            "eta_formatted": f"{int(self.coordinator.eta_seconds // 60)}:{int(self.coordinator.eta_seconds % 60):02d}",
        }


class MarketPredictionStatusSensor(CoordinatorEntity, SensorEntity):
    """Sensor for tracking prediction analysis status."""

    def __init__(self, coordinator: MarketPredictionCoordinator) -> None:
        """Initialize the status sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = UNIQUE_ID_STATUS
        self._attr_name = "Market Prediction Status"
        self._attr_icon = "mdi:information"

    @property
    def native_value(self) -> str:
        """Return the current status."""
        return self.coordinator.status

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return status attributes."""
        attrs = {
            "progress": self.coordinator.progress,
            "current_source": self.coordinator.current_source,
        }

        if self.coordinator.data:
            attrs.update({
                "last_update": self.coordinator.data.get("last_update"),
                "processing_time": f"{self.coordinator.data.get('processing_time', 0):.1f}s",
            })

        return attrs


class MarketPredictionCurrentSourceSensor(CoordinatorEntity, SensorEntity):
    """Sensor for tracking current data source being processed."""

    def __init__(self, coordinator: MarketPredictionCoordinator) -> None:
        """Initialize the current source sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = UNIQUE_ID_CURRENT_SOURCE
        self._attr_name = "Market Prediction Current Source"
        self._attr_icon = "mdi:database"

    @property
    def native_value(self) -> str:
        """Return the current source being processed."""
        return self.coordinator.current_source or "Idle"

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return current source attributes."""
        return {
            "status": self.coordinator.status,
            "progress": self.coordinator.progress,
        }


class MarketPredictionProcessingTimeSensor(CoordinatorEntity, SensorEntity):
    """Sensor for tracking processing time."""

    def __init__(self, coordinator: MarketPredictionCoordinator) -> None:
        """Initialize the processing time sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = UNIQUE_ID_PROCESSING_TIME
        self._attr_name = "Market Prediction Processing Time"
        self._attr_icon = "mdi:timer"
        self._attr_native_unit_of_measurement = "s"
        self._attr_device_class = SensorDeviceClass.DURATION

    @property
    def native_value(self) -> Optional[float]:
        """Return the processing time in seconds."""
        if self.coordinator.data:
            return self.coordinator.data.get("processing_time")
        elif self.coordinator.processing_start_time:
            return (datetime.now() - self.coordinator.processing_start_time).total_seconds()
        return None

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return processing time attributes."""
        attrs = {
            "status": self.coordinator.status,
            "progress": self.coordinator.progress,
        }

        if self.coordinator.processing_start_time:
            attrs["started_at"] = self.coordinator.processing_start_time.isoformat()

        if self.coordinator.eta_seconds > 0:
            attrs.update({
                "eta_seconds": self.coordinator.eta_seconds,
                "eta_formatted": f"{int(self.coordinator.eta_seconds // 60)}:{int(self.coordinator.eta_seconds % 60):02d}",
            })

        return attrs