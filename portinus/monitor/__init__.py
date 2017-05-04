import logging

import portinus

from portinus import systemd
from . import checker

log = logging.getLogger(__name__)


class Service(object):

    def __init__(self, name):
        self.name = name
        self._systemd_service = systemd.Unit(name + "-monitor")
        self._systemd_timer = systemd.Unit(name + "-monitor", type="timer")
        pass

    def _generate_service_file(self):
        template = portinus.get_template("monitor.service")

        return template.render(
                name=self.name,
                )

    def _generate_timer_file(self):
        template = portinus.get_template("monitor.timer")

        return template.render(
                name=self.name,
                )

    def ensure(self):
        log.info("Creating/updating {name} monitor timer".format(name=self.name))
        self._systemd_service.ensure(content=self._generate_service_file(), restart=False, enable=False)
        self._systemd_timer.ensure(content=self._generate_timer_file())

    def remove(self):
        log.info("Removing {name} monitor timer".format(name=self.name))
        self._systemd_timer.remove()
        self._systemd_service.remove()
