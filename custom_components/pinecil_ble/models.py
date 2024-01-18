"""The Pinecil integration models."""

from __future__ import annotations

from typing import TypedDict
import logging

from bleak import BleakClient, BLEDevice

from pinecil import Pinecil, BLE

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

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

PowerSources = ["DC", "QC", "PD VBUS", "PD"]
OperatingModes = ["Idle", "Soldering", "Boost", "Sleeping", "Settings", "Debug"]


class PinecilWrapper:
    """Data for the Pinecil integration."""

    title: str
    coordinator: DataUpdateCoordinator

    ble_device: BLEDevice | None
    client: Pinecil | None
    result: Result

    def __init__(self, title: str, coordinator: DataUpdateCoordinator):
        self.title = title
        self.coordinator = coordinator
        self.client = None
        self.ble_device = None
        self._cached_services = None
        self.name = "Pinecil"

    async def update(self):
        if self.ble_device is None:
            return self.result

        await self.connect()
        result = await self.client.get_live_data()
        # Normalize values
        self.result = {
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
        return self.result

    def set_ble_device(self, ble_device):
        self.ble_device = ble_device

    async def connect(self) -> None:
        """Ensure connection to device is established."""
        if self.client and self.client.is_connected:
            return

        # Check again while holding the lock
        if self.client and self.client.is_connected:
            return
        try:
            self.client = Pinecil(BLE(self.ble_device.address))
        except Exception:
            _LOGGER.debug(f"{self.name}: Error connecting to device")

    def disconnect(self) -> None:
        self.client = None
        self.ble_device = None

    def _disconnected(self, client: BleakClient) -> None:
        """Disconnected callback."""
        _LOGGER.debug(
            f"{self.name}: Disconnected from device; RSSI: {self.ble_device.rssi}"
        )
        self.client = None
