"""
This file is used to configure application settings.

Do not import this file directly.

You can use the settings API via:

    from ferris import settings

    mysettings = settings.get("mysettings")

The settings API will load the "settings" dictionary from this file. Anything else
will be ignored.

Optionally, you may enable the dynamic settings plugin at the bottom of this file.
"""

settings = {}

settings['timezone'] = {
    'local': 'US/Eastern'
}

settings['email'] = {
    # Configures what address is in the sender field by default.
    'sender': None
}

settings['app_config'] = {
    'webapp2_extras.sessions': {
        # WebApp2 encrypted cookie key
        # You can use a UUID generator like http://www.famkruithof.net/uuid/uuidgen
        'secret_key': '9a788030-837b-11e1-b0c4-0800200c9a66',
    }
}

settings['oauth2'] = {
    # OAuth2 Configuration should be generated from
    # the google cloud console (Credentials for Web Application)
    'client_id': None,  # '581834470130-r9e1et657iitjviebthvkv3aieofrbei.apps.googleusercontent.com',  # XXXXXXXXXXXXXXX.apps.googleusercontent.com
    'client_secret': None,  # '030txQTlh75wMQ1ZUqYd6Waw',
    'developer_key': None  # Optional
}

# arista-calendar-01
settings['oauth2_service_account'] = {
    # OAuth2 service account configuration should be generated
    # from the google cloud console (Service Account Credentials)
    'client_email': '61726108322-7gnl78qvf5b4iudpk6e7l9rb9totacjs@developer.gserviceaccount.com',  # XXX@developer.gserviceaccount.com
    'private_key': """-----BEGIN PRIVATE KEY-----
MIICdQIBADANBgkqhkiG9w0BAQEFAASCAl8wggJbAgEAAoGBAL3kfZbZC2maFrkc
7BoOWc5nvETUItuPYPwc4qmSpexA6lrWgx1po00jjYe7ZZSaFJgBMn+iBherEGxZ
ELwV8RV9tZkWpBuUkc3jHGZtUiYF9I8eMXnXTq32qLXA5+150isuNMfVgzMuE37X
pUa8k9rOT5fylma1jYneiCgYfz+FAgMBAAECgYArN0wJv52kS+gt+tIU3/06R0uG
kozYURouZliDZReT2/Y59CXk1LzQem3kXRayKhrTuToH6BTg4BKdxetUEt5Js/Tx
CscCAqnZJvMZATf087ZW0kTtVyoB2Hkk9kJlv9OEY2k2DNWpNBdGD6Jlgv54xxgT
Zv3oS4y6NVHoVUPcgQJBAPO3CZKEqveYMxUlwAsOW8S46v5ncEKvUdbUuxX0d7/Z
cH+K5L/0Su8EeJ8wkUh940YDew1hX7+P6zkiQAq3k2ECQQDHduoCWHHn93Zedlmw
os5//xhDFSLlUkJjKY0RtI3NuQNWov8T6lsg9k498MRlg5ABzaP5a8IOmnfE24lt
FoKlAkB/qRw5hIbtxOrVI/4RjIbjaB2n/1TdiWpsBuis2m6zrtlv5bhnGDb8NrJc
aJthhpe7P+2AF8aI2IFVXyx+sKRhAkAWBR+yYJc6l4wew4wFPwPzB3NjPHscu+cO
UXD8amVZN7qRnu7wAOhMjER4/BKCbnLAcDZQ+79xo0XjmqTiQSDtAkBVJIIaoOd8
cXTvclD9VA5QhJp3corbMmNpS5KJ38mTSSeXYRXl1T0oIx/0zfym27mgocEjU7RG
FbBGI6dxBm4s
-----END PRIVATE KEY-----""",  # Must be in PEM format
    'developer_key': 'AIzaSyBkMhZAbepklUuV5ZXrzPDdu5zOSSRUhZA',  # Optional
    'domain': 'arista.com',
    'default_user': 'sherpa_bot@arista.com'
}

settings['upload'] = {
    # Whether to use Cloud Storage (default) or the blobstore to store uploaded files.
    'use_cloud_storage': True,
    # The Cloud Storage bucket to use. Leave as "None" to use the default GCS bucket.
    # See here for info: https://developers.google.com/appengine/docs/python/googlecloudstorageclient/activate#Using_the_Default_GCS_Bucket
    'bucket': None
}

# Enables or disables app stats.
# Note that appstats must also be enabled in app.yaml.
settings['appstats'] = {
    'enabled': False,
    'enabled_live': False
}

settings['google_directory'] = {
    'domain': 'arista.com'
}

# Optionally, you may use the settings plugin to dynamically
# configure your settings via the admin interface. Be sure to
# also enable the plugin via app/routes.py.

# import plugins.settings

# import any additional dynamic settings classes here.

# import plugins.my_plugin.settings

# Un-comment to enable dynamic settings
# plugins.settings.activate(settings)
