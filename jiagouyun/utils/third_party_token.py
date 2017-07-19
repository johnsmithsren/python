#!/usr/bin/env python
# coding=utf-8
from __future__ import unicode_literals

import redis
import uuid
import time

from jiagouyun import config


token_redis = redis.StrictRedis(host=config['redis']['host'],
                                port=config['redis']['port'],
                                password=config['redis']['password'],
                                db=config['third_party']['token_redis_db'])

REDIS_PREFIX = config['third_party']['token_redis_prefix']


def _add_to_redis(token_data):
    global REDIS_PREFIX
    pipeline = token_redis.pipeline()
    account_token_key = "%s:account:%s:tokens" % (
        REDIS_PREFIX, token_data['account_id'])
    access_token_key = "%s:access_token:%s" % (
        REDIS_PREFIX, token_data['access_token'])
    refresh_token_key = "%s:refresh_token:%s" % (
        REDIS_PREFIX, token_data['refresh_token'])
    pipeline.hmset(access_token_key, token_data)
    pipeline.set(refresh_token_key, token_data['access_token'])
    pipeline.sadd(account_token_key, token_data['access_token'])

    a_week = 60 * 60 * 24 * 7
    pipeline.expire(access_token_key, a_week)
    pipeline.expire(refresh_token_key, a_week)
    return pipeline.execute()


def _delete_from_redis(token_data):
    global REDIS_PREFIX
    pipeline = token_redis.pipeline()
    account_token_key = "%s:account:%s:tokens" % (
        REDIS_PREFIX, token_data['account_id'])
    access_token_key = "%s:access_token:%s" % (
        REDIS_PREFIX, token_data['access_token'])
    refresh_token_key = "%s:refresh_token:%s" % (
        REDIS_PREFIX, token_data['refresh_token'])
    pipeline.delete(access_token_key)
    pipeline.delete(refresh_token_key)
    pipeline.srem(account_token_key, token_data['access_token'])
    return pipeline.execute()


def _get_from_redis(token):
    global REDIS_PREFIX
    access_token_key = "%s:access_token:%s" % (REDIS_PREFIX, token)
    if token_redis.type(access_token_key) != "hash":
        return None

    token_data = token_redis.hgetall(access_token_key)
    token_data['expire_time'] = int(token_data['expire_time'])
    return token_data


def _get_token_by_refresh_token(refresh_token):
    global REDIS_PREFIX
    refresh_token_key = "%s:refresh_token:%s" % (REDIS_PREFIX, refresh_token)

    access_token = token_redis.get(refresh_token_key)
    if access_token is None:
        return None
    return _get_from_redis(access_token)


class Token(object):

    @classmethod
    def get(cls, token, token_type):
        if token_type == "access":
            token_data = _get_from_redis(token)
            if token_data is not None:
                return cls(**token_data)
        elif token_type == "refresh":
            token_data = _get_token_by_refresh_token(token)
            if token_data is not None:
                return cls(**token_data)

        return None

    def __init__(self, account_id, access_token, refresh_token, expire_time):
        self.account_id = account_id
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.expire_time = int(expire_time)

    @classmethod
    def create(cls, third_party_account):
        now = int(time.time())
        token_data = {
            "account_id": third_party_account['id'],
            "access_token": uuid.uuid4().hex,
            "refresh_token": uuid.uuid4().hex,
            "expire_time": now + 3600
        }

        _add_to_redis(token_data)

        return cls(**token_data)

    def refresh(self):
        _delete_from_redis(self.to_dict())
        new_token_data = {
            "account_id": self.account_id,
            "access_token": uuid.uuid4().hex,
            "refresh_token": uuid.uuid4().hex,
            "expire_time": int(time.time()) + 3600
        }
        _add_to_redis(new_token_data)
        self.account_id = new_token_data['account_id']
        self.access_token = new_token_data['access_token']
        self.refresh_token = new_token_data['refresh_token']
        self.expire_time = new_token_data['expire_time']

    def to_dict(self):
        return {
            "account_id": self.account_id,
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "expire_time": self.expire_time
        }
