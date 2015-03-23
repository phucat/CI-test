from ferris import Controller, route_with, settings
from app.models.audit_log import AuditLog as AuditLogModel
from app.models.deprovisioned_account import DeprovisionedAccount
from app.models.user_removal import UserRemoval
from app.components.calendars import Calendars
from google.appengine.ext import deferred
from google.appengine.api import users, app_identity, urlfetch, memcache
from gdata.calendar_resource.client import CalendarResourceClient
import json
import time
import datetime
from plugins import calendar as calendar_api, google_directory, rfc3339
import logging
import urllib2

APP_ID = app_identity.get_application_id()
urlfetch.set_default_fetch_deadline(60)
config = settings.get('admin_account')
current_user = users.get_current_user()


class Calendars(Controller):
    class Meta:
        prefixes = ('api',)
        components = (Calendars,)
        View = 'json'

    @route_with(template='/api/calendar/events/<email>', methods=['GET'])
    def api_list_calendar_events(self, email):
        feed = []
        feed = calendar_api.get_all_events(email)
        self.context['data'] = feed

    @route_with(template='/api/calendar/users', methods=['GET'])
    def api_list_all_users(self):
        self.context['data'] = google_directory.get_all_users_cached()

    @route_with(template='/api/calendar/resource/<feed>', methods=['GET'])
    def api_list_resource(self, feed):
        data = {}
        client = CalendarResourceClient(domain=config['domain'])
        client.ClientLogin(email=config['email'], password=config['password'], source=APP_ID)

        if feed == 'feed':
            calendar_resources = str(client.GetResourceFeed())
        else:
            calendar_resources = str(client.GetResourceFeed(uri="https://apps-apis.google.com/a/feeds/calendar/resource/2.0/sherpatest.com/?%s" % feed))
            data['previous'] = 'feed'

        nextpage, res = self.components.calendars.find_resource(calendar_resources)
        sortedResource = sorted(res, key=lambda resource: resource['resourceCommonName'])
        data['items'] = sortedResource
        data['next'] = nextpage

        self.context['data'] = data

    @route_with(template='/api/calendar/resource_memcache', methods=['GET'])
    def api_list_resource2(self):
        data = self.components.calendars.list_resource_memcache()
        self.context['data'] = data

    @route_with(template='/api/calendar/resource/create', methods=['POST'])
    def api_create_resource(self):
        resultMessage = {}

        client = CalendarResourceClient(domain=config['domain'])
        client.ClientLogin(email=config['email'], password=config['password'], source=APP_ID)
        resource = json.loads(self.request.body)

        try:
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
            insert_audit_log(action, 'add new resource', self.session['current_user'], resource['resourceCommonName'], None, '')

            # AuditLogModel.new_resource_notification(config['email'], current_user.nickname(), resource)

            resultMessage['message'] = action
            resultMessage['items'] = res
            self.context['data'] = resultMessage

        except Exception as e:
            logging.info(e)
            # xml = str(e).split(',')
            # xml = xml[1]
            # sxml = xml.strip()

            # root = ET.fromstring(str(sxml))

            # for err in root.iter('error'):
            #     return err.get('errorCode')

            return 406
            # resultMessage['error'] = "There is an existing Resource with that ID"
            # self.context['data'] = resultMessage

    @route_with(template='/api/calendar/resource/update', methods=['POST'])
    def api_update_resource(self):
        resultMessage = {}
        try:
            client = CalendarResourceClient(domain=config['domain'])
            client.ClientLogin(email=config['email'], password=config['password'], source=APP_ID)
            resource = json.loads(self.request.body)

            updates_params = {
                'resourceDescription': None,
                'resourceType': None
            }

            resource_list = memcache.get('resource_list')
            if resource_list is None:
                resource_list = self.components.calendars.list_resource_memcache()

            for apiResource in resource_list:
                if apiResource['resourceId'] == resource['resourceId']:
                    updates_params['resourceId'] = resource['resourceId']

                    if apiResource['resourceDescription'] != resource['resourceDescription']:
                        updates_params['resourceDescription'] = resource['resourceDescription']

                    if apiResource['resourceType'] != resource['resourceType']:
                        updates_params['resourceType'] = resource['resourceType']

            resource['updates'] = updates_params

            updated_calendar_resource = client.UpdateResource(
                resource_id=resource['resourceId'],
                resource_common_name=resource['resourceCommonName'],
                resource_description=resource['resourceDescription'],
                resource_type=resource['resourceType'])

            self.process_update_resource(resource)
            res = self.components.calendars.find_resource(str(updated_calendar_resource))

            resultMessage['message'] = 'The app is in the process of updating the calendar.'
            resultMessage['items'] = res
            self.context['data'] = resultMessage
        except urllib2.HTTPError as e:
            logging.info('get_all_events: HTTPerror')
            logging.info(e.code)
            if e.code == 401:
                pass

    def process_update_resource(self, resource):
        # users_email = google_directory.get_all_users_cached()

        users_email = [
            # {"primaryEmail": "rcabeltis@sherpatest.com"},
            # {"primaryEmail": "appuser1@sherpatest.com"},
            # {"primaryEmail": "appuser2@sherpatest.com"},
            {"primaryEmail": "arista-test2@sherpatest.com"},
            {"primaryEmail": "richmond.gozarin@sherpatest.com"}
        ]

        for user_email in users_email:
            deferred.defer(self.get_all_events, user_email['primaryEmail'], '', '', resource, True, self.session['current_user'])

    @route_with('/api/calendar/remove_user/events/<selectedEmail>', methods=['POST'])
    def api_remove_users_events(self, selectedEmail):
        request = json.loads(self.request.body)
        comment = request['comment']
        resultMessage = {}
        # users_email = google_directory.get_all_users_cached()

        users_email = [
            # {"primaryEmail": "rcabeltis@sherpatest.com"},
            # {"primaryEmail": "appuser1@sherpatest.com"},
            # {"primaryEmail": "appuser2@sherpatest.com"},
            {"primaryEmail": "arista-test2@sherpatest.com"},
            {"primaryEmail": "richmond.gozarin@sherpatest.com"}
        ]

        insert_audit_log('User comment.', 'user manager', self.session['current_user'], '-', '-', comment)

        resultMessage['message'] = 'The app is in the process of removing %s in calendar events.' % selectedEmail
        self.context['data'] = resultMessage

        for user_email in users_email:
            deferred.defer(self.get_all_events, user_email['primaryEmail'], selectedEmail, comment, '', False, self.session['current_user'])

    @classmethod
    def get_all_events(self, user_email, selectedEmail, comment, resource_params, resource=False, current_user_email=''):
        try:
            events = calendar_api.get_all_events(user_email)
            if events is not None:
                for event in events['items']:
                    if 'dateTime' in event['start']:
                        current_date = time.time()
                        startDate = rfc3339.strtotimestamp(event['start']['dateTime'])
                    elif 'date' in event['start']:
                        current_date = str(datetime.date.today())
                        startDate = event['start']['date']

                    if startDate >= current_date:
                        if resource == False:
                            if 'attendees' in event:
                                if event['organizer']['email'] != selectedEmail:
                                    participants_email = [participant['email'] for participant in event['attendees']]
                                    if selectedEmail in participants_email:
                                        deferred.defer(self.filter_attendees, event, selectedEmail, user_email, comment, current_user_email)
                                    else:
                                        pass
                                else:
                                    if len(event['attendees']) > 1:
                                        action = 'Oops, %s is the owner in %s event with %s attendees.' % (selectedEmail, event['summary'], len(event['attendees']))
                                        insert_audit_log(action, 'Remove user in calendar events', current_user_email, selectedEmail, '%s' % event['summary'], '')
                                        attendees_list = []
                                        for attendee in event['attendees']:
                                            if attendee['email'] != selectedEmail and 'resource' not in attendee:
                                                attendees_list.append(attendee['email'])
                                        attendees_list.append(current_user_email)
                                        DeprovisionedAccount.remove_owner_failed_notification(attendees_list, selectedEmail, event['summary'], event['htmlLink'])
                                    elif len(event['attendees']) == 1:
                                        for attendee in event['attendees']:
                                            if attendee['email'] == selectedEmail and 'resource' not in attendee:
                                                deferred.defer(self.delete_owner_event, event, selectedEmail, user_email, current_user_email)
                            else:
                                if event['organizer']['email'] == selectedEmail:
                                    deferred.defer(self.delete_owner_event, event, selectedEmail, user_email, current_user_email)
                        else:
                            deferred.defer(self.filter_location, event, user_email, resource_params, current_user_email)

        except urllib2.HTTPError as e:
            logging.info('get_all_events: HTTPerror')
            logging.info(e.code)
            pass

    @classmethod
    def filter_attendees(self, event, selectedEmail, user_email, comment, current_user_email):
        attendees_list = []
        for attendee in event['attendees']:
            if attendee['email'] != selectedEmail and 'resource' not in attendee:
                attendees_list.append({'email': attendee['email']})

        params_body = {
            'attendees': attendees_list,
            'reminders': {'overrides': [{'minutes': 15, 'method': 'popup'}], 'useDefault': 'false' },
            'start': event['start'],
            'end': event['end'],
            'summary': event['summary']
        }

        update_event = {
            'event_id': event['id'],
            'user_email': user_email,
            'body': params_body,
            'organizer': event['organizer']['email'],
            'selectedEmail': selectedEmail,
            'comment': comment,
            'attendeesEmail': [email['email'] for email in attendees_list]
        }
        deferred.defer(self.update_calendar_events, update_event, False, current_user_email)

    @classmethod
    def filter_location(self, event, user_email, resource_params, current_user_email):
        attendees_list = []
        resourceName = None
        if 'attendees' in event:
            for attendee in event['attendees']:
                if 'resource' in attendee:
                    if attendee['displayName'] == resource_params['old_resourceCommonName']:
                        resourceName = resource_params['old_resourceCommonName']
                else:
                    attendees_list.append(attendee['email'])

        if resource_params['resourceCommonName'] != resource_params['old_resourceCommonName']:
            if resourceName:
                params_body = {
                    'location': resource_params['resourceCommonName'],
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
                    'organizerEmail': event['organizer']['email'],
                    'organizerName': event['organizer']['displayName'],
                    'event_link': event['htmlLink'],
                    'attendeesEmail': attendees_list,
                    'body': params_body,
                    'resource': resource_params
                }

                deferred.defer(self.update_calendar_events, update_event, True, current_user_email)
        else:
            if resourceName:
                update_event = {
                    'event_id': event['id'],
                    'user_email': user_email,
                    'summary': event['summary'],
                    'organizerEmail': event['organizer']['email'],
                    'organizerName': event['organizer']['displayName'],
                    'event_link': event['htmlLink'],
                    'attendeesEmail': attendees_list,
                    'resource': resource_params
                }
                deferred.defer(self.update_resource_events, update_event, current_user_email)


    @classmethod
    def update_calendar_events(self, params, cal_resource=False, current_user_email=''):
        try:
            calendar_api.update_event(params['event_id'], params['user_email'], params['body'], True)

            if cal_resource == False:
                if params['selectedEmail']:
                    insert_audit_log(
                        '%s has been removed from events.' % params['selectedEmail'],
                        'user manager',
                        current_user_email,
                        '%s calendar' % params['user_email'],
                        '%s' % params['body']['summary'], '')

                    AuditLogModel.attendees_update_notification(params['attendeesEmail'], params['selectedEmail'], params['body']['summary'])
            else:
                insert_audit_log(
                    "Event %s resource has been updated. " % (params['body']['summary']),
                    'resource manager',
                    current_user_email,
                    '%s resource name' % params['body']['old_resourceName'],
                    '%s' % (params['body']['location']), '')

                AuditLogModel.update_resource_notification(params['organizerEmail'], params['organizerName'], params['event_link'], params['resource'])

        except Exception, e:
            logging.error('== API UPDATE EVENT ERROR ==')
            logging.error(e)

    @classmethod
    def update_resource_events(self, params, current_user_email=''):
        try:
            insert_audit_log(
                """
                    Event %s resource has been updated.
                    Resource ID: %s
                    Resource Name: %s
                    Resource Type: %s
                    Resource Description: %s """
                % (params['summary'],
                    params['resource']['updates']['resourceId'],
                    params['resource']['resourceCommonName'],
                    params['resource']['updates']['resourceType'],
                    params['resource']['updates']['resourceDescription']),
                'resource manager',
                current_user_email,
                '%s resource name' % params['resource']['old_resourceCommonName'],
                'Calendar of %s on event %s.' % (params['user_email'], params['summary']), '')

            AuditLogModel.update_resource_notification(params['attendeesEmail'], 'Participants', params['event_link'], params['resource'])

        except Exception, e:
            logging.error('== API UPDATE RESOURCE ERROR ==')
            logging.error(e)

    @classmethod
    def delete_owner_event(self, event, selectedEmail, user_email, current_user_email):
        try:
            calendar_api.delete_event(event['id'], selectedEmail)

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

            DeprovisionedAccount.remove_owner_success_notification(current_user_email, selectedEmail, event['summary'], event['htmlLink'])

        except Exception, e:
            logging.error('== API DELETE EVENT ERROR ==')
            logging.error(e)

    @route_with(template='/api/user_removals/deleting/users')
    def api_deleting_users(self):
        # google_directory.prime_caches()
        deleted_users = google_directory.get_all_deleted_users()
        # list_user_emails = google_directory.get_all_users_cached()

        list_user_emails = [
            # {"primaryEmail": "rcabeltis@sherpatest.com"},
            # {"primaryEmail": "appuser1@sherpatest.com"},
            # {"primaryEmail": "appuser2@sherpatest.com"},
            {"primaryEmail": "arista-test2@sherpatest.com"},
            {"primaryEmail": "richmond.gozarin@sherpatest.com"}
        ]

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
                        modified_approver = config['email']

                    cal_params = {
                        'action': '%s has been de-provisioned.' % d_user,
                        'invoked': 'cron job',
                        'app_user': modified_approver,
                        'target_resource': 'Domain',
                        'target_event_altered': '-',
                        'comment': ''
                    }
                    insert_audit_log(
                        cal_params['action'], cal_params['invoked'],
                        cal_params['app_user'],
                        cal_params['target_resource'],
                        cal_params['target_event_altered'], cal_params['comment'])

                    DeprovisionedAccount.deprovision_success_notification(str(modified_approver), d_user)

                    DeprovisionedAccount.create(params)
                    deferred.defer(self.process_deleted_account, d_user, x_email, list_user_emails, str(modified_approver))

            return 'started...'
        else:
            return 'Empty list..'

    def get_approved_scheduled_user(self, d_user):
        schedule_user_removal = UserRemoval.list_all_approve()
        for remover in schedule_user_removal:
            if remover.email == d_user:
                return remover.modified_by.email()

    @classmethod
    def process_deleted_account(self, d_user, x_email, list_user_emails, current_user_email):

        for active_user in list_user_emails:
            deferred.defer(self.get_all_events, active_user['primaryEmail'], d_user, '', '', False, current_user_email)

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
