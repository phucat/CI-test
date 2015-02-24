from ferris import Model, ndb


class Calendar(Model):
    resourceId = ndb.StringProperty()


    @classmethod
    def list_all(cls):
        return cls.query()
