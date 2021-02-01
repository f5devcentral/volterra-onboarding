#!/usr/bin/env python
import click
import sys
import json
import os

from ms_graph import getGroupId, getGroupMembers, getUser
from msal_interactive_flow import retrieveAccessToken
from pathlib import Path
from helpers import readConfig, writeConfig

# Defile CLI group


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
def add(name, tenant, createns):
    """Adds user/group to the Volterra Console.

    NAME argument takes:

            - user's email address

            - Azure AD group name

    createns defaults to False.
    """
    click.echo('adding user/group')
    click.echo(f'tenant:{tenant}')
    click.echo(f'name:{name}')
    click.echo(f'create namespace:{createns}')

    # determine if name is a user or group
    if "@" in name:
        click.echo('adding a user')
        # Get user data from Azure AD
        try:
            user = getUser(authorization_token, name)
            print(user)
        except ValueError as e:
            click.echo(e)
    else:
        click.echo('adding a group')
        # Get group member data from Azure AD
        try:
            id = getGroupId(authorization_token, name)
            users = getGroupMembers(authorization_token, id)
            print(users)
        except ValueError as e:
            click.echo(e)


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
    click.echo('removing user/group')
    click.echo(f'tenant:{tenant}')
    click.echo(f'name:{name}')
    click.echo(f'remove namespace:{removens}')
    click.echo('FEATURE NOT IMPLEMENTED YET')
    pass


@click.command()
@click.option("--clientid", prompt="Client ID", help="Azure Client ID")
@click.option("--tenantid", prompt="Tenant ID", help="Azure Tenant ID")
def azure(clientid: str, tenantid: str):
    """Configure Azure access"""
    data = readConfig(config_file)
    data['client_id'] = clientid
    data['tenant_id'] = tenantid
    payload = writeConfig(config_file, data)
    pass


@click.command()
@click.option("--tenant", prompt="tenant", help="Volterra Tenant Name")
@click.option("--apikey", prompt="API Key", help="Volterra API ID")
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
    else:
        click.echo('No config file found')
    cli()
