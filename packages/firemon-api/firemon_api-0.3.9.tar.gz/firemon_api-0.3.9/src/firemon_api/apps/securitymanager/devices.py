# Standard packages
import logging
import uuid
from urllib.parse import quote
from typing import Literal
from typing import Optional


# Local packages
from firemon_api.core.app import App
from firemon_api.core.api import FiremonAPI
from firemon_api.core.endpoint import Endpoint
from firemon_api.core.errors import SecurityManagerError
from firemon_api.core.response import Record, JsonField
from firemon_api.core.query import Request, RequestResponse, RequestError
from firemon_api.apps.structure import ApaInterface
from firemon_api.apps.structure import RuleRecRequirement
from .access_path import AccessPath
from .devicepacks import DevicePack
from .collectionconfigs import CollectionConfigs
from .maps import Maps
from .revisions import Revision, Revisions, NormalizedData
from .routes import Routes
from .rulerec import RuleRecommendation
from .zones import Zones
from firemon_api.apps.structure.device import RuleDoc

log = logging.getLogger(__name__)


class DevicesError(SecurityManagerError):
    pass


class Device(Record):
    """Device Record

    Parameters:
        config (dict): dictionary of things values from json
        app (obj): App()

    Attributes:
        cc: CollectionConfigs()
        revisions: Revisions()

    Examples:

        Get device by ID

        >>> dev = fm.sm.devices.get(21)
        >>> dev
        vSRX-2

        Show configuration data

        >>> dict(dev)
        {'id': 21, 'domainId': 1, 'name': 'vSRX-2',
            'description': 'regression test SRX', ...}

        List all collection configs that device can use

        >>> dev.cc.all()
        [21, 46]
        >>> cc = dev.cc.get(46)

        List all revisions associated with device

        >>> dev.revisions.all()
        [76, 77, 108, 177, 178]

        Get the latest revision

        >>> rev = dev.revisions.filter(latest=True)[0]
        178
    """

    _ep_name = "device"
    _is_domain_url = True
    extendedSettingsJson = JsonField
    devicePack = DevicePack

    def __init__(self, config: dict, app: App):
        super().__init__(config, app)

        self._no_no_keys = [
            "securityConcernIndex",
            "gpcComputeDate",
            "gpcDirtyDate",
            "gpcImplementDate",
            "gpcStatus",
        ]

        # Add attributes to Record() so we can get more info
        self.collectionconfigs = CollectionConfigs(
            self._app.api,
            self._app,
            device_id=config["id"],
            devicepack_id=config["devicePack"]["id"],
        )
        self.maps = Maps(self._app.api, self._app, device_id=config["id"])
        self.revisions = Revisions(self._app.api, self._app, device_id=config["id"])
        self.routes = Routes(self._app.api, self._app, device_id=config["id"])
        self.zones = Zones(self._app.api, self._app, device_id=config["id"])

    def save(self, retrieve: bool = False) -> RequestResponse:
        """Saves changes to an existing object.
        Checks the state of `_diff` and sends the entire
        `serialize` to Request.put().

        Keyword Arguments:
            retrieve (bool): Perform manual retrieval on save

        Returns:
            bool: True if PUT request was successful.

        Examples:

            >>> dev = fm.sm.devices.get(name='vsrx3')
            >>> dev.description
            AttributeError: 'Device' object has no attribute 'description'
            >>> dev.attr_set('description','Virtual SRX - DC 3')
            >>> dev.save()
            True
            >>>
        """
        if self.id:
            diff = self._diff()
            if diff:
                serialized = self.serialize()
                # Make sure this is set appropriately. Cannot change.
                serialized["id"] = self._config["id"]
                # Check if parents or children `Records` weren't overwritten.
                if not "parents" in diff:
                    serialized["parents"] = self._config["parents"]
                if not "children" in diff:
                    serialized["children"] = self._config["children"]
                # Put all this redundant nonsense back in. Why api, why?
                serialized["devicePack"] = self._config["devicePack"]
                # log.debug(serialized)
                params = {"manualRetrieval": retrieve}
                req = Request(
                    base=self._url,
                    filters=params,
                    session=self._session,
                )
                req.put(serialized)
                return True

        return False

    def update(self, data: dict, retrieve: bool = False) -> RequestResponse:
        """Update an object with a dictionary.
        Accepts a dict and uses it to update the record and call save().
        For nested and choice fields you'd pass an int the same as
        if you were modifying the attribute and calling save().

        Parameters:
            data (dict): Dictionary containing the k/v to update the
            record object with.

        Returns:
            bool: True if PUT request was successful.

        Example:

            >>> dev = fm.sm.devices.get(1)
            >>> dev.update({
            ...   "name": "foo2",
            ...   "description": "barbarbaaaaar",
            ... })
            True
        """

        for k, v in data.items():
            self.attr_set(k, v)

        return self.save(retrieve=retrieve)

    def delete(
        self,
        deleteChildren: bool = False,
        a_sync: bool = False,
        sendNotification: bool = False,
        postProcessing: bool = True,
    ) -> RequestResponse:
        """Delete the device (and child devices)

        Keyword Arguments:
            deleteChildren (bool): delete all associated child devices
            a_sync (bool): ???
            sendNotification (bool): ???
            postProcessing (bool): ???

        Returns:
            bool

        Examples:

            >>> dev = fm.sm.devices.get(17)
            >>> dev
            CSM-2

            Delete device and all child devices
            >>> dev.delete(deleteChildren=True)
            True
        """

        filters = {
            "deleteChildren": deleteChildren,
            "async": a_sync,
            "sendNotification": sendNotification,
            "postProcessing": postProcessing,
        }

        req = Request(
            base=self._url,
            filters=filters,
            session=self._session,
        )
        return req.delete()

    def apa_starting_interface(
        self,
        *,
        source_ip: str,
        dest_ip: str,
        protocol: int,
        source_port: int = None,
        dest_port: int = None,
        icmp_type: int = None,
        icmp_code: int = None,
        user: str = None,
        users: list[str] = None,
        application: str = None,
        applications: list[str] = None,
        url_matchers: list[str] = None,
        profiles: list[str] = None,
        accept: bool = None,
        recommend: bool = None,
    ) -> list[ApaInterface]:
        """Get apa guessed starting interface

        Parameters:
            source_ip (str): ipv4/6 address ex: '192.168.202.95'
            dest_ip (str): ipv4/6 address ex: '192.168.203.66'
            protocol (int): for all practical purposes it is only 1 (icmp), 6 (tcp), 17 (udp), 58 (icmpv6)

        Keyword Arguments:
            source_port (int): source port
            dest_port (int): destination port. required if the protocol has ports
            icmp_type (int): apparently not required
            icmp_code (int): apparently not required
            user (str): User L7 (ver. 9.10+)
            users (list[str]): Users L7 (ver. 9.12+)
            application (str): Application L7 (ver. 9.10+)
            applications (list[str]): Applications L7 (ver. 9.12+)
            url_matchers (list[str]): URL Matcher L7 (ver. 9.12+)
            profiles (list[str]): Profiles L7 (ver. 9.12+)
            accept (bool): Rule Rec
            recommend (bool): Rule Rec

        Return:
            list (ApaInterface): a list of possible interfaces
        """

        key = "apa/starting-interface"
        json = {
            "testIpPacket": {
                "sourceIp": source_ip,
                "destinationIp": dest_ip,
                "protocol": protocol,
            },
        }
        if isinstance(source_port, int):
            json["testIpPacket"]["sourcePort"] = source_port
        if isinstance(dest_port, int):
            json["testIpPacket"]["port"] = dest_port
        if isinstance(icmp_type, int):
            json["testIpPacket"]["icmpType"] = icmp_type
        if isinstance(icmp_code, int):
            json["testIpPacket"]["icmpCode"] = icmp_code
        if isinstance(user, str):
            json["testIpPacket"]["user"] = user
        if isinstance(users, list):
            json["testIpPacket"]["users"] = users
        if isinstance(application, str):
            json["testIpPacket"]["application"] = application
        if isinstance(applications, list):
            json["testIpPacket"]["applications"] = applications
        if isinstance(url_matchers, list):
            json["testIpPacket"]["urlMatchers"] = url_matchers
        if isinstance(profiles, list):
            json["testIpPacket"]["profiles"] = profiles
        if isinstance(accept, bool):
            json["testIpPacket"]["accept"] = accept
        if isinstance(recommend, bool):
            json["testIpPacket"]["recommend"] = recommend

        req = Request(
            base=self._url,
            key=key,
            session=self._session,
        )
        return req.put(json=json)

    def apa(
        self,
        *,
        source_ip: str,
        dest_ip: str,
        protocol: int,
        interface: str = None,
        source_port: int = None,
        dest_port: int = None,
        icmp_type: int = None,
        icmp_code: int = None,
        user: str = None,
        users: list[str] = None,
        application: str = None,
        applications: list[str] = None,
        url_matchers: list[str] = None,
        profiles: list[str] = None,
        accept: bool = None,
        recommend: bool = None,
    ) -> AccessPath:
        """Perform an Access Path Analysis query

        Parameters:
            interface (str): Inbound interface name ex: 'ethernet1/2'. You will likely want to provide this.
            source_ip (str): ipv4/6 address ex: '192.168.202.95'
            dest_ip (str): ipv4/6 address ex: '192.168.203.66'
            protocol (int): for all practical purposes it is only 1 (icmp), 6 (tcp), 17 (udp), 58 (icmpv6)

        Keyword Arguments:
            source_port (int): source port
            dest_port (int): destination port. required if the protocol has ports
            icmp_type (int): apparently not required
            icmp_code (int): apparently not required
            user (str): User L7 (ver. 9.10+)
            users (list[str]): Users L7 (ver. 9.12+)
            application (str): Application L7 (ver. 9.10+)
            applications (list[str]): Applications L7 (ver. 9.12+)
            url_matchers (list[str]): URL Matcher L7 (ver. 9.12+)
            profiles (list[str]): Profiles L7 (ver. 9.12+)
            accept (bool): Rule Rec
            recommend (bool): Rule Rec

        Return:
            AccessPath: as always AccessPath().dump() gets you the dictionary. But the AccessPath object gets some parsed data. `events` as a list, `packet_result` as a dictionary.
        """
        kwargs = {
            "source_ip": source_ip,
            "dest_ip": dest_ip,
            "protocol": protocol,
        }
        json = {
            "testIpPacket": {
                "sourceIp": source_ip,
                "destinationIp": dest_ip,
                "protocol": protocol,
            },
        }
        if isinstance(source_port, int):
            json["testIpPacket"]["sourcePort"] = source_port
            kwargs["source_port"] = source_port
        if isinstance(dest_port, int):
            json["testIpPacket"]["port"] = dest_port
            kwargs["dest_port"] = dest_port
        if isinstance(icmp_type, int):
            json["testIpPacket"]["icmpType"] = icmp_type
            kwargs["icmp_type"] = icmp_type
        if isinstance(icmp_code, int):
            json["testIpPacket"]["icmpCode"] = icmp_code
            kwargs["icmp_code"] = icmp_code
        if isinstance(user, str):
            json["testIpPacket"]["user"] = user
            kwargs["user"] = user
        if isinstance(users, list):
            json["testIpPacket"]["users"] = users
            kwargs["users"] = users
        if isinstance(application, str):
            json["testIpPacket"]["application"] = application
            kwargs["application"] = application
        if isinstance(applications, list):
            json["testIpPacket"]["applications"] = applications
            kwargs["applications"] = applications
        if isinstance(url_matchers, list):
            json["testIpPacket"]["urlMatchers"] = url_matchers
            kwargs["url_matchers"] = url_matchers
        if isinstance(profiles, list):
            json["testIpPacket"]["profiles"] = profiles
            kwargs["profiles"] = profiles
        if isinstance(accept, bool):
            json["testIpPacket"]["accept"] = accept
            kwargs["accept"] = accept
        if isinstance(recommend, bool):
            json["testIpPacket"]["recommend"] = recommend
            kwargs["recommend"] = recommend

        if isinstance(interface, str):
            json["inboundInterface"] = interface
        else:
            si = self.apa_starting_interface(**kwargs)
            if len(si) != 1:
                raise DevicesError(
                    f"Found {len(si)} potential starting interfaces. Must provide specific value."
                )
            json["inboundInterface"] = si[0].get("intfName", None)

        key = "apa"

        req = Request(
            base=self._url,
            key=key,
            headers={
                "Content-Type": "application/json;",
                "accept": "application/json;",  # xml to get graphml
            },
            session=self._session,
        )
        return AccessPath(req.put(json=json), self, self.id, apa_request=json)

    def rev_export(self, meta: bool = True) -> RequestResponse:
        """Export latest configuration files as a zip file

        Support files include all NORMALIZED data and other meta data.
        Raw configs include only those files as found by Firemon
        during a retrieval.

        Keyword Arguments:
            meta (bool): True gets a SUPPORT file. False is Raw only

        Returns:
            bytes: file

        Examples:

            >>> import os
            >>> dev = fm.sm.devices.get(name='vsrx-2')
            >>> support = dev.rev_export()
            >>> with open('support.zip', 'wb') as f:
            ...   f.write(support)
            ...
            38047
        """
        if meta:
            key = "export"
        else:
            key = "export/config"
        req = Request(
            base=self._url,
            key=key,
            session=self._session,
        )
        return req.get_content()

    def config_import(
        self,
        f_list: list,
        change_user=None,
        correlation_id=None,
        action: Literal[
            "AUTOMATIC", "INSTALL", "MANUAL", "SAVE", "SCHEDULED", "MIGRATE", "IMPORT"
        ] = "IMPORT",
        file_type: Literal[
            "OS", "LOG", "CONFIG", "NORMALIZED", "BEHAVIOR", "LEGACY_NORMALIZED_XML"
        ] = "CONFIG",
    ) -> RequestResponse:
        """Import config files for device to create a new revision

        Warning:
            The API seems buggy and regardless of what `file_type` you attempt
            they will always be sent to the `normalizer`. Use `support_import` if you
            need to upload `.NORMALIZED` files to create a new revision.

        Parameters:
            f_list (list): a list of tuples. Tuples are intended to uploaded as a multipart form using 'requests'. format of the data in the tuple is: ('<file-name>', ('<file-name>', open(<path_to_file>, 'rb'), 'text/plain'))

        Keyword Arguments:
            change_user (str): A name for display field
            correlation_id (str): A UUID1
            action (str): AUTOMATIC, INSTALL, MANUAL, SAVE, SCHEDULED, MIGRATE, IMPORT
            file_type (str): OS, LOG, CONFIG, NORMALIZED, BEHAVIOR, LEGACY_NORMALIZED_XML

        Returns:
            bool

        Examples:

            >>> import os
            >>> dev = fm.sm.devices.get(name='vsrx-2')
            >>> dir = '/path/to/config/files/'
            >>> f_list = []
            >>> for fn in os.listdir(dir):
            ...     path = os.path.join(dir, fn)
            ...     f_list.append((fn, (fn, open(path, 'rb'), 'text/plain')))
            >>> dev.config_import(f_list)

        """
        if not change_user:
            # Not needed as server will go on its merry way with nothing
            change_user = f"{self._app.api.username}:[firemon_api]"
        if not correlation_id:
            # Not needed as server will generate one for us. But... whatever.
            correlation_id = str(uuid.uuid1())
        filters = {
            "action": action,
            "filetype": file_type,
            "changeUser": change_user,
            "correlationId": correlation_id,
        }
        key = "rev"

        req = Request(
            base=self._url,
            key=key,
            filters=filters,
            session=self._session,
        )
        return req.post(files=f_list)

    def support_import(
        self, zip_file: bytes, renormalize: bool = False
    ) -> RequestResponse:
        """Import a 'support' file, a zip file with the expected device
        config files along with 'NORMALIZED' and meta-data files. Use this
        function and set 'renormalize = True' and mimic 'import_config'.

        Notes:
            Device packs must match from the support files descriptor.json

        Parameters:
            zip_file (bytes): bytes that make a zip file

        Keyword Arguments:
            renormalize (bool): defualt (False). Tell system to re-normalize from
            config (True) or use imported 'NORMALIZED' files (False)

        Returns:
            bool

        Examples:

            >>> dev = fm.sm.devices.get(name='vsrx-2')
            >>> fn = '/path/to/file/vsrx-2.zip'
            >>> with open(fn, 'rb') as f:
            >>>     zip_file = f.read()
            >>> dev.support_import(zip_file)

            >>> dev = fm.sm.devices.get(name='vsrx-2')
            >>> fn = 'vsrx-2.zip'
            >>> path = '/path/to/file/vsrx-2.zip'
            >>> dev.support_import((fn, open(path, 'rb'))
        """
        filters = {"renormalize": renormalize}
        files = {"file": zip_file}
        key = "import"

        req = Request(
            base=self._url,
            key=key,
            filters=filters,
            session=self._session,
        )
        return req.post(files=files)

    def retrieval_exec(self, debug: bool = False) -> RequestResponse:
        """Execute a manual retrieval for device.

        Keyword Arguments:
            debug (bool): Unsure what this does

        Returns:
            RequestResponse
        """
        key = "manualretrieval"
        filters = {"debug": debug}

        req = Request(
            base=self._url,
            key=key,
            filters=filters,
            session=self._session,
        )
        return req.post()

    def rule_usage(self, type: Literal["total", "daily"] = "total") -> RequestResponse:
        """Get rule usage for device.
        total hits for all rules on the device.

        Keyword Arguments:
            type (Literal["daly", "total"]): either 'total' or 'daily'

        Return:
            dict

                daily:

                    {'hitDate': '....', 'totalHits': int}

                total:

                    {'totalHits': int}
        """
        key = f"ruleusagestat/{type}"
        req = Request(
            base=self._url,
            key=key,
            session=self._session,
        )
        return req.get()

    def nd_problem(self) -> RequestResponse:
        """Retrieve problems with latest normalization

        Return:
            RequestResponse
        """
        key = f"device/{self.id}/nd/problem"
        req = Request(
            base=self._app_url,
            key=key,
            session=self._session,
        )
        return req.get()

    def nd_latest_get(self) -> NormalizedData:
        """Gets the latest revision as a fully parsed object

        Return:
            NormalizedData
        """
        key = "rev/latest/nd/all"
        req = Request(
            base=self._url,
            key=key,
            session=self._session,
        )
        return NormalizedData(req.get(), self._app)

    def rev_latest_get(self) -> Revision:
        """Gets the latest revision object

        Return:
            Revision
        """
        key = "rev/latest"
        req = Request(
            base=self._url,
            key=key,
            session=self._session,
        )
        return Revision(req.get(), self._app)

    def ssh_key_remove(self) -> RequestResponse:
        """Remove ssh key from all Collectors for Device.

        Notes:
            SSH Key location: /var/lib/firemon/dc/.ssh/known_hosts

        Returns:
            bool
        """
        key = "sshhostkey"
        req = Request(
            base=self._url,
            key=key,
            session=self._session,
        )
        return req.put()

    def capabilities(self) -> RequestResponse:
        """Retrieve device capabilities

        Returns:
            dict
        """
        key = f"capabilities"
        req = Request(
            base=self._url,
            key=key,
            session=self._session,
        )
        return req.get()

    def status(self) -> RequestResponse:
        """Retrieve device status

        Returns:
            dict
        """
        key = f"status"
        req = Request(
            base=self._url,
            key=key,
            session=self._session,
        )
        return req.get()

    def health(self) -> RequestResponse:
        """Retrieve device health testSuites

        Returns:
            dict
        """
        key = f"health"
        req = Request(
            base=self._url,
            key=key,
            session=self._session,
        ).get()
        return req.get("testSuites", [])

    def license_add(
        self, product_key: Literal["SM", "PO", "PP", "RA", "GPC", "AUTO"]
    ) -> RequestResponse:
        """License device for feature

        Parameters:
            product_key (Literal["SM", "PO", "PP", "RA", "GPC", "AUTO"])

        Returns:
            bool
        """
        key = f"device/license/{self.id}/product/{product_key}"
        req = Request(
            base=self._domain_url,
            key=key,
            session=self._session,
        )
        try:
            return req.post()
        except RequestError as e:
            if e.req.status_code == 409:
                # Device is already licensed. We good.
                return True
            else:
                raise e

    def license_del(
        self, product_key: Literal["SM", "PO", "PP", "RA", "GPC", "AUTO"]
    ) -> RequestResponse:
        """License device for feature

        Parameters:
            product_key (Literal["SM", "PO", "PP", "RA", "GPC", "AUTO"]): SM, PO, PP, RA, GPC, AUTO

        Returns:
            bool
        """
        key = f"device/license/{self.id}/product/{product_key}"
        req = Request(
            base=self._domain_url,
            key=key,
            session=self._session,
        )
        return req.delete()

    def ruledoc_update(self, config: RuleDoc) -> RequestResponse:
        """Update Rule Documentation - meta data

        Parameters:
            config (RuleDoc): all the properties that make up all the rule doc updates. This can be gnarly looking

        Return:
            bool
        """

        key = "ruledoc"
        req = Request(
            base=self._url,
            key=key,
            session=self._session,
        )
        return req.put(json=config)

    def ruledoc_get(self, rule_id: str) -> RequestResponse:
        """Get RuleDoc for given rule id

        Parameters:
            rule_id (str): guid string data

        Return:
            dict
        """
        key = f"rule/{rule_id}/ruledoc"
        req = Request(
            base=self._url,
            key=key,
            session=self._session,
        )
        return req.get()

    def rule_rec(
        self,
        requirement: RuleRecRequirement,
        license_category: Optional[
            Literal[
                "LOG_SERVERS",
                "ROUTERS",
                "OPERATING_SYSTEMS",
                "FIREWALLS",
                "FIREWALL_MANAGER_MODULES",
                "EDGE_DEVICES",
                "GENERIC_DEVICES",
                "TRAFFIC_MANAGER_MODULES",
                "UNKNOWN",
                "SALES_ONLY_SMLO_HA",
                "SALES_ONLY_SMSO_HA",
                "SALES_ONLY_SMM_HA",
                "POLICY_PLANNER",
                "RISK",
                "POLICY_OPTIMIZER",
                "INSIGHT",
                "GLOBAL_POLICY_CONTROLLER",
                "AUTOMATION",
                "LICENSE_NOT_REQUIRED",
            ]
        ] = None,
        strategy: Literal["NAME_PATTERN", "HITCOUNT", "REFERENCES", "NONE"] = "NONE",
        force_tiebreak: Optional[bool] = None,
        pattern: Optional[str] = None,
    ) -> RuleRecommendation:
        """Make a Security Manager rule recomendation

        Parameters:
            requriments (RuleRecRequirement): dict of requirements

        Keyword Arguments:
            license_category (Literal[...])
            strategy (Literal[...])
            force_tiebreak (bool)
            pattern (str)

        Returns:
            RuleRecommendation

        """
        key = f"rulerec"
        filters = {}
        if license_category:
            filters["licenseCategory"] = license_category
        if strategy:
            filters["strategy"] = strategy
        if force_tiebreak:
            filters["forceTiebreak"] = force_tiebreak
        if pattern:
            filters["pattern"] = pattern
        req = Request(
            base=self._url,
            key=key,
            filters=filters,
            session=self._session,
        )
        return RuleRecommendation(req.put(json=requirement), self)


