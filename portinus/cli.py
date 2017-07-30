#!/usr/bin/env python3

import click
import logging
import sys

import portinus

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


def set_log_level(verbose):
    log_level = logging.WARNING
    if verbose == 1:
        log_level = logging.INFO
    if verbose >= 2:
        log_level = logging.DEBUG
    logging.basicConfig(level=log_level)


@click.group()
@click.option('-v', '--verbose', count=True, help="Enable more logging. More -v's for more logging")
def task(verbose):
    set_log_level(verbose)


@task.command()
@click.argument('name', required=True)
def remove(name):
    try:
        application = portinus.Application(name)
        application.remove()
    except PermissionError:
        click.echo("Failed to remove the application due to a permissions error")
        sys.exit(1)


@task.command()
@click.argument('name', required=True)
@click.option('--source', type=click.Path(exists=True), required=True, help="A path to a folder containg a docker-compose.yml")
@click.option('--env', help="A file containing the list of environment variables to use")
@click.option('--restart', help="Provide a systemd 'OnCalender' scheduling string to force a restart of the service on the specified interval (e.g. 'weekly' or 'daily')")
def ensure(name, source, env, restart):
    try:
        application = portinus.Application(name, source=source, environment_file=env, restart_schedule=restart)
    except PermissionError:
        click.echo("Failed to create the application due to a permissions error")
        sys.exit(1)
    application.ensure()


@task.command()
@click.argument('name', required=True)
def restart(name):
    application = portinus.Application(name)
    application.service.restart()


@task.command()
@click.argument('name', required=True)
def stop(name):
    application = portinus.Application(name)
    application.service.stop()


@task.command()
def list():
    try:
        portinus.list()
    except FileNotFoundError:
        pass

@task.command()
@click.pass_context
def ls(ctx):
    ctx.forward(list)
    ctx.invoke(list)


@task.command()
@click.argument('name', required=True)
@click.argument('args', required=True, nargs=-1)
def compose(name, args):
    application = portinus.Application(name)
    application.service.compose(args)


if __name__ == "__main__":
    task()
