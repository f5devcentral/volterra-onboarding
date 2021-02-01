#!/usr/bin/env python
import click
import sys
import json
import os

from ms_graph import getGroupId, getGroupMembers, getUser
from msal_interactive_flow import retrieveAccessToken
from pathlib import Path

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
    os.makedirs(os.path.dirname(config_file), exist_ok=True)
    if os.path.exists(config_file):
        with open(config_file, 'r+') as f:
            data = json.load(f)
            data['client_id'] = clientid
            data['tenant_id'] = tenantid
            f.seek(0)
            f.write(json.dumps(data))
            f.truncate()
    else:
        payload = {
            'client_id': clientid,
            'tenant_id': tenantid
        }
        with open(config_file, 'w') as f:
            f.write(json.dumps(payload))
            f.close
        os.chmod(config_file, 0o600)
    pass


@click.command()
@click.option("--tenant", prompt="tenant", help="Volterra Tenant Name")
@click.option("--apikey", prompt="API Key", help="Volterra API ID")
def volterra(tenant: str, apikey: str):
    """Configure Volterra access"""
    os.makedirs(os.path.dirname(config_file), exist_ok=True)
    if os.path.exists(config_file):
        with open(config_file, 'r+') as f:
            data = json.load(f)
            data[tenant] = apikey
            f.seek(0)
            f.write(json.dumps(data))
            f.truncate()
    else:
        payload = {
            tenant: apikey
        }
        with open(config_file, 'w') as f:
            f.write(json.dumps(payload))
            f.close
        os.chmod(config_file, 0o600)
    pass


cli.add_command(add)
cli.add_command(remove)
cli.add_command(config)
config.add_command(azure)
config.add_command(volterra)

if __name__ == '__main__':
    config_file = str(Path.home()) + '/.volterra/config.json'

    # Get authorization token
    config = json.load(open(config_file))
    authorization_token = retrieveAccessToken(
        config['client_id'], config['tenant_id'])
    cli()
