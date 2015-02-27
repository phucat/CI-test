from . import client
from google.appengine.api.users import User as AppengineUser
from ferris.core import template
import logging

# Register User Formatter

template.formatters[AppengineUser] = lambda x: x.domain_info['name']['fullName'] if x.domain_info and x.domain_info.get('name') else unicode(x)


# Monkey Patch App Engine users

def _get_info(self):
    if not hasattr(self, '_domain_info'):
        setattr(self, '_domain_info', None)
    if self._domain_info is None:
        try:
            self._domain_info = client.get_user_info_cached(self.email())
        except Exception as e:
            logging.error("Error occured while fetching user for %s info: %s" % (self.email(), e))
            self._domain_info = False
    return self._domain_info

setattr(AppengineUser, 'domain_info', property(_get_info))


# Monkey patch json

def _to_json(self):
    output = {'__class__': 'User'}
    methods = ['nickname', 'email', 'user_id']
    for method in methods:
        output[method] = getattr(self, method)()

    info = self.domain_info
    if info:
        output['name'] = info['name']['fullName']
        output['org_unit'] = info['orgUnitPath']
        output['groups'] = [
            {'name': x['name'], 'email': x['email']} for x in info['groups']
        ]

    return output

setattr(AppengineUser, '__json__', _to_json)


# Monkey Patch protopigeon

from protorpc import messages
from protopigeon import converters


class GroupMessage(messages.Message):
    name = messages.StringField(1)
    email = messages.StringField(2)

class ExtendedUserMessage(messages.Message):
    email = messages.StringField(1)
    user_id = messages.StringField(2)
    nickname = messages.StringField(3)
    name = messages.StringField(4)
    org_unit = messages.StringField(5)
    groups = messages.MessageField(GroupMessage, 6, repeated=True)


class ExtendedUserConverter(converters.UserConverter):
    @staticmethod
    def to_message(Mode, property, field, value):
        info = value.domain_info
        return ExtendedUserMessage(
            email=value.email(),
            user_id=value.user_id(),
            nickname=value.nickname(),
            name=info['name']['fullName'] if info else None,
            org_unit=info['orgUnitPath'] if info else None,
            groups=[
                GroupMessage(email=x['email'], name=x['name']) for x in info['groups']
                ] if info else [])

    @staticmethod
    def to_model(Message, property, field, value):
        from google.appengine.api import users
        if isinstance(value, basestring):
            return users.User(email=value)
        elif isinstance(value, ExtendedUserMessage) and value.email:
            return users.User(email=value.email)

    @staticmethod
    def to_field(Model, property, count):
        return messages.MessageField(ExtendedUserMessage, count, repeated=property._repeated)


converters.converters['UserProperty'] = ExtendedUserConverter
