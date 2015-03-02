from ferris import Controller, messages, route_with
from ferris.components.pagination import Pagination
from app.models.user_removal import UserRemoval
import logging
import json


class UserRemovals(Controller):
    class Meta:
        prefixes = ('api',)
        components = (messages.Messaging, Pagination)
        pagination_limit = 10
        Model = UserRemoval


    @route_with(template='/api/schedule/remove/user/<email>', methods=['GET'])
    def api_schedule_removal(self, email):
        UserRemoval.create({'email': email})
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
        params = json.loads(self.request.body)
        cancel = UserRemoval.update({'email': params['email'], 'status': params['status']})
        self.context['data'] = cancel
