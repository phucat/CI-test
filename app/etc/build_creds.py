from oauth2client.client import SignedJwtAssertionCredentials
import httplib2


def build_credentials(scope, service_account_name, private_key, user=None):
    """
    Builds service account credentials using the configuration stored in settings
    and masquerading as the provided user.
    """
    if not user:
        user = 'paul.mclain@sherpatest.com'

    if not isinstance(scope, (list, tuple)):
        scope = [scope]

    try:
        creds = SignedJwtAssertionCredentials(
            service_account_name=service_account_name,
            private_key=private_key,
            scope=scope,
            prn=user)
    except:
        creds = False

    return creds


def build_client(credentials):
    try:
        http = httplib2.Http()
        credentials.authorize(http)
    except:
        http = False

    return http
