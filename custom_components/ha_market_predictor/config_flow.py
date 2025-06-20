"""Config flow for HA Market Predictor integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, CONF_ALPHAVANTAGE_API_KEY, CONF_FINANCIALMODELPREP_API_KEY

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_ALPHAVANTAGE_API_KEY): str,
        vol.Required(CONF_FINANCIALMODELPREP_API_KEY): str,
    }
)

async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    # Basic validation - check if API keys are provided
    if not data[CONF_ALPHAVANTAGE_API_KEY].strip():
        raise InvalidAPIKey("Alpha Vantage API key is required")

    if not data[CONF_FINANCIALMODELPREP_API_KEY].strip():
        raise InvalidAPIKey("Financial Modeling Prep API key is required")

    # Return info that you want to store in the config entry.
    return {"title": "HA Market Predictor"}

class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for HA Market Predictor."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except InvalidAPIKey:
                errors["base"] = "invalid_api_key"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

class InvalidAPIKey(HomeAssistantError):
    """Error to indicate invalid API key."""
