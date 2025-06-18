"""Sensor platform for Market Prediction."""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    SENSOR_PREDICTION_SP500,
    SENSOR_PREDICTION_FTSE,
    SENSOR_PROGRESS,
    SENSOR_STATUS,
)
from .coordinator import MarketPredictionDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

SENSOR_DESCRIPTIONS: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="sp500_prediction",
        name=SENSOR_PREDICTION_SP500,
        icon="mdi:trending-up",
        native_unit_of_measurement=PERCENTAGE,
    ),
    SensorEntityDescription(
        key="ftse_prediction",
        name=SENSOR_PREDICTION_FTSE,
        icon="mdi:trending-up",
        native_unit_of_measurement=PERCENTAGE,
    ),
    SensorEntityDescription(
        key="progress",
        name=SENSOR_PROGRESS,
        icon="mdi:progress-clock",
        native_unit_of_measurement=PERCENTAGE,
        device_class=SensorDeviceClass.BATTERY,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="status",
        name=SENSOR_STATUS,
        icon="mdi:information",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = [
        MarketPredictionSensor(coordinator, description)
        for description in SENSOR_DESCRIPTIONS
    ]

    async_add_entities(entities)


class MarketPredictionSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Market Prediction sensor."""

    def __init__(
        self,
        coordinator: MarketPredictionDataUpdateCoordinator,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{DOMAIN}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, coordinator.entry.entry_id)},
            "name": "Market Prediction System",
            "manufacturer": "Home Assistant Community",
            "model": "Market Predictor v2.0",
            "sw_version": "2.0.0",
        }

    @property
    def native_value(self) -> str | float | None:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None

        key = self.entity_description.key
        
        if key == "sp500_prediction":
            prediction = self.coordinator.data.get("sp500_prediction", {})
            direction = prediction.get("direction", "FLAT")
            percentage = prediction.get("percentage", 0)
            
            if direction == "UP":
                return f"UP {percentage}%"
            elif direction == "DOWN":
                return f"DOWN {percentage}%"
            else:
                return "FLAT 0%"
                
        elif key == "ftse_prediction":
            prediction = self.coordinator.data.get("ftse_prediction", {})
            direction = prediction.get("direction", "FLAT")
            percentage = prediction.get("percentage", 0)
            
            if direction == "UP":
                return f"UP {percentage}%"
            elif direction == "DOWN":
                return f"DOWN {percentage}%"
            else:
                return "FLAT 0%"
                
        elif key == "progress":
            return self.coordinator.progress_percentage
            
        elif key == "status":
            return self.coordinator.progress_state.replace("_", " ").title()

        return None

    @property
    def icon(self) -> str:
        """Return the icon to use in the frontend."""
        key = self.entity_description.key
        
        if key in ["sp500_prediction", "ftse_prediction"]:
            if self.coordinator.data:
                prediction_key = key
                prediction = self.coordinator.data.get(prediction_key, {})
                direction = prediction.get("direction", "FLAT")
                
                if direction == "UP":
                    return "mdi:trending-up"
                elif direction == "DOWN":
                    return "mdi:trending-down"
                else:
                    return "mdi:trending-neutral"
        
        return self.entity_description.icon

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes."""
        if not self.coordinator.data:
            return {}

        key = self.entity_description.key
        
        if key == "sp500_prediction":
            prediction = self.coordinator.data.get("sp500_prediction", {})
            return {
                "direction": prediction.get("direction", "UNKNOWN"),
                "percentage": prediction.get("percentage", 0),
                "confidence": prediction.get("confidence", 0),
                "explanation": prediction.get("explanation", "No data available"),
                "technical_score": prediction.get("technical_score", 0),
                "sentiment_score": prediction.get("sentiment_score", 0),
                "last_update": self.coordinator.data.get("last_update"),
            }
            
        elif key == "ftse_prediction":
            prediction = self.coordinator.data.get("ftse_prediction", {})
            return {
                "direction": prediction.get("direction", "UNKNOWN"),
                "percentage": prediction.get("percentage", 0),
                "confidence": prediction.get("confidence", 0),
                "explanation": prediction.get("explanation", "No data available"),
                "technical_score": prediction.get("technical_score", 0),
                "sentiment_score": prediction.get("sentiment_score", 0),
                "last_update": self.coordinator.data.get("last_update"),
            }
            
        elif key == "progress":
            return {
                "state": self.coordinator.progress_state,
                "percentage": self.coordinator.progress_percentage,
                "eta": self.coordinator.data.get("eta"),
                "last_update": self.coordinator.data.get("last_update"),
            }
            
        elif key == "status":
            return {
                "progress_state": self.coordinator.progress_state,
                "progress_percentage": self.coordinator.progress_percentage,
                "eta": self.coordinator.data.get("eta"),
                "last_update": self.coordinator.data.get("last_update"),
                "has_alpha_vantage": bool(self.coordinator._alpha_vantage_key),
                "has_fmp": bool(self.coordinator._fmp_key),
            }

        return {}