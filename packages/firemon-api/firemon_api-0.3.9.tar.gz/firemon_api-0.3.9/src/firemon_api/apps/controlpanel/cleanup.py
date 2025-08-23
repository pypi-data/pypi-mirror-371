# Standard packages
import logging

# Local packages
from firemon_api.core.errors import ControlPanelError
from firemon_api.core.endpoint import EndpointCpl
from firemon_api.core.query import Request

log = logging.getLogger(__name__)


class Cleanup(EndpointCpl):
    ep_name = "cleanup"

    def __init__(self, api, app):
        super().__init__(api, app)

    def profiles(self):
        key = "profiles"
        req = Request(
            base=self.url,
            key=key,
            session=self.session,
        ).get()
        return req

    def exec(self, action: str):
        """
        Parameters:
            action (str): analyze, clean
        """

        if not action in ("analyze", "clean"):
            raise ControlPanelError("action must be either 'analyze', 'clean'")

        key = f"cleanup/{action}"
        req = Request(
            base=self.url,
            key=key,
            session=self.session,
        ).post()
        return req
