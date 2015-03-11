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
    def remove_owner_failed_notification(email, selectedEmail, event_summary):

        subject = "Arista Inc. - An attempt to remove an Owner of a Calendar Event has failed. "
        body = """
        Dear app user,
            This is to notify you that %s the owner of %s is trying to remove in calendar event.
        """ % (selectedEmail, event_summary)

        mail.send_mail("no-reply@" + APP_ID + ".appspotmail.com", email, subject, body)
