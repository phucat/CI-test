from ferris import Controller, route_with
from google.appengine.api import users


class Main(Controller):

    @route_with(template='/')
    def show(self):
        user = users.get_current_user()
        self.session['current_user'] = user.email()
        self.meta.view.template_name = 'angular/index.html'
