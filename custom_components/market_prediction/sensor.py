"""Market Prediction sensors."""
import logging
from typing import Any, Dict, Optional

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
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
    coordinator: MarketPredictionCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = [
        MarketPredictionSensor(coordinator, "sp500", "S&P 500"),
        MarketPredictionSensor(coordinator, "ftse", "FTSE 100"),
        MarketProgressSensor(coordinator),
        MarketStatusSensor(coordinator),
        MarketCurrentSourceSensor(coordinator),
        MarketProcessingTimeSensor(coordinator),
    ]

    async_add_entities(entities)


class MarketPredictionSensor(CoordinatorEntity, SensorEntity):
    """Market prediction sensor."""

    def __init__(
        self,
        coordinator: MarketPredictionCoordinator,
        market: str,
        market_name: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._market = market
        self._market_name = market_name
        self._attr_name = f"Market Prediction {market_name}"
        self._attr_unique_id = f"{DOMAIN}_{market}"
        self._attr_icon = "mdi:trending-up"
        self._attr_state_class = None

    @property
    def native_value(self) -> Optional[str]:
        """Return the state of the sensor."""
        if not self.coordinator.data or "predictions" not in self.coordinator.data:
            return "No prediction data available"

        prediction = self.coordinator.data["predictions"].get(self._market)
        if not prediction:
            return "No prediction data available"

        direction = prediction.get("direction", "FLAT")
        magnitude = prediction.get("magnitude", 0)
        
        if direction == "FLAT":
            return "FLAT 0.0%"
        
        return f"{direction} {magnitude}%"

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return additional state attributes."""
        if not self.coordinator.data or "predictions" not in self.coordinator.data:
            return {}

        prediction = self.coordinator.data["predictions"].get(self._market, {})
        metadata = self.coordinator.data.get("metadata", {})
        
        attributes = {
            "direction": prediction.get("direction", "FLAT"),
            "magnitude": prediction.get("magnitude", 0),
            "confidence": prediction.get("confidence", 0),
            "technical_score": prediction.get("technical_score", 0),
            "sentiment_score": prediction.get("sentiment_score", 0),
            "last_updated": metadata.get("last_updated"),
            "processing_time": metadata.get("processing_time", 0),
            "sources_processed": metadata.get("sources_processed", 0),
            "sentiment_items_processed": metadata.get("sentiment_items_processed", 0),
        }
        
        # Add sentiment source details if available
        if "sentiment_data" in self.coordinator.data:
            sentiment_sources = self.coordinator.data["sentiment_data"].get("sources", [])
            top_sources = sorted(sentiment_sources, key=lambda x: x.get("impact", 0), reverse=True)[:3]
            attributes["top_sentiment_sources"] = [
                {
                    "source": source.get("source", "Unknown"),
                    "sentiment": round(source.get("sentiment", 0), 3),
                    "weight": source.get("weight", 0),
                    "impact": round(source.get("impact", 0), 3),
                }
                for source in top_sources
            ]
        
        return attributes

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            self.coordinator.last_update_success
            and self.coordinator.data is not None
            and "predictions" in self.coordinator.data
            and self._market in self.coordinator.data["predictions"]
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        # Update icon based on prediction direction
        if self.coordinator.data and "predictions" in self.coordinator.data:
            prediction = self.coordinator.data["predictions"].get(self._market, {})
            direction = prediction.get("direction", "FLAT")
            
            if direction == "UP":
                self._attr_icon = "mdi:trending-up"
            elif direction == "DOWN":
                self._attr_icon = "mdi:trending-down"
            else:
                self._attr_icon = "mdi:trending-neutral"
        
        super()._handle_coordinator_update()


class MarketProgressSensor(CoordinatorEntity, SensorEntity):
    """Market prediction progress sensor."""

    def __init__(self, coordinator: MarketPredictionCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "Market Prediction Progress"
        self._attr_unique_id = f"{DOMAIN}_progress"
        self._attr_icon = "mdi:progress-clock"
        self._attr_native_unit_of_measurement = "%"
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> int:
        """Return the progress percentage."""
        return self.coordinator.progress_percent

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return additional state attributes."""
        eta_minutes = self.coordinator.eta_seconds // 60
        eta_seconds = self.coordinator.eta_seconds % 60
        
        return {
            "stage": self.coordinator.current_stage,
            "current_source": self.coordinator.current_source,
            "eta_seconds": self.coordinator.eta_seconds,
            "eta_formatted": f"{eta_minutes}m {eta_seconds}s" if eta_minutes > 0 else f"{eta_seconds}s",
            "processing_time": round(self.coordinator.processing_time, 1),
            "processing_time_formatted": f"{self.coordinator.processing_time:.1f}s",
        }


class MarketStatusSensor(CoordinatorEntity, SensorEntity):
    """Market prediction status sensor."""

    def __init__(self, coordinator: MarketPredictionCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "Market Prediction Status"
        self._attr_unique_id = f"{DOMAIN}_status"
        self._attr_icon = "mdi:information"

    @property
    def native_value(self) -> str:
        """Return the current status."""
        return self.coordinator.current_stage

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return additional state attributes."""
        return {
            "progress": self.coordinator.progress_percent,
            "current_source": self.coordinator.current_source,
            "processing_time": round(self.coordinator.processing_time, 1),
        }


class MarketCurrentSourceSensor(CoordinatorEntity, SensorEntity):
    """Market prediction current source sensor."""

    def __init__(self, coordinator: MarketPredictionCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "Market Prediction Current Source"
        self._attr_unique_id = f"{DOMAIN}_current_source"
        self._attr_icon = "mdi:newspaper"

    @property
    def native_value(self) -> str:
        """Return the current source being processed."""
        return self.coordinator.current_source or "Idle"

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return additional state attributes."""
        return {
            "stage": self.coordinator.current_stage,
            "progress": self.coordinator.progress_percent,
        }


class MarketProcessingTimeSensor(CoordinatorEntity, SensorEntity):
    """Market prediction processing time sensor."""

    def __init__(self, coordinator: MarketPredictionCoordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = "Market Prediction Processing Time"
        self._attr_unique_id = f"{DOMAIN}_processing_time"
        self._attr_icon = "mdi:timer"
        self._attr_native_unit_of_measurement = "s"
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def native_value(self) -> float:
        """Return the processing time in seconds."""
        return round(self.coordinator.processing_time, 1)

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        """Return additional state attributes."""
        processing_time = self.coordinator.processing_time
        minutes = int(processing_time // 60)
        seconds = int(processing_time % 60)
        
        return {
            "formatted_time": f"{minutes}m {seconds}s" if minutes > 0 else f"{seconds}s",
            "stage": self.coordinator.current_stage,
            "eta_seconds": self.coordinator.eta_seconds,
        }