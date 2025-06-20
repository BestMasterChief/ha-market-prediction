"""Config flow for Market Prediction integration."""
import logging
import voluptuous as vol
import aiohttp
import asyncio

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import (
    DOMAIN,
    CONF_ALPHA_VANTAGE_API_KEY,
    CONF_FMP_API_KEY,
    ALPHA_VANTAGE_BASE_URL,
    FMP_BASE_URL
)

_LOGGER = logging.getLogger(__name__)


class MarketPredictionConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Market Prediction."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            # Validate API keys
            alpha_vantage_valid = await self._validate_alpha_vantage_api(
                user_input[CONF_ALPHA_VANTAGE_API_KEY]
            )
            fmp_valid = True  # FMP is optional
            if user_input.get(CONF_FMP_API_KEY):
                fmp_valid = await self._validate_fmp_api(
                    user_input[CONF_FMP_API_KEY]
                )

            if not alpha_vantage_valid:
                errors["alpha_vantage_api_key"] = "invalid_api_key"

            if not fmp_valid:
                errors["fmp_api_key"] = "invalid_api_key"

            if not errors:
                return self.async_create_entry(
                    title="Market Prediction System",
                    data=user_input
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_ALPHA_VANTAGE_API_KEY): str,
                vol.Optional(CONF_FMP_API_KEY, default=""): str,
            }),
            errors=errors,
        )

    async def _validate_alpha_vantage_api(self, api_key: str) -> bool:
        """Validate Alpha Vantage API key."""
        try:
            url = f"{ALPHA_VANTAGE_BASE_URL}?function=GLOBAL_QUOTE&symbol=MSFT&apikey={api_key}"
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return "Global Quote" in data or "Time Series" in data
            return False
        except Exception as ex:
            _LOGGER.error("Error validating Alpha Vantage API key: %s", ex)
            return False

    async def _validate_fmp_api(self, api_key: str) -> bool:
        """Validate Financial Modeling Prep API key."""
        try:
            url = f"{FMP_BASE_URL}/v3/quote/AAPL?apikey={api_key}"
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return isinstance(data, list) and len(data) > 0
            return False
        except Exception as ex:
            _LOGGER.error("Error validating FMP API key: %s", ex)
            return False


class MarketPredictionOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for Market Prediction."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional(
                    "update_interval",
                    default=self.config_entry.options.get("update_interval", 6)
                ): vol.All(vol.Coerce(int), vol.Range(min=1, max=24)),
                vol.Optional(
                    "enable_notifications",
                    default=self.config_entry.options.get("enable_notifications", True)
                ): bool,
            })
        )