import logging
import os

from pathlib import Path
from jinja2 import Template

from .cli import task
from . import portinus, restart, monitor

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
        self._environment_file = portinus.EnvironmentFile(name, environment_file)
        self._service = portinus.Service(name, source)
        self._restart_timer = restart.Timer(name, restart_schedule=restart_schedule)
        self._monitor_service = monitor.Service(name)

    def _create_service_dir(self):
        try:
            os.mkdir(service_dir)
        except FileExistsError:
            pass

    def exists(self):
        return self._service.exists()

    def ensure(self):
        self._create_service_dir()
        self._environment_file.ensure()
        self._service.ensure()
        self._restart_timer.ensure()
        self._monitor_service.ensure()

    def remove(self):
        self._service.remove()
        self._environment_file.remove()
        self._restart_timer.remove()
        self._monitor_service.remove()
