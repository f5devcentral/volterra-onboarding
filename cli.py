#!/usr/bin/env python
import click


@click.group()
def cli():
    pass


@click.command()
@click.argument('name')
@click.option('--tenant', prompt='tenant', help='Volterra tenant name is required.')
@click.option('--createns', default=False, type=bool, help='Create Namespace for user.')
def add(name, tenant, createns):
    """Adds user/group to the Volterra Console.

    NAME argument takes:

            - user's email address

            - Azure AD group name
    """
    click.echo('adding user/group')
    click.echo(f'tenant:{tenant}')
    click.echo(f'name:{name}')
    click.echo(f'create namespace:{createns}')


@click.command()
@click.argument('name')
@click.option("--tenant", prompt="tenant", help="Volterra tenant.")
@click.option('--removens', default=True, type=bool, help='Remove Namespace for user.')
def remove(name, tenant, removens):
    """Removes user/group to the Volterra Console.

    NAME argument takes:

            - user's email address

            - Azure AD group name
    """
    click.echo('removing user/group')
    click.echo(f'tenant:{tenant}')
    click.echo(f'name:{name}')
    click.echo(f'remove namespace:{removens}')


cli.add_command(add)
cli.add_command(remove)

if __name__ == '__main__':
    cli()
