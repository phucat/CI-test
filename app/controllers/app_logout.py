from ferris import Controller, route_with
from google.appengine.api import users


class AppLogout(Controller):
    class Meta:
        prefixes = ('api',)

    @route_with(template='/api/app_logout', methods=['GET'])
    def api_app_logout(self):
        logoutURL = users.create_logout_url('/')
        return self.redirect(logoutURL)
