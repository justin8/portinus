import os
import subprocess


class Service(object):

    def __init__(self, name):
        self.name = name
        self.service_name = f"portinus-{name}.service"
        self.service_file_path = os.path.join('/etc/systemd/system', self.service_name)

    def _systemctl(self, args):
        try:
            subprocess.call(["systemctl"] + args)
        except subprocess.CalledProcessError as e:
            log.error(f"Failed to run systemctl with parameters #{args}")
            raise(e)

    def reload(self):
        self._systemctl(['daemon-reload'])

    def restart(self):
        self._systemctl(["restart", self.service_name])

    def stop(self):
        self._systemctl(["stop", self.service_name])

    def enable(self):
        self._systemctl(["enable", self.service_name])

    def disable(self):
        self._systemctl(["disable", self.service_name])
