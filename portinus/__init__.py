import subprocess
import logging

from .cli import task
from . import portinus, restart, systemd, monitor

log = logging.getLogger()

class Application(object):

    def __init__(self, name, source=None, environment_file=None, restart_schedule=None):
        self.name = name
        self._service = portinus.Service(name, source)
        self._environment_file = portinus.EnvironmentFile(name, environment_file)
        self._restart_timer = restart.Timer(name, restart_schedule) if restart_schedule else None
        self._monitor_service = monitor.Service(name)

        try:
            subprocess.check_output(['systemctl', '--help'])
        except FileNotFoundError as e:
            log.error("Unable to find systemctl!")
            raise(e)

    def exists(self):
        return self._service.exists()

    def ensure(self):
        self._environment_file.ensure()
        self._service.ensure(self._environment_file)
        #self._restart_timer.ensure()
        #self._monitor_service.ensure()

    def remove(self):
        self._environment_file.remove()
        self._service.remove()
        #self._restart_timer.remove()
        #self._monitor_service.remove()
        pass
