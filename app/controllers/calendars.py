from ferris import Controller, route_with, settings
from app.models.audit_log import AuditLog as AuditLogModel
from app.models.deprovisioned_account import DeprovisionedAccount
from app.models.user_removal import UserRemoval
from app.components.calendars import Calendars
from google.appengine.ext import deferred
from google.appengine.api import users, app_identity, urlfetch, memcache
from gdata.calendar_resource.client import CalendarResourceClient
from gdata.gauth import OAuth2TokenFromCredentials as CreateToken
from app.etc import build_creds
from app.models.email_recipient import EmailRecipient
import xml.etree.ElementTree as ET
import json
import time
import datetime
from plugins import calendar as calendar_api, google_directory, rfc3339
import logging
import urllib2


TEAM_EMAILS = EmailRecipient.list_all()
IT_ADMIN_EMAIL = [team_email.email for team_email in TEAM_EMAILS]
APP_ID = app_identity.get_application_id()
urlfetch.set_default_fetch_deadline(60)
oauth_config = settings.get('oauth2_service_account')
current_user = users.get_current_user()


class Calendars(Controller):
    class Meta:
        prefixes = ('api',)
        components = (Calendars,)
        View = 'json'

    @route_with(template='/api/calendar/events/<email>', methods=['GET'])
    def api_list_calendar_events(self, email):
        feed = []

        feed = calendar_api.get_all_events(email, None, None)

        self.context['data'] = feed

    @route_with(template='/api/calendar/recurring/events/<email>/<selectedemail>', methods=['GET'])
    def api_list_recurring_events(self, email, selectedemail):
        feed = []

        feed = calendar_api.get_all_events(email, selectedemail, None)

        self.context['data'] = feed

    @route_with(template='/api/calendar/users', methods=['GET'])
    def api_list_all_users(self):
        self.context['data'] = google_directory.get_all_users_cached()

    @route_with(template='/api/calendar/users/deleted', methods=['GET'])
    def api_deleted_users(self):
        deleted_users = google_directory.get_all_deleted_users(showDeleted=True)
        suspended_users = google_directory.get_all_deleted_users(showDeleted=False)

        for suspended in suspended_users:
            deleted_users.append(suspended)

        self.context['data'] = deleted_users

    @route_with(template='/api/calendar/resource/<feed>', methods=['GET'])
    def api_list_resource(self, feed):
        data = {}

        # client = CalendarResourceClient(domain=oauth_config['domain'])
        # client.ClientLogin(email=oauth_config['default_user'], password=oauth_config['password'], source=APP_ID)

        creds = build_creds.build_credentials(
            scope=[
                "https://apps-apis.google.com/a/feeds/calendar/resource/"
            ],
            service_account_name=oauth_config['client_email'],
            private_key=oauth_config['private_key'],
            user=oauth_config['default_user']
        )
        auth2token = CreateToken(creds)
        client = CalendarResourceClient(domain=oauth_config['domain'])
        auth2token.authorize(client)

        if feed == 'feed':
            calendar_resources = str(client.GetResourceFeed())
        else:
            calendar_resources = str(client.GetResourceFeed(uri="https://apps-apis.google.com/a/feeds/calendar/resource/2.0/%s/?%s" % (oauth_config['domain'], feed)))

        nextpage, res = self.components.calendars.find_resource(calendar_resources)
        data['items'] = res
        data['next'] = nextpage
        data['previous'] = None
        data['page'] = "start=%s" % res[0]['resourceId']

        self.context['data'] = data

    @route_with(template='/api/calendar/resource_memcache', methods=['GET'])
    def api_list_resource2(self):
        data = self.components.calendars.list_resource_memcache()
        self.context['data'] = data

    @route_with(template='/api/calendar/resource/create', methods=['POST'])
    def api_create_resource(self):
        resultMessage = {}

        creds = build_creds.build_credentials(
            scope=[
                "https://apps-apis.google.com/a/feeds/calendar/resource/"
            ],
            service_account_name=oauth_config['client_email'],
            private_key=oauth_config['private_key'],
            user=oauth_config['default_user']
        )
        auth2token = CreateToken(creds)
        client = CalendarResourceClient(domain=oauth_config['domain'])
        auth2token.authorize(client)

        resource = json.loads(self.request.body)

        try:
            resource['resourceId'] = generate_random_numbers(12)

            resource_list = memcache.get('resource_list')
            if resource_list is None:
                resource_list = self.components.calendars.list_resource_memcache()

            for apiResource in resource_list:
                if apiResource['resourceCommonName'] == resource['resourceCommonName']:
                    return 402

            if 'resourceDescription' in resource:
                resourceDescription = resource['resourceDescription']
            else:
                resourceDescription = None

            calendar_resource = client.CreateResource(
                resource_id=resource['resourceId'],
                resource_common_name=resource['resourceCommonName'],
                resource_description=resourceDescription,
                resource_type=resource['resourceType'])

            res = self.components.calendars.find_resource(str(calendar_resource))

            action = 'A new Calendar Resource has been created'
            insert_audit_log(
                """A new Calendar Resource has been created.
                    Resource ID: %s
                    Resource Name: %s
                    Resource Type: %s
                    Resource Description: %s """
                % (
                    resource['resourceId'],
                    resource['resourceCommonName'],
                    resource['resourceType'],
                    resource['resourceDescription']),
                'add new resource',
                self.session['current_user'],
                resource['resourceCommonName'], None, '')

            # AuditLogModel.new_resource_notification(config['email'], current_user.nickname(), resource)

            resultMessage['message'] = action
            resultMessage['items'] = res
            self.context['data'] = resultMessage

        except Exception as e:
            logging.info('create resource failed: %s' % e)
            return 406

    @route_with(template='/api/calendar/resource/update', methods=['POST'])
    def api_update_resource(self):
        resultMessage = {}
        try:
            current_user = users.get_current_user()
            creds = build_creds.build_credentials(
                scope=[
                    "https://apps-apis.google.com/a/feeds/calendar/resource/"
                ],
                service_account_name=oauth_config['client_email'],
                private_key=oauth_config['private_key'],
                user=oauth_config['default_user']
            )
            auth2token = CreateToken(creds)
            client = CalendarResourceClient(domain=oauth_config['domain'])
            auth2token.authorize(client)

            resource = json.loads(self.request.body)

            client.UpdateResource(
                resource_id=resource['resourceId'],
                resource_common_name=resource['resourceCommonName'],
                resource_description=resource['resourceDescription'],
                resource_type=resource['resourceType'])

            calendar_resource_email = client.GetResource(resource_id=resource['resourceId'])

            res = self.components.calendars.find_resource(str(calendar_resource_email))

            resultMessage['message'] = 'The app is in the process of updating the calendar.'
            resultMessage['items'] = res
            self.context['data'] = resultMessage
            resource['new_email'] = res[0]['resourceEmail']
            sharded = "sharded" + ("1" if int(time.time()) % 2 == 0 else "2")
            deferred.defer(self.process_update_resource, resource, current_user.email(), _queue=sharded)
        except urllib2.HTTPError as e:
            logging.info('get_all_events: HTTPerror')
            logging.info(e.code)
            if e.code == 401:
                pass

    @classmethod
    def process_update_resource(self, resource, current_user):
        insert_audit_log(
            """Old Resource Name '%s' has been updated to:
                Resource ID: %s
                Resource Name: %s
                Resource Type: %s
                Resource Description: %s """
            % (
                resource['old_resourceCommonName'],
                resource['resourceId'],
                resource['resourceCommonName'],
                resource['resourceType'],
                resource['resourceDescription']),
            'resource manager',
            current_user,
            '%s resource name' % resource['old_resourceCommonName'],
            '-', '')

        users_email = google_directory.get_all_users_cached()
        for user_email in users_email:
            sharded = "sharded" + ("1" if int(time.time()) % 2 == 0 else "2")
            deferred.defer(self.get_resource_events, user_email['primaryEmail'], resource['old_resourceCommonName'], '', resource, True, current_user, _countdown=1, _queue=sharded)

    @route_with('/api/calendar/remove_user/events/<selectedEmail>', methods=['POST'])
    def api_remove_users_events(self, selectedEmail):
        request = json.loads(self.request.body)
        comment = request['comment']
        resultMessage = {}

        insert_audit_log("User to be removed: %s | User comment: %s" % (selectedEmail, comment),
            'user manager', self.session['current_user'], '-', '-', comment)

        resultMessage['message'] = 'The app is in the process of removing %s in calendar events.' % selectedEmail
        self.context['data'] = resultMessage

        current_user = users.get_current_user()
        sharded = "sharded" + ("1" if int(time.time()) % 2 == 0 else "2")
        deferred.defer(self.get_all_events, selectedEmail, selectedEmail, comment, '', False, current_user.email(), _queue=sharded)

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

                approved_user = {'email': params['email'], 'status': True}
                DeprovisionedAccount.create(approved_user)
                sharded = "sharded" + ("1" if int(time.time()) % 2 == 0 else "2")
                deferred.defer(self.get_all_events, params['email'], params['email'], '', '', False, self.session['current_user'], _queue=sharded)

            elif params['status'] == 'Cancel':
                params['status'] += 'led'

            insert_audit_log('%s has been %s for removal.' % (params['email'], params['status']), 'api endpoint', user.email(), 'Schedule User Removal', '', '')

            return params['status']

    @classmethod
    def get_resource_events(self, user_email, selectedEmail, comment, resource_params, resource=False, current_user_email=''):
        pageToken = None
        event_id_pool = []
        try:
            while True:
                events, pageToken = calendar_api.get_all_events(user_email, selectedEmail, pageToken)
                if events['items']:
                    logging.info('RESOURCE ROOM 2: %s' % events)
                    for event in events['items']:
                        if event['status'] == 'cancelled':
                            continue
                        if 'recurringEventId' in event:
                            event['id'] = event['recurringEventId']

                        logging.info('CALENDAR OWNER: %s' % user_email)
                        if 'start' in event:
                            if 'dateTime' in event['start']:
                                current_date = time.time()
                                startDate = rfc3339.strtotimestamp(event['start']['dateTime'])
                            elif 'date' in event['start']:
                                current_date = str(datetime.date.today())
                                startDate = event['start']['date']

                            sharded = "sharded" + ("1" if int(time.time()) % 2 == 0 else "2")

                            if 'recurringEventId' in event:
                                logging.info('RECURRING EVENT ID: %s' % event_id_pool)
                                if event['recurringEventId'] not in event_id_pool:
                                    event_id_pool.append(event['recurringEventId'])

                                    deferred.defer(self.get_events, event, user_email, selectedEmail, comment, resource_params, resource, current_user_email, event_id_pool, _queue=sharded)
                            else:
                                if startDate >= current_date:
                                    deferred.defer(self.get_events, event, user_email, selectedEmail, comment, resource_params, resource, current_user_email, event_id_pool, _queue=sharded)
                        else:
                            pass

                if not pageToken:
                    break
        except urllib2.HTTPError as e:
            logging.info('get_all_events: HTTPerror')
            logging.info(e.code)
            pass

    @classmethod
    def get_all_events(self, user_email, selectedEmail, comment, resource_params, resource=False, current_user_email=''):
        pageToken = None
        event_id_pool = []
        while True:
            try:
                events, pageToken = calendar_api.get_all_events(user_email, selectedEmail, pageToken)
                if events['items']:
                    for event in events['items']:
                        if event['status'] == 'cancelled':
                            continue
                        if 'recurringEventId' in event:
                            event['id'] = event['recurringEventId']

                        if 'start' in event:
                            if 'dateTime' in event['start']:
                                current_date = time.time()
                                startDate = rfc3339.strtotimestamp(event['start']['dateTime'])
                            elif 'date' in event['start']:
                                current_date = str(datetime.date.today())
                                startDate = event['start']['date']

                            sharded = "sharded" + ("1" if int(time.time()) % 2 == 0 else "2")

                            if 'recurringEventId' in event:
                                logging.info('RECURRING EVENT ID: %s' % event_id_pool)
                                if event['recurringEventId'] not in event_id_pool:
                                    event_id_pool.append(event['recurringEventId'])
                                    deferred.defer(self.get_events, event, user_email, selectedEmail, comment, resource_params, resource, current_user_email, event_id_pool, _queue=sharded)
                            else:
                                if startDate >= current_date:
                                    deferred.defer(self.get_events, event, user_email, selectedEmail, comment, resource_params, resource, current_user_email, event_id_pool, _queue=sharded)
                        else:
                            pass

                if not pageToken:
                    break
            except urllib2.HTTPError as e:
                logging.info('get_all_events: HTTPerror')
                logging.info(e.code)
                pass

    @classmethod
    def get_events(self, event, user_email, selectedEmail, comment, resource_params, resource=False, current_user_email='', event_id_pool=[]):
        try:
            logging.info('RECURRING EVENT ID 1: %s' % event_id_pool)
            sharded = "sharded" + ("1" if int(time.time()) % 2 == 0 else "2")
            if resource == False:
                deferred.defer(self.filter_attendees, event, user_email, selectedEmail, comment, current_user_email, event_id_pool, _queue=sharded)
            else:
                deferred.defer(self.filter_location, event, user_email, selectedEmail, comment, current_user_email, resource_params, event_id_pool, _queue=sharded)

        except urllib2.HTTPError as e:
            logging.info('get_events: HTTPerror')
            logging.info(e.code)
            pass

    @classmethod
    def filter_attendees(self, event, user_email, selectedEmail, comment, current_user_email, event_id_pool):

        if 'attendees' in event:
            if event['organizer']['email'] != selectedEmail:
                participants_email = [participant['email'] for participant in event['attendees']]
                if selectedEmail in participants_email:

                    attendees_list = []
                    resource_list = []
                    for attendee in event['attendees']:
                        if attendee['email'] != selectedEmail and 'resource' not in attendee:
                            attendees_list.append({'email': attendee['email']})

                        if attendee['email'] != selectedEmail or 'resource' in attendee:
                            resource_list.append({'email': attendee['email']})

                    params_body = {
                        'attendees': resource_list,
                        'reminders': {'overrides': [{'minutes': 15, 'method': 'popup'}], 'useDefault': 'false' },
                        'start': event['start'],
                        'end': event['end'],
                        'summary': event['summary']
                    }

                    for guest in attendees_list:
                        sharded = "sharded" + ("1" if int(time.time()) % 2 == 0 else "2")
                        deferred.defer(self.attendees_2, event, user_email, selectedEmail, comment, current_user_email, guest, params_body, event_id_pool, _queue=sharded)
                else:
                    pass
            else:
                sharded = "sharded" + ("1" if int(time.time()) % 2 == 0 else "2")
                deferred.defer(self.event_owner, event, user_email, selectedEmail, current_user_email, event_id_pool, _queue=sharded)
        else:
            if event['organizer']['email'] == selectedEmail:
                logging.info('EVENT ID: %s' % event['id'])
                calendar_api.delete_event(event['id'], selectedEmail, True)
                sharded = "sharded" + ("1" if int(time.time()) % 2 == 0 else "2")
                deferred.defer(self.delete_owner_event, event, selectedEmail, user_email, current_user_email, _queue=sharded)

    @classmethod
    def attendees_2(self, event, user_email, selectedEmail, comment, current_user_email, guest, params_body, event_id_pool):
        if selectedEmail:
            calendar_api.update_event(event['id'], guest['email'], params_body, True)
            insert_audit_log(
                '%s has been removed from events.' % selectedEmail,
                'user manager',
                current_user_email,
                '%s calendar' % user_email,
                '%s' % event['summary'], '')

            AuditLogModel.attendees_update_notification(guest['email'], selectedEmail, event['summary'])

    @classmethod
    def event_owner(self, event, user_email, selectedEmail, current_user_email, event_id_pool):
        if len(event['attendees']) == 2:
            isResource = search_resource(event['attendees'])
            if isResource:
                logging.info('EVENT ID: %s' % event['id'])
                calendar_api.delete_event(event['id'], selectedEmail, True)
                sharded = "sharded" + ("1" if int(time.time()) % 2 == 0 else "2")
                deferred.defer(self.delete_owner_event, event, selectedEmail, user_email, current_user_email, _queue=sharded)
            else:
                remove_owner_failed(event, user_email, selectedEmail, current_user_email)

        elif len(event['attendees']) == 1:
            for attendee in event['attendees']:
                if attendee['email'] == selectedEmail and 'resource' not in attendee:
                    logging.info('EVENT ID: %s' % event['id'])
                    calendar_api.delete_event(event['id'], selectedEmail, True)
                    sharded = "sharded" + ("1" if int(time.time()) % 2 == 0 else "2")
                    deferred.defer(self.delete_owner_event, event, selectedEmail, user_email, current_user_email, _queue=sharded)

        elif len(event['attendees']) > 1:
            remove_owner_failed(event, user_email, selectedEmail, current_user_email)

    @classmethod
    def filter_location(self, event, user_email, selectedEmail, comment, current_user_email, resource_params, event_id_pool):
        attendees_list = []
        resource_list = []
        if 'attendees' in event:
            for attendee in event['attendees']:
                if 'resource' in attendee:
                    if attendee['displayName'] == selectedEmail:
                        locations = event['location'].split(', ')
                        logging.info('RESOURCE_LOC: %s' % locations)
                        if len(locations) > 1:
                            pos = locations.index(str(selectedEmail))
                            locations[pos] = resource_params['resourceCommonName']
                            new_location = ', '.join(locations)
                        else:
                            new_location = resource_params['resourceCommonName']

                        resource_list.append({'email': resource_params['new_email']})
                    else:
                        resource_list.append({'email': attendee['email']})
                else:
                    attendees_list.append(attendee['email'])
                    resource_list.append({'email': attendee['email']})

        logging.info('FILTER LOCATION 2: %s' % user_email)
        if 'displayName' in event['organizer']:
            organizerName = event['organizer']['displayName']
        else:
            organizerName = event['organizer']['email']

        sharded = "sharded" + ("1" if int(time.time()) % 2 == 0 else "2")

        if resource_params['resourceCommonName'] != resource_params['old_resourceCommonName']:
            logging.info('LOCATION: %s' % new_location)
            params_body = {
                'location': new_location,
                'old_resourceName': resource_params['old_resourceCommonName'],
                'attendees': attendees_list,
                'reminders': {'overrides': [{'minutes': 15, 'method': 'popup'}], 'useDefault': 'false' },
                'start': event['start'],
                'end': event['end'],
                'summary': event['summary']
            }

            update_event = {
                'event_id': event['id'],
                'user_email': user_email,
                'summary': event['summary'],
                'organizerEmail': event['organizer']['email'],
                'organizerName': organizerName,
                'event_link': event['htmlLink'],
                'attendeesEmail': attendees_list,
                'body': params_body,
                'resource': resource_params
            }

            deferred.defer(self.send_event_notification, event, user_email, params_body, resource_list, update_event, current_user_email, event_id_pool, _queue=sharded)
        else:
            update_event = {
                'event_id': event['id'],
                'user_email': user_email,
                'summary': event['summary'],
                'organizerEmail': event['organizer']['email'],
                'organizerName': organizerName,
                'event_link': event['htmlLink'],
                'attendeesEmail': attendees_list,
                'resource': resource_params
            }

            deferred.defer(self.update_resource_events, update_event, current_user_email, _queue=sharded)

    @classmethod
    def send_event_notification(self, event, user_email, params_body, resource_list, update_event, current_user_email, event_id_pool):
        logging.info('SEND NOTIF 1: %s' % user_email)

        logging.info('SEND NOTIF NOT RECURR: %s' % user_email)
        calendar_api.update_event(event['id'], user_email, params_body, False)
        params_body['attendees'] = resource_list
        calendar_api.update_event(event['id'], user_email, params_body, True)
        sharded = "sharded" + ("1" if int(time.time()) % 2 == 0 else "2")
        deferred.defer(self.update_resource_events, update_event, current_user_email, _queue=sharded)

    @classmethod
    def update_resource_events(self, params, current_user_email=''):
        try:
            logging.info('UPDATE RESOURCE NOTIF: %s' % params)
            insert_audit_log(
                """Old Resource Name '%s' in event '%s' has been updated to:
                    Resource ID: %s
                    Resource Name: %s
                    Resource Type: %s
                    Resource Description: %s """
                % ( params['resource']['old_resourceCommonName'],
                    params['summary'],
                    params['resource']['resourceId'],
                    params['resource']['resourceCommonName'],
                    params['resource']['resourceType'],
                    params['resource']['resourceDescription']),
                'resource manager',
                current_user_email,
                '%s resource name' % params['resource']['old_resourceCommonName'],
                'Calendar of %s on event %s.' % (params['user_email'], params['summary']), '')

            logging.info('UPDATE RESOURCE: %s' % params['user_email'])
            AuditLogModel.update_resource_notification(params['user_email'], 'Participants', params['event_link'], params['resource'])

        except Exception, e:
            logging.error('== API UPDATE RESOURCE ERROR ==')
            logging.error(e)

    @classmethod
    def delete_owner_event(self, event, selectedEmail, user_email, current_user_email):
        try:
            cal_params = {
                'action': '%s has been removed from calendar events.' % selectedEmail,
                'invoked': 'user manager',
                'app_user': current_user_email,
                'target_resource': '%s calendar' % user_email,
                'target_event_altered': '%s' % event['summary'],
                'comment': ''
            }
            insert_audit_log(
                cal_params['action'], cal_params['invoked'],
                cal_params['app_user'],
                cal_params['target_resource'],
                cal_params['target_event_altered'], cal_params['comment']
            )

            DeprovisionedAccount.remove_owner_success_notification(IT_ADMIN_EMAIL, selectedEmail, event['summary'], event['htmlLink'])

        except Exception, e:
            logging.error('== API DELETE EVENT ERROR ==')
            logging.error(e)

    @route_with(template='/api/user_removals/deleting/users')
    def api_deleting_users(self):
        google_directory.prime_caches()
        deleted_users = google_directory.get_all_deleted_users(showDeleted=True)
        suspended_users = google_directory.get_all_deleted_users(showDeleted=False)

        if suspended_users:
            for suspended in suspended_users:
                deleted_users.append(suspended)

        list_user_emails = google_directory.get_all_users_cached()

        ndbDeletedUserCount = DeprovisionedAccount.query().count()

        if ndbDeletedUserCount == 0:
            params = {'email': 'dummy@dummy.com', 'status': True}
            DeprovisionedAccount.create(params)

        ndbDeletedUserlist = DeprovisionedAccount.list_all()
        x_email = [x_email.email for x_email in ndbDeletedUserlist]

        if deleted_users:
            for d_user in deleted_users:
                if d_user not in x_email and x_email != 'dummy@dummy.com':
                    params = {'email': d_user, 'status': True}

                    modified_approver = self.get_approved_scheduled_user(d_user)
                    if modified_approver is None:
                        modified_approver = oauth_config['default_user']

                    cal_params = {
                        'action': '%s has been removed from events.' % d_user,
                        'invoked': 'cron job',
                        'app_user': modified_approver,
                        'target_resource': 'Calendar Events',
                        'target_event_altered': '-',
                        'comment': ''
                    }
                    insert_audit_log(
                        cal_params['action'], cal_params['invoked'],
                        cal_params['app_user'],
                        cal_params['target_resource'],
                        cal_params['target_event_altered'], cal_params['comment'])

                    DeprovisionedAccount.deprovision_success_notification(str(modified_approver), d_user)

                    sharded = "sharded" + ("1" if int(time.time()) % 2 == 0 else "2")
                    DeprovisionedAccount.create(params)
                    deferred.defer(self.process_deleted_account, d_user, x_email, list_user_emails, str(modified_approver), _queue=sharded)

            return 'started...'
        else:
            return 'Empty list..'

    def get_approved_scheduled_user(self, d_user):
        schedule_user_removal = UserRemoval.list_all_approve()
        for remover in schedule_user_removal:
            if remover.email == d_user:
                return remover.modified_by.email()

    @route_with(template='/api/google_directory/users/prime')
    def api_prime_user(self):
        google_directory.prime_caches()
        return 'user prime cache.'

    @classmethod
    def process_deleted_account(self, d_user, x_email, list_user_emails, current_user_email):

        for active_user in list_user_emails:
            sharded = "sharded" + ("1" if int(time.time()) % 2 == 0 else "2")
            deferred.defer(self.get_all_events, active_user['primaryEmail'], d_user, '', '', False, current_user_email, _queue=sharded)

    @route_with(template='/api/clear/datastore/deprovisioned_account')
    def api_clear_ndb(self):
        DeprovisionedAccount.remove()
        return 200

    @route_with(template='/api/clear/datastore/calendars')
    def api_clear_AuditLogModel(self):
        AuditLogModel.remove()
        return 200


