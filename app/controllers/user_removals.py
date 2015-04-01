from ferris import Controller, messages, route_with
from ferris.components.pagination import Pagination
from app.models.user_removal import UserRemoval
from app.models.audit_log import AuditLog as AuditLogModel
from plugins import google_directory
from google.appengine.api import users
from google.appengine.ext import deferred
import re
import json


class UserRemovals(Controller):
    class Meta:
        prefixes = ('api',)
        components = (messages.Messaging, Pagination)
        pagination_limit = 10
        Model = UserRemoval

    @route_with(template='/api/schedule/remove/user/<email>', methods=['GET'])
    def api_create_schedule_removal(self, email):
        if re.match("^[a-zA-Z0-9._%-]+@[a-zA-Z0-9._%-]+.[a-zA-Z]{2,6}$", email):
            user = users.get_current_user()
            UserRemoval.create({'email': email})
            self.insert_audit_log('%s has been schedule for removal.' % email, 'api endpoint', user.email(), 'Schedule User Removal', '', '')
            return 'The user has been added to the approval list.'
        else:
            return 'invalid email'

    @route_with(template='/api/schedule/list/all', methods=['GET'])
    def api_list_all(self):
        self.context['data'] = UserRemoval.list_all()

    @route_with(template='/api/schedule/list/pending', methods=['GET'])
    def api_list_pending(self):
        pending = UserRemoval.list_all_pending()
        if not pending:
            self.context['data'] = self.components.pagination.paginate(query=UserRemoval.list_all_pending())
        else:
            self.context['data'] = pending

    @route_with('/api/schedule/list/pending:<key>', methods=['GET'])
    def api_get_user(self, key):
        user = self.util.decode_key(key).get()
        if not user:
            return 404
        self.context['data'] = user

    @route_with(template='/api/schedule/update/user', methods=['POST'])
    def api_update_user_status(self):
        user = users.get_current_user()
        params = json.loads(self.request.body)
        response = UserRemoval.update({'email': params['email'], 'status': params['status']})

        if response == 403:
            return 403
        else:
            if params['status'] == 'Approve':
                params['status'] += 'd'

                google_directory.revoke_user(params['email'])
                deferred.defer(self.prime_caches)

            elif params['status'] == 'Cancel':
                params['status'] += 'led'

            self.insert_audit_log('%s has been %s for removal.' % (params['email'], params['status']), 'api endpoint', user.email(), 'Schedule User Removal', '', '')

            return params['status']

    @classmethod
    def prime_caches(self):
        google_directory.prime_caches()

    @route_with(template='/api/schedule/cancel/user', methods=['POST'])
    def api_delete_user_removal(self):
        user = users.get_current_user()
        params = json.loads(self.request.body)
        response = UserRemoval.remove({'email': params['email']})

        if response == 403:
            return 403
        else:
            params['status'] += 'led'

            self.insert_audit_log('%s has been %s for removal.' % (params['email'], params['status']), 'api endpoint', user.email(), 'Schedule User Removal', '', '')

            return params['status']

    def insert_audit_log(self, action, invoked, app_user, target_resource, target_event_altered, comment=None):
        params = {
            'action': action,
            'how_the_action_invoked': invoked,
            'app_user_invoked_action': app_user,
            'target_resource': target_resource,
            'target_event_altered': target_event_altered,
            'comment': comment
        }
        AuditLogModel.create(params)
