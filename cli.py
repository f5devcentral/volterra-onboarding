#!/usr/bin/env python
import click
import sys
import json

from ms_graph import getGroupId, getGroupMembers, getUser
from msal_interactive_flow import retrieveAccessToken

# Get authorization token
config = json.load(open("config.json"))
authorization_token = retrieveAccessToken(
    config['client_id'], config['authority'], config['scope'])

# Defile CLI group


@click.group()
def cli():
    pass


# Add user/group
@click.command()
@click.argument('name')
@click.option('--tenant', prompt='tenant', help='Volterra tenant name is required.')
@click.option('--createns', default=False, type=bool, help='Create Namespace for user.')
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


cli.add_command(add)
cli.add_command(remove)

if __name__ == '__main__':
    cli()
