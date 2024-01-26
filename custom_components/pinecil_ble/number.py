"""Platform for number integration."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import timedelta

from homeassistant import config_entries
from homeassistant.components.number import NumberEntityDescription, NumberDeviceClass, NumberEntity
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import PinecilDataUpdateCoordinator
from .entity import PinecilEntity

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=1)


@dataclass
class PinecilNumberEntityDescription(NumberEntityDescription):
    """Provide a description of a Pinecil numerical setting."""

    live_key: str | None = None
    live_max_key: str | None = None


ENTITIES = (
    PinecilNumberEntityDescription(
        key="SetTemperature",
        live_key="SetTemp",
        live_max_key="MaxTipTempAbility",
        name="Set Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=0,
        native_step=1,
    ),
    PinecilNumberEntityDescription(
        key="SleepTemperature",
        live_max_key="MaxTipTempAbility",
        name="Sleep Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_min_value=0,
        native_step=1,
    ),
)


async def async_setup_entry(
        hass: HomeAssistant,
        entry: config_entries.ConfigEntry,
        async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the numbers platform."""
    coordinator: PinecilDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        PinecilSetting(coordinator, description)
        for description in ENTITIES
    )


class PinecilSetting(PinecilEntity, NumberEntity):
    """Implementation of a Pinecil numerical setting."""
    entity_description: PinecilNumberEntityDescription

    def __init__(
            self,
            coordinator: PinecilDataUpdateCoordinator,
            description: PinecilNumberEntityDescription,
    ):
        """Initialize the setting."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.base_unique_id}-{description.key}"

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        await self.device.client.set_one_setting(self.entity_description.key, int(value))
        self.device.settings[self.entity_description.key] = int(value)

    @property
    def native_value(self) -> float | None:
        """Return current value."""
        if self.entity_description.live_key is not None:
            return self.device.live_info.get(self.entity_description.live_key, None)  # type: ignore
        return self.device.settings.get(self.entity_description.key, None)

    @property
    def native_max_value(self) -> float | None:
        """Return max value"""
        if self.entity_description.live_max_key is not None:
            return self.device.live_info.get(self.entity_description.live_max_key, None)  # type: ignore
        return self.entity_description.native_max_value
