#!/usr/bin/env python

import click
import json
import logging
import sys
import os

from ms_graph import getGroupId, getGroupMembers
from msal_interactive_flow import retrieveAccessToken
from volterra_helpers import createVoltSession, createUserCache
from helpers import readConfig
from pathlib import Path

# logging.basicConfig(level=logging.DEBUG)


@click.command()
@click.option('--name', prompt='group name', help='Azure AD Group name')
@click.option('--tenant', prompt='tenant', help='Volterra tenant name')
def compare(name, tenant):
    """Compares Volterra Console Users vs. AD Group"""

    # get group data from Azure AD
    id = getGroupId(authorization_token, name)
    # get group members from Azure AD
    u = getGroupMembers(authorization_token, id)
    # logging.debug(f'group_users:{u}')

    # get volterra console users
    try:
        token = volterraTenants[tenant]
    except KeyError as e:
        # err=True seems to do nothing
        click.echo('No API token found for tenant', err=True)

    s = createVoltSession(token, tenant)
    c = createUserCache(s)
    # logging.debug(f'console_users:{c["tenantUsers"]}')

    # convert c to a list
    c_list = []
    for user in c['tenantUsers']:
        c_list.append({
            'userPrincipalName': user['email'],
            'givenName': user['first_name'],
            'surname': user['last_name']
        })

    # normalize both lists and remove anything but userPrincipalName
    for user in u:
        user['userPrincipalName'] = user['userPrincipalName'].lower()
        del user['givenName']
        del user['surname']

    for user in c_list:
        user['userPrincipalName'] = user['userPrincipalName'].lower()
        del user['givenName']
        del user['surname']

    # compare lists
    res = [x for x in u + c_list if x not in u]
    # print(res)
    for user in res:
        click.echo(user['userPrincipalName'])
    pass


if __name__ == '__main__':

    # load config data
    config_file = str(Path.home()) + '/.volterra/config.json'
    config = {}
    if os.path.exists(config_file):
        config = json.load(open(config_file))

    if 'client_id' in config.keys() and 'tenant_id' in config.keys():
        authorization_token = retrieveAccessToken(
            config['client_id'], config['tenant_id'])

    # load possible tenant tokens
    volterraTenants = config['volterra_tenants']

    try:
        compare()
    except ValueError as e:
        click.echo(click.style(str(e), fg='red'))
