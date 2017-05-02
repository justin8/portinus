import docker
import logging
import os
import subprocess
import sys

import portinus

log = logging.getLogger(__name__)


def check_permissions():
    if os.geteuid() != 0:
        log.error("This script must be run as root!")
        raise PermissionError("You must be root")


def run(name):
    check_permissions()

    systemd_service = portinus.systemd.Unit(name)
    monitored_compose_containers = get_monitored_compose_containers(name)

    for container in monitored_compose_containers:
        log.debug(f"Checking container {container.id}, name: '{container.attrs['Name']}'")
        if not check_container_health(container):
            log.warning(f"Container {container.id}, name: '{container.attrs['Name']}'. Restarting stack for {name}")
            systemd_service.restart()
            return False
    log.info("No unhealthy containers found")


def check_container_health(container):
    status = container.attrs["State"]["Health"]["Status"]
    return status != "unhealthy"


def get_monitored_compose_containers(name):
    compose_container_ids = get_compose_container_ids(name)
    monitored_containers = get_monitored_containers()
    monitored_compose_containers = []

    for container_id in compose_container_ids:
        valid_container = next((x for x in monitored_containers if x.id == container_id), None)
        if valid_container: monitored_compose_containers.append(valid_container)

    log.debug(f"Found {len(monitored_compose_containers)} monitored containers from docker-compose")
    return monitored_compose_containers


def get_compose_container_ids(name):
    compose_source = portinus.portinus.ComposeSource(name, None)
    service_script = compose_source.service_script

    compose_output = subprocess.check_output([service_script, "ps", "-q"]).decode("utf-8")
    container_list = compose_output.split("\n")

    filtered_container_list = list((x for x in container_list if x))

    log.debug(f"Found {len(filtered_container_list)} total containers from docker-compose")
    return filtered_container_list


def get_monitored_containers():
    client = docker.from_env()

    all_containers = client.containers.list()

    monitored_containers = []

    for container in all_containers:
        if 'Health' in container.attrs['State']:
            monitored_containers.append(container)

    log.debug(f"Found {len(monitored_containers)} monitored containers from docker")
    return monitored_containers
