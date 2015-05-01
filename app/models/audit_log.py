import logging
from ferris import BasicModel, ndb, settings
from app.models.mailing_list import MailingList
from google.appengine.api import mail, app_identity
APP_ID = app_identity.get_application_id()
oauth_config = settings.get('oauth2_service_account')


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
        return cls.query().filter(ndb.AND(cls.created >= fromdate, cls.created < todate))

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
            oauth_config['default_user'],
            email,
            subject,
            body
        )

    @staticmethod
    def daily_notification_on_major_actions(filename, out):

        mailingList = MailingList.list_all()
        emails = [mailing.email for mailing in mailingList]

        subject = "Arista Inc. - Daily Notification"
        body = """
        Dear app user,

            This is to notify you on major actions performed today.
        """

        mail.send_mail(
            sender=oauth_config['default_user'],
            to=emails,
            subject=subject,
            body=body,
            attachments=[(filename, out)]
        )

    @staticmethod
    def weekly_notification_on_major_actions(filename, out):

        mailingList = MailingList.list_all()
        emails = [mailing.email for mailing in mailingList]

        subject = "Arista Inc. - Weekly Notification"
        body = """
        Dear app user,

            This is to notify you on major actions performed this week.
        """

        mail.send_mail(
            sender=oauth_config['default_user'],
            to=emails,
            subject=subject,
            body=body,
            attachments=[(filename, out)]
        )


    # @staticmethod
    # def attendees_update_notification(email, selectedEmail, event_summary):
    #     subject = "Arista Inc. - Calendar event update on %s." % event_summary
    #     body = """
    #     Hello,
    #
    #         "%s" has been removed in "%s" event.
    #
    #         Thank You.
    #     """ % (selectedEmail, event_summary)
    #
    #     mail.send_mail(oauth_config['default_user'], email, subject, body)

    # @staticmethod
    # def new_resource_notification(email, name, resource):
    #
    #     subject = "Arista Inc. - New Calendar Resource has been created."
    #     body = """
    #     Hello %s,
    #
    #         A New Calendar Resource has been created.
    #
    #         Resource Id: %s
    #         Resource Name: %s
    #         Resource Type: %s
    #         Resource Description: %s
    #
    #         Thank You.
    #     """ % (name, resource['resourceId'], resource['resourceCommonName'], resource['resourceType'], resource['resourceDescription'])
    #
    #     mail.send_mail(oauth_config['default_user'], email, subject, body)

    @staticmethod
    def update_resource_notification(email, event_name, event_link, resource, datetime, attendees_list_display_names):
        # Example of datetime: 2015-05-01T19:30:00Z
        logging.debug('test01')
        date = datetime[8:-10] + "-" + datetime[5:-13] + "-" + datetime[:-16]
        time = datetime[11:-1]
        datetime_f = date + " " + time
        logging.debug(datetime_f)


        # attendees_list_display_names = ["Ender Wiggin", "Mazer Rackham", "Bean", "Valentine Wiggin", "Petra Arkanian",
        #     "Peter Wiggin", "Hive Queen", "Jane", "Theresa Wiggin"]
        attendee_list = ', '.join(map(str, attendees_list_display_names))
        logging.debug(attendee_list)

        subject = "Arista Inc. - A Resource has been updated on one of your Events. "

        body = """
        Hello,

            The resource "%s" has been changed on the following event:
            %s
            %s
            %s
            Link: %s

        Thank You.
        """ % (resource['resourceCommonName'], datetime_f, event_name, attendee_list, event_link)

        logging.debug('test01')
        mail.send_mail(oauth_config['default_user'], email, subject, body)

