from ferris import BasicModel, ndb


class Calendar(BasicModel):
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
    def create(cls, params):
        item = cls()
        item.populate(**params)
        item.put()
        return item

