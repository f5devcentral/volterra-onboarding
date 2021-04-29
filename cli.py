#!/usr/bin/env python
from binascii import Error
import click
import sys
import json
import os
import logging

from pathlib import Path
from helpers import getAccessToken, processRequest, readConfig, writeConfig

IN_DOCKER = os.environ.get('IN_DOCKER', False)


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
@click.option('--aad-client-id', default=False, help='Azure Active Directory Application Client ID.')
@click.option('--aad-client-secret', default=False, help='Azure Active Directory Application Client secret.')
@click.option('--aad-tenant-id', default=False, help='Azure Active Directory Tenant ID.')
@click.option('--volt-token', default=False, help='VoltConsole access token.')
def add(name, tenant, createns, overwrite, admin, aad_client_id, aad_client_secret, aad_tenant_id, volt_token):
    """Adds user/group to the Volterra Console.

    NAME argument takes:

            - user's email address

            - Azure AD group name

    createns defaults to True.

    overwrite defaults to false.
    """
    try:
        # Get the VoltConsole access token
        if volt_token:
            # passed as option
            token = volt_token
        elif tenant in volterraTenants.keys():
            # in config file
            token = volterraTenants[tenant]
        elif 'volt-token' in os.environ:
            # environment variable
            token = os.getenv('volt-token')
        else:
            raise click.ClickException("No Volterra Tenant token found")

        # check if we're in docker and aad attributes are env vars
        if IN_DOCKER:
            if 'aad-client-id' in os.environ and 'aad-client-secret' in os.environ and 'aad-tenant-id' in os.environ:
                aad_client_id = os.getenv('aad-client-id')
                aad_client_secret = os.getenv('aad-client-secret')
                aad_tenant_id = os.getenv('aad-tenant-id')

        # Get the Azure AD Access Token
        if(aad_client_id and aad_client_secret and aad_tenant_id):
            # information passed via arguments
            authorization_token = getAccessToken(
                aad_client_id, aad_tenant_id, aad_client_secret)
        elif 'client_id' in config.keys() and 'tenant_id' in config.keys():
            # check if a secret is in the config file
            if 'secret' in config.keys():
                authorization_token = getAccessToken(
                    config['client_id'], config['tenant_id'], config['secret'])
            else:
                authorization_token = getAccessToken(
                    config['client_id'], config['tenant_id'])
        else:
            raise click.ClickException("No authorization token found")

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
@click.option('--aad-client-id', default=False, help='Azure Active Directory Application Client ID.')
@click.option('--aad-client-secret', default=False, help='Azure Active Directory Application Client secret.')
@click.option('--aad-tenant-id', default=False, help='Azure Active Directory Tenant ID.')
@click.option('--volt-token', default=False, help='VoltConsole access token.')
def remove(name, tenant, removens, aad_client_id, aad_client_secret, aad_tenant_id, volt_token):
    """Removes user/group to the Volterra Console.

    NAME argument takes:

            - user's email address

            - Azure AD group name

    removens defaults to True.
    """
    try:
        # Get the VoltConsole access token
        if volt_token:
            # passed as option
            token = volt_token
        elif tenant in volterraTenants.keys():
            # in config file
            token = volterraTenants[tenant]
        elif 'volt-token' in os.environ:
            # environment variable
            token = os.getenv('volt-token')
        else:
            raise click.ClickException("No Volterra Tenant token found")

        # check if we're in docker and aad attributes are env vars
        if IN_DOCKER:
            if 'aad-client-id' in os.environ and 'aad-client-secret' in os.environ and 'aad-tenant-id' in os.environ:
                aad_client_id = os.getenv('aad-client-id')
                aad_client_secret = os.getenv('aad-client-secret')
                aad_tenant_id = os.getenv('aad-tenant-id')

        # Get the Azure AD Access Token
        if(aad_client_id and aad_client_secret and aad_tenant_id):
            # information passed via arguments
            authorization_token = getAccessToken(
                aad_client_id, aad_tenant_id, aad_client_secret)
        elif 'client_id' in config.keys() and 'tenant_id' in config.keys():
            # check if a secret is in the config file
            if 'secret' in config.keys():
                authorization_token = getAccessToken(
                    config['client_id'], config['tenant_id'], config['secret'])
            else:
                authorization_token = getAccessToken(
                    config['client_id'], config['tenant_id'])
        else:
            raise click.ClickException("No authorization token found")

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
    # check if auth params passed into cli
    config_file = str(Path.home()) + '/.volterra/config.json'
    config = {}
    if os.path.exists(config_file):
        config = json.load(open(config_file))

    # Set log level
    if 'log_level' in config.keys():
        logging.basicConfig(level=config['log_level'])
    else:
        logging.basicConfig(level=logging.WARNING)

    # load possible tenant tokens
    if config != {}:
        volterraTenants = config['volterra_tenants']
    else:
        volterraTenants = {}

    try:
        cli()
    except ValueError as e:
        click.echo(click.style(str(e), fg='red'))
