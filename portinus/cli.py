#!/usr/bin/env python3

import click
import logging

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
@click.option('--name', required=True, help="The name of the service to remove")
def remove(name):
    service = portinus.Application(name)
    service.remove()


@task.command()
@click.option('--name', required=True, help="The name of the service to create or update.")
@click.option('--source', type=click.Path(exists=True), required=True, help="A path to a folder containg a docker-compose.yml")
@click.option('--env', help="A file containing the list of environment variables to use")
@click.option('--restart', help="Provide a systemd 'OnCalender' scheduling string to force a restart of the service on the specified interval (e.g. 'weekly' or 'daily')")
def ensure(name, source, env, restart):
    service = portinus.Application(name, source=source, environment_file=env, restart_schedule=restart)
    service.ensure()


if __name__ == "__main__":
    task()
