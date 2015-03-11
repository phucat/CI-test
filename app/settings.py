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
    'client_email': '1057100193776-q3kup97nscasd7rsrtf1emjshr3f4ouo@developer.gserviceaccount.com',  # XXX@developer.gserviceaccount.com
    'private_key': """-----BEGIN PRIVATE KEY-----
MIICdQIBADANBgkqhkiG9w0BAQEFAASCAl8wggJbAgEAAoGBAML88nviV553MYEA
FXxbY9dUVC8lYdH7K6+eAODGhVhiuMpvTmB69gjjO3Dd4WKYNvhpmmba2h01lJdd
R3OB4tRgl/hIB/wluxTDqgr+oFRQvly4Fcy+ZrblrQJ8UFazLU5z6lPhzOnB7gfa
BYFMSB2XNlzIrLMLMUjxJmt2JHkJAgMBAAECgYBQLsBwXUV2rsE2sRgkyVgnRlBQ
CulM9iKi1zC5Pim7jO08ocTzO91NDlR1N2jlqH6CbLrHrRugg1YVYJBvWWwy/bmO
I8QXoqiPfDZnfLGTjO+zJwnHo29HxGcKfQsKdvECP2SDFZry7AN17mcDFVG/II7R
tjofDUaylPgp53uomQJBAOIz/a1C8bpOInGhrzmHcuKxul+pDjAd9gOnywIh7bAn
V6+RCc2iYFls/VfzPE11leTwoXpbpj4gauqxOnCG5asCQQDcrFM8w8En2OliS84D
qr77O0/PejBJQVUvd9fSIM/syA6Cx2rGAeno3vML83C+tvp/0FbtxQWC8AB41qmk
/sAbAkAfoh+utDbz0+tzMqY7iFqjozEqIY0vY3E9D6EPOklwIgBcOA9D55pLxzci
roxXVMNSkegzIU/9TjFFguVmSScjAkAkOiokFKL2LrcJyxYUJgjaZ79PeWjJ7e7V
LyCAP6DC54jyUVinDxNehpNyB9IfjRyMtSBAQpMIDuyU6fDJxIS3AkByz0oe0Kbc
UqGDkLc93EHvBbxAj81U4oMel3F/b/pFf2FiPWozZr1gRjt+Ps0x+3O8bJUZR8U6
epL5tR80Xuvt
-----END PRIVATE KEY-----""",  # Must be in PEM format
    'developer_key': 'AIzaSyDBTTdoJDhIcRWW9Rt89QfmbSPyPNzvrIE',  # Optional
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
