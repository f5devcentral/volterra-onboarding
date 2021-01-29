import sys
# import requests
import json
from msal_interactive_flow import retrieveAccessToken
from ms_graph import getGroupMembers

config = json.load(open(sys.argv[1]))
authorization_token = retrieveAccessToken(
    config['client_id'], config['authority'], config['scope'])

if authorization_token:
    group_members = getGroupMembers(
        authorization_token, config['test_group_id'])

    print(group_members)

else:
    print("No Authorization token returned")
