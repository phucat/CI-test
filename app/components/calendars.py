from ferris import settings
from google.appengine.api import memcache, app_identity
from plugins import calendar as calendar_api
# from gdata.calendar_resource.client import CalendarResourceClient
# from gdata.gauth import OAuth2TokenFromCredentials as CreateToken
# from app.etc import build_creds
# import xml.etree.ElementTree as ET
oauth_config = settings.get('oauth2_service_account')
APP_ID = app_identity.get_application_id()


class Calendars(object):

    def __init__(self, controller):
        self.controller = controller

    def list_resource_memcache(self):
        result = []
        page_token = None
        params = None

        while True:
            if page_token:
                params = page_token

            res, page_token = calendar_api.list_resources(page_token=params)

            for resource in res["items"]:
                result.append(dict(
                    (k, v) for k, v in resource.iteritems()
                ))

            if not page_token:
                break

        sortedResource = sorted(result, key=lambda resource: resource['resourceName'])

        memcache.add('resource_list', sortedResource, 600)
        return sortedResource

    # def find_resource(self, resource):
    #     res = []
    #     nextpage = ''
    #     root = ET.fromstring(resource)
    #     if root.tag == '{http://www.w3.org/2005/Atom}feed':
    #         for link in root.iterfind('{http://www.w3.org/2005/Atom}link'):
    #             if link.get('rel') == 'next':
    #                 nextpage = link.get('href')

    #         for entry in root.iterfind('{http://www.w3.org/2005/Atom}entry'):
    #             param = {}
    #             for child in entry.getchildren():
    #                 label = ['resourceId', 'resourceName', 'resourceDescription', 'resourceType', 'resourceEmail']
    #                 if (child.get('name') in label):
    #                     param[child.get('name')] = child.get('value')
    #             res.append(param)
    #         return nextpage, res
    #     else:
    #         param = {}
    #         for child in root.getchildren():
    #             label = ['resourceId', 'resourceName', 'resourceDescription', 'resourceType', 'resourceEmail']
    #             if (child.get('name') in label):
    #                 param[child.get('name')] = child.get('value')
    #         res.append(param)
    #         return res
