from google.appengine.ext import ndb
from plugins.settings import SettingsModel


class ServiceAccountSettings(SettingsModel):
    _name = 'OAuth2 Service Account'
    _settings_key = 'oauth2_service_account'
    domain = ndb.StringProperty(indexed=False, verbose_name="arista.com")
    default_user = ndb.StringProperty(indexed=False, verbose_name="sherpa_bot@arista.com")
    client_email = ndb.StringProperty(indexed=False, verbose_name="61726108322-6jprbbvjrge9m5e6uqknskg534hgra8g@developer.gserviceaccount.com")
    private_key = ndb.TextProperty(verbose_name="PEM Format")
