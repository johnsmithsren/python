#!/usr/bin/env python
# coding=utf-8
"""Authentication.

Authentication tools
"""
from __future__ import unicode_literals

import functools
import time

from flask import request
from flask import session
from flask import g

from jiagouyun.models import session_scope
from jiagouyun.models.entities import ThirdPartyAccount

from jiagouyun.utils import exceptions
from jiagouyun.utils.third_party_token import Token


def need_login(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if "user" not in session:
            raise exceptions.NeedLogin()
        return func(*args, **kwargs)
    return wrapper


# Token验证
def token_verify(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if "X-Auth-Token" not in request.headers:
            raise exceptions.InvalidAcceessToken()
        token = Token.get(request.headers['X-Auth-Token'], "access")
        if token is None:
            raise exceptions.InvalidAcceessToken()
        now = int(time.time())
        if token.expire_time < now:
            raise exceptions.AcceessTokenExpired()
        with session_scope() as db_session:
            third_party_account = db_session.query(
                ThirdPartyAccount).get(token.account_id)
            if third_party_account is None:
                raise exceptions.InvalidAcceessToken()
            g.third_party_account = third_party_account.to_dict(
                exclude_columns=['password'])

        return func(*args, **kwargs)
    return wrapper
