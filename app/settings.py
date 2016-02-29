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

# # arista-calendar-01
# settings['oauth2_service_account'] = {
#     # OAuth2 service account configuration should be generated
#     # from the google cloud console (Service Account Credentials)
#     'client_email': '61726108322-7gnl78qvf5b4iudpk6e7l9rb9totacjs@developer.gserviceaccount.com',  # XXX@developer.gserviceaccount.com
#     'private_key': """-----BEGIN PRIVATE KEY-----
# MIICdQIBADANBgkqhkiG9w0BAQEFAASCAl8wggJbAgEAAoGBAL3kfZbZC2maFrkc
# 7BoOWc5nvETUItuPYPwc4qmSpexA6lrWgx1po00jjYe7ZZSaFJgBMn+iBherEGxZ
# ELwV8RV9tZkWpBuUkc3jHGZtUiYF9I8eMXnXTq32qLXA5+150isuNMfVgzMuE37X
# pUa8k9rOT5fylma1jYneiCgYfz+FAgMBAAECgYArN0wJv52kS+gt+tIU3/06R0uG
# kozYURouZliDZReT2/Y59CXk1LzQem3kXRayKhrTuToH6BTg4BKdxetUEt5Js/Tx
# CscCAqnZJvMZATf087ZW0kTtVyoB2Hkk9kJlv9OEY2k2DNWpNBdGD6Jlgv54xxgT
# Zv3oS4y6NVHoVUPcgQJBAPO3CZKEqveYMxUlwAsOW8S46v5ncEKvUdbUuxX0d7/Z
# cH+K5L/0Su8EeJ8wkUh940YDew1hX7+P6zkiQAq3k2ECQQDHduoCWHHn93Zedlmw
# os5//xhDFSLlUkJjKY0RtI3NuQNWov8T6lsg9k498MRlg5ABzaP5a8IOmnfE24lt
# FoKlAkB/qRw5hIbtxOrVI/4RjIbjaB2n/1TdiWpsBuis2m6zrtlv5bhnGDb8NrJc
# aJthhpe7P+2AF8aI2IFVXyx+sKRhAkAWBR+yYJc6l4wew4wFPwPzB3NjPHscu+cO
# UXD8amVZN7qRnu7wAOhMjER4/BKCbnLAcDZQ+79xo0XjmqTiQSDtAkBVJIIaoOd8
# cXTvclD9VA5QhJp3corbMmNpS5KJ38mTSSeXYRXl1T0oIx/0zfym27mgocEjU7RG
# FbBGI6dxBm4s
# -----END PRIVATE KEY-----""",  # Must be in PEM format
#     'developer_key': 'AIzaSyBkMhZAbepklUuV5ZXrzPDdu5zOSSRUhZA',  # Optional
#     'domain': 'arista.com',
#     'default_user': 'sherpa_bot@arista.com'
# }

# arista-qa
settings['oauth2_service_account'] = {
    # OAuth2 service account configuration should be generated
    # from the google cloud console (Service Account Credentials)
    'client_email': 'arista-dev-01@cs-arista-calendar-dev-env-01.iam.gserviceaccount.com',  # XXX@developer.gserviceaccount.com
    'private_key': """-----BEGIN PRIVATE KEY-----
MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQDnwR2o+Lw6eUkl
6Fk+xUJFZizN8CKqrO9kmqvJC+1ZotoPYfYHHY4mT1zNFADbP5FLCEw8o99K4xo6
oFv5pTrg7ZHItS7kaJ1WQA6N2i8HD22UXqe72Q77qF38kMlMv8HhQ7hXNs8kAVQj
94gteLJ9+HyC7dkwGZCA3qDgPXpJ/4/jxdWcd4+ZGp9k9U1bdL7faW4ReM2ZdvG4
E/469Vn+VtmaK9MdDeqvChLR7NCSYwHZCdCL8JLbIS0+eogNhxe3EuyY7M/TYfXC
sgBTiNzQ0fhZHOdrUIjXVVeNoELw63T0pgN1HG/C0xdH+U3SHA8imF+T6vE5aLL1
QOGmJkYxAgMBAAECggEAdhieeKBnqpRrhfmkoKv8XUj3w+l+gOKnCukWaNi/FlI6
NGSC7pVM/pCqhYaP+SmnbEjKMIyBGLQphX553/kmy7/D7jcFsjbtFiqGQBrSpBJk
kJq7dqnhTLQ7UJynN4jvz06m/Spc28ghjEJzDljW/AJH0KBLcItWa5UG/b3WNyYf
dDKyfG8yAPRbhZ96drygGW2Xwm/eyxOHzTSDDEYxDdbh2X9RihOVPSNzL6q1lgwJ
DYA4sUgkNu5efwYasmzu3+Qky0uHpk6zW2SZVOIoUZTBvOg7BobgUhF4wtXq2Iq5
pHk0EuwTXqmUJ2b84XNSVXuwBH7q6wuro+17hYPdAQKBgQD2+y5/Ujh3f9mfpn9T
LpONx+fflQ8ZvQC52ESQeOmDi1iGsj7rXi0fml2Yotl1Swz3qHUttaT29cO3YlGj
nHsVe7zE2WuOjFJ1hMaiA8zjtDd2mAkAQLxAJUB0FtRuwaMH/mq6U1SRFWu58NH6
dtTL7YmMKlLjTJiqHMqbA7yp+QKBgQDwN5dwa8c3X4OQNbbjh44i6Ppy+0vrhXxM
SizybY/cD2cRn3YYlH5+udi4d0VbdPMB3lWbrmWw7/wwPusn5QuhfFknqQ69OzzO
oSSj33u56yrmrpLA8Jzg1cJDMIc5abacAQiYuv/XezueVk043GVf5qtgVdMtCEQp
t/tiquFL+QKBgGvEJgHAKotZ6edTivMMu619sJtKOxCL+6kbyK8RUzLmtnXviKzC
pwXHIVfclu4rFTlq89ZCD/0CN6fo6p5tRPeWykNKazgD2mcUzGcdKWWh2SGSLTtD
A+EpX/pHi+HX8/8k8ATlH10+74ZuofCbsTZaK05RmWE8ptBzR6Rj+QphAoGAc7gk
EPkqsAcoJslpgDRmCXU4aTmbuirE1S+KdYLIIZed7ERoLLEkOsImn759P/CXvBey
H9wkitchItC8kaxqLPHtNQjg29H0mgnQz8yyGr8qHJSOh7mhqUHwYlO3YLYHTSHG
VWUIKHLqJn2ml7S8dTV262KM542q4HoL9N0iyWkCgYB5xVcNiP6+5GpDHuLKBbwf
ssQsPmhVDIl3deTBv+22bN/OsSDpcDy+hLy+emgY31aXDbCtxyZobeXqeHrjrHcq
ssK9vqs5hRlYhAgXNM8mNwtD7xoghCen3XwWbLnlM1RO3qJgdd5LHIdchKs7z+dM
831OUwofBEh+IP4O7s8oTw==
-----END PRIVATE KEY-----""",  # Must be in PEM format
    'developer_key': 'AIzaSyBEFGRs7uDqNIbS-JojXr_vme_VIgkAX6c',  # Optional
    'domain': 'sherpatest.com',
    'default_user': 'richmond.gozarin@sherpatest.com'
}

settings['notifications_recipient'] = {
    # 'email': 'arista-calendar-appspot-log@arista.com'
    'email': 'richmond.gozarin@sherpatest.com'
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
