import requests
import json
from string import Template

graph_url_template = "https://graph.microsoft.com/v1.0/groups/$group_id/transitiveMembers"


def getGroupMembers(authorization_token, group_id):

    graph_url = Template(graph_url_template)
    graph_response = requests.get(  # Use token to call downstream service
        graph_url.substitute(group_id=group_id),
        headers={'Authorization': 'Bearer ' + authorization_token},)
    graph_response.raise_for_status()

    users = []
    # Make sure we're processing a user
    for user in graph_response.json()['value']:
        if user['@odata.type'] == "#microsoft.graph.user":
            users.append({
                "userPrincipalName": user['userPrincipalName'],
                "givenName": user['givenName'],
                "surname": user['surname']
            })
    return users
