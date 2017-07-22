#!/usr/bin/env python3

import click
import logging
import sys

import portinus

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group()
@click.option('-v', '--verbose', count=True, help="Enable more logging. More -v's for more logging")
def task(verbose):
    log_level = logging.WARNING
    if verbose == 1:
        log_level = logging.INFO
    if verbose >= 2:
        log_level = logging.DEBUG
    logging.basicConfig(level=log_level)


@task.command()
@click.argument('name', required=True)
def remove(name):
    try:
        service = portinus.Application(name)
    except PermissionError:
        sys.exit(1)
    service.remove()


@task.command()
@click.argument('name', required=True)
@click.option('--source', type=click.Path(exists=True), required=True, help="A path to a folder containg a docker-compose.yml")
@click.option('--env', help="A file containing the list of environment variables to use")
@click.option('--restart', help="Provide a systemd 'OnCalender' scheduling string to force a restart of the service on the specified interval (e.g. 'weekly' or 'daily')")
def ensure(name, source, env, restart):
    try:
        service = portinus.Application(name, source=source, environment_file=env, restart_schedule=restart)
    except PermissionError:
        sys.exit(1)
    service.ensure()


@task.command()
@click.argument('name', required=True)
def restart(name):
    service = portinus.portinus.Service(name)
    service.restart()


@task.command()
@click.argument('name', required=True)
def stop(name):
    service = portinus.portinus.Service(name)
    service.stop()


@task.command()
def list():
    portinus.list()


@task.command()
@click.argument('name', required=True)
@click.argument('args', required=True, nargs=-1)
def compose(name, args):
    try:
        service = portinus.portinus.Service(name)
        service.compose(args)
    except (PermissionError, ValueError) as e:
        print(e)
        sys.exit(1)


if __name__ == "__main__":
    task()
