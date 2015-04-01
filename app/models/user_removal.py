from ferris import BasicModel, ndb


class UserRemoval(BasicModel):
    email = ndb.StringProperty()
    status = ndb.StringProperty(choices=('Approve', 'Cancel', 'Pending'), default='Pending')

    @classmethod
    def list_all(cls):
        return cls.query()

    @classmethod
    def list_all_pending(cls):
        return cls.query().filter(cls.status == 'Pending')

    @classmethod
    def list_all_approve(cls):
        return cls.query().filter(cls.status == 'Approve')

    @classmethod
    def create(cls, params):
        try:
            key = ndb.Key(cls, params['email'])

            if key.get() is None:
                cls(key=key, email=params['email']).put()

        except Exception, e:
            return e

    @classmethod
    def update(cls, params):
        instance = cls.query().filter(cls.email == params['email']).get()
        if instance.status == 'Pending':
            instance.status = params['status']
            instance.put()
            return instance
        else:
            return 403

    @classmethod
    def remove(cls, params):
        ndb.delete_multi(
            cls.query(cls.email == params['email']).fetch(keys_only=True)
        )

