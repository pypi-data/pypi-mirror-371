from abc import ABCMeta, abstractmethod
from copy import deepcopy
from typing import Iterable, Optional, Tuple

# import enoslib as en
from enoslib import Docker, Host, Roles

from e2clab.constants.layers_services import ENV, LAYER_ID, LAYER_NAME, NAME, SERVICE_ID
from e2clab.constants.workflow import SELF_PREFIX
from e2clab.errors import E2clabServiceError
from e2clab.log import get_logger

from .constants import (
    __ADDRESS4__,
    __ADDRESS6__,
    __ADDRESS__,
    __G5K_IPV6_ADDRESS__,
    _ID,
    IPV6_G5K,
    MACHINE_ID,
    URL,
    URL4,
    URL6,
)


class Service:
    """
    Abstract class for user-services implementation.
    A Service represents any system that provides
    a specific functionality or action in the scenario workflow.

    To implement your class:

    - Inherit from this class and define the abstract :func:`deploy` function
    - Tell `E2Clab` to register your new Service class using the
        :ref:`e2clab services add <e2clab-cli>` command

    Example with a 'Test' service:

    Create my class by inheriting from the :class:`Service` class in ``Test.py``.

    .. code-block:: python

        from e2clab import Service


        class Test(Service):
            def deploy(self):
                # Your service logic here
                pass

    Register my class with e2clab:

    .. code-block:: bash

        e2clab services add Test.py


    """

    __metaclass__ = ABCMeta

    # Register for all loaded subclasses of 'Service'
    __loaded_subservices: dict[str, type["Service"]] = {}

    def __init__(self, hosts: list[Host], service_metadata: dict):
        """E2Clab service class

        Args:
            hosts (Iterable[Host]): List | HostsView of hosts attached to the service
            service_metadata (dict): Service configuration dict.
        """
        self.hosts: list[Host] = hosts
        """all hosts associated with the serice"""
        self.roles: Roles = Roles({"all": self.hosts})
        """roles associated with the service"""
        self.service_metadata: dict = service_metadata
        """all metadata associated with the service"""
        self.env: dict = service_metadata.get(ENV, {})
        """information from the `env` param in your `layers_services.yaml`"""

        self.service_extra_info: dict = {}
        self.service_roles = Roles({})

        self.layer_name: str = service_metadata[LAYER_NAME]
        self.layer_id: int = service_metadata[LAYER_ID]
        self.service_name: str = service_metadata[NAME]
        self.service_id: int = service_metadata[SERVICE_ID]

        # self.env = {}
        # if service_metadata is not None and ENV in service_metadata:
        #     self.env = service_metadata[ENV]

        self.logger = get_logger(__name__, ["SERV"])

    def __init_subclass__(cls, **kwargs) -> None:
        """
        When a subclass of 'Service' is defined, it is stored in a dict for easy
        programmatic imports and instanciation.
        """
        super().__init_subclass__(**kwargs)
        if cls.__name__ not in cls.__loaded_subservices.keys():
            cls.__loaded_subservices[cls.__name__] = cls

    @classmethod
    def get_loaded_subservices(cls):
        return cls.__loaded_subservices

    @abstractmethod
    def deploy(self):
        """
        Implement the logic of your custom Service.
        Must register all services and return all of the service's
        extra info and roles

        Examples:

            .. code-block:: python

                # Register 'sub-services'
                def deploy(self):
                    if len(self.hosts) > 1:
                        self.roles.update(
                            {"master": [self.hosts[1]], "worker": [self.hosts[1:]]}
                        )


                # Register the first host as a 'master' subservice
                self.register_service(
                    roles=self.roles["master"], service_port=8080, sub_service="master"
                )
                # Register the other hosts as 'worker subservice
                self.register_service(
                    roles=self.roles["worker"], service_port=8081, sub_service="worker"
                )
        """
        pass

    def _init(self) -> Tuple[dict, Roles]:
        """initiate the service by running wrapping 'deploy'
            so it doesn't have to return anything

        Returns:
            Tuple[dict, Roles]: service_extra_info, service_roles
        """
        try:
            self.deploy()
        except Exception as e:
            self.logger.error(e)
            raise E2clabServiceError(f"Failed deploying {type(self).__name__}")

        # TODO: We should not have to pass the service extra_info in the future
        return self.service_extra_info, self.service_roles

    def _service_key(
        self,
        sub_service_name: Optional[str] = None,
        machine_id: Optional[int] = None,
    ):
        """
        Service ID (metadata['_id']) is: "LayerID_ServiceID_MachineID"
        e.g.: service_key = "layer.service.service_id.sub_service.machine_id"
                          = cloud.flink.1.job_manager.1
        e.g.: service_key = "layer.service.service_id.sub_service.machine_id"
                          = cloud.flink.1.task_manager.1

        In this example, Flink is the "Service" and Job_Manager
            and Task_Manager are the "sub Service(s)".

        e.g.: service_key = "layer.service.service_id.machine_id" = edge.producer.1.1
        In this example, Producer is the "Service" and it does not have a "sub Service".

        NOTE:
            "service_id" is generated in e2clab.infra.generate_service_id()"
            "machine_id" is generated in "register_service()"
        """
        service_key = f"{self.layer_name}.{self.service_name}.{self.service_id}"
        service_key += f".{sub_service_name}" if sub_service_name else ""
        service_key += f".{machine_id}" if machine_id else ""
        return service_key.lower()

    @staticmethod
    def _get_hosts_from_roles(roles: Roles) -> Iterable[Host]:
        return list(roles.all())

    @staticmethod
    def _format_ip(addr: str) -> str:
        return addr.split("/")[0]

    def register_service(
        self,
        hosts: Optional[list[Host]] = None,
        roles: Optional[Roles] = None,
        service_port: Optional[str] = None,
        sub_service: Optional[str] = None,
        extra: Optional[list[dict]] = None,
    ) -> Tuple[dict, Roles]:
        """
        Registers a Service with either a list of hosts or a roles object.
        If neither hosts or roles is supplied: all the service hosts are used.

        Args:
            hosts (list[Host], optional): Hosts attributed to the service.
                Defaults to None.
            roles (Roles, optional): Roles containing the hosts attributed to
                the Service. Defaults to None.
            service_port (str, optional): Service port. Defaults to None.
            sub_service (str, optional): Sub Service name e.g. 'master' or 'worker'.
                Defaults to None.
            extra (list[dict], optional): List of dicts with extra service information.
                Those are the extra attributes that you can access in 'workflow.yaml'
                to avoid hard coding.
                Defaults to None.

        Returns:
            Tuple[dict, Roles]: New Roles containing the hosts attributed to
                the Service.
        """

        if hosts:
            _hosts: Iterable = hosts
        elif roles:
            _hosts = self._get_hosts_from_roles(roles)
        else:
            _hosts = self.hosts

        for i, _h in enumerate(_hosts):
            # Needed when registering multiple services on the same host
            # And we are going to use "extra" to convey service extra information
            host = deepcopy(_h)

            machine_id = i + 1
            service_key = self._service_key(
                sub_service_name=sub_service, machine_id=machine_id
            )
            self.service_extra_info.update(
                {
                    service_key: {
                        _ID: f"{self.service_metadata['_id']}_{machine_id}",
                        LAYER_ID: str(self.layer_id),
                        SERVICE_ID: str(self.service_id),
                        MACHINE_ID: str(machine_id),
                        __ADDRESS__: f"{host.address}",
                        URL: f"{host.address}"
                        + (f":{service_port}" if service_port else ""),
                    }
                }
            )

            # All hosts except Chameleon Edge devices
            # TODO: check chameleon edge support
            if isinstance(host, Host):
                from enoslib.objects import IPv4Interface, IPv6Interface

                # Register IP addresses
                addresses = host.filter_addresses()
                _ipv4 = None
                _ipv6 = None
                for ad in addresses:
                    if isinstance(ad.ip, IPv4Interface) and _ipv4 is None:
                        _ipv4 = self._format_ip(str(ad.ip))
                    elif isinstance(ad.ip, IPv6Interface) and _ipv6 is None:
                        _ipv6 = self._format_ip(str(ad.ip))
                if _ipv6:
                    self.service_extra_info[service_key].update(
                        {
                            __ADDRESS6__: f"{_ipv6}",
                            URL6: f"[{_ipv6}]"
                            + (f":{service_port}" if service_port else ""),
                        }
                    )
                if _ipv4:
                    self.service_extra_info[service_key].update(
                        {
                            __ADDRESS4__: f"{_ipv4}",
                            URL4: f"{_ipv4}"
                            + (f":{service_port}" if service_port else ""),
                        }
                    )
                self.logger.debug(f"{host.address} IPv4: {_ipv4}, IPv6: {_ipv6}")
                # For g5k instances add IPv6 hostname
                if "grid5000" in host.address:
                    address = host.address.split(".")
                    address[0] += IPV6_G5K
                    ipv6_address = ".".join(address)

                    self.service_extra_info[service_key].update(
                        {
                            __G5K_IPV6_ADDRESS__: ipv6_address,
                        }
                    )

                # For chameleon cloud instances
                gateway = host.extra.get("gateway")
                if gateway:
                    self.service_extra_info[service_key].update({"gateway": gateway})

            # user-defined Service info
            # TODO: Change this stuff
            if extra is not None and i < len(extra) and extra[i] is not None:
                self.service_extra_info[service_key].update(extra[i])

            # Adding gateway to the hosts self info
            self._populate_self_extra(host, service_key)

            # new roles after Service registration
            self.service_roles.update({service_key: [host]})

        return self.service_extra_info, self.service_roles

    def _populate_self_extra(self, host: Host, service_key: str) -> None:
        """Populate hosts "extra._self" attribute for ansible host_vars.

        Args:
            host (Host): Service's Enoslib Host
            service_key (str): Service key to services_extra information
        """
        if "gateway" in host.extra:
            self.service_extra_info[service_key].update(
                {"gateway": host.extra["gateway"]}
            )

            # Self variables in host extra
        self_extra = {SELF_PREFIX: self.service_extra_info[service_key]}
        host.set_extra(**self_extra)

    def deploy_docker(
        self,
        hosts: Optional[list[Host]] = None,
        docker_version: Optional[str] = None,
        registry: Optional[list[Host]] = None,
        registry_opts: Optional[dict] = None,
        bind_var_docker: str = "/tmp/docker",
        swarm: bool = False,
        credentials: Optional[dict] = None,
        nvidia_toolkit: Optional[bool] = None,
    ) -> None:
        """Wrapper for easy Docker agent deployment on remote hosts. If roles is None,
        all hosts from the service are used

        Args:
            hosts: List of hosts to deploy the Docker agent on.
                If set to None, all hosts from the service are used. Defaults to None.
            docker_version: major version of Docker to install. Defaults
                to latest.
            registry: list of Hosts where the docker
                registry will be installed. Defaults to None.
            registry_opts: Docker registry option.
                Defaults to None.
            bind_var_docker: If set the default docker
                state directory. Defaults to '/tmp/docker'.
            swarm: Whether a docker swarm will be created to cover
                the agents. Defaults to False.
            credentials: Optional 'login' and 'password' for Docker hub.
                Useful to access private images, or to bypass Docker hub rate-limiting:
                in that case, it is recommended to use a token with the "Public Repo
                Read-Only" permission as password, because it is stored in cleartext
                on the nodes.
            nvidia_toolkit: Whether to install nvidia-container-toolkit.
                If set to None (the default), Enoslib will try to auto-detect the
                presence of a nvidia GPU and only install nvidia-container-toolkit
                if it finds such a GPU.  Set to True to force nvidia-container-toolkit
                installation in all cases, or set to False to prevent
                nvidia-container-toolkit installation in all cases.
        """
        if hosts is None:
            hosts = self.hosts
        d = Docker(
            agent=hosts,
            docker_version=docker_version,
            registry=registry,
            registry_opts=registry_opts,
            bind_var_docker=bind_var_docker,
            swarm=swarm,
            credentials=credentials,
            nvidia_toolkit=nvidia_toolkit,
        )
        d.deploy()
