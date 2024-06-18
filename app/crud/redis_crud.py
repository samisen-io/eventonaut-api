import logging
import time
from datetime import datetime
import redis
import json
from fastapi import HTTPException, status
import os

redis_host = os.getenv('REDIS_HOST')
redis_port = os.getenv('REDIS_PORT')
redis_password = os.getenv('REDIS_PASSWORD')
session_expire_time = os.getenv('SESSION_EXPIRE')

r = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, ssl=True)

def get_everything():
    keys_values_expirations = {}
    for key in r.keys():
        data_type = r.type(key)
        if data_type == b'string':
            value = r.get(key)
        elif data_type == b'list':
            value = r.lrange(key, 0, -1)
        else:
            value = None
        expiration_time = r.pttl(key)
        if expiration_time > 0:
            expire_timestamp = datetime.fromtimestamp(time.time() + expiration_time / 1000.0)
        else:
            expire_timestamp = None
        keys_values_expirations[key] = {'value': value, 'expiration': expire_timestamp}
    return keys_values_expirations

def save_session_to_redis(key, value):
    value_str = json.dumps(value)
    r.set(key, value_str, ex=session_expire_time)
    expiration_time = r.pttl(key)
    if expiration_time > 0:
        expire_timestamp = datetime.fromtimestamp(time.time() + expiration_time / 1000.0)
    else:
        expire_timestamp = None
    return expire_timestamp

def update_session_in_redis(key, value):
    expiration_timer = r.ttl(key)
    if expiration_timer > 0:
        value_str = json.dumps(value)
        r.set(key, value_str, ex=expiration_timer)
        expiration_time = r.pttl(key)
        if expiration_time > 0:
            expire_timestamp = datetime.fromtimestamp(time.time() + expiration_time / 1000.0)
        else:
            expire_timestamp = None
    else:
        logging.exception(f"Session {key} expired")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Session {key} expired")
    return expire_timestamp

def save_list_of_sessions_to_redis(key, value):
    r.rpush(key, value)
    return True

def get_session_from_redis(key):
    return r.get(key)

def get_list_of_sessions_from_redis(key):
    return r.lrange(key, 0, -1)

def delete_data_from_redis(key):
    return r.delete(key)

def remove_session_from_list(key, value):
    return r.lrem(key, 0, value)

def delete_list_from_redis(key):
    return r.delete(key)