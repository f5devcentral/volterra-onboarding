import os
import json
import logging

from ms_graph import getGroupId, getGroupMembers, getUser
from msal_flow import retrieveAccessToken
from volterra_helpers import createVoltSession, cliAdd, cliRemove


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


def processRequest(action: str, authorization_token: str, name: str, namespace_action: bool, overwrite: bool, tenant: str, token: str, admin: bool) -> dict:
    """Process request to add or remove user(s) from Volterra Console"""
    logging.debug(
        f'action:{action}, name:{name}, tenant:{tenant}, namespace_action:{namespace_action}')

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
