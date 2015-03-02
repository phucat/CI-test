from ferris import BasicModel, ndb
import logging

class UserRemoval(BasicModel):
    email = ndb.StringProperty()
    status = ndb.StringProperty(choices=('Approve','Cancel','Pending'), default='Pending')

    @classmethod
    def list_all(cls):
        return cls.query()

    @classmethod
    def list_all_pending(cls):
        return cls.query().filter(cls.status == 'Pending')

    @classmethod
    def create(cls, params):
        try:
            item = cls(**params).put()
            return item
        except Exception, e:
            return e

    @classmethod
    def update(cls, params):
        #instance = ndb.Key(UserRemoval, tracker_name).get()
        instance = cls.query().filter(cls.email == params['email']).get()
        instance.status = params['status']
        instance.put()
        return instance
