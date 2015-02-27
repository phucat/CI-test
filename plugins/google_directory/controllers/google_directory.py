from ferris import Controller, route_with, auth, add_authorizations, settings
from ferris.components.cache import Cache
from plugins import google_directory
from google.appengine.api import backends
import functools
import logging
import threading

config = settings.get('google_directory')
USE_BACKENDS = config.get('use_backend')
BACKEND_NAME = config.get('backend_name')
DEFAULT_LIMIT = config.get('limit', 30)

def backend_redirect(f):
    @functools.wraps(f)
    def inner(self, *args, **kwargs):
        if USE_BACKENDS and backends.get_backend() != BACKEND_NAME:
            return self.redirect(backends.get_url(BACKEND_NAME) + self.request.path_qs)
        return f(self, *args, **kwargs)
    return inner


require_user = add_authorizations(auth.require_user)


### WARNING: HACK ####
# This is a dangerous optimization.
# This would not be acceptable on a multi-threaded frontend and it's barely
# acceptable on a multithreaded backend. This should be re-worked with some locks
# or something.
# NOTE: the function should be called by /_ah/start, thus building the cache before
# any requests have a chance to come in.
_local_cache = {}

def get_all_users_local_cached(force=False):
    if not 'users' in _local_cache or force:
        _local_cache['users'] = google_directory.get_all_users_cached()
        logging.warning('Rebuilding Local Cache')
    return _local_cache['users']


if USE_BACKENDS:
    get_all_users_local_cached = lambda x=False: google_directory.get_all_users_cached()


class GoogleDirectory(Controller):
    class Meta:
        components = (Cache,)
        prefixes = ('api',)
        View = 'json'
        authorization_chains = ()
        default_cache_expiration = 6 * 60

    def startup(self):
        def enable_cors(controller):
            controller.response.headers.add_header("Access-Control-Allow-Origin", "*")
        self.events.dispatch_complete += enable_cors

    @route_with('/api/google/directory/prime')
    @require_user
    def api_prime(self):
        google_directory.prime_caches()
        return 'started'

    @route_with('/api/google/directory/users/<user>')
    @require_user
    def api_user(self, user):
        if user == 'me':
            user = self.user.email()
            self.components.cache('private')
        else:
            self.components.cache('public')

        user = google_directory.get_user_info_cached(user)
        if not user:
            return 404

        self.context['data'] = user

    @route_with('/api/google/directory/users')
    @backend_redirect
    def api_users(self):
        self.components.cache('public')
        query = self.request.params.get('q')
        users = get_all_users_local_cached()

        if query:
            query = query.lower()
            users = filter(
                lambda x: query in x['name']['fullName'].lower() or query in x['primaryEmail'].lower(),
                users)

        if not 'nolimit' in self.request.params:
            users = users[:DEFAULT_LIMIT]

        self.context['data'] = users

    @route_with('/api/google/directory/groups')
    @route_with('/api/google/directory/groups/<user>')
    @backend_redirect
    def api_groups(self, user=None):
        if user == 'me':
            user = self.user.email()
            self.components.cache('private')
        else:
            self.components.cache('public')

        query = self.request.params.get('q')

        if user:
            groups = google_directory.get_all_groups_cached(user)
        else:
            groups = google_directory.get_groups_list_cached()

        if query:
            query = query.lower()
            groups = filter(
                lambda x: query in x['name'].lower() or query in x['email'].lower(),
                groups)

        if not 'nolimit' in self.request.params:
            groups = groups[:DEFAULT_LIMIT]

        self.context['data'] = groups

    @route_with('/api/google/directory/members/<group>')
    @require_user
    def api_members(self, group):
        self.components.cache('public')
        self.context['data'] = google_directory.get_group_members_cached(group)

    @route_with('/api/google/directory')
    @backend_redirect
    def api_unified(self):
        logging.info(backends.get_backend())

        self.components.cache('public')
        query = self.request.params.get('q')

        users = get_all_users_local_cached()
        groups = google_directory.get_groups_list_cached()

        if query:
            query = query.lower()
            users = filter(
                lambda x: query in x['name']['fullName'].lower() or query in x['primaryEmail'].lower(),
                users)
            groups = filter(
                lambda x: query in x['name'].lower() or query in x['email'].lower(),
                groups)

        users.extend(groups)

        if not 'nolimit' in self.request.params:
            users = users[:DEFAULT_LIMIT]

        self.context['data'] = users
