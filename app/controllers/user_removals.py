from ferris import Controller, messages, route_with
from ferris.components.pagination import Pagination
from ferris.components.cache import Cache
from app.models.user_removal import UserRemoval
from app.models.audit_log import AuditLog as AuditLogModel
from plugins import google_directory
from google.appengine.api import users
import logging
import json


class UserRemovals(Controller):
    class Meta:
        prefixes = ('api',)
        components = (Cache, messages.Messaging, Pagination)
        pagination_limit = 10
        Model = UserRemoval

    @route_with(template='/api/schedule/remove/user/<email>', methods=['GET'])
    def api_create_schedule_removal(self, email):
        user = users.get_current_user()
        UserRemoval.create({'email': email})
        self.insert_audit_log('%s has been schedule for removal.' % email, 'api endpoint', user.email(), 'Schedule User Removal', '', '')
        return 200

    @route_with(template='/api/schedule/list/all', methods=['GET'])
    def api_list_all(self):
        self.context['data'] = UserRemoval.list_all()

    @route_with(template='/api/schedule/list/pending', methods=['GET'])
    def api_list_pending(self):
        self.context['data'] = self.components.pagination.paginate(query=UserRemoval.list_all_pending())

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

        if params['status'] == 'Approve':
            params['status'] += 'd'

            gdirectory_response = google_directory.revoke_user(params['email'])

        elif params['status'] == 'Cancel':
            params['status'] += 'led'

        self.insert_audit_log('%s has been %s for removal.' % (params['email'], params['status']), 'api endpoint', user.email(), 'Schedule User Removal', '', '')
        self.context['data'] = response

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
