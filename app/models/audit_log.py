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

        return cls.query(
            ndb.AND(
                cls.created >= fromdate,
                cls.created < todate
            )

        ).fetch()

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
    def email_fluff(email):

        subject = "Arista Inc. - Test Notification"
        body = """
        Dear app user,

            Email Test only
        """

        mail.send_mail(
            "no-reply@" + APP_ID + ".appspotmail.com",
            email,
            subject,
            body
        )

    @staticmethod
    def daily_notification_on_major_actions(email, filename, out):

        subject = "Arista Inc. - Daily Notification"
        body = """
        Dear app user,

            This is to notify you on major actions performed today.
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

            This is to notify you on major actions performed this week.
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
        subject = "Arista Inc. - Calendar event update on %s." % event_summary
        body = """
        Hello,

            %s has been removed in %s.

            Thank You.
        """ % (selectedEmail, event_summary)

        mail.send_mail("no-reply@" + APP_ID + ".appspotmail.com", email, subject, body)

    @staticmethod
    def new_resource_notification(email, name, resource):

        subject = "Arista Inc. - New Calendar Resource has been created."
        body = """
        Hello %s,

            A New Calendar Resource has been created.

            Resource Id: %s
            Resource Name: %s
            Resource Type: %s
            Resource Description: %s

            Thank You.
        """ % (name, resource['resourceId'], resource['resourceCommonName'], resource['resourceType'], resource['resourceDescription'])

        mail.send_mail("no-reply@" + APP_ID + ".appspotmail.com", email, subject, body)

    @staticmethod
    def update_resource_notification(email, name, event_link, resource):

        subject = "Arista Inc. - Update on Calendar Resource. "
        body = """
        Hello %s,

            A Calendar Event you are a participant on has a Resource that has been changed. Please use the link below to review this Event.

            Resource ID: %s
            Resource Name: %s
            Resource Type: %s
            Resource Description: %s

            %s

        Thank You.
        """ % (name, resource['updates']['resourceId'], resource['resourceCommonName'], resource['updates']['resourceType'], resource['updates']['resourceDescription'], event_link)

        mail.send_mail("no-reply@" + APP_ID + ".appspotmail.com", email, subject, body)
