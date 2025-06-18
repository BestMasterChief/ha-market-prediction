"""Market Prediction config flow with enhanced API validation."""
import asyncio
import logging
import aiohttp
import voluptuous as vol
from typing import Any, Dict, Optional

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv
from homeassistant.exceptions import HomeAssistantError

from .const import (
    DOMAIN,
    CONF_ALPHA_VANTAGE_API_KEY,
    CONF_FMP_API_KEY,
    ALPHA_VANTAGE_BASE_URL,
    FMP_BASE_URL,
)

_LOGGER = logging.getLogger(__name__)

class MarketPredictionConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Market Prediction."""

    VERSION = 1

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            alpha_vantage_key = user_input[CONF_ALPHA_VANTAGE_API_KEY]
            fmp_key = user_input.get(CONF_FMP_API_KEY)
            
            # Alpha Vantage key is required
            if not alpha_vantage_key:
                errors[CONF_ALPHA_VANTAGE_API_KEY] = "alpha_vantage_key_required"
            else:
                # Validate Alpha Vantage API key
                av_valid = await self._validate_alpha_vantage_key(alpha_vantage_key)
                if not av_valid:
                    errors[CONF_ALPHA_VANTAGE_API_KEY] = "invalid_alpha_vantage_key"
                
                # Validate FMP API key if provided
                if fmp_key:
                    fmp_valid = await self._validate_fmp_key(fmp_key)
                    if not fmp_valid:
                        errors[CONF_FMP_API_KEY] = "invalid_fmp_key"
            
            # If validation passed, create entry
            if not errors:
                return self.async_create_entry(
                    title="Market Prediction System",
                    data={
                        CONF_ALPHA_VANTAGE_API_KEY: alpha_vantage_key,
                        CONF_FMP_API_KEY: fmp_key,
                    },
                )

        # Show form with fields
        data_schema = vol.Schema({
            vol.Required(CONF_ALPHA_VANTAGE_API_KEY): str,
            vol.Optional(CONF_FMP_API_KEY): vol.Any(str, None),
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "alpha_vantage_url": "https://www.alphavantage.co/support/#api-key",
                "fmp_url": "https://site.financialmodelingprep.com/developer/docs/",
            },
        )

    async def _validate_alpha_vantage_key(self, api_key: str) -> bool:
        """Validate the Alpha Vantage API key."""
        try:
            # Test with a simple API call
            url = f"{ALPHA_VANTAGE_BASE_URL}?function=TIME_SERIES_DAILY&symbol=SPY&apikey={api_key}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status != 200:
                        _LOGGER.error("Alpha Vantage API key validation failed: HTTP %s", response.status)
                        return False
                    
                    data = await response.json()
                    
                    # Check for error responses
                    if "Error Message" in data:
                        _LOGGER.error("Alpha Vantage API key validation failed: %s", data["Error Message"])
                        return False
                    
                    # Check for rate limit messages
                    if "Note" in data and "API call frequency" in data["Note"]:
                        _LOGGER.warning("Alpha Vantage API rate limit warning: %s", data["Note"])
                        # Allow this as it's still a valid key
                    
                    # Verify we have actual data
                    if "Time Series (Daily)" not in data:
                        _LOGGER.error("Alpha Vantage API key validation failed: No time series data")
                        return False
                    
                    return True
                    
        except asyncio.TimeoutError:
            _LOGGER.error("Alpha Vantage API key validation timeout")
            return False
        except Exception as e:
            _LOGGER.error("Alpha Vantage API key validation error: %s", e)
            return False

    async def _validate_fmp_key(self, api_key: str) -> bool:
        """Validate the Financial Modeling Prep API key (optional)."""
        # FMP key is optional, so empty is valid
        if not api_key:
            return True
            
        try:
            # Test with a simple API call
            url = f"{FMP_BASE_URL}/v3/quote/SPY?apikey={api_key}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status != 200:
                        _LOGGER.error("FMP API key validation failed: HTTP %s", response.status)
                        return False
                    
                    data = await response.json()
                    
                    # Check for error responses (FMP returns empty array for invalid keys)
                    if not data or not isinstance(data, list) or len(data) == 0:
                        _LOGGER.error("FMP API key validation failed: Empty response")
                        return False
                    
                    return True
                    
        except asyncio.TimeoutError:
            _LOGGER.error("FMP API key validation timeout")
            return False
        except Exception as e:
            _LOGGER.error("FMP API key validation error: %s", e)
            return False

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Market Prediction."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        alpha_vantage_key = self.config_entry.data.get(CONF_ALPHA_VANTAGE_API_KEY, "")
        fmp_key = self.config_entry.data.get(CONF_FMP_API_KEY, "")

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Required(CONF_ALPHA_VANTAGE_API_KEY, default=alpha_vantage_key): str,
                vol.Optional(CONF_FMP_API_KEY, default=fmp_key): str,
            }),
        )