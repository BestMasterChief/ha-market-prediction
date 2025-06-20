"""Config flow for Market Prediction System integration."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("alpha_vantage_api_key"): str,
        vol.Optional("fmp_api_key"): str,
    }
)


async def validate_alpha_vantage_key(
    hass: HomeAssistant, api_key: str
) -> dict[str, Any]:
    """Validate the Alpha Vantage API key."""
    url = (
        f"https://www.alphavantage.co/query?"
        f"function=GLOBAL_QUOTE&symbol=SPY&apikey={api_key}"
    )
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=10) as response:
                if response.status != 200:
                    raise InvalidAuth("Invalid Alpha Vantage API key")
                
                data = await response.json()
                if "Error Message" in data or "Note" in data:
                    raise InvalidAuth("Invalid Alpha Vantage API key")
                    
                return {"title": "Market Prediction System"}
        except aiohttp.ClientError as err:
            raise CannotConnect from err


async def validate_fmp_key(hass: HomeAssistant, api_key: str) -> bool:
    """Validate the FMP API key (optional)."""
    if not api_key:
        return True
    
    url = f"https://financialmodelingprep.com/api/v3/quote/SPY?apikey={api_key}"
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=10) as response:
                if response.status != 200:
                    return False
                
                data = await response.json()
                return not (
                    "Error Message" in data or
                    "error" in data or
                    len(data) == 0
                )
        except aiohttp.ClientError:
            return False


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Market Prediction System."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}

        try:
            # Validate Alpha Vantage API key (required)
            info = await validate_alpha_vantage_key(
                self.hass, user_input["alpha_vantage_api_key"]
            )
            
            # Validate FMP API key (optional)
            fmp_valid = await validate_fmp_key(
                self.hass, user_input.get("fmp_api_key", "")
            )
            
            if not fmp_valid and user_input.get("fmp_api_key"):
                _LOGGER.warning("Invalid FMP API key provided")
            
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except InvalidAuth:
            errors["alpha_vantage_api_key"] = "invalid_auth"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""