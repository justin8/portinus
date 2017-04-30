import logging

import portinus
from . import systemd

log = logging.getLogger(__name__)


class Timer(object):

    def __init__(self, name, restart_schedule):
        self.name = name
        self.restart_schedule = restart_schedule
        self._systemd_service = systemd.Service(name + "-restart")
        self._systemd_timer = systemd.Service(name + "-restart", type="timer")
        log.debug(f"Initialized restart.Timer for '{name}' with restart_schedule: '{restart_schedule}'")

    def __bool__(self):
        return bool(self.restart_schedule)

    def _generate_service_file(self):
        template_file = portinus.get_template("portinus-restart.service")
        instance_service = systemd.Service(self.name)

        return template_file.render(
                name=self.name,
                service_name=instance_service.service_name,
                )

    def _generate_timer_file(self):
        template_file = portinus.get_template("portinus-restart.timer")

        return template_file.render(
                name=self.name,
                restart_schedule=self.restart_schedule,
                )

    def ensure(self):
        if self:
            log.info(f"Creating/updating {self.name} restart timer")
            self._systemd_timer.ensure(content=self._generate_timer_file())
            self._systemd_service.ensure(content=self._generate_service_file(), restart=False, enable=False)
        else:
            log.info(f"No restart schedule specified for {self.name}. Removing any existing restart timers")
            self.remove()

    def remove(self):
        log.info(f"Removing {self.name} restart timer")
        self._systemd_timer.remove()
        self._systemd_service.remove()
