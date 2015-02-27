from ferris.tests.lib import FerrisTestCase
from ferris import settings, messages

try:
    import test_settings
except ImportError as e:
    raise ImportError("You must create a test_settings.py file with a service account before testing this plugin.")

from plugins import google_directory
from plugins.google_directory.controllers.google_directory import GoogleDirectory
from google.appengine.api import users
from google.appengine.ext import ndb


class DirectoryTests(FerrisTestCase):

    def test_sanity(self):
        print(settings.get('oauth2_service_account'))

    def test_backend_methods(self):
        all_users = google_directory.get_all_users_cached()
        assert len(all_users)

        all_groups = google_directory.get_all_groups_cached()
        assert len(all_groups)

        user = google_directory.get_user_by_email_cached('jonathan.parrott@sherpademo.com')
        assert user['primaryEmail'] == 'jonathan.parrott@sherpademo.com'

        group = google_directory.get_group_by_email_cached('_underscore@sherpademo.com')
        assert group['email'] == '_underscore@sherpademo.com'

        members = google_directory.get_group_members_cached('_underscore@sherpademo.com')
        assert len(members)

        groups = google_directory.get_all_groups_cached('jonathan.parrott@sherpademo.com')
        assert len(groups)

        info = google_directory.get_user_info_cached('jonathan.parrott@sherpademo.com')
        assert info

    def test_api_methods(self):
        self.loginUser('jonathan.parrott@sherpademo.com')
        self.addController(GoogleDirectory)

        r = self.testapp.get('/api/google/directory/users/jonathan.parrott@sherpademo.com')
        assert r.json['primaryEmail'] == 'jonathan.parrott@sherpademo.com'

        r = self.testapp.get('/api/google/directory/users/me')
        assert r.json['primaryEmail'] == 'jonathan.parrott@sherpademo.com'

        r = self.testapp.get('/api/google/directory/users')
        assert len(r.json)

        r = self.testapp.get('/api/google/directory/users?q=jonathan parrott')
        assert len(r.json)
        assert r.json[0]['primaryEmail'] == 'jonathan.parrott@sherpademo.com'

        r = self.testapp.get('/api/google/directory?q=jonathan parrott')
        assert len(r.json)
        assert r.json[0]['primaryEmail'] == 'jonathan.parrott@sherpademo.com'

        r = self.testapp.get('/api/google/directory?q=underscore')
        assert len(r.json)
        assert r.json[0]['email'] == '_underscore@sherpademo.com'

        r = self.testapp.get('/api/google/directory/groups')
        assert len(r.json)

        r = self.testapp.get('/api/google/directory/groups/jonathan.parrott@sherpademo.com')
        assert len(r.json)

        r = self.testapp.get('/api/google/directory/groups/me')
        assert len(r.json)

        r = self.testapp.get('/api/google/directory/members/_underscore@sherpademo.com')
        assert len(r.json)

    def test_monkey(self):
        user = users.User(email='jonathan.parrott@sherpademo.com')
        assert user.domain_info

        user = users.User(email='jonathan.parrott@cloudsherpas.com')
        assert not user.domain_info

        class DummyModel(ndb.Model):
            user = ndb.UserProperty()

        DummyMessage = messages.model_message(DummyModel)
        instance = DummyModel(user=users.User(email='jonathan.parrott@sherpademo.com'))
        message = messages.to_message(instance, DummyMessage)

        assert message.user.name == 'Jonathan Parrott'
        assert len(message.user.groups)


        instance = DummyModel(user=users.User(email='jonathan.parrott@cloudsherpas.com'))
        message = messages.to_message(instance, DummyMessage)

        assert not message.user.name
        assert not message.user.groups
