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
    ALPHA_VANTAGE_BASE_URL,
    FMP_BASE_URL,
    DEFAULT_TIMEOUT,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_ALPHA_VANTAGE_API_KEY): str,
        vol.Optional(CONF_FMP_API_KEY): str,
    }
)


async def validate_api_key(hass: HomeAssistant, api_key: str, api_type: str) -> dict[str, Any]:
    """Validate the API key."""
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT)) as session:
        try:
            if api_type == "alpha_vantage":
                url = f"{ALPHA_VANTAGE_BASE_URL}?function=GLOBAL_QUOTE&symbol=SPY&apikey={api_key}"
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        if "Error Message" in data:
                            raise InvalidAuth(f"Alpha Vantage API error: {data['Error Message']}")
                        if "Note" in data and "API call frequency" in data["Note"]:
                            raise InvalidAuth("Alpha Vantage API rate limit exceeded")
                        if "Global Quote" not in data:
                            raise InvalidAuth("Invalid Alpha Vantage API response format")
                        return {"api_valid": True, "api_type": "alpha_vantage"}
                    else:
                        raise CannotConnect(f"Alpha Vantage API returned status {response.status}")
            
            elif api_type == "fmp":
                url = f"{FMP_BASE_URL}/quote/SPY?apikey={api_key}"
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        if isinstance(data, dict) and "Error Message" in data:
                            raise InvalidAuth(f"FMP API error: {data['Error Message']}")
                        if not isinstance(data, list) or len(data) == 0:
                            raise InvalidAuth("Invalid FMP API response format")
                        return {"api_valid": True, "api_type": "fmp"}
                    else:
                        raise CannotConnect(f"FMP API returned status {response.status}")
                        
        except asyncio.TimeoutError as err:
            raise CannotConnect(f"Timeout connecting to {api_type} API") from err
        except aiohttp.ClientError as err:
            raise CannotConnect(f"Cannot connect to {api_type} API: {err}") from err


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
                # Validate Alpha Vantage API key (required)
                await validate_api_key(
                    self.hass, 
                    user_input[CONF_ALPHA_VANTAGE_API_KEY], 
                    "alpha_vantage"
                )
                
                # Validate FMP API key if provided (optional)
                if user_input.get(CONF_FMP_API_KEY):
                    await validate_api_key(
                        self.hass, 
                        user_input[CONF_FMP_API_KEY], 
                        "fmp"
                    )

                # Check for existing entries
                await self.async_set_unique_id("market_prediction_instance")
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title="Market Prediction System",
                    data=user_input,
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
                "alpha_vantage_note": "Get your free API key from https://www.alphavantage.co/support/#api-key",
                "fmp_note": "Optional: Get your free API key from https://financialmodelingprep.com/developer/docs"
            },
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""