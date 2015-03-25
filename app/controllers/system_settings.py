from ferris import Controller, scaffold
from ferris.components.pagination import Pagination
from app.models.system_setting import SystemSetting


class SystemSettings(Controller):
    class Meta:
        prefixes = ('admin',)
        components = (scaffold.Scaffolding, Pagination)
        Model = SystemSetting
        pagination_limit = 10

    admin_add = scaffold.add
    admin_list = scaffold.list
    admin_edit = scaffold.edit
    admin_delete = scaffold.delete
