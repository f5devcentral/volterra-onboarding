from msal_interactive_flow import retrieveAccessToken
import json
import requests
import sys

config = json.load(open(sys.argv[1]))
authorization_token = retrieveAccessToken(
    config['client_id'], config['authority'], config['scope'])

if authorization_token:
    # Calling graph using the access token
    graph_response = requests.get(  # Use token to call downstream service
        config["test_group"],
        headers={'Authorization': 'Bearer ' + authorization_token},)
    print("Graph API call result: %s ..." % graph_response.text[:100])
    for user in graph_response:
        print(user)
else:
    print("No Authorization token returned")
