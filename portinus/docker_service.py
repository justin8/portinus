import subprocess
import shutil
import os
import logging

from docker_restart_timer import DockerRestartTimer
from docker_health_monitor import HealthMonitor
from docker_compose_source import ComposeSource

class DockerService(object):

    _SERVICE_DIR = '/usr/local/docker-services'
    log = logging.getLogger()

    def __init__(self, name, source=None, env=None, restart=None):
        self._name = name
        self._source = ComposeSource(name, source) if source else None
        self._env = EnvironmentFile(name, env) if env else None
        self._restart = RestartService(name) if restart else None

        try:
            subprocess.check_output(['systemctl', '--help'])
        except FileNotFoundError as e:
            log.error("Unable to find systemctl!")
            raise(e)


    def _systemctl(self, args):
        try:
            subprocess.call(["systemctl"] + args)
        except subprocess.CalledProcessError as e:
            log.error(f"Failed to run systemctl with parameters #{args}")
            raise(e)


    def restart(self):
        self._systemctl(["restart", self._name])


    def stop(self):
        self._systemctl(["stop", self._name])


    def exists(self):
        return os.path.isdir(os.path.join(self._SERVICE_DIR, self._name)


    def create(self):
        try:
            with open(os.path.join(self._source, 'docker-compose.yml')):
                pass
        except:
            log.error("Cannot find docker-compose.yml in the specified source")
            raise(IOError("Unable to find docker-compose.yml"))

        env_file = DockerEnvironmentFile(self.name, self.env)
        env_file.ensure()

        self._sync_source()
        self._ensure_service()
        
        restart_timer = RestartTimer(name)
        restart_timer.ensure()

        monitor_service = MonitorService(name)
        monitor_service.ensure()



    def remove(self):
        pass
