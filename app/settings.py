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

settings['oauth2_service_account'] = {
    # OAuth2 service account configuration should be generated
    # from the google cloud console (Service Account Credentials)
    'client_email': '118341588591-47m8igkcn0h9r3uajajcetsgo7f574qc@developer.gserviceaccount.com',  # XXX@developer.gserviceaccount.com
    'private_key': """-----BEGIN PRIVATE KEY-----
MIICeAIBADANBgkqhkiG9w0BAQEFAASCAmIwggJeAgEAAoGBAMq/SGGMKaYpGEu/
WDkdbzRGAiYz0Yi4Uvz5CuEt0TDV6KOrRsnF53V9nOlksNv+fwqbC+kdtlBpGlho
D/I3js54NqPVs4AL2Ggt2ICQK4457KfeJK+D0o2zPXSrqORzZ6uPkatHeavd1ZwP
Qv1bq65Pgrwrf4xNml9roogbVke7AgMBAAECgYEAul0Dmm7tJcgmhhIXdUCiJImp
lhYRp7vOxKvjHUMxQ9OMaU2Z3wSkEnJpVnvwufeALW6Bj0F5gQZrahIVfk8lWu7f
SoP6kMBffJFqTU58A5Ijna8QX9aIEuJ0JbEVJtXKVMhZkpeBUlboN/pJ8a1PvL1F
K+aJU+AYrE6oP1GnKfkCQQDwkttL8C0Xhpcw8r5cYLNau9D8KJs6I6I23wGzRCCF
ah8hgsxiRPOoA1nzdPVzsvFWItdAMUDilmN89mBD6dLFAkEA1798HdGQymADtzrq
3zLUYuS9BE3fJaJi0zSALmpIHAAHI23tCaRxMKOBMRU3Thigf154SbbD1B1BN2KO
lIdYfwJBALrRgGTXLV0gkpZbW0KHgaBLS74Vln2uoFC2Gy7oD80rHOO8HBWP8Bsg
ByFNSTLA2jMGuVtLJFURbk7jUNxMXvUCQH1Je6AtVLHRNBcxpbdb4y5SutlHB3Dp
bg5MjKtnmNx5v6t5aI+S6RBfwuRn96focTvF9oCIHAyPuJGbMEVcm60CQQDEQnyn
+Q03Ht3IPwca6KNBKJ2MFB/9SStUJJeXm9aMnZqMTT7Oo+17zkyQLz+3aniX90a5
iY83JVEZq4AWsMOk
-----END PRIVATE KEY-----
    """,  # Must be in PEM format
    'developer_key': 'AIzaSyB3Rh5njM_iE6Mli6w-IGklWSiiEol8kgo',  # Optional
    'domain': 'sherpatest.com',
    'default_user': 'richmond.gozarin@sherpatest.com'
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
    'domain': 'sherpatest.com'
}

settings['admin_account'] = {
    'email': 'richmond.gozarin@sherpatest.com',
    'domain': 'sherpatest.com',
    'password': 'cloudsherpas'
}

# Optionally, you may use the settings plugin to dynamically
# configure your settings via the admin interface. Be sure to
# also enable the plugin via app/routes.py.

# import plugins.settings

# import any additional dynamic settings classes here.

# import plugins.my_plugin.settings

# Un-comment to enable dynamic settings
# plugins.settings.activate(settings)
