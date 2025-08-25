"""
This file defines all functions and utilities needded to enforce
the 'networking' of our experiment
"""

from pathlib import Path
from typing import Iterable, Optional, Union

import enoslib as en
from enoslib import NetemHTB
from enoslib.service.emul.objects import BaseNetem

from e2clab.config import NetConf, NetworkConfig
from e2clab.constants.default import NET_VALIDATE_DIR
from e2clab.constants.layers_services import MONITORING_NETWORK_ROLE
from e2clab.errors import E2clabNetworkError
from e2clab.log import get_logger
from e2clab.utils import get_hosts_from_pattern, is_chameleon_device, load_yaml_file


class Network:
    """
    Enforce network definition
    a.k.a. Network manager
    """

    def __init__(self, config: Path, roles, networks) -> None:
        """Create a new experiment network emulation

        Args:
            config (Path): Path to 'network.yaml' configuration file
            roles (en.Roles): EnOSlib Roles associated with th experiment
            networks (en.Networks): EnOSlib Networks associated with the experiment
        """
        self.logger = get_logger(__name__, ["NET"])
        self.config = self._load_config(config)
        self.roles = roles
        self.networks = networks
        self.netems: dict[str, Union[en.Netem, en.NetemHTB]] = {}

    def _load_config(self, config_path: Path) -> NetworkConfig:
        c = load_yaml_file(config_path)
        if c is not None:
            assert isinstance(c, dict)
        return NetworkConfig(c)

    # User Methods

    def prepare(self) -> None:
        # TODO: check that source and dest are correctly setup
        """Prepare network emulation"""
        self.networks_to_em = self._get_filtered_networks()

        self.logger.debug(f"[NETWORK TO EMMULATE] {self.networks_to_em}")

    def deploy(self) -> None:
        """Deploy configured network emulation"""
        networks_confs = self.config.get_netconfs()
        if len(networks_confs) == 0:
            self.logger.info("No network emulation to deploy")
            return

        self.logger.info("Deploying network emulation")

        netem: Union[BaseNetem, NetemHTB]
        for net_config in networks_confs:
            if self._check_edgeChameleonDevice(net_config):
                netem = self._configure_netem(net_config)
            else:
                netem = self._configure_netemhtb(net_config, self.networks_to_em)

            self.logger.debug(f"[NETEM CONFIG] {net_config}")
            self.logger.debug(f"[NETEM] {netem}")

            try:
                netem.deploy()
            except Exception as e:
                self.logger.error(f"Network deploy error: {e}")
                raise E2clabNetworkError

            key = net_config.get_netem_key()
            self.netems.update({key: netem})

            self.logger.info(f"Network emulation {key} deployed")
        self.logger.info("Done deploying network emulations")

    def validate(self, experiment_dir: Path) -> None:
        """Validate network emmulation deployment

        Args:
            experiment_dir (Path): Path to output validation file
        """
        if self.netems:
            self.logger.info(
                f"Network emulation validation files stored in {experiment_dir}"
            )
        for key, netem in self.netems.items():
            # Creating dir to store validation files
            netem_validate_dir: Path = experiment_dir / NET_VALIDATE_DIR / key
            netem_validate_dir.mkdir(parents=True, exist_ok=True)

            netem.validate(output_dir=netem_validate_dir)
            self.logger.debug(f"Validated netem {key} in {netem_validate_dir}")

    def destroy(self, key: Optional[str] = None) -> None:
        """Destroy network emulations, if key is not specified, detroys all

        Args:
            key (Optional[str], optional): netem key id. Defaults to None.
        """
        keys_to_destroy = []
        if key is None:
            keys_to_destroy = list(self.netems.keys())
            self.logger.info("Destroying all network emulations...")
            if len(keys_to_destroy) == 0:
                self.logger.warning("No deployed network emulations to destroy")
        else:
            if key in self.netems:
                keys_to_destroy = [key]
            else:
                self.logger.error(f"{key} is not a valid deployed netowrk emulation")

        for key in keys_to_destroy:
            netem = self.netems.pop(key)
            self.logger.info(f"Destroying {key} emulation...")
            netem.destroy()
            self.logger.info(f"Done destroying {key} emulation")

    # End User methods

    def _get_filtered_networks(self) -> Iterable[en.Network]:
        networks_to_em = []
        for key, value in self.networks.items():
            # TODO: Maybe also add provenance networks ?
            if key not in [MONITORING_NETWORK_ROLE]:
                networks_to_em.extend(value)
        return networks_to_em

    def _configure_netem(self, net_config: NetConf) -> en.Netem:
        netem = en.Netem().add_constraints(
            net_config.get_netem_command(),
            en.get_hosts(roles=self.roles, pattern_hosts=net_config.src),
            symmetric=False,
        )
        return netem

    def _configure_netemhtb(
        self, net_config: NetConf, networks_to_em: Iterable[en.Network]
    ) -> en.NetemHTB:
        netem = en.NetemHTB()
        src_hosts = get_hosts_from_pattern(roles=self.roles, pattern=net_config.src)
        dst_hosts = get_hosts_from_pattern(roles=self.roles, pattern=net_config.dst)
        netem.add_constraints(
            src=src_hosts,
            dest=dst_hosts,
            delay=net_config.delay,
            rate=net_config.rate,
            loss=net_config.loss,
            symmetric=net_config.symmetric,
            networks=networks_to_em,
        )
        return netem

    def _check_edgeChameleonDevice(self, net_config: NetConf) -> bool:
        hosts = self.roles[net_config.dst]
        for host in hosts:
            if is_chameleon_device(host):
                self.logger.debug(f"Network ChameleonDevice: {host}")
                return True
        return False
