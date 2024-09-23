"""Platform for SmartEVSE 2 switch integration."""

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, SWITCH_ENTITY


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the SmartEVSE 2 switch."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities([SmartEVSESwitch(coordinator, config_entry)], True)


class SmartEVSESwitch(CoordinatorEntity, SwitchEntity):
    """Representation of a SmartEVSE 2 Switch."""

    def __init__(self, coordinator, config_entry):
        """Initialize the switch."""
        super().__init__(coordinator)
        self._attr_name = f"{DOMAIN} Access"
        self._attr_unique_id = f"{config_entry.entry_id}_{SWITCH_ENTITY}"
        self._config_entry = config_entry

    @property
    def is_on(self):
        """Return true if switch is on."""
        return self.coordinator.data.get(SWITCH_ENTITY, False)

    async def async_turn_on(self, **_):
        """Turn the switch on."""
        await self.coordinator.smartevse.set_access_bit(True)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **_):
        """Turn the switch off."""
        await self.coordinator.smartevse.set_access_bit(False)
        await self.coordinator.async_request_refresh()

    @property
    def device_info(self):
        """Return device information about this SmartEVSE 2 device."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.config_entry.entry_id)},
            "name": "SmartEVSE 2",
            "manufacturer": "SmartEVSE",
            "model": "SmartEVSE 2",
        }
