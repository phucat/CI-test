from ferris import Controller, messages, route_with, settings
from app.models.calendar import Calendar as calendar_model
from google.appengine.ext import deferred
from google.appengine.api import users, app_identity, urlfetch
from gdata.calendar_resource.client import CalendarResourceClient
import json
import urllib
import time
import xml.etree.ElementTree as ET
from plugins import calendar as calendar_api, google_directory, rfc3339
import logging, urllib2

APP_ID = app_identity.get_application_id()
urlfetch.set_default_fetch_deadline(60)
config = settings.get('admin_account')


class Calendars(Controller):
    class Meta:
        prefixes = ('api',)
        View = 'json'

    @route_with(template='/api/calendar/events/<email>', methods=['GET'])
    def api_calendar_events(self, email):
        feed = []
        feed = calendar_api.get_all_events(email)
        self.context['data'] = feed

    @route_with(template='/api/calendar/users', methods=['GET'])
    def api_get_all_users(self):
        self.context['data'] = google_directory.get_all_users_cached()

    @route_with(template='/api/calendar/resource/<feed>', methods=['GET'])
    def api_list_resource(self, feed):
        data = {}
        client = CalendarResourceClient(domain=config['domain'])
        client.ClientLogin(email=config['email'], password=config['password'], source=APP_ID)

        if feed == 'feed':
            calendar_resources = str(client.GetResourceFeed())
        else:
            uri = urllib.unquote(feed).decode('utf8')
            calendar_resources = str(client.GetResourceFeed(uri=uri))
            data['previous'] = 'feed'

        nextpage, res = self.find_resource(calendar_resources)
        sortedResource = sorted(res, key=lambda resource: resource['resourceCommonName'])
        data['items'] = sortedResource
        data['next'] = nextpage

        self.context['data'] = data

    @route_with(template='/api/calendar/resource/create', methods=['POST'])
    def api_create_resource(self):
        resultMessage = {}
        user = users.get_current_user()
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
        self.insert_audit_log(action, 'add new resource', user.email(), resource['resourceCommonName'], None, None)

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

        users_email = [
            {"primaryEmail": "abe@sherpatest.com"},
            {"primaryEmail": "arvin.corpuz@sherpatest.com"},
            {"primaryEmail": "abby.vaillancourt@sherpatest.com"},
            {"primaryEmail": "aaron.erickson@sherpatest.com"},
            {"primaryEmail": "kristin.abbott@sherpatest.com"},
            {"primaryEmail": "richmond.gozarin@sherpatest.com"}
        ]

        for user_email in users_email:
            #self.get_all_events(user_email['primaryEmail'], '', '', resource, True)
            deferred.defer(self.get_all_events, user_email['primaryEmail'], '', '', resource, True)


    @route_with('/api/calendar/remove_user/events/<selectedEmail>', methods=['POST'])
    def api_remove_users_events(self, selectedEmail):
        request = json.loads(self.request.body)
        comment = request['comment']
        resultMessage = {}
        # users_email = google_directory.get_all_users_cached()

        users_email = [
            {"primaryEmail": "arvin.corpuz@sherpatest.com"},
            {"primaryEmail": "abe@sherpatest.com"},
            {"primaryEmail": "abby.vaillancourt@sherpatest.com"},
            {"primaryEmail": "aaron.erickson@sherpatest.com"},
            {"primaryEmail": "kristin.abbott@sherpatest.com"},
            {"primaryEmail": "richmond.gozarin@sherpatest.com"}
        ]

        resultMessage['message'] = 'The app is in the process of removing %s in calendar events.' % selectedEmail
        self.context['data'] = resultMessage

        for user_email in users_email:
            if user_email['primaryEmail'] != selectedEmail:
                #self.get_all_events(user_email['primaryEmail'], selectedEmail, comment, '' ,resource=False)
                deferred.defer(self.get_all_events, user_email['primaryEmail'], selectedEmail, comment, '', resource=False)

    @classmethod
    def get_all_events(self, user_email, selectedEmail, comment, resource_params, resource=False):
        try:
            events = calendar_api.get_all_events(user_email)
            current_date = time.time()
            if events is not None:
                for event in events['items']:
                    startDate = rfc3339.strtotimestamp(event['start']['dateTime'])
                    if startDate >= current_date and 'attendees' in event:
                        if resource == False:
                            #self.filter_attendees(event, selectedEmail, user_email, comment)
                            deferred.defer(self.filter_attendees, event, selectedEmail, user_email, comment)
                        else:
                            self.filter_location(event, user_email, resource_params)
                            #deferred.defer(self.filter_location, event, user_email, resource_params)

        except urllib2.HTTPError as e:
            logging.info('get_all_events: HTTPerror')
            logging.info(e.code)
            if e.code == 401:
                pass

    @classmethod
    def filter_attendees(self, event, selectedEmail, user_email, comment):
        attendees_list = []
        user = users.get_current_user()
        if event['creator']['email'] == selectedEmail and len(event['attendees']) > 0:
                action = 'Oops, %s is owner in %s event.' % (selectedEmail, event['summary'])
                self.insert_audit_log(action, 'Remove user manager', user.email(), selectedEmail, '%s' % event['summary'], None)
                pass
        else:
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
                'selectedEmail': selectedEmail,
                'comment': comment
            }
            #self.update_calendar_events(update_event, False)
            deferred.defer(self.update_calendar_events, update_event, False)

    @classmethod
    def filter_location(self, event, user_email, resource_params):
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
            #self.update_calendar_events(update_event, True)
            deferred.defer(self.update_calendar_events, update_event, True)

    @classmethod
    def update_calendar_events(self, params, cal_resource=False):
        c_user = users.get_current_user()
        update_event = calendar_api.update_event(params['event_id'], params['user_email'], params['body'], True)

        if cal_resource == False:
            cal_params = {
                'action': '%s has been removed from events.' % params['selectedEmail'],
                'invoked': 'user manager',
                'app_user': c_user.email(),
                'target_resource': '%s calendar' % params['user_email'],
                'target_event_altered': '%s' % params['body']['summary'],
                'comment': params['comment']
            }
            if update_event is not None:
                self.insert_audit_log(cal_params['action'], cal_params['invoked'],
                    cal_params['app_user'],
                    cal_params['target_resource'],
                    cal_params['target_event_altered'], cal_params['comment'])
            else:
                self.insert_audit_log('An attempt to remove %s from events.' % params['selectedEmail'],
                    cal_params['invoked'],
                    cal_params['app_user'],
                    cal_params['target_resource'],
                    cal_params['target_event_altered'], cal_params['comment'])
        else:
            if update_event is not None:
                cal_params = {
                    'action': 'Event %s resource has been updated.' % params['body']['summary'],
                    'invoked': 'resource manager',
                    'app_user': c_user.email(),
                    'target_resource': '%s resource name' % params['body']['old_resourceName'],
                    'target_event_altered': '%s' % (params['body']['location'])
                }
                self.insert_audit_log(cal_params['action'], cal_params['invoked'],
                    cal_params['app_user'],
                    cal_params['target_resource'],
                    cal_params['target_event_altered'], '')

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

    def insert_audit_log(self, action, invoked, app_user, target_resource, target_event_altered, comment=None):
        cal_params = {
            'action': action,
            'how_the_action_invoked': invoked,
            'app_user_invoked_action': app_user,
            'target_resource': target_resource,
            'target_event_altered': target_event_altered,
            'comment': comment
        }
        calendar_model.create(cal_params)
