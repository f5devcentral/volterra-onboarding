import sys
import json
import logging
import msal
import os
from pathlib import Path

logging.getLogger("msal").setLevel(logging.INFO)
IN_DOCKER = os.environ.get('IN_DOCKER', False)


def retrieveAccessToken(client_id, tenant_id, secret=None):
    """Authenticate against Azure AD"""
    token_file = str(Path.home()) + '/.volterra/token_cache.json'
    authority = f'https://login.microsoftonline.com/{tenant_id}'

    # setup token cache
    if not IN_DOCKER:
        tokenCache = msal.SerializableTokenCache()
        if os.path.exists(token_file):
            tokenCache.deserialize(
                open(token_file, "r").read())

    # The pattern to acquire a token looks like this.
    app = None
    result = None

    # Check if auth is interactive or not then create a long-lived app instance
    if secret:
        scope = ["https://graph.microsoft.com/.default"]
        app = msal.ConfidentialClientApplication(
            client_id,
            authority=authority,
            client_credential=secret
        )
        result = app.acquire_token_silent(scope, account=None)
    else:
        scope = ["User.ReadBasic.All"]
        if not IN_DOCKER:
            app = msal.PublicClientApplication(
                client_id, authority=authority, token_cache=tokenCache
            )
        else:
            app = msal.PublicClientApplication(
                client_id, authority=authority)
        # Firstly, check the cache to see if this end user has signed in before
        accounts = app.get_accounts()
        if accounts:
            logging.info(
                "Account(s) exists in cache, probably with token too. Let's try.")
            logging.debug("Account(s) already signed in:")
            for a in accounts:
                logging.debug(a["username"])
            # Assuming the end user chose this one to proceed
            chosen = accounts[0]
            logging.debug("Proceed with account: %s" % chosen["username"])
            # Now let's try to find a token in cache for this account
            result = app.acquire_token_silent(scope, account=chosen)

    if not result:
        logging.info(
            "No suitable token exists in cache. Let's get a new one from AAD.")
        if secret:
            logging.info(
                "The Application secret will be used to obtain a token.")
            result = app.acquire_token_for_client(scopes=scope)
        else:
            logging.info(
                "A local browser window will be open for you to sign in. CTRL+C to cancel.")
            result = app.acquire_token_interactive(scope)

    if "access_token" in result:
        if not IN_DOCKER:
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