def insert_audit_log(action, invoked, app_user, target_resource, target_event_altered, comment=None):

    cal_params = {
        'action': action,
        'how_the_action_invoked': invoked,
        'app_user_invoked_action': app_user,
        'target_resource': target_resource,
        'target_event_altered': target_event_altered,
        'comment': comment
    }
    AuditLogModel.create(cal_params)


def remove_owner_failed(event, user_email, selectedEmail, current_user_email):
    logging.info('REMOVE_OWNER: %s' % event['summary'])
    action = "Oops %s is the owner in %s event with %s attendees." % (selectedEmail, event['summary'], len(event['attendees']))
    insert_audit_log(action, 'Remove user in calendar events', current_user_email, selectedEmail, '%s %s' % (user_email, event['summary']), '')

    DeprovisionedAccount.remove_owner_failed_notification(IT_ADMIN_EMAIL, selectedEmail, event['summary'], event['htmlLink'])


def find_resource(resource):
        res = []
        nextpage = ''
        root = ET.fromstring(resource)
        if root.tag == '{http://www.w3.org/2005/Atom}feed':
            for link in root.iterfind('{http://www.w3.org/2005/Atom}link'):
                if link.get('rel') == 'next':
                    nextpage = link.get('href')

            for entry in root.iterfind('{http://www.w3.org/2005/Atom}entry'):
                param = {}
                for child in entry.getchildren():
                    label = ['resourceId', 'resourceCommonName', 'resourceDescription', 'resourceType', 'resourceEmail']
                    if (child.get('name') in label):
                        param[child.get('name')] = child.get('value')
                res.append(param)
            return nextpage, res
        else:
            param = {}
            for child in root.getchildren():
                label = ['resourceId', 'resourceCommonName', 'resourceDescription', 'resourceType', 'resourceEmail']
                if (child.get('name') in label):
                    param[child.get('name')] = child.get('value')
            res.append(param)
            return res


def generate_random_numbers(n):
    from random import randint
    range_start = 10**(n-1)
    range_end = (10**n)-1
    gen_number = randint(range_start, range_end)
    return str("-%s" % gen_number)


def search_resource(attendees):
    return [element for element in attendees if 'resource' in element]
