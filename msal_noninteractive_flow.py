import sys
import json
import logging
import msal
import os
from pathlib import Path

logging.getLogger("msal").setLevel(logging.DEBUG)


def retrieveAccessToken(client_id, tenant_id, secret):
    """Authenticate against Azure AD"""
    token_file = str(Path.home()) + '/.volterra/token_cache.json'
    authority = f'https://login.microsoftonline.com/{tenant_id}'
    scope = ["https://graph.microsoft.com/.default"]
    tokenCache = msal.SerializableTokenCache()
    if os.path.exists(token_file):
        tokenCache.deserialize(
            open(token_file, "r").read())

    # Create a preferably long-lived app instance which maintains a token cache.
    app = msal.ConfidentialClientApplication(
        client_id,
        authority=authority,
        client_credential=secret
    )

    # The pattern to acquire a token looks like this.
    result = None

    result = app.acquire_token_silent(scope, account=None)

    if not result:
        logging.info(
            "No suitable token exists in cache. Let's get a new one from AAD.")
    result = app.acquire_token_for_client(scopes=scope)

    if "access_token" in result:
        open(token_file, "w").write(
            tokenCache.serialize())
        os.chmod(token_file, 0o600)
        return result['access_token']
    else:
        logging.debug(result.get("error"))
        logging.debug(result.get("error_description"))
        # You may need this when reporting a bug
        logging.debug(result.get("correlation_id"))
        return None
