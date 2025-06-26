"""Config flow for Market Prediction System integration."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema({
    vol.Required("alpha_vantage_api_key"): str,
    vol.Optional("fmp_api_key", default=""): str,
    vol.Optional("update_interval", default=3): vol.All(
        vol.Coerce(int), vol.Range(min=1, max=24)
    ),
    vol.Optional("prediction_times", default="06:30,12:00,17:30"): str,
})

OPTIONS_SCHEMA = vol.Schema({
    vol.Optional("update_interval", default=3): vol.All(
        vol.Coerce(int), vol.Range(min=1, max=24)
    ),
    vol.Optional("prediction_times", default="06:30,12:00,17:30"): str,
    vol.Optional("enable_weekend_analysis", default=True): bool,
    vol.Optional("confidence_threshold", default=50): vol.All(
        vol.Coerce(int), vol.Range(min=10, max=95)
    ),
    vol.Optional("max_prediction_change", default=4.0): vol.All(
        vol.Coerce(float), vol.Range(min=1.0, max=10.0)
    ),
})


async def validate_alpha_vantage_api(api_key: str) -> dict[str, Any]:
    """Validate the Alpha Vantage API key."""
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": "SPY",
        "apikey": api_key,
    }
    
    timeout = aiohttp.ClientTimeout(total=30)
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    raise InvalidAPIKey(
                        f"Alpha Vantage API returned status {response.status}"
                    )
                
                data = await response.json()
                
                if "Error Message" in data:
                    raise InvalidAPIKey("Invalid Alpha Vantage API key")
                elif "Note" in data:
                    raise APIRateLimit("Alpha Vantage API rate limit exceeded")
                elif "Global Quote" not in data:
                    raise InvalidAPIKey("Unexpected response from Alpha Vantage")
                
                return {"status": "ok"}
                
    except aiohttp.ClientError as err:
        raise CannotConnect(f"Cannot connect to Alpha Vantage: {err}") from err


async def validate_fmp_api(api_key: str) -> dict[str, Any]:
    """Validate the Financial Modeling Prep API key."""
    if not api_key.strip():
        return {"status": "skipped"}
    
    url = "https://financialmodelingprep.com/api/v3/quote/SPY"
    params = {"apikey": api_key}
    
    timeout = aiohttp.ClientTimeout(total=30)
    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, params=params) as response:
                if response.status == 401:
                    raise InvalidAPIKey("Invalid Financial Modeling Prep API key")
                elif response.status == 429:
                    raise APIRateLimit("FMP API rate limit exceeded")
                elif response.status != 200:
                    raise InvalidAPIKey(
                        f"FMP API returned status {response.status}"
                    )
                
                data = await response.json()
                
                if isinstance(data, dict) and "error" in data:
                    raise InvalidAPIKey("Invalid FMP API key")
                elif not isinstance(data, list) or len(data) == 0:
                    raise InvalidAPIKey("Unexpected response from FMP API")
                
                return {"status": "ok"}
                
    except aiohttp.ClientError as err:
        raise CannotConnect(f"Cannot connect to FMP: {err}") from err


class MarketPredictionConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Market Prediction System."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        
        if user_input is not None:
            try:
                # Validate Alpha Vantage API key (required)
                await validate_alpha_vantage_api(
                    user_input["alpha_vantage_api_key"]
                )
                
                # Validate FMP API key (optional)
                if user_input.get("fmp_api_key"):
                    await validate_fmp_api(user_input["fmp_api_key"])
                
                # Create unique ID based on Alpha Vantage key
                unique_id = user_input["alpha_vantage_api_key"][:8]
                await self.async_set_unique_id(unique_id)
                self._abort_if_unique_id_configured()
                
                return self.async_create_entry(
                    title="Market Prediction System",
                    data=user_input,
                )
                
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAPIKey:
                errors["base"] = "invalid_api_key"
            except APIRateLimit:
                errors["base"] = "api_rate_limit"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle reconfiguration of the integration."""
        errors: dict[str, str] = {}
        config_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )
        
        if user_input is not None:
            try:
                # Validate Alpha Vantage API key
                await validate_alpha_vantage_api(
                    user_input["alpha_vantage_api_key"]
                )
                
                # Validate FMP API key if provided
                if user_input.get("fmp_api_key"):
                    await validate_fmp_api(user_input["fmp_api_key"])
                
                # Update the config entry
                self.hass.config_entries.async_update_entry(
                    config_entry, data=user_input
                )
                
                return self.async_create_entry(
                    title="Market Prediction System", data={}
                )
                
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAPIKey:
                errors["base"] = "invalid_api_key"
            except APIRateLimit:
                errors["base"] = "api_rate_limit"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        # Populate form with current values
        current_data = config_entry.data
        schema = vol.Schema({
            vol.Required(
                "alpha_vantage_api_key",
                default=current_data.get("alpha_vantage_api_key", "")
            ): str,
            vol.Optional(
                "fmp_api_key",
                default=current_data.get("fmp_api_key", "")
            ): str,
            vol.Optional(
                "update_interval",
                default=current_data.get("update_interval", 3)
            ): vol.All(vol.Coerce(int), vol.Range(min=1, max=24)),
            vol.Optional(
                "prediction_times",
                default=current_data.get("prediction_times", "06:30,12:00,17:30")
            ): str,
        })

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Market Prediction options flow."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Get current options or use defaults from config data
        options = self.config_entry.options
        data = self.config_entry.data
        
        current_options = {
            "update_interval": options.get(
                "update_interval", data.get("update_interval", 3)
            ),
            "prediction_times": options.get(
                "prediction_times", data.get("prediction_times", "06:30,12:00,17:30")
            ),
            "enable_weekend_analysis": options.get(
                "enable_weekend_analysis", True
            ),
            "confidence_threshold": options.get("confidence_threshold", 50),
            "max_prediction_change": options.get("max_prediction_change", 4.0),
        }

        return self.async_show_form(
            step_id="init",
            data_schema=self.add_suggested_values_to_schema(
                OPTIONS_SCHEMA, current_options
            ),
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAPIKey(HomeAssistantError):
    """Error to indicate there is an invalid API key."""


class APIRateLimit(HomeAssistantError):
    """Error to indicate API rate limit exceeded."""