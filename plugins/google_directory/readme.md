Google Directory API Plugin
===========================

Enable plugin via routes.py:

    plugins.enable('google_directory')

Configure an OAuth Service account via settings.py or the settings manager that has the following scopes:

    https://www.googleapis.com/auth/admin.directory.group.readonly
    https://www.googleapis.com/auth/admin.directory.user.readonly
    https://www.googleapis.com/auth/admin.directory.orgunit.readonly

If you wish to query a different domain or customer, configure the following in settings.py

    defaults['google_directory'] = {
      'customer': ...
      OR
      'domain': ...
    }

By default will use the same domain as the oauth2 service account


API Usage
=========

There are a few endpoints exposed to allow you to get information from the domain:

 1. **/api/google/directory/users/{user_email}** - gets the domain information (including groups) for the provided user.
 2. **/api/google/directory/users** - get all users (not including group membership) from the domain. Provide the *q* query string parameter to filter.
 3. **/api/google/directory/groups** - get all groups in the domain.
 4. **/api/google/directory/groups/{user_email}** - get the groups that the provided user belongs to.
 5. **/api/google/directory** - unified users and group list. Provide the *q* query string parameter to filter.


Direct Usage
============

This plugin monkey patches the `google.appengine.api.users` module and adds the `domain_info` property to `User` to provide domain information:

    user = users.get_current_user()
    print user.domain_info['name']['fullName']

This also provides group membership infomation (via `domain_info['groups']`):

    print user.domain_info['groups'][0]['email']

Be careful though, if the plugin can't retrieve the domain info for the user the `domain_info` property will be `False`. Just be sure to check it before doing anything with the domain info:

    if user.domain_info:
        groups = user.domain_info['groups']


Running Tests
=============

In order to run tests, you have to create a test_settings.py file in the root of your application with service account credentials. This should never be committed in git for security reasons (and I will check and find you if you do). You should use a sherpademo service account because the tests depend on data that's in the sherpademo domain.

Example:

    import settings
    from ferris import settings

    defaults = {}

    defaults['oauth2_service_account'] = {
        'client_email': '...@developer.gserviceaccount.com',
        'default_user': '...@sherpademo.com',
        'domain': 'sherpademo.com',
        'private_key':
    """-----BEGIN PRIVATE KEY-----
    -----END PRIVATE KEY-----"""
    }


    settings.defaults(defaults)

Once you have this in place, run the tests with nose:

    nosetests --with-ferris --logging-level=INFO plugins/google_directory
