from ferris import plugins, settings, ndb
import hashlib

plugins.register('service_account')


def get_config():
    config = settings.get('oauth2_service_account')
    if not config['private_key'] or not config['client_email'] or not config['domain']:
        raise RuntimeError("OAuth2 Service Account is not configured correctly")
    return config


from oauth2client.client import SignedJwtAssertionCredentials
from oauth2client.appengine import StorageByKeyName, CredentialsNDBProperty


def build_credentials(scope, user=None):
    """
    Builds service account credentials using the configuration stored in settings
    and masquerading as the provided user.
    """
    config = get_config()

    if not user:
        user = config['default_user']

    if not isinstance(scope, (list, tuple)):
        scope = [scope]

    key = generate_storage_key(config['client_email'], scope, user)
    storage = StorageByKeyName(ServiceAccountStorage, key, 'credentials')

    creds = SignedJwtAssertionCredentials(
        service_account_name=config['client_email'],
        private_key=config['private_key'],
        scope=scope,
        prn=user)
    creds.set_store(storage)

    return creds


def credentials_to_token(credentials):
    """
    Transforms an Oauth2 credentials object into an OAuth2Token object
    to be used with the legacy gdata API
    """
    import httplib2
    import gdata.gauth

    credentials.refresh(httplib2.Http())
    token = gdata.gauth.OAuth2Token(
        client_id=credentials.client_id,
        client_secret=credentials.client_secret,
        scope=credentials.scope,
        user_agent='lolidk/wtfbbq/cloudsherpas',
        access_token=credentials.access_token,
        refresh_token=credentials.refresh_token)
    return token


class ServiceAccountStorage(ndb.Model):
    """
    Tracks access tokens in the database. The key is
    based on the scopes, user, and clientid
    """
    credentials = CredentialsNDBProperty()

    @classmethod
    def _get_kind(cls):
        return '_ferris_OAuth2ServiceAccountStorage'


def generate_storage_key(client_id, scopes, user):
    s = u"%s%s%s" % (client_id, sorted(scopes), user)
    hash = hashlib.sha1(s.encode())
    return hash.hexdigest()
