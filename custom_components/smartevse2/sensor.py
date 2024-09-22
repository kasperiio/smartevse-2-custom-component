"""Platform for SmartEVSE 2 sensor integration."""

from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CHARGER_SENSORS


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the SmartEVSE 2 sensors."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    entities = []

    for sensor_id, details in CHARGER_SENSORS.items():
        entities.append(SmartEVSESensor(coordinator, config_entry, sensor_id, details))

    async_add_entities(entities, True)


class SmartEVSESensor(CoordinatorEntity, SensorEntity):
    """Representation of a SmartEVSE 2 Sensor."""

    def __init__(self, coordinator, config_entry, sensor_id, details):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_id = sensor_id
        self._attr_name = details["name"]
        self._attr_native_unit_of_measurement = details["unit"]
        self._attr_unique_id = f"{config_entry.entry_id}_{sensor_id}"

        if sensor_id == "state":
            self._attr_device_class = SensorDeviceClass.ENUM
            self._attr_options = ["Not connected", "Connected", "Charging"]
        elif sensor_id in ["error", "mode", "used_phases"]:
            self._attr_device_class = SensorDeviceClass.ENUM
        elif "current" in sensor_id:
            self._attr_device_class = SensorDeviceClass.CURRENT
            self._attr_state_class = SensorStateClass.MEASUREMENT
        elif sensor_id == "temperature":
            self._attr_device_class = SensorDeviceClass.TEMPERATURE
            self._attr_state_class = SensorStateClass.MEASUREMENT
        elif sensor_id == "solar_timer":
            self._attr_device_class = SensorDeviceClass.DURATION
            self._attr_state_class = SensorStateClass.MEASUREMENT
        elif sensor_id == "serial_number":
            self._attr_device_class = SensorDeviceClass.ENUM

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.coordinator.data.get(self._sensor_id)

    @property
    def device_info(self):
        """Return device information about this SmartEVSE 2 device."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.config_entry.entry_id)},
            "name": "SmartEVSE 2",
            "manufacturer": "SmartEVSE",
            "model": "SmartEVSE 2",
        }
