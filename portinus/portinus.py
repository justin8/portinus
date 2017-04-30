import subprocess
import shutil
import os
import logging

from jinja2 import Template

import portinus
from . import systemd

log = logging.getLogger(__name__)


class Service(object):

    def __init__(self, name, source, environment_file):
        self.name = name
        self._source = ComposeSource(name, source)
        self._systemd_service = systemd.Service(name)
        self._environment_file = environment_file
        log.debug(f"Initialized portinus.Service for '{name}' with source: '{source}', and environment file: '{environment_file}'")

    def exists(self):
        return os.path.isdir(portinus.get_instance_dir(self.name))

    def _generate_service_file(self):
        start_command = f"{self._source.service_script} up"
        stop_command = f"{self._source.service_script} down"

        template = portinus.get_template("instance.service")
        return template.render(
            name=self.name,
            environment_file=self._environment_file,
            start_command=start_command,
            stop_command=stop_command,
            )

    def ensure(self):
        log.info(f"Creating/updating {self.name} portinus instance")
        self._source.ensure()
        self._systemd_service.ensure(content=self._generate_service_file())

    def remove(self):
        log.info(f"Removing {self.name} portinus instance")
        self._systemd_service.remove()
        self._source.remove()


class ComposeSource(object):

    def __init__(self, name, source):
        self.name = name
        self._source = source
        self.path = portinus.get_instance_dir(name)
        self.service_script = os.path.join(self.path, name)

        if source:
            try:
                with open(os.path.join(source, "docker-compose.yml")):
                    pass
            except Exception as e:
                log.error(f"Unable to access the specified source docker compose file in (#{source})")
                raise(e)
        log.debug(f"Initialized ComposeSource for '{name}' from source: '{source}'")

    def _ensure_service_script(self):
        service_script_template = os.path.join(portinus.template_dir, "service-script")
        shutil.copy(service_script_template, self.service_script)
        os.chmod(self.service_script, 0o755)

    def ensure(self):
        if not self._source:
            log.error("No valid source specified")
            raise(IOError("No valid source specified"))
        log.info("Copying source files for '{self.name}' to '{self.path}'")
        self.remove()
        shutil.copytree(self._source, self.path, symlinks=True, copy_function=shutil.copy)
        self._ensure_service_script()
        log.debug("Successfully copied source files")

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
        self.path = portinus.get_instance_dir(self.name) + ".environment"
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
