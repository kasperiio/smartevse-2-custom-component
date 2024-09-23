"""The SmartEVSE 2 integration."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DEFAULT_POLL_INTERVAL, DOMAIN
from .coordinator import SmartEVSECoordinator
from .smartevse import SmartEVSE

PLATFORMS = [Platform.SENSOR, Platform.SWITCH]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up SmartEVSE 2 from a config entry."""
    host = entry.data[CONF_HOST]
    port = entry.data[CONF_PORT]
    poll_interval = entry.options.get("poll_interval", DEFAULT_POLL_INTERVAL)

    smartevse = SmartEVSE(host, port)
    try:
        await smartevse.async_setup()
    except ConfigEntryNotReady as exc:
        raise ConfigEntryNotReady from exc

    coordinator = SmartEVSECoordinator(hass, smartevse, poll_interval)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(update_listener))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Update listener."""
    await hass.config_entries.async_reload(entry.entry_id)
