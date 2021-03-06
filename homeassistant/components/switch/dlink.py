"""
Support for D-link W215 smart switch.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/switch.dlink/
"""
import logging

import voluptuous as vol

from homeassistant.components.switch import (SwitchDevice, PLATFORM_SCHEMA)
from homeassistant.const import (
    CONF_HOST, CONF_NAME, CONF_PASSWORD, CONF_USERNAME)
import homeassistant.helpers.config_validation as cv
from homeassistant.const import TEMP_CELSIUS, STATE_UNKNOWN

REQUIREMENTS = ['https://github.com/LinuxChristian/pyW215/archive/'
                'v0.3.5.zip#pyW215==0.3.5']

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = 'D-link Smart Plug W215'
DEFAULT_PASSWORD = ''
DEFAULT_USERNAME = 'admin'
CONF_USE_LEGACY_PROTOCOL = 'use_legacy_protocol'

ATTR_CURRENT_CONSUMPTION = 'Current Consumption'
ATTR_TOTAL_CONSUMPTION = 'Total Consumption'
ATTR_TEMPERATURE = 'Temperature'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Required(CONF_USERNAME, default=DEFAULT_USERNAME): cv.string,
    vol.Required(CONF_PASSWORD, default=DEFAULT_PASSWORD): cv.string,
    vol.Optional(CONF_USE_LEGACY_PROTOCOL, default=False): cv.boolean,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
})


# pylint: disable=unused-argument
def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup a D-Link Smart Plug."""
    from pyW215.pyW215 import SmartPlug

    host = config.get(CONF_HOST)
    username = config.get(CONF_USERNAME)
    password = config.get(CONF_PASSWORD)
    use_legacy_protocol = config.get(CONF_USE_LEGACY_PROTOCOL)
    name = config.get(CONF_NAME)

    add_devices([SmartPlugSwitch(hass, SmartPlug(host,
                                                 password,
                                                 username,
                                                 use_legacy_protocol),
                                 name)])


class SmartPlugSwitch(SwitchDevice):
    """Representation of a D-link Smart Plug switch."""

    def __init__(self, hass, smartplug, name):
        """Initialize the switch."""
        self.units = hass.config.units
        self.smartplug = smartplug
        self._name = name

    @property
    def name(self):
        """Return the name of the Smart Plug, if any."""
        return self._name

    @property
    def device_state_attributes(self):
        """Return the state attributes of the device."""
        try:
            ui_temp = self.units.temperature(int(self.smartplug.temperature),
                                             TEMP_CELSIUS)
            temperature = "%i %s" % \
                          (ui_temp, self.units.temperature_unit)
        except ValueError:
            temperature = STATE_UNKNOWN

        try:
            current_consumption = "%.2f W" % \
                                  float(self.smartplug.current_consumption)
        except ValueError:
            current_consumption = STATE_UNKNOWN

        try:
            total_consumption = "%.1f kWh" % \
                                float(self.smartplug.total_consumption)
        except ValueError:
            total_consumption = STATE_UNKNOWN

        attrs = {
            ATTR_CURRENT_CONSUMPTION: current_consumption,
            ATTR_TOTAL_CONSUMPTION: total_consumption,
            ATTR_TEMPERATURE: temperature
        }

        return attrs

    @property
    def current_power_watt(self):
        """Return the current power usage in Watt."""
        try:
            return float(self.smartplug.current_consumption)
        except ValueError:
            return None

    @property
    def is_on(self):
        """Return true if switch is on."""
        return self.smartplug.state == 'ON'

    def turn_on(self, **kwargs):
        """Turn the switch on."""
        self.smartplug.state = 'ON'

    def turn_off(self):
        """Turn the switch off."""
        self.smartplug.state = 'OFF'
