from ferris import Controller, route_with
import Cookie



class AppLogut(Controller):

    @route_with(template='/api/app_logout', methods=['GET'])
    def api_app_logout(self):
    # On the production instance, we just remove the session cookie, because
        # redirecting users.create_logout_url(...) would log out of all Google
        # (e.g. Gmail, Google Calendar).
        #
        # It seems that AppEngine is setting the ACSID cookie for http:// ,
        # and the SACSID cookie for https:// . We just unset both below.
        cookie = Cookie.SimpleCookie()
        cookie['ACSID'] = ''
        cookie['ACSID']['expires'] = -86400  # In the past, a day ago.
        self.response.headers.add_header(*cookie.output().split(': ', 1))
        cookie = Cookie.SimpleCookie()
        cookie['SACSID'] = ''
        cookie['SACSID']['expires'] = -86400
        self.response.headers.add_header(*cookie.output().split(': ', 1))
        self.redirect('/')

        return
