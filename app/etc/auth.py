import os, logging
from google.appengine.api import users
from google.appengine.api import app_identity
from google.appengine.ext import ndb
import json


def require_domain(controller):
    if not controller.__class__.__name__ in ("AuditLogs", "Calendars"):
        if not controller.user:
            return False, "You must be logged in"

        user = users.get_current_user().email()
        domain = user.split('@').pop()

        #logging.info("USER =====>" + str(user))

        # Test domains

        if app_identity.get_application_id() in ('arista-calendar-01', 'cs-arista-calendar-qa') and domain not in (
            'cloudsherpas.com',
            'arista.com'
            ):
            return False, "Your domain does not have access to this application"

        return True
    else:
        return True
