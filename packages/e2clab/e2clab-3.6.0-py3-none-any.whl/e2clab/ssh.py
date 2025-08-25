"""
Ssh command implementation
"""

import pickle
import subprocess
from pathlib import Path
from typing import Optional

import questionary
from enoslib import Host, Roles

from e2clab.constants import SSH_STATE_NAME, STATE_DIR
from e2clab.errors import E2clabError, E2clabSSHError
from e2clab.log import get_logger


class SSH:
    """User roles for SSH access"""

    def __init__(self, data: dict[str, Roles], dir_name: Path):
        self.data = data
        self.dir_name = dir_name
        self.logger = get_logger(__name__, ["SSH"])

    def dump(self):
        """Dumps self to a pickled file"""
        self.dir_name.mkdir(parents=True, exist_ok=True)
        filename = self.dir_name.joinpath(STATE_DIR).joinpath(SSH_STATE_NAME)
        with filename.open("wb") as f:
            pickle.dump(self, f)

    @classmethod
    def load(cls, dir_name: Path) -> "SSH":
        """Load SSH state from a pickled file in the directory"""
        filename = dir_name.joinpath(STATE_DIR).joinpath(SSH_STATE_NAME)
        if not filename.is_file():
            raise E2clabError(
                f"SSH state file {filename} not found. "
                "Have you successfully deployed an infrastructure yet?"
            )

        with filename.open("rb") as f:
            return pickle.load(f)

    def ssh(
        self,
        forward: Optional[bool] = False,
        local_port: Optional[int] = None,
        remote_port: Optional[int] = None,
    ) -> None:
        """Runs a subprocess to ssh to selected remote host"""
        host = self._ask_ssh_host()
        ssh_target = f"{host.user}@{host.address}"
        identity = host.keyfile
        port = host.port
        command = ["ssh", ssh_target]
        # if we want to run ssh tunnelling
        if forward and local_port and remote_port:
            command += ["-NL", f"{local_port}:localhost:{remote_port}"]
        if port is not None:
            command += ["-p", str(port)]
        if identity is not None:
            command += ["-i", str(identity)]
        self.logger.debug(f"SSH COMMAND : {command}")
        # TODO: Get inspiration from G5K tunnel in enoslib, may be better
        try:
            if forward:
                self.logger.info(f"Access localhost:{local_port}")
            else:
                self.logger.info(f"Accessing {host.address}")
            subprocess.run(command)
        except Exception as e:
            self.logger.error(f"Failed to connect: {e}")
            raise E2clabSSHError

    def _ask_ssh_host(self) -> Host:
        """Queries user for host to ssh to

        Returns:
            Host: host to ssh to
        """
        self.logger.debug(f"SSH roles: {self.data}")

        choices = [str(k) for k in self.data.keys()]
        layer_answer: str = questionary.select(
            "Select layer to ssh to", choices=choices
        ).ask()

        choices = [str(k) for k in self.data[layer_answer].keys()]
        roles_answer: str = questionary.select(
            "Select host to ssh to", choices=choices
        ).ask()

        host: Host = self.data[layer_answer][roles_answer][0]
        return host
