"""The Pinecil integration."""
from __future__ import annotations

import logging

from bleak_retry_connector import close_stale_connections_by_address
from homeassistant.components import bluetooth
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_ADDRESS,
    CONF_MAC,
    Platform,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN
from .coordinator import PinecilDataUpdateCoordinator
from .models import PinecilWrapper

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.NUMBER]
_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up pinecil from a config entry."""
    assert entry.unique_id is not None
    hass.data.setdefault(DOMAIN, {})
    if CONF_ADDRESS not in entry.data and CONF_MAC in entry.data:
        # Bleak uses addresses not mac addresses which are actually
        # UUIDs on some platforms (MacOS).
        mac = entry.data[CONF_MAC]
        if "-" not in mac:
            mac = dr.format_mac(mac)
        hass.config_entries.async_update_entry(
            entry,
            data={**entry.data, CONF_ADDRESS: mac},
        )

    address: str = entry.data[CONF_ADDRESS]

    await close_stale_connections_by_address(address)

    ble_device = bluetooth.async_ble_device_from_address(hass, address.upper(), True)
    if not ble_device:
        raise ConfigEntryNotReady(f"Could not find Pinecil with address {address}")

    device = PinecilWrapper(address, ble_device)

    coordinator = hass.data[DOMAIN][entry.entry_id] = PinecilDataUpdateCoordinator(
        hass,
        _LOGGER,
        ble_device,
        device,
        entry.title,
        entry.unique_id,
        True,
        "Pinecil v2",
    )
    entry.async_on_unload(coordinator.async_start())
    if not await coordinator.async_wait_ready():
        raise ConfigEntryNotReady(f"{address} is not advertising state")

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
        if not hass.config_entries.async_entries(DOMAIN):
            hass.data.pop(DOMAIN)

    return unload_ok
