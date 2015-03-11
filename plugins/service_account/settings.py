from google.appengine.ext import ndb
from plugins.settings import SettingsModel


class ServiceAccountSettings(SettingsModel):
    _name = 'OAuth2 Service Account'
    _settings_key = 'oauth2_service_account'
    domain = ndb.StringProperty(indexed=False, verbose_name="sherpatest.com")
    default_user = ndb.StringProperty(indexed=False, verbose_name="richmond.gozarin@sherpatest.com")
    client_email = ndb.StringProperty(indexed=False, verbose_name="566305864248-jqrmu5pup0t108pt97nqq9mt1ijv7mto@developer.gserviceaccount.com")
    private_key = ndb.TextProperty(verbose_name="PEM Format")
