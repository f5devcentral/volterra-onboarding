import requests
import json
from string import Template

get_group_by_name_url_template = "https://graph.microsoft.com/v1.0/groups?$$filter=displayName eq '$name'&$$select=id"
get_group_members_url_template = "https://graph.microsoft.com/v1.0/groups/$group_id/transitiveMembers"
get_user_url_template = "https://graph.microsoft.com/v1.0/users?$$filter=userPrincipalName eq '$email'&$$select=givenName,surname,userPrincipalName"


def getGroupId(authorization_token: str, name: str) -> str:
    """Obtain Azure AD Group ID based upon Group displayName value"""
    graph_url = Template(get_group_by_name_url_template).substitute(name=name)
    resp = getAzureGraph(authorization_token, graph_url)

    # ensure we have an ID
    if resp.json()['value'] and 'id' in resp.json()['value'][0].keys():
        return resp.json()['value'][0]['id']
    else:
        raise ValueError(f'Azure AD Group {name} not found')


def getGroupMembers(authorization_token: str, group_id: str) -> [dict]:
    """Get list of Users belonging to the Azure AD group ID"""
    # TODO: handle result pagination

    graph_url = Template(get_group_members_url_template).substitute(
        group_id=group_id)

    resp = getAzureGraph(authorization_token, graph_url)
    users = []
    # Make sure we're processing a user
    if resp.json()['value']:
        for user in resp.json()['value']:
            if user['@odata.type'] == "#microsoft.graph.user":
                users.append({
                    "userPrincipalName": user['userPrincipalName'],
                    "givenName": user['givenName'],
                    "surname": user['surname']
                })
        return users
    else:
        raise ValueError(f'Azure AD Group {group_id} has no members')


def getUser(authorization_token: str, email: str) -> dict:
    """Obtain Azure AD user based upon email address"""
    graph_url = Template(get_user_url_template).substitute(email=email)
    resp = getAzureGraph(authorization_token, graph_url)
    if resp.json()['value']:
        return resp.json()['value'][0]
    else:
        raise ValueError(f'Azure AD user {email} not found')


def getAzureGraph(authorization_token: str, url: str) -> dict:
    """Make Azure API Graph GET call with supplied url"""
    graph_response = requests.get(  # Use token to call downstream service
        url,
        headers={'Authorization': 'Bearer ' + authorization_token},)
    graph_response.raise_for_status()
    return graph_response
