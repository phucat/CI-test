from ferris import Controller, route_with, settings
from ferris.components.pagination import Pagination
from app.models.calendar import Calendar as calendar_model
from google.appengine.ext import deferred
from google.appengine.api import users, app_identity
from gdata.calendar_resource.client import CalendarResourceClient
import time
import json
import xml.etree.ElementTree as ET
from plugins import calendar as calendar_api, google_directory, rfc3339
import logging

APP_ID = app_identity.get_application_id()
config = settings.get('admin_account')


class Calendars(Controller):
    class Meta:
        prefixes = ('api', 'admin',)
        View = 'json'
        components = (Pagination,)
        Model = calendar_model
        pagination_limit = 10

    @route_with(template='/api/calendar/resource', methods=['GET'])
    def api_list_resource(self):
        data = {}
        client = CalendarResourceClient(domain=config['domain'])
        client.ClientLogin(email=config['email'], password=config['password'], source=APP_ID)

        calendar_resources = str(client.GetResourceFeed())
        res = self.find_resource(calendar_resources)

        #sortedResource = sorted(res, key=lambda resource: resource['resourceCommonName'])
        data['items'] = res #self.components.pagination.paginate(res)
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

        resultMessage['response'] = calendar_resource
        self.context['data'] = resultMessage

    @route_with(template='/api/calendar/update', methods=['POST'])
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

            self.process_users_location(resource)
            res = self.find_resource(str(updated_calendar_resource))

            resultMessage['message'] = 'Calendar Resource has been updated.'
            resultMessage['items'] = res
            self.context['data'] = resultMessage
        except Exception, e:
            logging.error(e)
            self.context['data'] = e

    @route_with(template='/api/calendar/events/<email>', methods=['GET'])
    def api_calendar_events(self, email):
        feed = []
        feed = calendar_api.get_all_events(email)
        self.context['data'] = feed

    def process_users_location(self,resource):
        # c_user = users.get_current_user()
        # users_email = google_directory.get_all_users_cached()

        users_email = [
            {"primaryEmail": "arvin.corpuz@sherpatest.com"},
            {"primaryEmail": "abby.vaillancourt@sherpatest.com"},
            {"primaryEmail": "aaron.erickson@sherpatest.com"},
            {"primaryEmail": "richmond.gozarin@sherpatest.com"}
        ]

        for user_email in users_email:
            deferred.defer(self.get_all_events, user_email['primaryEmail'], '', '', resource, True)
            logging.info("Deffered Started!")

    @route_with('/api/calendar/remove_user/events/<selectedEmail>', methods=['POST'])
    def api_users_events(self,selectedEmail):
        logging.info("Deffered Started!")
        request = json.loads(self.request.body)
        comment = request['comment']
        #resultMessage = {}
        c_user = users.get_current_user()
        # users_email = google_directory.get_all_users_cached()

        users_email = [
            {"primaryEmail": "arvin.corpuz@sherpatest.com"},
            {"primaryEmail": "abby.vaillancourt@sherpatest.com"},
            {"primaryEmail": "aaron.erickson@sherpatest.com"},
            {"primaryEmail": "richmond.gozarin@sherpatest.com"}
        ]

        cal_params = {
            'action': 'an attempt to remove %s from all events.' % selectedEmail, 'how_the_action_invoked': 'remove user',
            'app_user_invoked_action': c_user.email(),
            'target_resource' : 'calendar events', 'target_event_altered' : 'future events', 'comment': comment
        }
        calendar_model.create(cal_params)

        for user_email in users_email:
            if user_email['primaryEmail'] != selectedEmail:
                #resultMessage['response'] = self.get_all_events(user_email['primaryEmail'], selectedEmail, comment, '')
                deferred.defer(self.get_all_events, user_email['primaryEmail'], selectedEmail, comment, '')
        #self.context['data'] = resultMessage

    def get_all_events(self, user_email, selectedEmail, comment, resource_params, resource=False):
        events = calendar_api.get_all_events(user_email)
        current_date = time.time()

        if events is not None:
            for event in events['items']:
                startDate = rfc3339.strtotimestamp(event['start']['dateTime'])
                if startDate >= current_date and 'attendees' in event:
                    if resource == False:
                        self.filter_attendees(event, selectedEmail, user_email, comment)
                    else:
                        self.filter_location(event,user_email, resource_params)

    def filter_attendees(self,event, selectedEmail, user_email, comment):
        attendees_list = []
        for attendee in event['attendees']:
            if attendee['email'] != selectedEmail:
                attendees_list.append({'email': attendee['email']})
        params_body = {
            'attendees': attendees_list,
            'reminders': {'overrides': [{'minutes': 15, 'method': 'popup'}],'useDefault': 'false' },
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
        self.update_calendar_events(update_event)
        #deferred.defer(self.update_calendar_events, update_event)

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
                'reminders': {'overrides': [{'minutes': 15, 'method': 'popup'}],'useDefault': 'false' },
                'start': event['start'],
                'end': event['end'],
                'summary': event['summary']
            }

            update_event = {
                'event_id': event['id'],
                'user_email': user_email,
                'body': params_body
            }

            self.update_calendar_events(update_event, True)
            #deferred.defer(self.update_calendar_events, update_event)

    def update_calendar_events(self, params, cal_resource=False):
        c_user = users.get_current_user()
        update_event = calendar_api.update_event(params['event_id'], params['user_email'], params['body'])

        if cal_resource == False:
            cal_params = {
                'action': '%s has been removed from all events.' % params['selectedEmail'],
                'how_the_action_invoked': 'user manager',
                'app_user_invoked_action': c_user.email(),
                'target_resource' : '%s calendar' % params['user_email'],
                'target_event_altered' : '%s - %s' % (params['event_id'], params['body']['summary']),
                'comment': params['comment']
            }
        else:
            cal_params = {
                'action': 'Event %s resource has been updated.' % params['body']['summary'],
                'how_the_action_invoked': 'resource manager',
                'app_user_invoked_action': c_user.email(),
                'target_resource' : '%s resource name' % params['body']['old_resourceName'],
                'target_event_altered' : '%s' % (params['body']['location'])
            }
        calendar_model.create(cal_params)

        return update_event

    @route_with(template='/api/calendar/users', methods=['GET'])
    def get_all_users(self):
        self.context['data'] = google_directory.get_all_users_cached()

    def find_resource(self, resource):
        res = []
        root = ET.fromstring(resource)
        if root.tag == '{http://www.w3.org/2005/Atom}feed':
            for entry in root.iterfind('{http://www.w3.org/2005/Atom}entry'):
                param = {}
                for child in entry.getchildren():
                    label = ['resourceId', 'resourceCommonName', 'resourceDescription', 'resourceType']
                    if (child.get('name') in label):
                        param[child.get('name')] = child.get('value')
                res.append(param)
        else:
            param = {}
            for child in root.getchildren():
                label = ['resourceId', 'resourceCommonName', 'resourceDescription', 'resourceType']
                if (child.get('name') in label):
                    param[child.get('name')] = child.get('value')
            res.append(param)
        return res
