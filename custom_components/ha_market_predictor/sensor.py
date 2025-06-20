"""Sensor platform for HA Market Predictor."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .coordinator import MarketPredictorCoordinator

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = [
        FTSEPredictionSensor(coordinator),
        SP500PredictionSensor(coordinator),
        APIUsageSensor(coordinator),
    ]

    async_add_entities(entities)

class MarketPredictorSensorBase(CoordinatorEntity, SensorEntity):
    """Base class for market predictor sensors."""

    def __init__(self, coordinator: MarketPredictorCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_device_info = {
            "identifiers": {(DOMAIN, "market_predictor")},
            "name": "HA Market Predictor",
            "manufacturer": "HA Market Predictor",
            "model": "Market Prediction System",
            "sw_version": "1.0.0",
        }

class FTSEPredictionSensor(MarketPredictorSensorBase):
    """FTSE prediction sensor."""

    def __init__(self, coordinator: MarketPredictorCoordinator) -> None:
        """Initialize the FTSE prediction sensor."""
        super().__init__(coordinator)
        self._attr_name = "FTSE Prediction"
        self._attr_unique_id = f"{DOMAIN}_ftse_prediction"
        self._attr_icon = "mdi:trending-up"

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        if self.coordinator.data and self.coordinator.data.get("ftse_prediction"):
            return self.coordinator.data["ftse_prediction"]["prediction"]
        return None

    @property
    def extra_state_attributes(self) -> dict[str, any] | None:
        """Return extra state attributes."""
        if self.coordinator.data and self.coordinator.data.get("ftse_prediction"):
            data = self.coordinator.data["ftse_prediction"]
            return {
                "confidence": data.get("confidence"),
                "current_price": data.get("current_price"),
                "momentum": data.get("momentum"),
                "last_updated": data.get("timestamp"),
            }
        return None

class SP500PredictionSensor(MarketPredictorSensorBase):
    """S&P 500 prediction sensor."""

    def __init__(self, coordinator: MarketPredictorCoordinator) -> None:
        """Initialize the S&P 500 prediction sensor."""
        super().__init__(coordinator)
        self._attr_name = "S&P 500 Prediction"
        self._attr_unique_id = f"{DOMAIN}_sp500_prediction"
        self._attr_icon = "mdi:trending-up"

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        if self.coordinator.data and self.coordinator.data.get("sp500_prediction"):
            return self.coordinator.data["sp500_prediction"]["prediction"]
        return None

    @property
    def extra_state_attributes(self) -> dict[str, any] | None:
        """Return extra state attributes."""
        if self.coordinator.data and self.coordinator.data.get("sp500_prediction"):
            data = self.coordinator.data["sp500_prediction"]
            return {
                "confidence": data.get("confidence"),
                "current_price": data.get("current_price"),
                "momentum": data.get("momentum"),
                "last_updated": data.get("timestamp"),
            }
        return None

class APIUsageSensor(MarketPredictorSensorBase):
    """API usage tracking sensor."""

    def __init__(self, coordinator: MarketPredictorCoordinator) -> None:
        """Initialize the API usage sensor."""
        super().__init__(coordinator)
        self._attr_name = "API Usage Today"
        self._attr_unique_id = f"{DOMAIN}_api_usage"
        self._attr_icon = "mdi:api"
        self._attr_native_unit_of_measurement = "calls"

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        if self.coordinator.data and self.coordinator.data.get("api_usage"):
            return self.coordinator.data["api_usage"].get("alphavantage", 0)
        return 0

    @property
    def extra_state_attributes(self) -> dict[str, any] | None:
        """Return extra state attributes."""
        if self.coordinator.data and self.coordinator.data.get("api_usage"):
            usage = self.coordinator.data["api_usage"]
            return {
                "alphavantage_calls": usage.get("alphavantage", 0),
                "alphavantage_limit": 25,
                "fmp_calls": usage.get("fmp", 0),
                "fmp_limit": 250,
                "last_update": self.coordinator.data.get("last_update"),
            }
        return None
