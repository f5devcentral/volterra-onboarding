#!/usr/bin/env python
from binascii import Error
import click
import sys
import json
import os
import logging

from ms_graph import getGroupId, getGroupMembers, getUser
from msal_interactive_flow import retrieveAccessToken
from pathlib import Path
from helpers import processRequest, readConfig, writeConfig
from volterra_helpers import cliAdd, cliRemove


@click.group()
def cli():
    """CLI to add and remove Azure AD users and groups to the Volterra console"""
    pass


@click.group()
def config():
    """Configure Azure and Volterra access"""
    pass


# Add user/group
@click.command()
@click.argument('name')
@click.option('--tenant', prompt='tenant', help='Volterra tenant name is required.')
@click.option('--createns', default=True, type=bool, help='Create Namespace for user.')
@click.option('--overwrite', default=False, type=bool, help='Overwrite existing Volterra API objects.')
@click.option('--admin', default=False, type=bool, help='Make user Volterra tenant admin')
def add(name, tenant, createns, overwrite, admin):
    """Adds user/group to the Volterra Console.

    NAME argument takes:

            - user's email address

            - Azure AD group name

    createns defaults to True.

    overwrite defaults to false.
    """
    try:
        token = volterraTenants[tenant]
    except KeyError as e:
        # err=True seems to do nothing
        click.echo('No API token found for tenant', err=True)

    response = processRequest(
        'add', authorization_token, name, createns, overwrite, tenant, token, admin)
    logging.debug(f'response:{response}')
    cliDisplayRequestResults('add', response)

    pass


# remove user/group
@click.command()
@click.argument('name')
@click.option('--tenant', prompt='tenant', help='Volterra tenant.')
@click.option('--removens', default=True, type=bool, help='Remove Namespace for user.')
def remove(name, tenant, removens):
    """Removes user/group to the Volterra Console.

    NAME argument takes:

            - user's email address

            - Azure AD group name

    removens defaults to True.
    """
    try:
        token = volterraTenants[tenant]
    except KeyError as e:
        # err=True seems to do nothing
        click.echo('No API token found for tenant', err=True)

    response = processRequest(
        'remove', authorization_token, name, removens, False, tenant, token, False)
    logging.debug(f'response:{response}')

    cliDisplayRequestResults('remove', response)
    pass


@click.command()
@click.option("--clientid", prompt="Client ID", help="Azure Client ID")
@click.option("--tenantid", prompt="Tenant ID", help="Azure Tenant ID")
def azure(clientid: str, tenantid: str):
    """Configure Azure access"""
    data = readConfig(config_file)
    if data is None:
        data = {
            'client_id': clientid,
            'tenant_id': tenantid
        }
    else:
        data['client_id'] = clientid
        data['tenant_id'] = tenantid

    payload = writeConfig(config_file, data)
    pass


@ click.command()
@ click.option("--tenant", prompt="tenant", help="Volterra Tenant Name")
@ click.option("--apikey", prompt="API Key", help="Volterra API ID")
def volterra(tenant: str, apikey: str):
    """Configure Volterra access"""
    data = readConfig(config_file)
    if data is None:
        data = {
            'volterra_tenants': {
                tenant: apikey
            }
        }
    else:
        if 'volterra_tenants' in data.keys():
            data['volterra_tenants'][tenant] = apikey
        else:
            data['volterra_tenants'] = {tenant: apikey}
    payload = writeConfig(config_file, data)
    pass


@ click.command()
@ click.option("--level", prompt="log level", help="CLI log level")
def logLevel(level: str):
    """Configure CLI log level.

    Supported levels:

    - CRITICAL

    - ERROR

    - WARNING

    - INFO

    - DEBUG
    """
    data = readConfig(config_file)
    if data is None:
        data = {'log_level': level}
    else:
        data['log_level'] = level
    payload = writeConfig(config_file, data)
    pass


def cliDisplayRequestResults(action, users):
    """Display the process requests results in the CLI"""
    # display results
    msg = ''
    err_msg = ''
    if action == 'add':
        msg = 'added'
        err_msg = 'not added'
    else:
        msg = 'removed'
        err_msg = 'not removed'
    for user in users:
        if user['result']['status'] == 'success':
            click.echo(click.style(
                f'user {user["surname"]}, {user["givenName"]} {msg}', fg='green'))
        else:
            click.echo(click.style(
                f'user {user["surname"]}, {user["givenName"]} {err_msg}: {user["result"]["reason"]}', fg='red'))

    pass


cli.add_command(add)
cli.add_command(remove)
cli.add_command(config)
config.add_command(azure)
config.add_command(volterra)
config.add_command(logLevel)

if __name__ == '__main__':
    # load config data
    config_file = str(Path.home()) + '/.volterra/config.json'
    config = {}
    if os.path.exists(config_file):
        config = json.load(open(config_file))

    # Set log level
    if 'log_level' in config.keys():
        logging.basicConfig(level=config['log_level'])
    else:
        logging.basicConfig(level=logging.WARNING)
    # Get authorization token

    if 'client_id' in config.keys() and 'tenant_id' in config.keys():
        authorization_token = retrieveAccessToken(
            config['client_id'], config['tenant_id'])

    # load possible tenant tokens
    volterraTenants = config['volterra_tenants']

    try:
        cli()
    except ValueError as e:
        click.echo(click.style(str(e), fg='red'))
