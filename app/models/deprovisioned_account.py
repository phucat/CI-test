from ferris import BasicModel, ndb
from google.appengine.api import mail, app_identity
APP_ID = app_identity.get_application_id()


class DeprovisionedAccount(BasicModel):
    status = ndb.BooleanProperty()
    email = ndb.StringProperty()

    @classmethod
    def list_all(cls):
        return cls.query()

    @classmethod
    def create(cls, params):
        item = cls()
        item.populate(**params)
        item.put()
        return item

    @classmethod
    def remove(cls):
        ndb.delete_multi(
            DeprovisionedAccount.query().fetch(keys_only=True)
        )

    @staticmethod
    def remove_owner_failed_notification(email, cc, selectedEmail, event_summary, event_link):

        subject = "Arista Inc. - An attempt to remove an Owner of a Calendar Event has failed. "
        body = """
         Hello,

            This notice is to let you know that %s the owner of the %s has been removed from our systems.
            Please review this event and make different plans if necessary.

            %s

        Thanks,
        Arista IT
        """ % (selectedEmail, event_summary, event_link)

        mail.send_mail(sender="no-reply@" + APP_ID + ".appspotmail.com", to=email, cc=cc, subject=subject, body=body)


    @staticmethod
    def remove_owner_success_notification(email, selectedEmail, event_summary, event_link):

        subject = "Arista Inc. - Owner of a calendar event has been successfully removed."
        body = """
         Hello,

            This notice is to let you know that %s the owner of the %s has been removed from our systems.
            Please review this event and make different plans if necessary.

            %s

        Thanks,
        Arista IT
        """ % (selectedEmail, event_summary, event_link)

        mail.send_mail("no-reply@" + APP_ID + ".appspotmail.com", email, subject, body)


    @staticmethod
    def deprovision_success_notification(email, selectedEmail):

        subject = "Arista Inc. - %s has been successfully removed." % selectedEmail
        body = """
         Hello,

            This notice is to let you know that %s has been removed from our systems.

        Thanks,
        Arista IT
        """ % selectedEmail

        mail.send_mail("no-reply@" + APP_ID + ".appspotmail.com", email, subject, body)
