"""Platform for sensor integration."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
import logging

from homeassistant import config_entries
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE, UnitOfTemperature, UnitOfElectricPotential, UnitOfTime, UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import PinecilWrapper
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=1)


@dataclass
class PinecilSensorEntityDescription(SensorEntityDescription):
    """Provide a description of a Pinecil sensor."""

    # For backwards compat, allow description to override unique ID key to use
    unique_id: str | None = None


ENTITIES = (
    PinecilSensorEntityDescription(
        key="LiveTemp",
        name="Tip Temperature",
        unique_id="pinecil_live_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    PinecilSensorEntityDescription(
        key="SetTemp",
        name="Set Temperature",
        unique_id="pinecil_set_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    PinecilSensorEntityDescription(
        key="Voltage",
        name="DC Voltage",
        unique_id="pinecil_voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    PinecilSensorEntityDescription(
        key="HandleTemp",
        name="Handle Temperature",
        unique_id="pinecil_handle_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    PinecilSensorEntityDescription(
        key="PWMLevel",
        name="Power PWM",
        unique_id="pinecil_pwm_level",
        native_unit_of_measurement=PERCENTAGE,
        suggested_display_precision=2,
        device_class=SensorDeviceClass.POWER_FACTOR,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    PinecilSensorEntityDescription(
        key="PowerSource",
        name="Power Source",
        unique_id="pinecil_power_source",
        device_class=SensorDeviceClass.ENUM,
        icon="mdi:power-plug",
    ),
    PinecilSensorEntityDescription(
        key="TipResistance",
        name="Tip Resistance",
        unique_id="pinecil_tip_resistance",
        native_unit_of_measurement="Ω",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:omega",
    ),
    PinecilSensorEntityDescription(
        key="Uptime",
        name="Uptime",
        unique_id="pinecil_uptime",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    PinecilSensorEntityDescription(
        key="MovementTime",
        name="Last Movement Time",
        unique_id="pinecil_movemenet_time",
        native_unit_of_measurement=UnitOfTime.MILLISECONDS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    PinecilSensorEntityDescription(
        key="MaxTipTempAbility",
        name="Max Temperature",
        unique_id="pinecil_max_tip_temp_ability",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer-alert",
    ),
    PinecilSensorEntityDescription(
        key="VoltsTip",
        name="Raw Tip Voltage",
        unique_id="pinecil_u_volts_tip",
        native_unit_of_measurement=UnitOfElectricPotential.MILLIVOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    PinecilSensorEntityDescription(
        key="HallSensor",
        name="Hall Effect Strength",
        unique_id="pinecil_hall_sensor",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    PinecilSensorEntityDescription(
        key="OperatingMode",
        name="Operating Mode",
        unique_id="pinecil_operating_mode",
        device_class=SensorDeviceClass.ENUM,
    ),
    PinecilSensorEntityDescription(
        key="Watts",
        name="Power",
        unique_id="pinecil_power_estimate",
        native_unit_of_measurement=UnitOfPower.WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: config_entries.ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    data: PinecilWrapper = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        PinecilSensor(data, description)
        for description in ENTITIES
    )


class PinecilSensor(CoordinatorEntity, SensorEntity):
    """Implementation of the Pinecil sensor."""

    _attr_has_entity_name = True

    def __init__(self, pinecil: PinecilWrapper, description):
        """Initialize the sensor."""
        super().__init__(pinecil.coordinator)
        self.entity_description = description
        self.pinecil = pinecil

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self.pinecil.ble_device.address)},
            manufacturer="Pine64",
            name="Pinecil v2",
        )

        self._attr_unique_id = (
            f"{self.pinecil.ble_device.address}_{description.unique_id}"
        )

    @property
    def native_value(self) -> float | None:
        """Return sensor state."""
        value = self.pinecil.result[self.entity_description.key]
        return value
