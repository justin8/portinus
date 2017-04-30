import subprocess
import logging

from .cli import task
from . import portinus, restart, systemd, monitor


class Application(object):

    log = logging.getLogger()

    def __init__(self, name, source=None, environment_file=None, restart_schedule=None):
        self.name = name
        self._environment_file = portinus.EnvironmentFile(name, environment_file)
        self._service = portinus.Service(name, source, self._environment_file)
        #self._restart_timer = restart.Timer(name, restart_schedule)
        #self._monitor_service = monitor.Service(name)

    def exists(self):
        return self._service.exists()

    def ensure(self):
        self._environment_file.ensure()
        self._service.ensure()
        #self._restart_timer.ensure()
        #self._monitor_service.ensure()

    def remove(self):
        self._service.remove()
        self._environment_file.remove()
        #self._restart_timer.remove()
        #self._monitor_service.remove()
        pass
