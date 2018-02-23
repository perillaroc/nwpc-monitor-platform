#!/usr/bin/env python
"""
run a simple nwpc_monitor_broker server.

Set environment variable NWPC_MONITOR_BROKER_CONFIG.
"""
import click
import os
import sys

if 'NWPC_MONITOR_PLATFORM_BASE' in os.environ:
    sys.path.append(os.environ['NWPC_MONITOR_PLATFORM_BASE'])


@click.command()
@click.option('-c', '--config-file', help='config file path')
def runserver(config_file):
    """
    DESCRIPTION
        Run nwpc monitor broker.
    """
    if config_file:
        os.environ['NWPC_MONITOR_BROKER_CONFIG'] = config_file

    from nwpc_monitor_broker import create_app
    app = create_app()

    app.run(
        host=app.config['BROKER_CONFIG']['host']['ip'],
        port=app.config['BROKER_CONFIG']['host']['port']
    )

if __name__ == '__main__':
    runserver()