from google.appengine.api import memcache
from decorator import decorator


def cached(key, ttl=0):
    @decorator
    def inner(f, *args, **kwargs):
        data = memcache.get(key)
        if not data:
            data = f(*args, **kwargs)
            memcache.set(key, data, ttl)
        return data
    return inner


def cached_by_args(key, ttl=0, method=False):
    @decorator
    def inner(f, *args, **kwargs):
        if method:
            targs = args[1:]
        else:
            targs = args
        tkey = (key + '-' + _args_to_string(*targs, **kwargs))
        data = memcache.get(tkey)
        if not data:
            data = f(*args, **kwargs)
            memcache.set(tkey, data, ttl)
        return data
    return inner


def _args_to_string(*args, **kwargs):
    return ('-'.join(map(str, args)) + '-' +
        '-'.join(map(str, kwargs.keys())) +
        '-'.join(map(str, kwargs.values())) + '-')


def chunked_cache(key, ttl=0, chunk_size=500):
    def chunks(l, n):
        """ Yield successive n-sized chunks from l.
        """
        for i in xrange(0, len(l), n):
            yield l[i:i + n]

    @decorator
    def inner(f, *args, **kwargs):
        check = memcache.get(key + '-check')
        data = []
        if check:
            for i in range(0, check):
                data += (memcache.get(key + '-chunk-' + str(i)))
            return data
        else:
            data = f(*args, **kwargs)
            chunk_count = 0
            for chunk in chunks(data, chunk_size):
                memcache.set(key + '-chunk-' + str(chunk_count), chunk, ttl)
                chunk_count += 1
            memcache.set(key + '-check', chunk_count, ttl)
        return data
    return inner
