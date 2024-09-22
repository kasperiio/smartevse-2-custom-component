"""Constants for the SmartEVSE 2 integration."""

DOMAIN = "smartevse2"

DEFAULT_MODBUS_PORT = 26
DEFAULT_POLL_INTERVAL = 30

CHARGER_SENSORS = {
    "state": {"name": "State", "unit": None},
    "error": {"name": "Error", "unit": None},
    "charging_current": {"name": "Charging Current", "unit": "A"},
    "mode": {"name": "Mode", "unit": None},
    "solar_timer": {"name": "Solar Timer", "unit": "s"},
    "max_charging_current": {"name": "Max Charging Current", "unit": "A"},
    "used_phases": {"name": "Used Phases", "unit": None},
    "temperature": {"name": "Temperature", "unit": "°C"},
    "serial_number": {"name": "Serial Number", "unit": None},
}

SWITCH_ENTITY = "access"
