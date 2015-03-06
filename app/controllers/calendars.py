from ferris import Controller, messages, route_with, settings
from app.models.audit_log import AuditLog as AuditLogModel
from app.models.deprovisioned_account import DeprovisionedAccount
from google.appengine.ext import deferred
from google.appengine.api import users, app_identity, urlfetch
from gdata.calendar_resource.client import CalendarResourceClient
import json
import urllib
import time
import datetime
import xml.etree.ElementTree as ET
from plugins import calendar as calendar_api, google_directory, rfc3339
import logging, urllib2

APP_ID = app_identity.get_application_id()
urlfetch.set_default_fetch_deadline(60)
config = settings.get('admin_account')
current_user = users.get_current_user()


class Calendars(Controller):
    class Meta:
        prefixes = ('api',)
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
            # uri = urllib.unquote(feed).decode('utf8')
            calendar_resources = str(client.GetResourceFeed(uri="https://apps-apis.google.com/a/feeds/calendar/resource/2.0/sherpatest.com/?%s" % feed))
            data['previous'] = 'feed'

        nextpage, res = self.find_resource(calendar_resources)
        sortedResource = sorted(res, key=lambda resource: resource['resourceCommonName'])
        data['items'] = sortedResource
        data['next'] = nextpage

        self.context['data'] = data

    @route_with(template='/api/calendar/resource/create', methods=['POST'])
    def api_create_resource(self):
        resultMessage = {}

        client = CalendarResourceClient(domain=config['domain'])
        client.ClientLogin(email=config['email'], password=config['password'], source=APP_ID)
        resource = json.loads(self.request.body)

        calendar_resource = client.CreateResource(
            resource_id=resource['resourceId'],
            resource_common_name=resource['resourceCommonName'],
            resource_description=resource['resourceDescription'],
            resource_type=resource['resourceType'])

        res = self.find_resource(str(calendar_resource))
        action = 'A new Calendar Resource has been created'
        insert_audit_log(action, 'add new resource', current_user.email(), resource['resourceCommonName'], None, None)

        resultMessage['message'] = action
        resultMessage['items'] = res
        self.context['data'] = resultMessage

    @route_with(template='/api/calendar/resource/update', methods=['POST'])
    def api_update_resource(self):
        resultMessage = {}
        try:
            client = CalendarResourceClient(domain=config['domain'])
            client.ClientLogin(email=config['email'], password=config['password'], source=APP_ID)
            resource = json.loads(self.request.body)

            updated_calendar_resource = client.UpdateResource(
                resource_id=resource['resourceId'],
                resource_common_name=resource['resourceCommonName'],
                resource_description=resource['resourceDescription'],
                resource_type=resource['resourceType'])

            self.process_update_resource(resource)
            res = self.find_resource(str(updated_calendar_resource))

            resultMessage['message'] = 'The app is in the process of updating the calendar.'
            resultMessage['items'] = res
            self.context['data'] = resultMessage
        except urllib2.HTTPError as e:
            logging.info('get_all_events: HTTPerror')
            logging.info(e.code)
            if e.code == 401:
                pass

    def process_update_resource(self, resource):
        #users_email = google_directory.get_all_users_cached()
        current_user = users.get_current_user()

        users_email = [
            {"primaryEmail": "rich.test5@sherpatest.com"},
            {"primaryEmail": "richmond.gozarin@sherpatest.com"},
            {"primaryEmail": "zaldy.santos@sherpatest.com"},
            {"primaryEmail": "arvin.corpuz@sherpatest.com"}
        ]

        for user_email in users_email:
            deferred.defer(self.get_all_events, user_email['primaryEmail'], '', '', resource, True, current_user.email())

    @route_with('/api/calendar/remove_user/events/<selectedEmail>', methods=['POST'])
    def api_remove_users_events(self, selectedEmail):
        request = json.loads(self.request.body)
        comment = request['comment']
        current_user = users.get_current_user()
        resultMessage = {}
        # users_email = google_directory.get_all_users_cached()

        users_email = [
            {"primaryEmail": "rich.test5@sherpatest.com"},
            {"primaryEmail": "richmond.gozarin@sherpatest.com"},
            {"primaryEmail": "zaldy.santos@sherpatest.com"},
            {"primaryEmail": "arvin.corpuz@sherpatest.com"}
        ]

        resultMessage['message'] = 'The app is in the process of removing %s in calendar events.' % selectedEmail
        self.context['data'] = resultMessage

        for user_email in users_email:
            deferred.defer(self.get_all_events, user_email['primaryEmail'], selectedEmail, comment, '', False, current_user.email())

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
                                    deferred.defer(self.filter_attendees, event, selectedEmail, user_email, comment, current_user_email)
                                else:
                                    if len(event['attendees']) > 1:
                                            action = 'Oops, %s is the owner in %s event with %s attendees.' % (selectedEmail, event['summary'], len(event['attendees']))
                                            insert_audit_log(action, 'Remove user in calendar events', current_user_email, selectedEmail, '%s' % event['summary'], None)

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
            if e.code == 401:
                pass

    @classmethod
    def filter_attendees(self, event, selectedEmail, user_email, comment, current_user_email):
        attendees_list = []

        for attendee in event['attendees']:
            if attendee['email'] != selectedEmail:
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
            'summary': event['summary'],
            'user_email': user_email,
            'body': params_body,
            'organizer': event['organizer']['email'],
            'selectedEmail': selectedEmail,
            'comment': comment
        }
        deferred.defer(self.update_calendar_events, update_event, False, current_user_email)

    @classmethod
    def filter_location(self, event, user_email, resource_params, current_user_email):
        attendees_list = []
        if 'location' in event and event['location'] == resource_params['old_resourceCommonName']:
            for attendee in event['attendees']:
                if attendee['displayName'] == resource_params['old_resourceCommonName']:
                    attendees_list.append(
                        {
                            'email': attendee['email'],
                            'displayName': resource_params['resourceCommonName']
                        }
                    )
                else:
                    attendees_list.append(
                        {
                            'email': attendee['email'],
                            'displayName': attendee['displayName']
                        }
                    )
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
                'body': params_body
            }
            deferred.defer(self.update_calendar_events, update_event, True, current_user_email)

    @classmethod
    def update_calendar_events(self, params, cal_resource=False, current_user_email=''):

        update_event = calendar_api.update_event(params['event_id'], params['user_email'], params['body'], True)

        if cal_resource == False:
            if params['selectedEmail']:
                cal_params = {
                    'action': '%s has been removed from events.' % params['selectedEmail'],
                    'invoked': 'user manager',
                    'app_user': current_user_email,
                    'target_resource': '%s calendar' % params['user_email'],
                    'target_event_altered': '%s' % params['body']['summary'],
                    'comment': params['comment']
                }
                if update_event is not None:
                    insert_audit_log(cal_params['action'], cal_params['invoked'],
                        cal_params['app_user'],
                        cal_params['target_resource'],
                        cal_params['target_event_altered'], cal_params['comment'])
                else:
                    if params['organizer'] == params['selectedEmail']:
                            DeprovisionedAccount.remove_owner_failed_notification(current_user_email, params['selectedEmail'], params['body']['summary'], 'update_calendar_events')

                    insert_audit_log('An attempt to remove %s from events.' % params['selectedEmail'],
                        cal_params['invoked'],
                        cal_params['app_user'],
                        cal_params['target_resource'],
                        cal_params['target_event_altered'], cal_params['comment'])
        else:
            if update_event is not None:
                cal_params = {
                    'action': 'Event %s resource has been updated.' % params['body']['summary'],
                    'invoked': 'resource manager',
                    'app_user': current_user_email,
                    'target_resource': '%s resource name' % params['body']['old_resourceName'],
                    'target_event_altered': '%s' % (params['body']['location'])
                }
                insert_audit_log(cal_params['action'], cal_params['invoked'],
                    cal_params['app_user'],
                    cal_params['target_resource'],
                    cal_params['target_event_altered'], '')

    @classmethod
    def delete_owner_event(self, event, selectedEmail, user_email, current_user_email):
        del_response = calendar_api.delete_event(event['id'], selectedEmail)
        if del_response is None:
            cal_params = {
                'action': '%s has been removed from calendar events.' % selectedEmail,
                'invoked': 'user manager',
                'app_user': current_user_email,
                'target_resource': '%s calendar' % user_email,
                'target_event_altered': '%s' % event['summary'],
                'comment': ''
            }
            insert_audit_log(cal_params['action'], cal_params['invoked'],
            cal_params['app_user'],
            cal_params['target_resource'],
            cal_params['target_event_altered'], cal_params['comment'])
        else:
            DeprovisionedAccount.remove_owner_failed_notification(current_user_email, selectedEmail, event['summary'], 'delete_owner_event')

    def find_resource(self, resource):
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
                    label = ['resourceId', 'resourceCommonName', 'resourceDescription', 'resourceType']
                    if (child.get('name') in label):
                        param[child.get('name')] = child.get('value')
                res.append(param)
            return nextpage, res
        else:
            param = {}
            for child in root.getchildren():
                label = ['resourceId', 'resourceCommonName', 'resourceDescription', 'resourceType']
                if (child.get('name') in label):
                    param[child.get('name')] = child.get('value')
            res.append(param)
            return res

    @route_with(template='/api/user_removals/deleting/users')
    def api_deleting_users(self):
        # google_directory.prime_caches()
        deleted_users = google_directory.get_all_deleted_users()
        # users_email = google_directory.get_all_users_cached()

        current_user = users.get_current_user()

        list_user_emails = [
            {"primaryEmail": "arvin.corpuz@sherpatest.com"},
            {"primaryEmail": "richmond.gozarin@sherpatest.com"},
            {"primaryEmail": "zaldy.santos@sherpatest.com"}
        ]

        ndbDeletedUserCount = DeprovisionedAccount.query().count()

        if ndbDeletedUserCount == 0:
            params = {'email': 'dummy@dummy.com', 'status': True}
            DeprovisionedAccount.create(params)

        ndbDeletedUserlist = DeprovisionedAccount.list_all()
        x_email = [x_email.email for x_email in ndbDeletedUserlist]

        for d_user in deleted_users:
            if d_user not in x_email and x_email != 'dummy@dummy.com':
                params = {'email': d_user, 'status': True}
                DeprovisionedAccount.create(params)
                deferred.defer(self.process_deleted_account, d_user, x_email, list_user_emails, current_user.email())
        return 'Started...'

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
