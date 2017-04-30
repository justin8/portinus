import logging
import os
import subprocess

log = logging.getLogger(__name__)

class Service(object):

    def __init__(self, name):
        self.name = name
        self.service_name = f"portinus-{name}.service"
        self.service_file_path = os.path.join('/etc/systemd/system', self.service_name)

        try:
            subprocess.check_output(['systemctl', '--help'])
        except FileNotFoundError as e:
            log.error("Unable to find systemctl!")
            raise(e)

    def _systemctl(self, args):
        try:
            output = subprocess.call(["systemctl"] + args)
        except subprocess.CalledProcessError as e:
            log.error(f"Failed to run systemctl with parameters #{args}")
            raise(e)

    def reload(self):
        log.info("Reloading daemon files")
        self._systemctl(['daemon-reload'])

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
