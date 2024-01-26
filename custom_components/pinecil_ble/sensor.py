"""Platform for sensor integration."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant import config_entries
from homeassistant.components.bluetooth import async_last_service_info
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE, UnitOfTemperature, UnitOfElectricPotential, UnitOfTime, UnitOfPower, \
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT, EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import PinecilDataUpdateCoordinator
from .entity import PinecilEntity

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=1)

ENTITIES = (
    SensorEntityDescription(
        key="LiveTemp",
        name="Tip Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="Voltage",
        name="DC Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="HandleTemp",
        name="Handle Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="PWMLevel",
        name="Power PWM",
        native_unit_of_measurement=PERCENTAGE,
        suggested_display_precision=2,
        device_class=SensorDeviceClass.POWER_FACTOR,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="PowerSource",
        name="Power Source",
        device_class=SensorDeviceClass.ENUM,
        icon="mdi:power-plug",
    ),
    SensorEntityDescription(
        key="TipResistance",
        name="Tip Resistance",
        native_unit_of_measurement="Ω",
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:omega",
    ),
    SensorEntityDescription(
        key="Uptime",
        name="Uptime",
        native_unit_of_measurement=UnitOfTime.SECONDS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="MovementTime",
        name="Last Movement Time",
        native_unit_of_measurement=UnitOfTime.MILLISECONDS,
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="MaxTipTempAbility",
        name="Max Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:thermometer-alert",
    ),
    SensorEntityDescription(
        key="VoltsTip",
        name="Raw Tip Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.MILLIVOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="HallSensor",
        name="Hall Effect Strength",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="OperatingMode",
        name="Operating Mode",
        device_class=SensorDeviceClass.ENUM,
    ),
    SensorEntityDescription(
        key="Watts",
        name="Power",
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
    coordinator: PinecilDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [
        PinecilSensor(coordinator, description)
        for description in ENTITIES
    ]
    entities.append(PinecilRSSISensor(coordinator, SensorEntityDescription(
        key="rssi",
        translation_key="bluetooth_signal",
        native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
        device_class=SensorDeviceClass.SIGNAL_STRENGTH,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
        entity_category=EntityCategory.DIAGNOSTIC,
    )))
    async_add_entities(entities)


class PinecilSensor(PinecilEntity, SensorEntity):
    """Implementation of the Pinecil sensor."""

    def __init__(
            self,
            coordinator: PinecilDataUpdateCoordinator,
            description: SensorEntityDescription,
    ):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.base_unique_id}-{description.key}"

    @property
    def native_value(self) -> float | None:
        """Return sensor state."""
        value = self.device.live_info.get(self.entity_description.key, None)  # type: ignore
        return value


class PinecilRSSISensor(PinecilSensor):
    """Representation of an RSSI sensor."""

    @property
    def native_value(self) -> str | int | None:
        """Return the state of the sensor."""
        return self.device.rssi
        if service_info := async_last_service_info(self.hass, self._address, self.coordinator.connectable):
            return service_info.rssi
        return None
