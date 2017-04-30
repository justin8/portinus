import logging
import os
import subprocess

log = logging.getLogger(__name__)


class Service(object):

    def __init__(self, name, type="service", content=None):
        self.name = name
        self.service_name = f"portinus-{name}.{type}"
        self.service_file_path = os.path.join("/etc/systemd/system", self.service_name)
        self._content = content

        try:
            subprocess.check_output(["systemctl", "--help"])
        except FileNotFoundError as e:
            log.error("Unable to find systemctl!")
            raise(e)
        log.debug(f"Initialized systemd.Service for '{name}' with type '{type}'")

    def _systemctl(self, args):
        try:
            output = subprocess.check_output(["systemctl"] + args)
        except subprocess.CalledProcessError as e:
            log.error(f"Failed to run systemctl with parameters #{args}")
            raise(e)

    def set_content(self, content):
        self._content = content

    def create_service_file(self):
        log.info(f"Creating/updating service file for '{self.name}' at '{self.service_file_path}'")
        with open(self.service_file_path, "w") as f:
            f.write(self._content)

    def ensure(self, restart=True, enable=True, content=None):
        if content: self.set_content(content)
        self.create_service_file()
        self.reload()
        if restart: self.restart()
        if enable: self.enable()

    def remove(self):
        try:
            self.stop()
            self.disable()
        except subprocess.CalledProcessError:
            pass

        log.info(f"Removing service file for {self.name} from {self.service_file_path}")
        try:
            os.remove(self.service_file_path)
            log.debug("Successfully removed service file")
        except FileNotFoundError:
            log.debug("No service file found")
        self.reload()

    def reload(self):
        log.info("Reloading daemon files")
        self._systemctl(["daemon-reload"])

    def restart(self):
        log.info(f"Restarting {self.service_name}")
        self._systemctl(["restart", self.service_name])

    def stop(self):
        log.info(f"Stopping {self.service_name}")
        self._systemctl(["stop", self.service_name])

    def enable(self):
        log.info(f"Enabling {self.service_name}")
        self._systemctl(["enable", self.service_name])

    def disable(self):
        log.info(f"Disabling {self.service_name}")
        self._systemctl(["disable", self.service_name])