class Devices(Endpoint):
    """Represents the Devices

    Parameters:
        api (obj): FiremonAPI()
        app (obj): App()

    Keyword Arguments:
        record (obj): default `Record` object
    """

    ep_name = "device"
    _is_domain_url = True

    def __init__(self, api: FiremonAPI, app: App, record=Device):
        super().__init__(api, app, record=record)
        self._ep.update({"filter": "filter"})

    def get(self, *args, **kwargs) -> Device:
        """Get single Device

        Parameters:
            *args (int/str): (optional) id or name to retrieve.
            **kwargs (str): (optional) see filter() for available filters

        Returns:
            Device

        Examples:

            Get by ID

            >>> fm.sm.devices.get(12)
            <Device(vSRX-2)>

            Get by name. Case sensative.

            >>> fm.sm.devices.get("vSRX-2")
            <Device(vSRX-2)>

            >>> fm.sm.devices.get(mgmtip='192.168.104.12')
            <Device(vSRX-2)>
        """

        try:
            key = str(int(args[0]))
        except ValueError:
            key = f"name/{quote(args[0], safe='')}"
        except IndexError:
            key = None

        if not key:
            if kwargs:
                filter_lookup = self.filter(**kwargs)
            else:
                filter_lookup = self.filter(*args)
            if filter_lookup:
                if len(filter_lookup) > 1:
                    raise ValueError(
                        "get() returned more than one result. "
                        "Check that the kwarg(s) passed are valid for this "
                        "endpoint or use filter() or all() instead."
                    )
                else:
                    return filter_lookup[0]
            return None

        req = Request(
            base=self.url,
            key=key,
            session=self.api.session,
        )

        return self._response_loader(req.get())

    def create(self, dev_config: dict, retrieve: bool = False) -> Device:
        """Create a new device

        Parameters:
            dev_config (dict): dictionary of configuration data.
            retrieve (bool): whether to kick off a manual retrieval

        Return:
            Device (obj): a Device() of the newly created device

        Examples:

            >>> cg = fm.sm.collectorgroups.all()[0]
            >>> config = fm.sm.dp.get('juniper_srx').template()
            >>> config['name'] = 'Conan'
            >>> config['description'] = 'A test of the API'
            >>> config['managementIp'] = '10.2.2.2'
            >>> config['collectorGroupId'] = cg.id
            >>> config['collectorGroupName'] = cg.name
            >>> config['extendedSettingsJson']['password'] = 'abc12345'
            >>> dev = fm.sm.devices.create(config)
            >>> dev
            <Device(Conan)>
        """
        filters = {"manualRetrieval": retrieve}
        req = Request(
            base=self.url,
            filters=filters,
            session=self.session,
        ).post(json=dev_config)

        return self._response_loader(req)
