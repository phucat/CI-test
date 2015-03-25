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
    'client_email': '61726108322-6jprbbvjrge9m5e6uqknskg534hgra8g@developer.gserviceaccount.com',  # XXX@developer.gserviceaccount.com
    'private_key': """-----BEGIN PRIVATE KEY-----
MIICdwIBADANBgkqhkiG9w0BAQEFAASCAmEwggJdAgEAAoGBALCUhVrvCi6e061i
yyuusNKuqUUPaia/NmN3W0/Je81Vo7wJSMIj4VGrioL3/6TZF8a12NxFyYSXoZwn
4qTXXopDYOi7c7AuLSH001Hc+4y/WYruZKSCIsB/ZbUmKzOAMcYjG3AscAS/VTFc
RJE++odGW1nCV9TLRGBY39qYTd+DAgMBAAECgYA2hpYrPzcIsFiy6JfONFI7rF1u
itT/g/n6eufCWngVLsWxkbha4pN4EZ1i1cumDrdNz+dYFWClxeDMhHBy8GIrkjrR
T72LkAhkgkDUw3tRhesoo+FuIxH5ICUQ5Ut+4IRo3AbPAxazz3WHVGkoGVg/a/1o
9+8s/o7mzonieUO7UQJBAN1fstcrssKw3jzdEUmfd8SW+1xX1+zXKeu6mBR++jVE
FN2Wq8gfDwy6mHPBc7IdXI/lXqbHumwjcoY2Yj06qqkCQQDMMy8nodO7ASWdqHdy
ogL5ts1DuD7lUYGGjD8uiQqtSsEkVDcxWkWBTVvFZulzaFVg5dInqs7qyXlpQK00
uuBLAkEAtJiy1LkQj6Ys16hdxxsyYQ3vKCl9vPjXeTjzgp0IUFYnU5Lst0knRPIh
FyY11ZQAhF/R9Oux2TCd6IILaPooaQJBAKIrxDdlfhH2Rzl+od6YbGSFmV8+5DSb
FpMUrtj2XVRjGiEQAQVg+/JEza1ond7Z7XSXEOAP92TfvVyp0OUfxSECQHfNs6yB
L7iWJhp8JLq1qbg7DbjKNyndB3xU8JDnvGMCkMwVB17V4mIdBYvim7jIxrzuFYPI
1+/1D9yG+2L+PVA=
-----END PRIVATE KEY-----""",  # Must be in PEM format
    'developer_key': 'AIzaSyBkMhZAbepklUuV5ZXrzPDdu5zOSSRUhZA',  # Optional
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
