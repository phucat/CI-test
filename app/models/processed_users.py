from ferris import Model, ndb


class ProcessedUsers(Model):
    eventId = ndb.StringProperty()
    resource = ndb.StringProperty()

    @classmethod
    def list_all(cls):
        return cls.query()

    @classmethod
    def create(cls, params):
        item = cls(id=params.get('eventId'))
        item.populate(**params)
        item.put()
        return item

    @classmethod
    def remove(cls, params):
        ndb.delete_multi(
            cls.query(cls.resource == params['resource']).fetch(keys_only=True)
        )
