from ferris import Controller, route_with, settings
from plugins import calendar
# from app.models.calendar import Calendar
from google.appengine.api import users, urlfetch, app_identity
from gdata.calendar_resource.client import CalendarResourceClient
import re
import logging
import xml.etree.ElementTree as ET
from cStringIO import StringIO

urlfetch.set_default_fetch_deadline(60)
APP_ID = app_identity.get_application_id()
config = settings.get('admin_account')

class Calendars(Controller):
    class Meta:
        prefixes = ('api', 'admin',)
        View = 'json'

    @route_with(template='/api/calendars/resource', methods=['GET'])
    def api_calendar_resource(self):
        client = CalendarResourceClient(domain=config['domain'])
        client.ClientLogin(email=config['email'], password=config['password'], source=APP_ID)

        res = []
        calendar_resources = client.GetResourceFeed()
        root = ET.fromstring(calendar_resources)

        logging.info(root)

        for entry in root.iterfind('feed/entry'):
            #edited = entry.find('edited').text
            # name = entry.get('name')
            res.append({'attrib' : entry.attrib['name'], 'tag': entry.tag})

        self.context['data'] = root

    @route_with(template='/api/calendars/events', methods=['GET'])
    def api_calendar_events(self):
        feed = []
        user = users.get_current_user()
        feed = calendar.get_all_events(user.email())
        self.context['data'] = feed

    @route_with(template='/api/calendars/events/remove/<id>/<email>', methods=['GET'])
    def api_calendar_events_remove(self, id, email):
        response = calendar.delete_event(id, email)
        self.context['data'] = response

    @route_with(template='/api/calendars/update/<resource>', methods=['GET'])
    def api_resource_update(self,resource):
        client = CalendarResourceClient(domain=config['domain'])
        client.ClientLogin(email=config['email'], password=config['password'], source=APP_ID)

        updated_calendar_resource = client.UpdateResource(
            resource_id=resource.id,
            resource_common_name=resource.name,
            resource_description=resource.resource_description,
            resource_type=resource.type)

        return updated_calendar_resource
