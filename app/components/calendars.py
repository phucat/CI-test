from ferris import settings
from google.appengine.api import memcache, app_identity
from gdata.calendar_resource.client import CalendarResourceClient
import xml.etree.ElementTree as ET
config = settings.get('admin_account')
APP_ID = app_identity.get_application_id()


class Calendars(object):

    def __init__(self, controller):
        self.controller = controller

    def list_resource_memcache(self):
        params = {}
        result = []
        nextpage = None
        client = CalendarResourceClient(domain=config['domain'])
        client.ClientLogin(email=config['email'], password=config['password'], source=APP_ID)

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
