from ferris import Model, ndb


class EmailRecipient(Model):
    email = ndb.StringProperty()

    @classmethod
    def list_all(cls):
        return cls.query()
