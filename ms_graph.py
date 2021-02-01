import requests
import json
from string import Template

get_group_by_name_url_template = "https://graph.microsoft.com/v1.0/groups?$$filter=displayName eq '$name'&$$select=id"
get_group_members_url_template = "https://graph.microsoft.com/v1.0/groups/$group_id/transitiveMembers"


def getGroupId(authorization_token: str, name: str) -> str:
    """Obtain Azure AD Group ID based upon Group displayName value"""
    graph_url = Template(get_group_by_name_url_template).substitute(name=name)
    resp = getAzureGraph(authorization_token, graph_url)

    # ensure we have an ID
    if resp.json()['value'] and 'id' in resp.json()['value'][0].keys():
        return resp.json()['value'][0]['id']
    else:
        raise ValueError(f'Azure AD Group {name} not found')


def getGroupMembers(authorization_token: str, group_id: str) -> str:
    """Get list of Users belonging to the Azure AD group ID"""
    # TODO: handle result pagination

    graph_url = Template(get_group_members_url_template).substitute(
        group_id=group_id)

    resp = getAzureGraph(authorization_token, graph_url)
    users = []
    # Make sure we're processing a user
    for user in resp.json()['value']:
        if user['@odata.type'] == "#microsoft.graph.user":
            users.append({
                "userPrincipalName": user['userPrincipalName'],
                "givenName": user['givenName'],
                "surname": user['surname']
            })
    return users


def getAzureGraph(authorization_token: str, url: str) -> str:
    graph_response = requests.get(  # Use token to call downstream service
        url,
        headers={'Authorization': 'Bearer ' + authorization_token},)
    graph_response.raise_for_status()
    return graph_response
