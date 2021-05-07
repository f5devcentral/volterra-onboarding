import os
import json
import logging

from ms_graph import getGroupId, getGroupMembers, getUser
from msal_flow import retrieveAccessToken
from volterra_helpers import createVoltSession, cliAdd, cliRemove, isWingmanReady, getWingmanSecret
from pathlib import Path

IN_DOCKER = os.environ.get('IN_DOCKER', False)


def getAccessToken(client_id: str, tenant_id: str, secret: str = None) -> str:
    """Return an Azure AD OAuth token"""
    return retrieveAccessToken(client_id, tenant_id, secret)


def readConfig(config_file: str) -> str:
    """Read the supplied JSON config config_file"""
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            data = json.load(f)
        return data
    else:
        return None


def writeConfig(config_file: str, data: str) -> str:
    """Overwrite data to the supplied JSON config config_file"""
    os.makedirs(os.path.dirname(config_file), exist_ok=True)
    with open(config_file, 'w') as f:
        f.write(json.dumps(data))
        f.close
    os.chmod(config_file, 0o600)


def processUser(session: dict, action: str, namespace_action: bool, overwrite: bool, tenant: str, token: str, user: dict, admin: bool) -> dict:
    """Add or remove a user from Volterra Console"""
    if action == 'add':
        result = cliAdd(session, user['userPrincipalName'],
                        user['givenName'], user['surname'], namespace_action, overwrite, admin)
        logging.debug(f'result:{result}')
        return result
    else:
        result = cliRemove(session, user['userPrincipalName'])
        logging.debug(f'result:{result}')
        return result


def processRequest(action: str, name: str, namespace_action: bool, overwrite: bool, tenant: str, admin: bool) -> dict:
    """Process request to add or remove user(s) from Volterra Console"""
    logging.debug(
        f'action:{action}, name:{name}, tenant:{tenant}, namespace_action:{namespace_action}')

    # obtain Volterra and Azure AD access tokens
    authorization_token = None
    token = None
    secrets = {}

    # Check if cli is interactive or in a container
    if IN_DOCKER:
        # Check if token is in environment variable
        secrets = {
            "volt-token": os.environ.get('VOLT_TOKEN', None),
            "aad-client-id": os.environ.get('AAD_CLIENT_ID', None),
            "aad-client-secret": os.environ.get('AAD_CLIENT_SECRET', None),
            "aad-tenant-id": os.environ.get('AAD_TENANT_ID', None)
        }

        # If we're in Volterra, unblindfold the secrets
        if isWingmanReady():
            for secret in secrets:
                value = getWingmanSecret(secret)
                if value is None:
                    click.ClickException(f"No value for {secret} found")
                else:
                    secrets[secret] = value

    # CLI interactive, find token in config file
    else:
        # load config data
        # check if auth params passed into cli
        config_file = str(Path.home()) + '/.volterra/config.json'
        config = {}
        if os.path.exists(config_file):
            config = json.load(open(config_file))

        if tenant in config['volterra_tenants'].keys():
            secrets = {
                "volt-token": config['volterra_tenants'][tenant],
                "aad-client-id": config['client_id'],
                "aad-client-secret": None,
                "aad-tenant-id": config['tenant_id'],
            }
        else:
            raise click.ClickException(
                "No Volterra Tenant configuration found")

    # get authorization token:
    authorization_token = getAccessToken(
        secrets['aad-client-id'], secrets['aad-tenant-id'], secrets['aad-client-secret'])

    # setup volterra access token
    token = secrets['volt-token']

    payload = []
    # create session for volt api
    session = createVoltSession(token, tenant)

    # determine if we're processing a user or a group
    if "@" in name:
        logging.debug(f'{action} a user')
        # get user data from Azure AD
        user = getUser(authorization_token, name)
        logging.debug(f'user:{user}')
        # Process user
        result = processUser(session, action, namespace_action,
                             overwrite, tenant, token, user, admin)
        logging.debug(f'processUser:{result}')
        # build response payload
        logging.debug(f'user:{user}')
        user['result'] = result
        payload.append(user)
    else:
        logging.debug(f'{action} a group')
        # get group data from Azure AD
        id = getGroupId(authorization_token, name)
        # get group members from Azure AD
        users = getGroupMembers(authorization_token, id)
        logging.debug(f'users:{users}')
        # process each user
        for user in users:
            result = processUser(session, action, namespace_action,
                                 overwrite, tenant, token, user, admin)
            logging.debug(f'processUser:{result}')
            # build response payload
            user['result'] = result
            payload.append(user)

    return payload
