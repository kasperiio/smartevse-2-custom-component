"""Config flow for SmartEVSE 2 integration."""

from __future__ import annotations

import asyncio
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import DEFAULT_MODBUS_PORT, DEFAULT_POLL_INTERVAL, DOMAIN

STEP_MODBUS_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PORT, default=DEFAULT_MODBUS_PORT): int,
    }
)

STEP_DEVICE_SCHEMA = vol.Schema(
    {
        vol.Required("device"): vol.In([]),  # Will be populated dynamically
        vol.Optional("poll_interval", default=DEFAULT_POLL_INTERVAL): int,
    }
)


async def validate_modbus_connection(host: str, port: int) -> None:
    """Validate the Modbus connection."""
    from pymodbus.client import AsyncModbusTcpClient
    from pymodbus.exceptions import ConnectionException, ModbusException

    client = AsyncModbusTcpClient(host, port=port)
    try:
        await client.connect()
        if not client.connected:
            raise CannotConnect("Failed to connect to the Modbus server")

        # Try to read a register to confirm communication
        result = await client.read_holding_registers(address=0, count=1, slave=1)
        if result.isError():
            raise CannotConnect(f"Error reading register: {result}")
    except ConnectionException as conn_err:
        raise CannotConnect(f"Connection error: {conn_err}") from conn_err
    except ModbusException as modbus_err:
        raise CannotConnect(f"Modbus error: {modbus_err}") from modbus_err
    except asyncio.TimeoutError:
        raise CannotConnect("Connection timed out") from None
    except Exception as err:
        raise CannotConnect(f"Unexpected error: {err}") from err
    finally:
        client.close()


async def discover_smartevse_devices(host: str, port: int) -> list[dict[str, Any]]:
    """Discover SmartEVSE devices on the Modbus network."""
    from pymodbus.client import AsyncModbusTcpClient

    client = AsyncModbusTcpClient(host, port=port)
    devices = []
    try:
        await client.connect()
        for slave_id in range(1, 248):  # Modbus supports up to 247 devices
            try:
                result = await client.read_holding_registers(
                    address=0, count=1, slave=slave_id
                )
                if not result.isError():
                    # Attempt to read device-specific information
                    info = await client.read_holding_registers(
                        address=10, count=2, slave=slave_id
                    )
                    if not info.isError():
                        serial_number = (info.registers[0] << 16) | info.registers[1]
                        devices.append(
                            {
                                "slave_id": slave_id,
                                "serial_number": serial_number,
                            }
                        )
            except Exception:
                continue  # Move to the next slave ID if there's an error
    finally:
        client.close()
    return devices


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SmartEVSE 2."""

    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        self.modbus_config = None
        self.devices = []

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        return await self.async_step_modbus()

    async def async_step_modbus(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the Modbus connection step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                await validate_modbus_connection(
                    user_input[CONF_HOST], user_input[CONF_PORT]
                )
                self.modbus_config = user_input
                return await self.async_step_device()
            except CannotConnect as conn_err:
                errors["base"] = "cannot_connect"
                errors["details"] = str(conn_err)
            except Exception:
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="modbus", data_schema=STEP_MODBUS_SCHEMA, errors=errors
        )

    async def async_step_device(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the device selection step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            # Combine Modbus config and selected device info
            full_config = {**self.modbus_config, **user_input}
            return self.async_create_entry(
                title=f"SmartEVSE-2 ({full_config['device']})", data=full_config
            )

        if not self.devices:
            try:
                self.devices = await discover_smartevse_devices(
                    self.modbus_config[CONF_HOST], self.modbus_config[CONF_PORT]
                )
                if not self.devices:
                    return self.async_abort(reason="no_devices_found")
            except Exception:
                return self.async_abort(reason="device_discovery_failed")

        device_schema = vol.Schema(
            {
                vol.Required("device"): vol.In(
                    {
                        f"{device['slave_id']}": f"SmartEVSE (SN: {device['serial_number']})"
                        for device in self.devices
                    }
                ),
                vol.Optional("poll_interval", default=DEFAULT_POLL_INTERVAL): int,
            }
        )

        return self.async_show_form(
            step_id="device", data_schema=device_schema, errors=errors
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for SmartEVSE 2 integration."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        options = {
            vol.Optional(
                "poll_interval",
                default=self.config_entry.options.get(
                    "poll_interval", DEFAULT_POLL_INTERVAL
                ),
            ): int,
        }

        return self.async_show_form(step_id="init", data_schema=vol.Schema(options))


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidHost(HomeAssistantError):
    """Error to indicate there is an invalid hostname."""
