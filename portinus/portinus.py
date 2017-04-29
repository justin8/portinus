import subprocess
import shutil
import os
import logging

from jinja2 import Template

_PORTINUS_SERVICE_DIR = '/usr/local/portinus-services'
_SYSTEMD_SERVICE_PATH = '/etc/systemd/system'
_LOCAL_PATH = os.path.dirname(os.path.realpath(__file__))
log = logging.getLogger()


class Service(object):

    def __init__(self, name, source=None, environment_file=None, restart_schedule=None):
        self.name = name
        self._service = _Service(name, source)
        self._environment_file = EnvironmentFile(name, environment_file)
        self._restart_timer = RestartTimer(name, restart_schedule) if restart_schedule else None
        self._monitor_service = MonitorService(name)

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


class _SystemdService(object):

    def __init__(self, name):
        self.name = name
        self.service_name = f"portinus-{name}.service"
        self.service_file_path = os.path.join(_SYSTEMD_SERVICE_PATH, self.service_name)

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


class _Service(object):

    def __init__(self, name, source):
        self.name = name
        self._source = _ComposeSource(name, source)
        self._systemd_service = _SystemdService(name)

    def exists(self):
        return os.path.isdir(self._source.path)

    def ensure(self, environment_file):
        self._source.ensure()
        self._ensure_service_file(environment_file)
        self._systemd_service.restart()
        self._systemd_service.enable()

    def _ensure_service_file(self, environment_file):
        template_file = os.path.join(_LOCAL_PATH, "templates", "portinus-instance.service")
        target = self._systemd_service.service_file_path
        start_command = f"{self._source.service_script} up"
        stop_command = f"{self._source.service_script} down"

        with open(template_file) as f:
            service_template = Template(f.read())

        with open(target, 'w') as f:
            f.write(service_template.render(name=self.name,
                                            environment_file_path=environment_file,
                                            start_command=start_command,
                                            stop_command=stop_command,
                                            ))

        self._systemd_service.reload()

    def remove(self):
        self._systemd_service.stop()
        self._systemd_service.disable()
        os.remove(self._systemd_service.service_file_path)
        self._source.remove()
        self._systemd_service.reload()
        pass


class _ComposeSource(object):

    def __init__(self, name, source):
        self.name = name
        self._source = source
        self.path = os.path.join(_PORTINUS_SERVICE_DIR, name)
        self.service_script = os.path.join(self.path, name)

        if source:
            try:
                with open(os.path.join(source, 'docker-compose.yml')):
                    pass
            except Exception as e:
                log.error(f"Unable to access the specified source docker compose file in (#{source})")
                raise(e)

    def _generate_service_script(self):
        service_script_template = os.path.join(_LOCAL_PATH, "templates", "service-script")
        shutil.copy(service_script_template, self.service_script)
        os.chmod(self.service_script, 0o755)

    def ensure(self):
        if not self._source:
            raise(IOError("No valid source specified"))
        self.remove()
        shutil.copytree(self._source, self.path, symlinks=True, copy_function=shutil.copy)
        self._generate_service_script()

    def remove(self):
        try:
            shutil.rmtree(self.path)
        except FileNotFoundError:
            pass


class EnvironmentFile(object):

    def __init__(self, name, source_environment_file=None):
        self.name = name
        self._source_environment_file = source_environment_file
        self.path = os.path.join(_PORTINUS_SERVICE_DIR, name + '.environment')

        if source_environment_file:
            try:
                with open(source_environment_file):
                    pass
            except FileNotFoundError as e:
                log.error(f"Unable to access the specified environment file (#{source_environment_file})")
                raise(e)

    def __bool__(self):
        return bool(self._source_environment_file)

    def ensure(self):
        if self:
            shutil.copy(self._source_environment_file, self.path)
        else:
            try:
                os.remove(self.path)
            except:
                pass

    def remove(self):
        try:
            os.remove(self.path)
        except FileNotFoundError:
            pass


class RestartTimer(object):
    # TODO

    def __init__(self, name, restart_schedule):
        pass

    def ensure(self):
        pass

    def remove(self):
        pass


class MonitorService(object):
    # TODO

    def __init__(self, name):
        pass

    def ensure(self):
        pass

    def remove(self):
        pass
