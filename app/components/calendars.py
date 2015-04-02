from ferris import settings
from google.appengine.api import memcache, app_identity
from gdata.calendar_resource.client import CalendarResourceClient
from oauth2client.client import SignedJwtAssertionCredentials
import xml.etree.ElementTree as ET
config = settings.get('admin_account')
oauth_config = settings.get('oauth2_service_account')
APP_ID = app_identity.get_application_id()


class Calendars(object):

    def __init__(self, controller):
        self.controller = controller

    def list_resource_memcache(self):
        params = {}
        result = []
        nextpage = None

        scope = [
            "https://www.googleapis.com/auth/calendar",
            "https://www.googleapis.com/auth/admin.directory.user",
            "https://apps-apis.google.com/a/feeds/calendar/resource/#readonly",
            "https://www.googleapis.com/auth/admin.directory.group.readonly",
            "https://www.googleapis.com/auth/admin.directory.orgunit.readonly",
        ]

        # Impersonate Admin user
        creds = SignedJwtAssertionCredentials(
            service_account_name=oauth_config['client_email'],
            private_key=oauth_config['private_key'],
            scope=scope,
            sub=config['email'])

        client = CalendarResourceClient(domain=config['domain'], auth_token=creds)

        #client = CalendarResourceClient(domain=config['domain'])
        #client.ClientLogin(email=config['email'], password=config['password'], source=APP_ID)

        while True:
            if nextpage:
                params['uri'] = nextpage

            calendar_resources = str(client.GetResourceFeed(**params))
            nextpage, res = self.find_resource(calendar_resources)

            for resource in res:
                result.append(dict(
                    (k, v) for k, v in resource.iteritems()
                ))

            if not nextpage:
                break

        sortedResource = sorted(result, key=lambda resource: resource['resourceCommonName'])
        data = memcache.get('resource_list')
        if data is not None:
            return data
        else:
            memcache.add('resource_list', sortedResource, 600)
            data = memcache.get('resource_list')
            return data

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
