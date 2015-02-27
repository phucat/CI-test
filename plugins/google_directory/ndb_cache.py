from google.appengine.ext import deferred, ndb
import json
import datetime
import functools


class DomainCache(ndb.Model):
    modified = ndb.DateTimeProperty(indexed=False, auto_now=True)
    data = ndb.TextProperty(indexed=False, compressed=True)
    refreshing = ndb.BooleanProperty(indexed=False, default=False)
    count = ndb.IntegerProperty(indexed=False, default=0)

    @classmethod
    def _get_kind(cls):
        return "_domain_plugin_cache"

    @classmethod
    def instance(cls, key='users'):
        key = ndb.Key(cls, key)
        ins = key.get()
        if not ins:
            ins = cls(key=key)
            ins.put()
        return ins

    @classmethod
    @ndb.toplevel
    def store_sharded(cls, key, data, size=1500):
        def chunks(l, n):
            for i in xrange(0, len(l), n):
                yield l[i:i+n]

        count = 0
        
        for chunk in chunks(data, size):
            count += 1
            ins = cls.instance('%s-%s' % (key, count)) 
            ins.data = json.dumps(chunk)
            ins.put_async()

        ins = cls.instance(key)
        ins.data = None
        ins.count = count
        ins.refreshing = False
        ins.put_async()

    @classmethod
    def retrieve_sharded(cls, key):
        control = cls.instance(key)
        if not control.count:
            return None

        items = ndb.get_multi([ndb.Key(cls, '%s-%s' % (key, i)) for i in xrange(1,control.count+1)])

        results = []
        for i in items:
            results.extend(json.loads(i.data))

        return results


def ndb_cached_impl(cache, func, refresh=False):
    if not refresh and cache.data:
        return json.loads(cache.data)

    cache.refreshing = True
    cache.put()

    results = func()
    cache.data = json.dumps(results)
    cache.refreshing = False
    cache.put()

    return results


def ndb_cached_refresh_task(key, func, impl):
    from google.appengine.api import urlfetch
    urlfetch.set_default_fetch_deadline(60)

    cache = DomainCache.instance(key)

    if not cache.refreshing:
        impl(cache, func, True)


def ndb_sharded_cached_impl(cache, func, refresh=False):
    if not refresh and cache.count:
        data = DomainCache.retrieve_sharded(cache.key.id())
        if data:
            return data

    cache.refreshing = True
    cache.put()

    results = func()

    if results:
        DomainCache.store_sharded(cache.key.id(), results)

    return results


def ndb_cached(key, func, impl=ndb_cached_impl, _target=None):
    @functools.wraps(func)
    def inner():
        cache = DomainCache.instance(key)
        six_hours_ago = datetime.datetime.utcnow() - datetime.timedelta(hours=6)

        if cache.modified and cache.modified < six_hours_ago:
            deferred.defer(ndb_cached_refresh_task, key, func, impl, _target=_target)

        return impl(cache, func)

    return inner


def refresh(key, func, impl=ndb_cached_impl, _target=None):
    cache = DomainCache.instance(key)
    cache.refreshing = False
    cache.put()
    deferred.defer(ndb_cached_refresh_task, key, func, impl, _target=_target)
