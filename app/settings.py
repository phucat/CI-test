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

# arista-qa
settings['oauth2_service_account'] = {
    # OAuth2 service account configuration should be generated
    # from the google cloud console (Service Account Credentials)
    'client_email': '566305864248-jqrmu5pup0t108pt97nqq9mt1ijv7mto@developer.gserviceaccount.com',  # XXX@developer.gserviceaccount.com
    'private_key': """-----BEGIN PRIVATE KEY-----
MIICdwIBADANBgkqhkiG9w0BAQEFAASCAmEwggJdAgEAAoGBAJqTms3P+p9OTyOL
Pv+Xpxb7loL/tEWcCvmVbq+y938O4z6KQhNSlh135cpkYdUmak0vy7PJeaGYd9hD
UNbfRN0JLudbMCUWvV8QkIBJgbeDa+hJV3KK3ZTJxDL07WwE8VfXnpPtaZ605ISk
2K4rkYwlQI0hxebSXyuiFZAcmfdtAgMBAAECgYEAkxEWevSCvajS0L197c3Ksqoh
tHc2e/gP1RBgpBfBNAjlGi6O2TV9D4JwhdRl5FdNUizEQUTSTXXzqDW7pwP7zlqT
0axRDOvlCjOWNzzWKm8kJqFJTKtSyNsMabdOvkBD2nvS3YYTNRTJQQbAzytoYLvw
1Hk29kRAW21kDHS8O4ECQQDHOG7VVPU6IvrDm0x62ZsFcAXjUX4Q8xjqk3FN9zET
gM1RAjon+8diOcuVm+Yc+vF6b09T5YyzmliHnwtQdOxNAkEAxqHbNcGHnLYFwMOt
MvCWW+vGU4xQEiTEXKun+PMtbWF4ZHiE6NqRA3nBaAK3Klk3P1qENkCwdQjKfaEI
j6hHoQJBALIBbJbVaKBfrOymkLmcQfWj2L76i8gdToAa6jydyI4ConHlqY0cXVUZ
Cx1MxVnTp3ychKcUDppUKRJVO8jSEGkCQCCHr2vdVwVONiD8qufVyPoi4eca6p4e
EV6P6kF2KfFo7hueNT4hVXB5RzhugWrZE5g3jcGI1J1GJEtwzQMh7yECQEEBDkh+
mFCQw6Ca1YME8dXcxzIRCOpMa9ZSSGw6ib7Uwi2LPNQYUg1zWNCIbJZTXWjxhfmQ
OXQX6pqMRBhm5xg=
-----END PRIVATE KEY-----""",  # Must be in PEM format
    'developer_key': 'AIzaSyCY2AHYltYng1JbyHJk8EH80JbMqaiy9NU',  # Optional
    'domain': 'sherpatest.com',
    'default_user': 'aris-test-11-admin@sherpatest.com'
}

settings['notifications_recipient'] = {
    'email': 'andrew.fleming@sherpatest.com'
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

# Optionally, you may use the settings plugin to dynamically
# configure your settings via the admin interface. Be sure to
# also enable the plugin via app/routes.py.

# import plugins.settings

# import any additional dynamic settings classes here.

# import plugins.my_plugin.settings

# Un-comment to enable dynamic settings
# plugins.settings.activate(settings)
