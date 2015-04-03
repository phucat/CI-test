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
    'client_email': '566305864248-jqrmu5pup0t108pt97nqq9mt1ijv7mto.apps.googleusercontent.com',  # XXX@developer.gserviceaccount.com
    'private_key': """-----BEGIN PRIVATE KEY-----
MIICdwIBADANBgkqhkiG9w0BAQEFAASCAmEwggJdAgEAAoGBANIFoWtO4dwtAwXM
CmxyXYvW1dGHNkDqp7Va3ZiByZJACaRyQdX2y1lhPb7mi98mvbf3nwEoxCh+PoWj
zbCSlZxNsynNHLMoK8nGnuG5SPN/oZ7BuN27MvGqOxqLhnswopnet5WzuqzfzvNR
UH02NrFd9OvibCn7j+150Qh3J5sZAgMBAAECgYBJUZvjmVsyASi/+lZdO6O6sNpe
VmSzTvgTUNBxcEXNX7u+BAFFz+13m4Hxxgxob97lfXWt8uxf8oqjHucs0E+X6daa
r24z+oBK2S4UF7t+NNo2xNNV7uyAy1/D2kj6GlfbMsNVZce3VZopJMw4cpJacuwI
Bc4W5vvq0s4iHZWZTQJBAP4+i7ZQFhJvY5kKfp8bP7A4cc5avBafNlQdrlMGK2k3
5t67pGuYl4CYB1+eg8KwX5fzvm8PI+e3zmECO/Xke+cCQQDTeOiK0oc2j/OJ0zZE
01l2w7ZjbWhSogjso2l9beDmjpxeRTsKVVcjmoU87ZDeARlxhR9U4elAyFAqQ3tU
aFD/AkAem8USM94UZhilih/oY81tF76Ly1ytlIlj4xbjo/CCAFrpIcoPshU7RBJP
LrRKMhWwI4YftMDr2rMb9rrlRZatAkEAm6IYQlK+gEFhEsYG4pBI/0b6LCKQ7H+j
4cRCFrWPFx9NpXN+CBTWlLVb6YNNYpWcjBdU/7tjVvIVTYVsdqpvMQJBANyHrmFR
bcq1P4UfA9XoWZEb0snuNvAS2vg8pFDJq2FH3goooyK2zOvzEyHyfzcDVREIGZYt
F8MYraapekbrPoU=
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
