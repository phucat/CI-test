from ferris import Controller, scaffold
from ferris.components.pagination import Pagination
from app.models.mailing_list import MailingList


class DailyAndWeeklyEmailRecipients(Controller):
    class Meta:
        prefixes = ('admin',)
        components = (scaffold.Scaffolding, Pagination)
        Model = MailingList
        pagination_limit = 10

    admin_add = scaffold.add
    admin_list = scaffold.list
    admin_edit = scaffold.edit
    admin_delete = scaffold.delete
