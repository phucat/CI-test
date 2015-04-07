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
    'client_email': '566305864248-jqrmu5pup0t108pt97nqq9mt1ijv7mto@developer.gserviceaccount.com',  # XXX@developer.gserviceaccount.com
    'private_key': """-----BEGIN PRIVATE KEY-----
MIICdgIBADANBgkqhkiG9w0BAQEFAASCAmAwggJcAgEAAoGBAN5zpukOfpLSaUNc
EQDPLnTLadd6Oh0FwRZHXQeW7nGHthgTziDqp4EuOgod8TpXB+vnX+zyY35Clegm
0CDx8PTy5/TKlGubd10FQBy2Xsahv5gO1pc4L1bDqmSpoxsRRRXoquUYhlvY4Df5
ctXOcBuOLaV9XXNSuECKKH1kWCc9AgMBAAECgYAyy6vgaevjMOLSe9JyId0U1GId
zw44FFlL8g2/LurRx9B/3P3jrFGFgP3F06KC1N69Mn9IBu1LJn8+nKZH75c6msS8
XWenvQbnxES/PUy+0FjwqFCybbUrd6nfiyJV17JTT0umKH1dGmJ37NEXd2I/sdWd
GuqZZoxwl+NfgSLIjQJBAO+J5TBym+QfJ4Ke403NxOg0gPrfDg6wlSwxTxPnWnBZ
bnbk3tygia064t9qyVzRdH/7UAwd7uuDzxnL6UtLJjcCQQDtvSd2nlPneLKtGL0/
gsoKkHYm6jszUjmLv8hDVURvK/UmJWLC17cLM7SI0DmY2Zm6XnykP3Xgi2kaNqWA
7yQrAkEAi2BsF+2H4YtzHODAl8PT/9yU8+QXtNpwYd9rCMTD7b1LtihjuHI8yawK
2D61XamOJO2g3PwJycXPGk54t1PJrwJAL/w59utGLDZkeiPALw2LEk7OSlSE1nsG
OnrfRRf01CufM6/gG0vHGm+5RNQijAN/z+o6ZjyY4lXBRRU6mqeqOQJAbLllhUMY
wk/GS5bPTcro3c1iQAGto1X8nQNEc0HMOHaAaVsz6sn2rJpjOhJc3fyIGAb/Uq4Z
D8/8xduc0qeZBw==
-----END PRIVATE KEY-----""",  # Must be in PEM format
    'developer_key': 'AIzaSyBkMhZAbepklUuV5ZXrzPDdu5zOSSRUhZA',  # Optional
    'domain': 'sherpatest.com',
    'default_user': 'andrew.fleming@sherpatest.com'
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

settings['admin_account'] = {
    'email': 'andrew.fleming@sherpatest.com',
    'password': 'cloudsherpas',
    'domain': 'sherpatest.com'
}

# Optionally, you may use the settings plugin to dynamically
# configure your settings via the admin interface. Be sure to
# also enable the plugin via app/routes.py.

# import plugins.settings

# import any additional dynamic settings classes here.

# import plugins.my_plugin.settings

# Un-comment to enable dynamic settings
# plugins.settings.activate(settings)
