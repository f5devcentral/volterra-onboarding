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
from helpers import readConfig, writeConfig
from volterra_helpers import cliAdd, cliRemove

# logging.basicConfig(level=logging.WARNING)
logging.basicConfig(level=logging.DEBUG)


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
def add(name, tenant, createns, overwrite):
    """Adds user/group to the Volterra Console.

    NAME argument takes:

            - user's email address

            - Azure AD group name

    createns defaults to True.

    overwrite defaults to false.
    """
    logging.debug('adding user/group')
    logging.debug(f'tenant:{tenant}')
    logging.debug(f'name:{name}')
    logging.debug(f'create namespace:{createns}')
    logging.debug(f'overwrite:{overwrite}')

    # ensure we have an authorization token
    if "authorization_token" not in globals():
        logging.debug('No authorization token found')
        raise ValueError('No configuration found')

    # ensure we have an API token for the Volterra tenant
    try:
        token = volterraTenants[tenant]
    except KeyError as e:
        click.echo('No API token found for tenant', err=True) #err=True seems to do nothing

    # determine if name is a user or group
    if "@" in name:
        logging.debug('adding a user')
        # Get user data from Azure AD
        try:
            user = getUser(authorization_token, name)
            logging.debug(f'user:{user}')
            click.echo(click.style(
                f'Adding user:{user["surname"]}, {user["givenName"]}', fg='green'))
        except ValueError as e:
            click.echo(e, err=True)

        # Call Volterra API for proposed changes
        try:
            result = cliAdd(token, tenant, user['userPrincipalName'], user['givenName'], user['surname'], createns, overwrite)
            logging.debug(f'result:{result}')
        except Exception as e:
            click.echo(e, err=True)

    else:
        logging.debug('adding a group')
        # Get group member data from Azure AD
        try:
            id = getGroupId(authorization_token, name)
            users = getGroupMembers(authorization_token, id)
            logging.debug(f'users:{users}')
            for user in users:
                click.echo(click.style(
                    f'Adding user:{user["surname"]}, {user["givenName"]}', fg='green'))
                # Call Volterra API for each user. 
                # TBD: refactor this to share a session 
                try:
                    result = cliAdd(token, tenant, user['userPrincipalName'], user['givenName'], user['surname'], createns, overwrite)
                    logging.debug(f'result:{result}')
                except Exception as e:
                    click.echo(e, err=True)
        except ValueError as e:
            click.echo(e, err=True)


# remove user/group
@click.command()
@click.argument('name')
@click.option("--tenant", prompt="tenant", help="Volterra tenant.")
@click.option('--removens', default=True, type=bool, help='Remove Namespace for user.')
def remove(name, tenant, removens):
    """Removes user/group to the Volterra Console.

    NAME argument takes:

            - user's email address

            - Azure AD group name

    removens defaults to True.
    """
    logging.debug('removing user/group')
    logging.debug(f'tenant:{tenant}')
    logging.debug(f'name:{name}')
    logging.debug(f'remove namespace:{removens}')
    click.echo('FEATURE NOT IMPLEMENTED YET')
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
        data['volterra_tenants'][tenant] = apikey
    payload = writeConfig(config_file, data)
    pass


cli.add_command(add)
cli.add_command(remove)
cli.add_command(config)
config.add_command(azure)
config.add_command(volterra)

if __name__ == '__main__':
    config_file = str(Path.home()) + '/.volterra/config.json'
    if os.path.exists(config_file):

        # Get authorization token
        config = json.load(open(config_file))
        if 'client_id' in config.keys() and 'tenant_id' in config.keys():
            authorization_token = retrieveAccessToken(
                config['client_id'], config['tenant_id'])
            # logging.debug(f'authorization_token: {authorization_token}')

        # load possible tenant tokens
        volterraTenants = config['volterra_tenants']
    

    try:
        cli()
    except ValueError as e:
        click.echo(click.style(str(e), fg='red'))
