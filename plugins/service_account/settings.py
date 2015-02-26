from google.appengine.ext import ndb
from plugins.settings import SettingsModel


class ServiceAccountSettings(SettingsModel):
    _name = 'OAuth2 Service Account'
    _settings_key = 'oauth2_service_account'
    domain = ndb.StringProperty(indexed=False, verbose_name="The Google Apps Domain")
    default_user = ndb.StringProperty(indexed=False, verbose_name="The email of the user to impersonate by default")
    client_email = ndb.StringProperty(indexed=False, verbose_name="1057100193776-hq0fqvtkvs6t69qo14ajvblr27a5gv95.apps.googleusercontent.com")
    private_key = ndb.TextProperty(verbose_name="PEM Format")
