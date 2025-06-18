"""Config flow for Market Prediction integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
import aiohttp
import asyncio

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import (
    DOMAIN,
    CONF_ALPHA_VANTAGE_API_KEY,
    CONF_FMP_API_KEY,
    CONF_UPDATE_INTERVAL,
    DEFAULT_UPDATE_INTERVAL,
    ALPHA_VANTAGE_BASE_URL,
    FMP_BASE_URL,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_ALPHA_VANTAGE_API_KEY): str,
        vol.Optional(CONF_FMP_API_KEY, default=""): str,
        vol.Optional(CONF_UPDATE_INTERVAL, default=DEFAULT_UPDATE_INTERVAL): vol.All(
            vol.Coerce(int), vol.Range(min=15, max=120)
        ),
    }
)


async def validate_alpha_vantage_key(hass: HomeAssistant, api_key: str) -> dict[str, Any]:
    """Validate the Alpha Vantage API key."""
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{ALPHA_VANTAGE_BASE_URL}?function=GLOBAL_QUOTE&symbol=SPY&apikey={api_key}"
            async with session.get(url, timeout=10) as response:
                data = await response.json()
                
                if "Error Message" in data:
                    raise InvalidAuth("Invalid API key")
                
                if "Note" in data and "premium" in data["Note"].lower():
                    raise InvalidAuth("API key rate limit exceeded")
                
                return {"title": "Alpha Vantage API"}
                
    except asyncio.TimeoutError:
        raise CannotConnect("Timeout connecting to Alpha Vantage")
    except Exception as exc:
        _LOGGER.exception("Unexpected exception")
        raise CannotConnect("Unknown error occurred") from exc


async def validate_fmp_key(hass: HomeAssistant, api_key: str) -> dict[str, Any]:
    """Validate the FMP API key."""
    if not api_key:
        return {"title": "FMP API (Optional)"}
    
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{FMP_BASE_URL}/v3/quote/SPY?apikey={api_key}"
            async with session.get(url, timeout=10) as response:
                data = await response.json()
                
                if isinstance(data, dict) and "Error Message" in data:
                    raise InvalidAuth("Invalid FMP API key")
                
                return {"title": "FMP API"}
                
    except asyncio.TimeoutError:
        raise CannotConnect("Timeout connecting to FMP")
    except Exception as exc:
        _LOGGER.exception("Unexpected exception validating FMP key")
        raise CannotConnect("Unknown error occurred") from exc


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Market Prediction."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            try:
                # Validate Alpha Vantage API key
                await validate_alpha_vantage_key(
                    self.hass, user_input[CONF_ALPHA_VANTAGE_API_KEY]
                )
                
                # Validate FMP API key if provided
                if user_input.get(CONF_FMP_API_KEY):
                    await validate_fmp_key(
                        self.hass, user_input[CONF_FMP_API_KEY]
                    )
                
                return self.async_create_entry(
                    title="Market Prediction System", data=user_input
                )
                
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
            description_placeholders={
                "alpha_vantage_url": "https://www.alphavantage.co/support/#api-key",
                "fmp_url": "https://financialmodelingprep.com/developer/docs",
            },
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""