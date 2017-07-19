#!/usr/bin/env python
# coding=utf-8

from __future__ import unicode_literals
from cerberus import Validator

from jiagouyun.utils import exceptions


__v = {
    'auth_login': {
        'username': {
            'required': True
        },
        'password': {
            'required': True
        }
    },
    'user_create': {
        'full_name': {
            'required': True
        },
        'password': {
            'type': 'string'
        },
        'email': {
            'required': True,
            'regex': "^[\w!#$%&'*+/=?^_`{|}~-]+(?:\.[\w!#$%&'*+/=?^_`{|}~-]+)*@(?:[\w](?:[\w-]*[\w])?\.)+[\w](?:[\w-]*[\w])?$"
        },
        'mobile': {
            'required': True,
            'regex': '^\d{11}$'
        }
    },
}


def validate(key, params):
    v = Validator()
    v.allow_unknown = True
    v.validate(params, __v[key])
    if v.errors:
        raise exceptions.ParamsError(info=v.errors)

    return True

# 传入需要检查字体的参数


def need_validate(schema, params):
    v = Validator()
    v.allow_unknown = True
    v.validate(params, schema)

    if v.errors:
        raise exceptions.ParamsError(info=v.errors)

    return True


for (key, attr) in __v.items():
    if not key.startswith('auth_'):
        attr['view_id'] = {
            'regex': '^\d+$'
        }
