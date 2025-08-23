# Standard packages
import logging

# Local packages
from firemon_api.core.app import App
from firemon_api.core.api import FiremonAPI
from firemon_api.core.endpoint import Endpoint
from firemon_api.core.response import Record
from firemon_api.core.query import Request, RequestResponse
from .centralsyslogconfigs import CentralSyslogConfig

log = logging.getLogger(__name__)


class CentralSyslog(Record):
    """Central Syslog Record

    Parameters:
        config (dict): dictionary of things values from json
        app (obj): App()
    """

    _ep_name = "central-syslog"
    _is_domain_url = True
    centralSyslogConfig = CentralSyslogConfig

    def __init__(self, config: dict, app: App):
        super().__init__(config, app)

        # not needed for `serialize` update using ep function
        self._no_no_keys = ["centralSyslogConfig"]

    def device_set(self, id: int) -> RequestResponse:
        """Set a device to this Central Syslog

        Parameters:
            id (int): device id to assign

        Returns:
            bool: True if assigned
        """
        key = f"devices/{id}"
        req = Request(
            base=self._url,
            key=key,
            session=self._session,
        )
        return req.post()

    def device_unset(self, id: int) -> RequestResponse:
        """Unset a device to this Central Syslog

        Parameters:
            id (int): device id to assign

        Returns:
            bool: True if assigned
        """
        key = f"devices/{id}"
        req = Request(
            base=self._url,
            key=key,
            session=self._session,
        )
        return req.delete()

    def csc_set(self, id: int) -> RequestResponse:
        """Set a Central Syslog Config to this CS

        Parameters:
            id (int): Central Syslog Config id to assign

        Returns:
            bool: True if assigned
        """
        key = f"config/{id}"
        req = Request(
            base=self._url,
            key=key,
            session=self._session,
        )
        return req.put()

    def devices(self):
        """
        Todo:
            return all devices assigned to this CS

        Raises:
            NotImplemented
        """
        raise NotImplemented("todo")


class CentralSyslogs(Endpoint):
    """Central Syslogs Endpoint

    Parameters:
        api (obj): FiremonAPI()
        app (obj): App()

    Keyword Arguments:
        record (obj): default `Record` object
    """

    ep_name = "central-syslog"
    _is_domain_url = True

    def __init__(self, api: FiremonAPI, app: App, record=CentralSyslog):
        super().__init__(api, app, record=record)

    def _make_filters(self, values):
        # Only a 'search' for a single value. Take all key-values
        # and use the first key's value for search query
        filters = {"search": values[next(iter(values))]}
        return filters
