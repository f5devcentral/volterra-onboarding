import requests
import json
import logging
from string import Template

get_group_by_name_url_template = "https://graph.microsoft.com/v1.0/groups?$$filter=displayName eq '$name'&$$select=id"
get_group_members_url_template = "https://graph.microsoft.com/v1.0/groups/$group_id/transitiveMembers?$$select=givenName,surname,userPrincipalName,displayName"
get_user_url_template = "https://graph.microsoft.com/v1.0/users?$$filter=userPrincipalName eq '$email'&$$select=givenName,surname,userPrincipalName,displayName"


def getGroupId(authorization_token: str, name: str) -> str:
    """Obtain Azure AD Group ID based upon Group displayName value"""
    graph_url = Template(get_group_by_name_url_template).substitute(name=name)
    resp = getAzureGraph(authorization_token, graph_url)

    # ensure we have an ID
    if len(resp) > 0:
        return resp[0]['id']
    else:
        raise ValueError(f'Azure Group {name} not found')


def getGroupMembers(authorization_token: str, group_id: str) -> [dict]:
    """Get list of Users belonging to the Azure AD group ID"""
    # TODO: handle result pagination

    graph_url = Template(get_group_members_url_template).substitute(
        group_id=group_id)

    resp = getAzureGraph(authorization_token, graph_url)
    users = []
    for user in resp:
        if user['@odata.type'] == "#microsoft.graph.user":
            # make sure givenName and surname exist
            if not user['givenName'] and not user['surname']:
                if user['displayName']:
                    user['givenName'], user['surname'] = user['displayName'].split(
                        " ", 2)
                else:
                    raise ValueError("No givenName or surname found for user")
            users.append({
                "userPrincipalName": user['userPrincipalName'],
                "givenName": user['givenName'],
                "surname": user['surname']
            })
    return users


def getUser(authorization_token: str, email: str) -> dict:
    """Obtain Azure AD user based upon email address"""
    graph_url = Template(get_user_url_template).substitute(email=email)
    resp = getAzureGraph(authorization_token, graph_url)
    if resp:
        # make sure givenName and surname exist
        user = resp[0]
        logging.debug(user)
        logging.debug(
            f'if not {user["givenName"]} and not {user["surname"]}')
        if user['givenName'] is None and user['surname'] is None:
            if user['displayName']:
                user['givenName'], user['surname'] = user['displayName'].split(
                    " ", 2)
            else:
                raise ValueError("No givenName or surname found for user")
        return user
    else:
        raise ValueError(f'Azure AD user {email} not found')


def getAzureGraph(authorization_token: str, url: str) -> dict:
    """Make Azure API Graph GET call with supplied url"""
    payload = []
    graph_response = requests.get(  # Use token to call downstream service
        url,
        headers={'Authorization': 'Bearer ' + authorization_token},)
    graph_response.raise_for_status()

    payload.extend(graph_response.json()['value'])

    # check for pagination
    if '@odata.nextLink' in graph_response.json().keys():
        logging.debug('Pagination detected, process nextLink')
        next_graph_response = getAzureGraph(authorization_token,
                                            graph_response.json()['@odata.nextLink'])
        # check if anything was returned
        if type(next_graph_response) is list:
            payload.extend(next_graph_response)
        elif 'value' in next_graph_response.json().keys():
            payload.extend(next_graph_response.json()['value'])

    # return graph_response
    return payload
