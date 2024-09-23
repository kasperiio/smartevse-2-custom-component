"""SmartEVSE 2 integration."""

import asyncio
import logging

from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ConnectionException

from homeassistant.exceptions import ConfigEntryNotReady

_LOGGER = logging.getLogger(__name__)
MAX_RETRIES = 3
RETRY_DELAY = 5


class SmartEVSE:
    """SmartEVSE 2 integration class."""

    def __init__(self, host: str, port: int):
        """Initialize the SmartEVSE 2 integration."""
        self.host = host
        self.port = port
        self.client = None
        self.data = {}

    async def async_setup(self):
        """Set up the Sensorbox 1.5 client."""
        for attempt in range(MAX_RETRIES):
            try:
                self.client = AsyncModbusTcpClient(self.host, port=self.port)
                if await self.client.connect():
                    _LOGGER.debug(
                        f"Successfully connected to SmartEVSE 2 at {self.host}:{self.port}"
                    )
                    return
                else:
                    _LOGGER.warning(
                        f"Failed to connect to SmartEVSE 2 at {self.host}:{self.port}, attempt {attempt + 1}/{MAX_RETRIES}"
                    )
            except ConnectionException as exc:
                _LOGGER.warning(
                    f"Connection error to SmartEVSE 2: {exc}, attempt {attempt + 1}/{MAX_RETRIES}"
                )
            except Exception as exc:
                _LOGGER.error(
                    f"Unexpected error connecting to SmartEVSE 2: {exc}, attempt {attempt + 1}/{MAX_RETRIES}"
                )

            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(RETRY_DELAY)

        raise ConfigEntryNotReady(
            f"Failed to connect to Sensorbox 1.5 at {self.host}:{self.port} after {MAX_RETRIES} attempts"
        )

    async def async_update_data(self):
        """Update data via library."""
        if not self.client or not self.client.connected:
            await self.async_setup()

        try:
            evse_data = await self.read_evse_registers()

            self.data = evse_data
            _LOGGER.debug("Updated SmartEVSE 2 data: %s", self.data)
            return self.data
        except ConnectionException as error:
            _LOGGER.error("Error connecting to SmartEVSE 2: %s", error)
            raise

    async def read_evse_registers(self):
        """Read EVSE registers."""
        response = await self.client.read_holding_registers(
            address=0, count=12, slave=1
        )
        if not response.isError():
            return self.parse_evse_registers(response.registers)
        _LOGGER.error("Modbus error reading EVSE registers: %s", response)
        return {}

    @staticmethod
    def parse_evse_registers(registers):
        """Parse EVSE register data."""
        state_map = {0: "Not connected", 1: "Connected", 2: "Charging"}
        error_flags = {
            1: "LESS_6A",
            2: "NO_COMM",
            4: "TEMP_HIGH",
            16: "RCD",
            32: "NO_SUN",
        }
        mode_map = {0: "Normal", 1: "Smart", 2: "Solar"}

        return {
            "state": state_map.get(registers[0], "Unknown"),
            "error": ", ".join(
                [flag for bit, flag in error_flags.items() if registers[1] & bit]
            ),
            "charging_current": registers[2] / 10 if registers[2] != 0 else 0,
            "mode": mode_map.get(registers[3], "Unknown"),
            "solar_timer": registers[4],
            "access": bool(registers[5]),
            "max_charging_current": registers[7],
            "used_phases": registers[8] if registers[8] != 0 else "Undetected",
            "temperature": registers[10] - 273.15,  # Convert Kelvin to Celsius
            "serial_number": registers[11],
        }

    async def set_access_bit(self, value):
        """Set access bit."""
        try:
            result = await self.client.write_register(
                address=5, value=int(value), slave=1
            )
            if result.isError():
                _LOGGER.error("Error setting access bit: %s", result)
            else:
                _LOGGER.debug("Access bit set to %s", value)
                await self.async_update_data()
        except Exception as e:
            _LOGGER.error("Error setting access bit: %s", str(e))

    async def async_close(self):
        """Close the Modbus client."""
        if self.client:
            await self.client.close()
