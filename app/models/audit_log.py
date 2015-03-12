from ferris import BasicModel, ndb
from google.appengine.api import mail, app_identity
APP_ID = app_identity.get_application_id()


class AuditLog(BasicModel):
    action = ndb.StringProperty()
    how_the_action_invoked = ndb.StringProperty()
    app_user_invoked_action = ndb.StringProperty()
    target_resource = ndb.StringProperty()
    target_event_altered = ndb.StringProperty()
    comment = ndb.StringProperty()

    @classmethod
    def list_all(cls):
        return cls.query()

    @classmethod
    def fetch_date_range(cls, fromdate, todate):
        return cls.query(cls.created >= fromdate, cls.created <= todate).fetch()

    @classmethod
    def create(cls, params):
        item = cls()
        item.populate(**params)
        item.put()
        return item

    @classmethod
    def remove(cls):
        ndb.delete_multi(
            AuditLog.query().fetch(keys_only=True)
        )


    @staticmethod
    def daily_notification_on_major_actions(email, filename, out):

        subject = "Arista Inc. - Daily Notification"
        body = """
        Dear app user,

            This is to notify you on major actions performed yesterday.
        """

        mail.send_mail(
            "no-reply@" + APP_ID + ".appspotmail.com",
            email,
            subject,
            body,
            attachments=[(filename, out)]
        )

    @staticmethod
    def weekly_notification_on_major_actions(email, filename, out):

        subject = "Arista Inc. - Weekly Notification"
        body = """
        Dear app user,

            This is to notify you on major actions performed last week.
        """

        mail.send_mail(
            "no-reply@" + APP_ID + ".appspotmail.com",
            email,
            subject,
            body,
            attachments=[(filename, out)]
        )


    @staticmethod
    def attendees_update_notification(email, selectedEmail, event_summary):

        subject = "Arista Inc. - Update on %s's Attendees."
        body = """
        Hello,

            %s has been removed in %s.

            Thank You.
        """ % (event_summary, selectedEmail, event_summary)

        mail.send_mail("no-reply@" + APP_ID + ".appspotmail.com", email, subject, body)

    @staticmethod
    def new_resource_notification(email, name, resource):

        subject = "Arista Inc. - New Calendar Resource has been created."
        body = """
        Hello %s,

            A New Calendar Resource has been created.

            Resource Id: %s
            Resource Name: %s
            Resource Description: %s
            Resource Type: %s

            Thank You.
        """ % (name, resource['resourceId'], resource['resourceCommonName'], resource['resourceDescription'], resource['resourceType'])

        mail.send_mail("no-reply@" + APP_ID + ".appspotmail.com", email, subject, body)

    @staticmethod
    def update_resource_notification(email, name, event_link):

        subject = "Arista Inc. - Update on Calendar Resource. "
        body = """
        Hello %s,

            A Calendar Event you are a participant on has a Resource that has been changed. Please use the link below to review this Event.

            %s

        Thank You.
        """ % (name, event_link)

        mail.send_mail("no-reply@" + APP_ID + ".appspotmail.com", email, subject, body)
