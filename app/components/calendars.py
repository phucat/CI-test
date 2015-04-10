from ferris import settings
from google.appengine.api import memcache, app_identity
from gdata.calendar_resource.client import CalendarResourceClient
from gdata.gauth import OAuth2TokenFromCredentials as CreateToken
<<<<<<< HEAD
import xml.etree.ElementTree as ET
from app.etc import build_creds
config = settings.get('admin_account')
=======
from app.etc import build_creds
import xml.etree.ElementTree as ET
>>>>>>> e7e3110a7bcb7750f46f94b6fe957edf64bc3e27
oauth_config = settings.get('oauth2_service_account')
APP_ID = app_identity.get_application_id()


class Calendars(object):

    def __init__(self, controller):
        self.controller = controller

    def list_resource_memcache(self):
        params = {}
        result = []
        nextpage = None
<<<<<<< HEAD
        #client = CalendarResourceClient(domain=config['domain'])
        #client.ClientLogin(email=config['email'], password=config['password'], source=APP_ID)

        creds = build_creds.build_credentials(
            scope=[
                "https://apps-apis.google.com/a/feeds/calendar/resource/"
            ],
            service_account_name=oauth_config['client_email'],
            private_key=oauth_config['private_key'],
            user=config['email']
        )
        auth2token = CreateToken(creds)
        client = CalendarResourceClient(domain=config['domain'])
        auth2token.authorize(client)
=======
        client = CalendarResourceClient(domain=oauth_config['domain'])
        client.ClientLogin(email=oauth_config['default_user'], password=oauth_config['password'], source=APP_ID)

        # creds = build_creds.build_credentials(
        #     scope=[
        #         "https://apps-apis.google.com/a/feeds/calendar/resource/"
        #     ],
        #     service_account_name=oauth_config['client_email'],
        #     private_key=oauth_config['private_key'],
        #     user=oauth_config['default_user']
        # )
        # auth2token = CreateToken(creds)
        # client = CalendarResourceClient(domain=oauth_config['domain'])
        # auth2token.authorize(client)
>>>>>>> e7e3110a7bcb7750f46f94b6fe957edf64bc3e27

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

        memcache.add('resource_list', sortedResource, 600)
        return sortedResource

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
