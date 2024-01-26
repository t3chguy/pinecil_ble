"""An abstract class common to all Pinecil entities."""
from __future__ import annotations

import logging

from homeassistant.components.bluetooth.passive_update_coordinator import (
    PassiveBluetoothCoordinatorEntity,
)
from homeassistant.const import ATTR_CONNECTIONS
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.device_registry import DeviceInfo

from .const import MANUFACTURER, DOMAIN
from .coordinator import PinecilDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


class PinecilEntity(
    PassiveBluetoothCoordinatorEntity[PinecilDataUpdateCoordinator]
):
    """Generic entity encapsulating common features of Pinecil device."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: PinecilDataUpdateCoordinator) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self.device = coordinator.device
        self._last_run_success: bool | None = None
        self._address = coordinator.ble_device.address
        self._attr_device_info = DeviceInfo(
            connections={(dr.CONNECTION_BLUETOOTH, self._address)},
            manufacturer=MANUFACTURER,
            model=coordinator.model,  # Sometimes the modelName is missing from the advertisement data
            name=coordinator.device_name,
            identifiers={(DOMAIN, coordinator.device.address)},
        )
        if ":" not in self._address:
            # MacOS Bluetooth addresses are not mac addresses
            return
        # If the bluetooth address is also a mac address,
        # add this connection as well to prevent a new device
        # entry from being created when upgrading from a previous
        # version of the integration.
        self._attr_device_info[ATTR_CONNECTIONS].add(
            (dr.CONNECTION_NETWORK_MAC, self._address)
        )

    @property
    def device_info(self) -> DeviceInfo | None:
        if self.coordinator.device.device_info:
            self._attr_device_info["sw_version"] = self.coordinator.device.device_info["build"]
        return self._attr_device_info
