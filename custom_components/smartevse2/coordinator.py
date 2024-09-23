"""DataUpdateCoordinator for SmartEVSE 2."""

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN
from .smartevse import SmartEVSE

_LOGGER = logging.getLogger(__name__)


class SmartEVSECoordinator(DataUpdateCoordinator):
    """Class to manage fetching SmartEVSE 2 data."""

    def __init__(
        self, hass: HomeAssistant, smartevse: SmartEVSE, poll_interval: int
    ) -> None:
        """Initialize global SmartEVSE 2 data updater."""
        self.smartevse = smartevse
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=poll_interval),
        )

    async def _async_update_data(self):
        """Fetch data from SmartEVSE 2."""
        try:
            return await self.smartevse.async_update_data()
        except ConfigEntryAuthFailed as err:
            raise ConfigEntryAuthFailed from err
        except Exception as err:
            raise UpdateFailed(f"Error communicating with SmartEVSE 2: {err}")
