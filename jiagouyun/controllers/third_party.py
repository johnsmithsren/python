#!/usr/bin/env python
# coding=utf-8
from __future__ import unicode_literals

import time
import uuid

from jiagouyun import config
from jiagouyun.app import third_party_login_redis

from jiagouyun.utils import encrypt
from jiagouyun.utils import exceptions
from jiagouyun.utils.third_party_token import Token

from jiagouyun.models import session_scope
from jiagouyun.models.entities import User
from jiagouyun.models.entities import ThirdPartyAccount

REDIS_PREFIX = config['third_party']['login_redis_prefix']


def create_token(third_party_account):
    return Token.create(third_party_account).to_dict()


def create_third_party_account(username, password, company):
    now = int(time.time())
    third_party_account = ThirdPartyAccount()
    third_party_account.username = username
    third_party_account.password = encrypt(password, now)
    third_party_account.company = company
    third_party_account.create_time = now
    third_party_account.update_time = now
    with session_scope() as db_session:
        db_session.add(third_party_account)
        db_session.commit()
        return third_party_account.to_dict(exclude_columns=['password'])


def verify_third_party_account(username, password):
    with session_scope() as db_session:
        third_party_account = db_session.query(ThirdPartyAccount).filter(
            ThirdPartyAccount.username == username).first()
        if third_party_account is None:
            return None

        encrypted_password = encrypt(password, third_party_account.create_time)
        if third_party_account.password != encrypted_password:
            return None

        return third_party_account.to_dict(exclude_columns=['password'])


def refresh_token(refresh_token):
    token = Token.get(refresh_token, token_type="refresh")
    if token is None:
        raise exceptions.RefreshTokenNotExists()
    token.refresh()
    return token.to_dict()


def user_third_party_key(user_id, third_party_account):
    global REDIS_PREFIX
    with session_scope() as db_session:
        user = db_session.query(User).get(user_id)
        if user is None:
            raise exceptions.UserNotFound()
        if user.third_party_account_id != third_party_account['id']:
            raise exceptions.UserNotFound()
        key = uuid.uuid4().hex
        redis_key = "%s:%s" % (REDIS_PREFIX, key)
        third_party_login_redis.set(redis_key, user.id)
        third_party_login_redis.expire(redis_key, 60)
        return key


def user_third_party_login(key, real_ip):
    global REDIS_PREFIX
    full_key = "%s:%s" % (REDIS_PREFIX, key)
    user_id = third_party_login_redis.get(full_key)
    if user_id is None:
        return None
    third_party_login_redis.delete(full_key)
    with session_scope() as db_session:
        user = db_session.query(User).get(user_id)
        if user is None:
            return None
        user.last_login_time = int(time.time())
        user.last_login_ip = real_ip
        return user.to_dict(exclude_columns=['password'])
