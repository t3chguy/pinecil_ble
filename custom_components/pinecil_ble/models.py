"""The Pinecil integration models."""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass
from typing import TypedDict, Dict

from bleak import BLEDevice, AdvertisementData
from pinecil import Pinecil, BLE

from custom_components.pinecil_ble.const import SERVICE_UUID

_LOGGER = logging.getLogger(__name__)

Result = TypedDict("Result", {
    "LiveTemp": int,
    "SetTemp": int,
    "Voltage": int,
    "HandleTemp": int,
    "PWMLevel": float,
    "PowerSource": str,
    "TipResistance": int,
    "Uptime": int,
    "MovementTime": int,
    "MaxTipTempAbility": int,
    "VoltsTip": int,
    "HallSensor": int,
    "OperatingMode": str,
    "Watts": int,
})

PinecilInfo = TypedDict("PinecilInfo", {
    "name": str,
    "id": str,
    "build": str
})

PowerSources = ["DC", "QC", "PD VBUS", "PD"]
OperatingModes = ["Idle", "Soldering", "Boost", "Sleeping", "Settings", "Debug"]


@dataclass
class PinecilAdvertisement:
    """Pinecil advertisement."""

    address: str
    device: BLEDevice
    model: str
    rssi: int


def parse_advertisement_data(
        device: BLEDevice,
        advertisement_data: AdvertisementData,
        model: str,
) -> PinecilAdvertisement | None:
    """Parse advertisement data."""
    if SERVICE_UUID not in advertisement_data.service_uuids:
        return None

    return PinecilAdvertisement(device.address, device, model, advertisement_data.rssi)


class PinecilWrapper:
    """Data for the Pinecil integration."""

    device_info: PinecilInfo = None
    live_info: Result = {}
    settings: Dict[str, int] = {}

    def __init__(
            self,
            address: str,
            ble_device: BLEDevice = None,
    ):
        self.address = address
        self._device = None
        self.client: Pinecil = None
        self._last_ibeacon = None
        self.rssi: int = None
        self._poll_needed = False

        self._connect_lock = asyncio.Lock()
        self.connection_timeout = 40

        if ble_device:
            self.set_ble_device(ble_device)

    async def update(self):
        if self.client is None:
            _LOGGER.info(f"Pinecil update_state no client {self.live_info}")
            return self.live_info

        _LOGGER.info(f"Pinecil connecting")
        await self.connect()
        result = await self.client.get_live_data()
        # Normalize values
        self.live_info = {
            "LiveTemp": result["LiveTemp"],
            "SetTemp": result["SetTemp"],
            "Voltage": result["Voltage"] / 10,
            "HandleTemp": result["HandleTemp"] / 10,
            "PWMLevel": result["PWMLevel"] * 100 / 255.0,
            "PowerSource": PowerSources[result["PowerSource"]],
            "TipResistance": result["TipResistance"] / 10,
            "Uptime": result["Uptime"] / 10,
            "MovementTime": result["MovementTime"] / 10,
            "MaxTipTempAbility": result["MaxTipTempAbility"],
            "VoltsTip": result["uVoltsTip"] / 1000,  # microVolts
            "HallSensor": result["HallSensor"],  # units?
            "OperatingMode": OperatingModes[result["OperatingMode"]],
            "Watts": result["Watts"] / 10,
        }
        return self.live_info

    def set_ble_device(self, ble_device: BLEDevice = None):
        _LOGGER.info(f"Pinecil set_ble_device {ble_device}")
        if ble_device:
            self.client = Pinecil(BLE(ble_device.address))
        else:
            self.client = Pinecil(BLE(address=self.address))

    async def connect(self) -> None:
        _LOGGER.debug(f"Pinecil: Connecting")

        """Ensure connection to device is established."""
        if self.client and self.client.is_connected:
            return

        async with self._connect_lock:
            await asyncio.sleep(0.01)
            # Check again while holding the lock
            if self.client and self.client.is_connected:
                return
            try:
                await self.client.connect()
                _LOGGER.debug(f"Pinecil: Connected! Fetching settings")
                self.settings = await self.client.get_all_settings()
                self.device_info = await self.client.get_info()
                _LOGGER.debug(f"Pinecil: Connected! Settings fetched")
            except Exception:
                _LOGGER.debug(f"Pinecil: Error connecting to device")

    async def disconnect(self) -> None:
        if self.client and self.client.is_connected:
            _LOGGER.info(f"Pinecil disconnecting...")
            try:
                self.client = None
                self._device = None
                # await self.client.disconnect()
                _LOGGER.info("Pinecil disconnected")
            except Exception as e:
                _LOGGER.error(f"Error while disconnecting")
                _LOGGER.exception(e)

    def update_from_advertisement(self, advertisement: PinecilAdvertisement) -> None:
        """Update device data from advertisement."""
        # Only accept advertisements if the data is not missing
        # if we already have an advertisement with data
        self.set_ble_device(advertisement.device)

    def parse_advertisement_data(self, device: BLEDevice, advertisement_data: AdvertisementData):
        if device.address == self.address:
            _LOGGER.info(f"Pinecil: {device.address}, RSSI: {advertisement_data.rssi}")
            if self.just_got_beacon:
                _LOGGER.info(f"Ignoring duplicate beacon from Pinecil {device.address}")
                return
            self.set_ble_device(device)
            self.rssi = advertisement_data.rssi
            if not self.live_info:
                self._poll_needed = True
            return
        else:
            _LOGGER.error(f"called with invalid address {device.address}")

    @property
    def just_got_beacon(self):
        if self._last_ibeacon is None:
            self._last_ibeacon = time.time()
            return False
        seen_recently = time.time() - self._last_ibeacon <= 1
        if not seen_recently:
            self._last_ibeacon = time.time()
        return seen_recently

    def poll_needed(self, seconds_since_last_poll=None):
        _LOGGER.debug(f"Pinecil poll_needed {self._poll_needed} {seconds_since_last_poll}")
        return self._poll_needed or seconds_since_last_poll is None or seconds_since_last_poll > 1
