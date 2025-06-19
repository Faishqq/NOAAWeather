"""Config flow for NOAA Weather integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol  # Not strictly needed now if STEP_USER_DATA_SCHEMA is removed for zero-input

from homeassistant import config_entries
from homeassistant.const import (
    CONF_ELEVATION,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_NAME,
    # CONF_HOST, # Not used in the current zero-input schema
    # CONF_API_KEY, # Not used in the current zero-input schema
    UnitOfLength,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
)


from .const import (
    CONF_TRACK_HOME,
    DEFAULT_HOME_LATITUDE,
    DEFAULT_HOME_LONGITUDE,
    DOMAIN,
    HOME_LOCATION_NAME,
)

_LOGGER = logging.getLogger(__name__)

# STEP_USER_DATA_SCHEMA is not strictly needed if async_step_user is zero-input
# and doesn't show a form using it. If an API key or other initial parameters
# were to be introduced, this would be uncommented and used.
# STEP_USER_DATA_SCHEMA = vol.Schema(
#     {
#         vol.Optional(CONF_API_KEY): str,
#     }
# )


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the input.

    For a zero-input flow, data might be empty.
    This function's primary role here is to return the default title.
    If any background validation were needed (e.g. checking global HA config), it could go here.
    """
    _LOGGER.debug("Config flow: validate_input called with data: %s", data)
    # Return info that you want to store in the config entry, primarily the title.
    return {"title": "Weather"}  # Default title for the integration instance


@callback
def configured_instances(hass: HomeAssistant) -> set[str]:
    """Return a set of configured NOAA Weather instances.
    Used to prevent duplicate configurations based on lat/lon or tracking home.
    """
    # This is an example if you want to prevent re-configuring for the exact same location
    # or for "Home" if CONF_TRACK_HOME is used.
    # The actual data stored and checked would depend on your integration's needs.
    entries = []
    for entry in hass.config_entries.async_entries(DOMAIN):
        if entry.data.get(CONF_TRACK_HOME):  # Using the constant
            entries.append(HOME_LOCATION_NAME)  # Using the constant
            continue
        lat = entry.data.get(CONF_LATITUDE)
        lon = entry.data.get(CONF_LONGITUDE)
        if (
            lat is not None and lon is not None
        ):  # Ensure lat/lon exist if they define uniqueness
            entries.append(f"{lat}-{lon}")
    _LOGGER.debug("Config flow: Found configured instances by identifier: %s", entries)
    return set(entries)


def _get_data_schema(  # This schema is for the OPTIONS FLOW
    hass: HomeAssistant, config_entry: config_entries.ConfigEntry | None = None
) -> vol.Schema:
    """Get a schema with default values for the options flow."""
    # Default to Home Assistant's core coordinates
    default_lat = (
        hass.config.latitude
        if hass.config.latitude is not None
        else DEFAULT_HOME_LATITUDE
    )
    default_lon = (
        hass.config.longitude
        if hass.config.longitude is not None
        else DEFAULT_HOME_LONGITUDE
    )
    default_elev_val = hass.config.elevation if hass.config.elevation is not None else 0

    # Determine default name for options flow:
    # Use existing name from options, then data, then title, then a fallback.
    default_options_name = "NOAA Weather"  # Fallback default
    if config_entry:  # If we have a config entry (i.e., editing options)
        default_options_name = (
            config_entry.options.get(CONF_NAME)  # Check options first
            or config_entry.data.get(
                CONF_NAME
            )  # Then data (if name was ever stored there)
            or config_entry.title  # Then the current title of the entry
            or default_options_name  # Fallback
        )
        # For lat/lon/elev, default to existing values from options or data if available
        default_lat = config_entry.options.get(
            CONF_LATITUDE, config_entry.data.get(CONF_LATITUDE, default_lat)
        )
        default_lon = config_entry.options.get(
            CONF_LONGITUDE, config_entry.data.get(CONF_LONGITUDE, default_lon)
        )
        default_elev_val = config_entry.options.get(
            CONF_ELEVATION, config_entry.data.get(CONF_ELEVATION, default_elev_val)
        )

    # This schema is for an options flow, allowing users to change settings post-setup.
    # If CONF_TRACK_HOME were an option, it would influence defaults.
    # Assuming for now options allow setting Name, Lat, Lon, Elev.
    return vol.Schema(
        {
            vol.Optional(CONF_NAME, default=default_options_name): str,
            vol.Optional(CONF_LATITUDE, default=default_lat): cv.latitude,
            vol.Optional(CONF_LONGITUDE, default=default_lon): cv.longitude,
            vol.Optional(CONF_ELEVATION, default=default_elev_val): NumberSelector(
                NumberSelectorConfig(
                    mode=NumberSelectorMode.BOX,
                    unit_of_measurement=UnitOfLength.METERS,  # Assuming meters
                )
            ),
            # Example: If you wanted to add API Key to options:
            # vol.Optional(CONF_API_KEY, default=config_entry.options.get(CONF_API_KEY, "")): str,
        }
    )


class NoaaConfigFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for NOAA Weather."""

    VERSION = 1
    _LOGGER.debug("NOAA Weather ConfigFlow, START. Version: %s", VERSION)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step for a zero-input configuration."""
        _LOGGER.debug("Config flow: async_step_user called, user_input: %s", user_input)

        # For a true zero-input flow from the user's perspective for this step:
        # We can check if an instance is already configured to guide the user or abort.
        # Example: if self._async_current_entries():
        #     return self.async_abort(reason="already_configured")
        # However, allowing multiple instances is often fine if they can be differentiated
        # (e.g., by different lat/lon set via options flow later, or if each uses HA's core lat/lon).
        # For now, we'll proceed to create an entry.

        # Data to be stored in config_entry.data.
        # For this zero-input initial step, it will be empty.
        # The integration will rely on HA's core settings for lat/lon,
        # and any other specific settings (like API key or custom name)
        # would ideally be configured via an Options Flow after setup.
        data_for_entry: dict[str, Any] = {}

        try:
            # validate_input's main role here is to provide the default title.
            # It's passed `data_for_entry` in case it needs to inspect it, though currently it doesn't.
            info = await validate_input(self.hass, data_for_entry)
            _LOGGER.debug("Config flow: validate_input returned info: %s", info)
        except CannotConnect:
            _LOGGER.error(
                "Config flow: Cannot connect (as raised by validate_input - placeholder)."
            )
            return self.async_abort(reason="cannot_connect")
        except InvalidAuth:
            _LOGGER.error(
                "Config flow: Invalid auth (as raised by validate_input - placeholder)."
            )
            return self.async_abort(reason="invalid_auth")
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Config flow: Unexpected exception during validation.")
            return self.async_abort(reason="unknown")

        _LOGGER.debug(
            "Config flow: Creating entry with title '%s' and data %s",
            info["title"],
            data_for_entry,
        )
        # Create the config entry. `data_for_entry` will be stored in `config_entry.data`.
        return self.async_create_entry(title=info["title"], data=data_for_entry)

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        _LOGGER.debug(
            "Config flow: Getting options flow for entry ID: %s", config_entry.entry_id
        )
        return NoaaOptionsFlowHandler(config_entry)


class NoaaOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle an options flow for NOAA Weather."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry
        # Initialize options with existing options, or empty dict if none
        self.options = dict(config_entry.options)
        _LOGGER.debug(
            "OptionsFlow: Initialized for entry %s with options: %s",
            config_entry.entry_id,
            self.options,
        )

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options for the NOAA Weather integration."""
        errors: dict[str, str] = {}
        if user_input is not None:
            # user_input contains the new option values from the form.
            # You can validate them here if needed.
            # For example, if API key is an option:
            # if not user_input.get(CONF_API_KEY): # Basic check
            #    errors[CONF_API_KEY] = "api_key_required"
            # else: # Validation passed
            #    self.options.update(user_input)
            #    return self.async_create_entry(title="", data=self.options)

            # For now, just updating options and creating entry
            self.options.update(user_input)
            _LOGGER.debug(
                "OptionsFlow: Creating/updating options entry with data: %s",
                self.options,
            )
            return self.async_create_entry(
                title="", data=self.options
            )  # title is not used for options entry

        # Get the schema for the options form, pre-filled with current settings
        options_schema = _get_data_schema(self.hass, self.config_entry)

        return self.async_show_form(
            step_id="init",
            data_schema=options_schema,
            errors=errors,
            description_placeholders={  # Optional: if you have placeholders in your strings.json for options
                "documentation_url": "https://www.weather.gov/documentation/services-web-api"
            },
        )


# Custom Exceptions for the Config Flow (if validate_input were to raise them)
class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""

    pass


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""

    pass
