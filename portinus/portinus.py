import subprocess
import shutil
import os
import logging

from jinja2 import Template

from . import systemd

_PORTINUS_SERVICE_DIR = '/usr/local/portinus-services'
template_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'templates')
log = logging.getLogger(__name__)


class Service(object):

    def __init__(self, name, source, environment_file):
        self.name = name
        self._source = _ComposeSource(name, source)
        self._systemd_service = systemd.Service(name)
        self._environment_file = environment_file

    def exists(self):
        return os.path.isdir(self._source.path)

    def ensure(self):
        self._source.ensure()
        self._ensure_service_file()
        self._systemd_service.restart()
        self._systemd_service.enable()

    def _ensure_service_file(self):
        template_file = os.path.join(template_dir, "portinus-instance.service")
        target = self._systemd_service.service_file_path
        start_command = f"{self._source.service_script} up"
        stop_command = f"{self._source.service_script} down"
        log.info(f"Creating/updating service file for '{self.name}' at '{target}'")

        with open(template_file) as f:
            service_template = Template(f.read())

        with open(target, 'w') as f:
            f.write(service_template.render(name=self.name,
                                            environment_file_path=self._environment_file,
                                            start_command=start_command,
                                            stop_command=stop_command,
                                            ))

        self._systemd_service.reload()

    def _remove_service_file(self):
        log.info(f"Removing service file for {self.name} from {self._systemd_service.service_file_path}")
        try:
            os.remove(self._systemd_service.service_file_path)
            log.debug("Successfully removed service file")
        except FileNotFoundError:
            log.debug("No service file found")

    def remove(self):
        self._systemd_service.stop()
        self._systemd_service.disable()
        self._remove_service_file
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
        service_script_template = os.path.join(template_dir, "service-script")
        shutil.copy(service_script_template, self.service_script)
        os.chmod(self.service_script, 0o755)

    def ensure(self):
        if not self._source:
            log.error("No valid source specified")
            raise(IOError("No valid source specified"))
        self.remove()
        shutil.copytree(self._source, self.path, symlinks=True, copy_function=shutil.copy)
        self._generate_service_script()

    def remove(self):
        log.info(f"Removing source files for '{self.name}' from '{self.path}'")
        try:
            shutil.rmtree(self.path)
            log.debug("Successfully removed source files")
        except FileNotFoundError:
            log.debug("No source files found")


class EnvironmentFile(object):

    def __init__(self, name, source_environment_file=None):
        self.name = name
        self._source_environment_file = source_environment_file
        self.path = os.path.join(_PORTINUS_SERVICE_DIR, name + '.environment')
        log.debug(f"Initialized EnvironmentFile for '{name}' from source: '{source_environment_file}'")

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
            log.info(f"Creating/updating environment file for '{self.name}' at '{self.path}'")
            shutil.copy(self._source_environment_file, self.path)
        else:
            self.remove()

    def remove(self):
        log.info(f"Removing environment file for {self.name}")
        try:
            os.remove(self.path)
            log.debug("Sucessfully removed environment file")
        except FileNotFoundError:
            log.debug("No environment file found")
