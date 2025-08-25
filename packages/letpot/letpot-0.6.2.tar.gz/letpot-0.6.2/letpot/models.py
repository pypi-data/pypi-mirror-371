"""Models for Python client for LetPot hydroponic gardens."""

import time as systime
from dataclasses import dataclass
from datetime import time
from enum import IntEnum, IntFlag, auto


class DeviceFeature(IntFlag):
    """Features that a LetPot device can support."""

    CATEGORY_HYDROPONIC_GARDEN = auto()
    """Features common to the hydroponic garden device category."""

    LIGHT_BRIGHTNESS_LOW_HIGH = auto()
    LIGHT_BRIGHTNESS_LEVELS = auto()
    NUTRIENT_BUTTON = auto()
    PUMP_AUTO = auto()
    PUMP_STATUS = auto()
    TEMPERATURE = auto()
    TEMPERATURE_SET_UNIT = auto()
    WATER_LEVEL = auto()


class LightMode(IntEnum):
    """Device light mode."""

    FLOWER = 0
    """Fruits/flowers light mode (red/white LEDs)."""
    VEGETABLE = 1
    """Vegetables/herbs light mode (red/blue/white LEDs)."""


class TemperatureUnit(IntEnum):
    """Device temperate sensor/display unit."""

    FAHRENHEIT = 0
    CELSIUS = 1


@dataclass
class AuthenticationInfo:
    """Authentication info model."""

    access_token: str
    access_token_expires: int
    refresh_token: str
    refresh_token_expires: int
    user_id: str
    email: str

    @property
    def is_valid(self) -> bool:
        """Returns if the access token is valid."""
        return self.access_token_expires > int(systime.time())


@dataclass
class LetPotDevice:
    """Device model."""

    serial_number: str
    name: str
    device_type: str
    is_online: bool
    is_remote: bool | None


@dataclass
class LetPotDeviceInfo:
    """Information about a device model, based on the serial number."""

    model: str
    model_name: str | None
    model_code: str | None
    features: DeviceFeature


@dataclass
class LetPotDeviceErrors:
    """Device errors model. Errors not supported by the device will be None."""

    low_water: bool | None
    low_nutrients: bool | None = None
    pump_malfunction: bool | None = None
    refill_error: bool | None = None


@dataclass
class LetPotDeviceStatus:
    """Device status model."""

    errors: LetPotDeviceErrors
    light_brightness: int | None
    light_mode: LightMode
    light_schedule_end: time
    light_schedule_start: time
    online: bool
    plant_days: int
    pump_mode: int
    pump_nutrient: int | None
    pump_status: int | None
    raw: list[int]
    system_on: bool
    system_sound: bool | None
    temperature_unit: TemperatureUnit | None = None
    temperature_value: int | None = None
    water_mode: int | None = None
    water_level: int | None = None
