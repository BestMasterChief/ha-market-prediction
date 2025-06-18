"""Enhanced Market Prediction System Integration v2.2.0"""
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN, CONF_ALPHA_VANTAGE_API_KEY, CONF_FMP_API_KEY
from .coordinator import MarketPredictionCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Market Prediction from a config entry."""
    alpha_vantage_key = entry.data.get(CONF_ALPHA_VANTAGE_API_KEY)
    fmp_key = entry.data.get(CONF_FMP_API_KEY)
    
    if not alpha_vantage_key:
        _LOGGER.error("Alpha Vantage API key is required")
        raise ConfigEntryNotReady("Alpha Vantage API key not configured")
    
    _LOGGER.info("Setting up Market Prediction System v2.2.0 with enhanced sentiment analysis")
    
    # Create coordinator
    coordinator = MarketPredictionCoordinator(hass, alpha_vantage_key, fmp_key)
    
    # Store coordinator
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator
    
    # Perform initial data fetch
    await coordinator.async_config_entry_first_refresh()
    
    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    _LOGGER.info("Market Prediction System setup complete - ready for enhanced sentiment analysis")
    
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    
    return unload_ok