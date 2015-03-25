from ferris import Model, ndb


class SystemSetting(Model):
    email_group = ndb.StringProperty()

    @classmethod
    def list_all(cls):
        return cls.query()
