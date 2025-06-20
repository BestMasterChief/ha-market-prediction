"""The HA Market Predictor integration."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.exceptions import ServiceValidationError

from .coordinator import MarketPredictorCoordinator
from .const import DOMAIN, CONF_ALPHAVANTAGE_API_KEY, CONF_FINANCIALMODELPREP_API_KEY

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up HA Market Predictor from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    coordinator = MarketPredictorCoordinator(
        hass,
        entry.data[CONF_ALPHAVANTAGE_API_KEY],
        entry.data[CONF_FINANCIALMODELPREP_API_KEY]
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register services
    async def handle_manual_prediction(call: ServiceCall) -> None:
        """Handle manual prediction service call."""
        try:
            await coordinator.async_manual_prediction()
        except Exception as err:
            raise ServiceValidationError(f"Failed to run manual prediction: {err}") from err

    hass.services.async_register(
        DOMAIN,
        "manual_prediction",
        handle_manual_prediction,
    )

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

        # Remove services if this is the last entry
        if not hass.data[DOMAIN]:
            hass.services.async_remove(DOMAIN, "manual_prediction")

    return unload_ok
