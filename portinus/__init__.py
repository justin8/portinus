import logging
import os
from operator import attrgetter

from pathlib import Path
from jinja2 import Template

from .cli import task
from . import restart, monitor
from .portinus import Service, ComposeSource, EnvironmentFile

_script_dir = os.path.dirname(os.path.realpath(__file__))
template_dir = os.path.join(_script_dir, 'templates')
service_dir = '/usr/local/portinus-services'


def list():
    for i in Path(service_dir).iterdir():
        if i.is_dir():
            print(i.name)


def get_instance_dir(name):
    return os.path.join(service_dir, name)


def get_template(file_name):
    template_file = os.path.join(template_dir, file_name)
    with open(template_file) as f:
        template_contents = f.read()

    return Template(template_contents)


class Application(object):

    log = logging.getLogger()

    def __init__(self, name, source=None, environment_file=None, restart_schedule=None):
        self.name = name
        self.environment_file = EnvironmentFile(name, environment_file)
        self.service = Service(name, source)
        self.restart_timer = restart.Timer(name, restart_schedule=restart_schedule)
        self.monitor_service = monitor.Service(name)

    service = property(attrgetter('_service'))

    @service.setter
    def service(self, value):
        if value and not isinstance(value, Service):
            raise TypeError("Must be set to a Service object")
        self._service = value

    environment_file = property(attrgetter('_environment_file'))

    @environment_file.setter
    def environment_file(self, value):
        if value and not isinstance(value, EnvironmentFile):
            raise TypeError("Must be set to an EnvironmentFile object")
        self._environment_file = value

    restart_timer = property(attrgetter('_restart_timer'))

    @restart_timer.setter
    def restart_timer(self, value):
        if value and not isinstance(value, restart.Timer):
            raise TypeError("Must be set to a restart.Timer object")
        self._restart_timer = value

    monitor_service = property(attrgetter('_monitor_service'))

    @monitor_service.setter
    def monitor_service(self, value):
        if value and not isinstance(value, monitor.Service):
            raise TypeError("Must be set to a monitor.Service object")
        self._monitor_service = value

    def _create_service_dir(self):
        try:
            os.mkdir(service_dir)
        except FileExistsError:
            pass

    def exists(self):
        return self.service.exists()

    def ensure(self):
        self._create_service_dir()
        self.environment_file.ensure()
        self.service.ensure()
        self.restart_timer.ensure()
        self.monitor_service.ensure()

    def remove(self):
        self.service.remove()
        self.environment_file.remove()
        self.restart_timer.remove()
        self.monitor_service.remove()
