from google.appengine.ext import ndb
from plugins.settings import SettingsModel


class ServiceAccountSettings(SettingsModel):
    _name = 'OAuth2 Service Account'
    _settings_key = 'oauth2_service_account'
    domain = ndb.StringProperty(indexed=False, verbose_name="sherpatest.com")
    default_user = ndb.StringProperty(indexed=False, verbose_name="richmond.gozarin@sherpatest.com")
    client_email = ndb.StringProperty(indexed=False, verbose_name="118341588591-47m8igkcn0h9r3uajajcetsgo7f574qc@developer.gserviceaccount.com")
    private_key = ndb.TextProperty(verbose_name="PEM Format")
