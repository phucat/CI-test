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
    'client_email': '566305864248-41dsmsoqtbqc77d7op2og3u73ib7b982.apps.googleusercontent.com',  # XXX@developer.gserviceaccount.com
    'private_key': """-----BEGIN PRIVATE KEY-----
MIICdwIBADANBgkqhkiG9w0BAQEFAASCAmEwggJdAgEAAoGBANhi5BK2/RiS5N+W
l8j9Z3qXdmRtVsh/eklGSCPvE2t20a7nINS+mDugbegi2FAfB0fuTavuUnAnjGfg
BQDMkZwsf40w1HE8QARV+cOY0wFT+ObFcrJFXIXE0872ehO1nzKHx3BrGsUrkKct
6qPB8V06U3y+isR849N2a4Q56wFdAgMBAAECgYBZdfEjR6I2Aa08P097mkCo72vU
M1w4wnN1TehPau1VdadVL1tkeXQI2tf1rEpQPbPN6lkUZxCQK9mhrH2FCg58huyC
qUb6Nbt+IALpLn45b/VmzhnwzVGdQFrnPUDqG2wdq2K0b5X2T1m1m9s8QB7WYPAQ
/3EDOlcuwreX3OfWpQJBAPq1/m//VuqGNkkeg30meMpjReMjt709Q79S2o14Dhlo
tf4CyMjHSh86cRjPf6brjaZ4aFb+bVZJGlPD/5N9ke8CQQDc84Vrn0fykOLLNbJS
86ag22V/QW5HljJFhgXXOFr2YBE60xpVO/IybCQY28LhPIfDfVW799YOYnoUKrhp
i71zAkEAurrKY0heyBZmYFdlv9Tjqnn+F4sG0t/Kkbl4Jl4AwlQHGMWiHkiwoEm6
6qvBe+V9fzu3GvQtI1MXVMRqmsOv6QJAZO+urLqoEIzVvoV6QGDkZymzFU5bxcI8
lvwh4O7yxwid9mSH7BYlj5lNaDnErkaLsuen6eXPWOTt5haaBkV7NwJBAJc2Ds0u
BfDq24UauPCKT88NS9Uolj2/85bZaWdha/TFT1ozNXrujF6qP21Yh44NSe4OzD9Z
cZIKnCB2tJZWZ8M=
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
