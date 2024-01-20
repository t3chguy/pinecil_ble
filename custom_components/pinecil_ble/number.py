"""Platform for number integration."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
import logging

from homeassistant import config_entries
from homeassistant.components.number import NumberEntityDescription, NumberDeviceClass, NumberEntity
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import PinecilWrapper
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=1)


@dataclass
class PinecilNumberEntityDescription(NumberEntityDescription):
    """Provide a description of a Pinecil numerical setting."""

    # For backwards compat, allow description to override unique ID key to use
    unique_id: str | None = None
    read_key: str | None = None


ENTITIES = (
    PinecilNumberEntityDescription(
        key="SetTemperature",
        read_key="SetTemp",
        name="Set Temperature",
        unique_id="pinecil_set_temp",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=0,
        native_max_value=500,  # TODO
        native_step=1,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: config_entries.ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the numbers platform."""
    data: PinecilWrapper = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        PinecilSetting(data, description)
        for description in ENTITIES
    )


class PinecilSetting(CoordinatorEntity, NumberEntity):
    """Implementation of a Pinecil numerical setting."""

    _attr_has_entity_name = True

    def __init__(self, pinecil: PinecilWrapper, description: PinecilNumberEntityDescription):
        """Initialize the setting."""
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

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        await self.pinecil.client.set_one_setting(self.entity_description.key, int(value))

    @property
    def native_value(self) -> float | None:
        """Return sensor state."""
        value = self.pinecil.result[self.entity_description.read_key]
        return value
