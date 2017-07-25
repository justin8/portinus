import subprocess
import shutil
import os
import logging
from operator import attrgetter

from jinja2 import Template

import portinus
import systemd_unit

log = logging.getLogger(__name__)


class Service(object):

    def __init__(self, name, source=None):
        if not name:
            raise ValueError("Invalid value for 'name'")
        self.name = name
        self.service_name = "{}-{}".format("portinus", name)
        self._source = ComposeSource(name, source)
        self._systemd_service = systemd_unit.Unit(self.service_name)
        log.debug("Initialized Service for '{name}' with source: '{source}'".format(name=name, source=source))

    def exists(self):
        return os.path.isdir(portinus.get_instance_dir(self.name))

    def _generate_service_file(self):
        start_command = "{service_script} up".format(service_script=self._source.service_script)
        stop_command = "{service_script} down".format(service_script=self._source.service_script)

        template = portinus.get_template("instance.service")
        return template.render(
            name=self.name,
            start_command=start_command,
            stop_command=stop_command,
            )

    def ensure(self):
        log.info("Creating/updating {name} portinus instance".format(name=self.name))
        try:
            self._systemd_service.stop()
        except subprocess.CalledProcessError:
            pass
        self._source.ensure()
        self._systemd_service.ensure(content=self._generate_service_file())

    def remove(self):
        log.info("Removing {name} portinus instance".format(name=self.name))
        self._systemd_service.remove()
        self._source.remove()

    def restart(self):
        log.info("Restarting {name}".format(name=self.name))
        self._systemd_service.restart()

    def stop(self):
        log.info("Stopping {name}".format(name=self.name))
        self._systemd_service.stop()

    def compose(self, command):
        log.info("Running compose for {name} with command: '{command}'".format(name=self.name, command=command))
        if not self.exists():
            raise ValueError("The specified service does not exist")
        subprocess.call([self._source.service_script] + list(command))


class ComposeSource(object):

    def __init__(self, name, source=None):
        self.name = name
        self.source = source
        self.path = portinus.get_instance_dir(name)
        self.service_script = os.path.join(self.path, name)
        log.debug("Initialized ComposeSource for '{name}' from source: '{source}'".format(name=name, source=source))

    source = property(attrgetter('_source'))

    @source.setter
    def source(self, value):
        if value is not None:
            try:
                with open(os.path.join(value, "docker-compose.yml")):
                    pass
            except FileNotFoundError as e:
                log.error("Unable to access the specified source docker compose file in ({source})".format(source=value))
                raise(e)
        self._source = value

    def _ensure_service_script(self):
        service_script_template = os.path.join(portinus.template_dir, "service-script")
        shutil.copy(service_script_template, self.service_script)
        os.chmod(self.service_script, 0o755)

    def ensure(self):
        if not self.source:
            log.error("No valid source specified")
            raise(IOError("No valid source specified"))
        log.info("Copying source files for '{self.name}' to '{self.path}'")
        self.remove()
        shutil.copytree(self.source, self.path, symlinks=True, copy_function=shutil.copy)
        self._ensure_service_script()
        log.debug("Successfully copied source files")

    def remove(self):
        log.info("Removing source files for '{name}' from '{path}'".format(name=self.name, path=self.path))
        try:
            shutil.rmtree(self.path)
            log.debug("Successfully removed source files")
        except FileNotFoundError:
            log.debug("No source files found")


class EnvironmentFile(object):

    def __init__(self, name, source_environment_file=None):
        self.name = name
        self._source_environment_file = source_environment_file
        self.path = portinus.get_instance_dir(self.name) + ".environment"
        log.debug("Initialized EnvironmentFile for '{name}' from source: '{source_environment_file}'".format(name=name, source_environment_file=source_environment_file))

        if source_environment_file:
            try:
                with open(source_environment_file):
                    pass
            except FileNotFoundError as e:
                log.error("Unable to access the specified environment file ({source_environment_file})".format(source_environment_file=source_environment_file))
                raise(e)

    def __bool__(self):
        return bool(self._source_environment_file)

    def ensure(self):
        if self:
            log.info("Creating/updating environment file for '{name}' at '{path}'".format(name=self.name, path=self.path))
            shutil.copy(self._source_environment_file, self.path)
        else:
            self.remove()

    def remove(self):
        log.info("Removing environment file for {name}".format(name=self.name))
        try:
            os.remove(self.path)
            log.debug("Sucessfully removed environment file")
        except FileNotFoundError:
            log.debug("No environment file found")
