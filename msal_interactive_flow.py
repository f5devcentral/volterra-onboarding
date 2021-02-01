# For simplicity, we'll read config file from 1st CLI param sys.argv[1]
import sys
import json
import logging
import msal
import os
from pathlib import Path

logging.getLogger("msal").setLevel(logging.INFO)


def retrieveAccessToken(client_id, tenant_id):
    """Authenticate against Azure AD"""
    token_file = str(Path.home()) + '/.volterra/token_cache.json'
    authority = f'https://login.microsoftonline.com/{tenant_id}'
    scope = ["User.ReadBasic.All"]
    tokenCache = msal.SerializableTokenCache()
    if os.path.exists(token_file):
        tokenCache.deserialize(
            open(token_file, "r").read())

    # Create a preferably long-lived app instance which maintains a token cache.
    app = msal.PublicClientApplication(
        client_id, authority=authority, token_cache=tokenCache
    )

    # The pattern to acquire a token looks like this.
    result = None

    # Firstly, check the cache to see if this end user has signed in before
    accounts = app.get_accounts()
    if accounts:
        logging.info(
            "Account(s) exists in cache, probably with token too. Let's try.")
        logging.debug("Account(s) already signed in:")
        for a in accounts:
            logging.debug(a["username"])
        chosen = accounts[0]  # Assuming the end user chose this one to proceed
        logging.debug("Proceed with account: %s" % chosen["username"])
        # Now let's try to find a token in cache for this account
        result = app.acquire_token_silent(scope, account=chosen)

    if not result:
        logging.info(
            "No suitable token exists in cache. Let's get a new one from AAD.")
        logging.info(
            "A local browser window will be open for you to sign in. CTRL+C to cancel.")
        result = app.acquire_token_interactive(scope)

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
