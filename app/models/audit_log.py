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
