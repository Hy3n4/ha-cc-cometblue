"""
Support for Eurotronic CometBlue thermostats.
They are identical to the Xavax Bluetooth thermostats and others, e.g. sold by discounters.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/climate.cometblue/
"""
import logging
from datetime import timedelta
from datetime import datetime
import threading
import voluptuous as vol

from sys import stderr

from homeassistant.components.climate import (
    ClimateDevice,
    PLATFORM_SCHEMA,
    STATE_ON,
    STATE_OFF,
    STATE_AUTO,
    STATE_HEAT,
    STATE_COOL,
    ATTR_TARGET_TEMP_LOW,
    ATTR_TARGET_TEMP_HIGH,
    SUPPORT_TARGET_TEMPERATURE,
    SUPPORT_TARGET_TEMPERATURE_HIGH,
    SUPPORT_TARGET_TEMPERATURE_LOW,
    SUPPORT_AWAY_MODE,
    SUPPORT_OPERATION_MODE)
from homeassistant.const import (
    CONF_NAME,
    CONF_MAC,
    CONF_PIN,
    CONF_DEVICES,
    TEMP_CELSIUS,
    ATTR_TEMPERATURE,
    PRECISION_HALVES)

import homeassistant.helpers.config_validation as cv

REQUIREMENTS = ['cometblue']

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(10)

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=300)
SCAN_INTERVAL = timedelta(seconds=300)

STATE_AUTO_LOCKED = "auto_locked"
STATE_MANUAL = "manual"
STATE_MANUAL_LOCKED = "manual_locked"

ATTR_STATE_WINDOW_OPEN = 'window_open'
ATTR_STATE_VALVE = 'valve'
ATTR_STATE_LOCKED = 'is_locked'
ATTR_STATE_LOW_BAT = 'low_battery'
ATTR_BATTERY = 'battery_level'
ATTR_TARGET = 'target_temp'
ATTR_VENDOR_NAME = 'vendor_name'
ATTR_MODEL = 'model'
ATTR_FIRMWARE = 'firmware'
ATTR_VERSION = 'version'
ATTR_WINDOW = 'window_open'

DEVICE_SCHEMA = vol.Schema({
    vol.Required(CONF_MAC): cv.string,
    vol.Optional(CONF_PIN, default=0): cv.positive_int,
})

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_DEVICES):
        vol.Schema({cv.string: DEVICE_SCHEMA}),
})

SUPPORT_FLAGS = (SUPPORT_TARGET_TEMPERATURE | SUPPORT_OPERATION_MODE | SUPPORT_TARGET_TEMPERATURE_HIGH
                 | SUPPORT_TARGET_TEMPERATURE_LOW | SUPPORT_AWAY_MODE)

gatt_mgr = None


def setup_platform(hass, config, add_devices, discovery_info=None):
    from cometblue import device as cometblue_dev

    global gatt_mgr

    gatt_mgr = cometblue_dev.CometBlueManager('hci0')

    class ManagerThread(threading.Thread):
        def run(self):
            gatt_mgr.run()

    ManagerThread().start()

    devices = []

    for name, device_cfg in config[CONF_DEVICES].items():
        dev = CometBlueThermostat(device_cfg[CONF_MAC], name, device_cfg[CONF_PIN])
        devices.append(dev)

    add_devices(devices)


class CometBlueStates():
    BIT_MANUAL = 0x01
    BIT_LOCKED = 0x80
    BIT_WINDOW = 0x10

    def __init__(self):
        self._temperature = None
        self.target_temp = None
        self.target_temp_l = None
        self.target_temp_h = None
        self.manual = None
        self.locked = None
        self.window = None
        self.low_battery = None
        self._battery_level = None
        self.manufacturer = None
        self.software_rev = None
        self.firmware_rev = None
        self.model_no = None
        self.name = None
        self.holidays = None
        self.last_seen = None
        self.last_talked = None

    @property
    def temperature_value(self):
        val = {
            'manual_temp': self.target_temp,
            'current_temp': self.temperature,
            'target_temp_l': self.target_temp_l,
            'target_temp_h': self.target_temp_h,
            'offset_temp': 0.0,
            'window_open_detection': 12,
            'window_open_minutes': 10
        }
        return val

    @property
    def mode_value(self):
        val = {
            'not_ready': None,
            'childlock': self.locked,
            'state_as_dword': None,
            'manual_mode': self.manual,
            'adapting': None,
            'unused_bits': None,
            'low_battery': self.low_battery,
            'antifrost_activated': None,
            'motor_moving': None,
            'installing': None,
            'satisfied': None
        }
        return val
    
    @property
    def holidays_value(self):
        val = [
            {'end': None, 'start': None, 'temp': None},
            {'end': None, 'start': None, 'temp': None},
            {'end': None, 'start': None, 'temp': None},
            {'end': None, 'start': None, 'temp': None},
            {'end': None, 'start': None, 'temp': None},
            {'end': None, 'start': None, 'temp': None},
            {'end': None, 'start': None, 'temp': None},
            {'end': None, 'start': None, 'temp': None}
        ]
        return val
    
    @mode_value.setter
    def mode_value(self, value):
        self.manual = value['manual_mode']
        self.window = False
        self.low_battery = value['low_battery']
        self.locked = value['childlock']

    @property
    def mode_code(self):
        if self.manual is None or self.locked is None:
            return None
        if self.manual:
            if self.locked:
                return STATE_MANUAL_LOCKED
            else:
                return STATE_MANUAL
        else:
            if self.locked:
                return STATE_AUTO_LOCKED
            else:
                return STATE_AUTO

    @mode_code.setter
    def mode_code(self, value):
        if value == STATE_MANUAL:
            self.manual = True
            self.locked = False
        elif value == STATE_MANUAL_LOCKED:
            self.manual = True
            self.locked = True
        elif value == STATE_AUTO:
            self.manual = False
            self.locked = False
        elif value == STATE_AUTO_LOCKED:
            self.manual = False
            self.locked = True

    @property
    def battery_level(self):
        return self._battery_level

    @battery_level.setter
    def battery_level(self, value):
        if value is not None and 0 <= value <= 100:
            self._battery_level = value

    @property
    def temperature(self):
        return self._temperature

    @temperature.setter
    def temperature(self, value):
        _LOGGER.debug('Setting temperature to: {}'.format(value))
        if value is not None and 8 <= 28:
            self._temperature = value


