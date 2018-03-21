import redis

from config import REDIS

store = redis.StrictRedis(host=REDIS['HOST'], port=REDIS['PORT'], db=REDIS['DB'])

def get_float(store_name):
    value = store.get(store_name)
    if not value:
        return float(0.0)
    value = float(value)
    return value