class CometBlueThermostat(ClimateDevice):
    """Representation of a CometBlue thermostat."""

    def __init__(self, _mac, _name, _pin=None):
        """Initialize the thermostat."""
        from cometblue import device as cometblue_dev

        global gatt_mgr

        self.modes = [STATE_AUTO, STATE_AUTO_LOCKED, STATE_MANUAL, STATE_MANUAL_LOCKED]
        self._mac = _mac
        self._name = _name
        self._pin = _pin
        self._thermostat = cometblue_dev.CometBlue(_mac, gatt_mgr, _pin)
        self._target = CometBlueStates()
        self._current = CometBlueStates()
        self.update()

    # def __del__(self):
    #    self._thermostat.disconnect()

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return SUPPORT_FLAGS

    @property
    def available(self) -> bool:
        """Return if thermostat is available."""
        # return True
        return not self.is_stale()

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    @property
    def temperature_unit(self):
        """Return the unit of measurement that is used."""
        return TEMP_CELSIUS

    @property
    def precision(self):
        """Return cometblue's precision 0.5."""
        return PRECISION_HALVES

    @property
    def current_temperature(self):
        """Return current temperature"""
        return self._current.temperature

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        return self._target.target_temp

    @property
    def target_temperature_low(self):
        """ Return low """
        if self._current.mode_code == STATE_AUTO or self._current.mode_code == STATE_AUTO_LOCKED:
            return self._current.target_temp_l
        return None

    @property
    def target_temperature_high(self):
        """ Return low """
        if self._current.mode_code == STATE_AUTO or self._current.mode_code == STATE_AUTO_LOCKED:
            return self._current.target_temp_h
        return None

    def set_temperature(self, **kwargs):
        """Set new target temperature."""
        low_temp = kwargs.get(ATTR_TARGET_TEMP_LOW)
        high_temp = kwargs.get(ATTR_TARGET_TEMP_HIGH)
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if low_temp is not None or high_temp is not None:
            _LOGGER.debug("Low Temperature to set: {}".format(low_temp))
            _LOGGER.debug("High Temperature to set: {}".format(high_temp))
            self._target.target_temp_l = low_temp
            self._target.target_temp_h = high_temp
        if temperature is None and (low_temp is None or high_temp is None):
            return
        if temperature < self.min_temp:
            temperature = self.min_temp
        if temperature > self.max_temp:
            temperature = self.max_temp
        _LOGGER.debug("Temperature to set: {}".format(temperature))
        self._target.target_temp = temperature

    @property
    def min_temp(self):
        """Return the minimum temperature."""
        # return self._thermostat.min_temp
        return 8.0

    @property
    def max_temp(self):
        """Return the maximum temperature."""
        # return self._thermostat.max_temp
        return 28.0

    @property
    def current_operation(self):
        """Current mode."""
        return self._current.mode_code

    @property
    def operation_list(self):
        """List of available operation modes."""
        return self.modes

    def set_operation_mode(self, operation_mode):
        """Set operation mode."""
        self._target.mode_code = operation_mode

    def is_stale(self):
        _LOGGER.info(
            "{} last seen {} last talked {}".format(self._mac, self._current.last_seen, self._current.last_talked))
        now = datetime.now()
        if self._current.last_seen is not None and (now - self._current.last_seen).total_seconds() < 600:
            return False
        if self._current.last_talked is not None and (now - self._current.last_talked).total_seconds() < 600:
            return False
        return True

    @property
    def icon(self):
        """Return the icon to use in the frontend, if any."""
        if self.is_stale():
            return 'mdi:bluetooth-off'
        if self._current.battery_level is None:
            return 'mdi:bluetooth-off'
        if self._current.battery_level == 100:
            return 'mdi:battery'
        if self._current.battery_level == 0:
            return 'mdi:battery-alert'
        if self._current.battery_level < 10:
            return 'mdi:battery-outline'
        if 10 <= self._current.battery_level <= 99:
            return 'mdi:battery-{}0'.format(int(self._current.battery_level / 10))
        return None

    @property
    def device_state_attributes(self):
        """Return the device specific state attributes."""
        return {
            ATTR_VENDOR_NAME: self._current.manufacturer,
            ATTR_MODEL: self._current.model_no,
            ATTR_FIRMWARE: self._current.firmware_rev,
            ATTR_VERSION: self._current.software_rev,
            ATTR_BATTERY: self._current.battery_level,
            ATTR_STATE_LOW_BAT: self._current.low_battery,
            ATTR_TARGET: self._current.target_temp,
            ATTR_WINDOW: self._current.window,
        }

    def update(self):
        """Update the data from the thermostat."""
        get_temperatures = True
        _LOGGER.info("Update called {}".format(self._mac))
        self._thermostat.connect()
        self._thermostat.attempt_to_get_ready()
        with self._thermostat as device:
            if self._current.mode_code != self._target.mode_code and self._target.manual is not None:
                _LOGGER.debug("Setting mode to: {}".format(self._target.mode_value))
                device.set_status(self._target.mode_value)
            _LOGGER.debug("_current.target_temp: {}".format(self._current.target_temp))
            _LOGGER.debug("_current.target_temp diff: {}".format(
                self._current.target_temp != self._target.target_temp)
            )
            _LOGGER.debug("_current.target_temp_h diff: {}".format(
                self._current.target_temp_h != self._target.target_temp_h)
            )
            _LOGGER.debug("_current.target_temp_l diff: {}".format(
                self._current.target_temp_l != self._target.target_temp_l)
            )
            if self._current.target_temp != self._target.target_temp and self._target.target_temp is not None\
                    or (self._target.target_temp_l != self._current.target_temp_l
                        and self._target.target_temp_l is not None) \
                    or (self._target.target_temp_h != self._current.target_temp_h
                        and self._target.target_temp_h is not None):
                # TODO: Fix temperature settings. It works but there is an ugly fix for reading value immediately
                # after change.
                _LOGGER.info("Values to set: {}".format(str(self._target.temperature_value)))
                device.set_temperatures(self._target.temperature_value)
                get_temperatures = False
            self._current.battery_level = device.get_battery()
            _LOGGER.debug("Current Battery Level: {}%".format(self._current.battery_level))
            self._current.mode_value = device.get_status()
            self._current.holidays = device.get_holidays()
            cur_temps = device.get_temperatures()
            _LOGGER.debug("target_temp_h: {}".format(cur_temps['target_temp_h']))
            _LOGGER.debug("target_temp_l: {}".format(cur_temps['target_temp_l']))
            _LOGGER.debug("current_temp: {}".format(cur_temps['current_temp']))
            if cur_temps['current_temp'] != -64.0 \
                    or cur_temps['target_temp_l'] != -64.0 \
                    or cur_temps['target_temp_h'] != -64.0:
                _LOGGER.debug('Setting _current.temperature: {}'.format(cur_temps['current_temp']))
                self._current.temperature = cur_temps['current_temp']
                _LOGGER.debug('Current _current.temperature: {}'.format(self._current.temperature))
                self._current.target_temp_l = cur_temps['target_temp_l']
                self._current.target_temp_h = cur_temps['target_temp_h']
                _LOGGER.debug('Setting _current.target_temp: {}'.format(cur_temps['manual_temp']))
                self._current.target_temp = cur_temps['manual_temp']
                if self._target.target_temp is None:
                    self._target.target_temp = cur_temps['manual_temp']
                _LOGGER.debug('Current _current.target_temp: {}'.format(self._current.target_temp))
            if self._current.model_no is None:
                self._current.model_no = device.get_model_number()
                self._current.firmware_rev = device.get_firmware_revision()
                self._current.software_rev = device.get_software_revision()
                self._current.manufacturer = device.get_manufacturer_name()
                _LOGGER.debug("Current Mode: {}".format(self._current.mode_value))
                _LOGGER.debug("Current Model Number: {}".format(self._current.model_no))
                _LOGGER.debug("Current Firmware Revision: {}".format(self._current.firmware_rev))
                _LOGGER.debug("Current Software Revision: {}".format(self._current.software_rev))
                _LOGGER.debug("Current Manufacturer Name: {}".format(self._current.manufacturer))
        self._thermostat.disconnect()
        if self._target.target_temp is not None:
            self._current.target_temp = self._target.target_temp
        self._current.last_seen = datetime.now()
        self._current.last_talked = datetime.now()
