#!/usr/bin/env python
# coding=utf-8


import time
# import datetime
# import pytz
import base64
import hmac
import sha
import urllib
import xmltodict
import json
from hashlib import sha1
from hashlib import sha256
from jiagouyun import config
from random import choice


def ensure_update_params(data, supported_columns):
    for key in data.keys():
        if key not in supported_columns:
            del data[key]

    if len(data.keys()) > 0:
        data['update_time'] = int(time.time())


def encrypt(password, salt):
    _sha = sha256(password)
    _sha.update(str(salt))
    _sha.update(config['security']['secret_key'])
    return _sha.hexdigest()


def percent_encode(encode_str):
    encode_str = unicode(encode_str).encode("utf8")
    res = urllib.quote(
        encode_str, '')
    res = res.replace('+', '%20')
    res = res.replace('*', '%2A')
    res = res.replace('%7E', '~')
    return res


def sign(access_key_secret, parameters):
    sorted_parameters = sorted(
        parameters.items(), key=lambda parameter: parameter[0])

    canonicalized_query_string = ''
    for (k, v) in sorted_parameters:
        canonicalized_query_string += '&' + \
            percent_encode(k) + '=' + percent_encode(v)

    string_to_sign = 'GET&%2F&' + \
        percent_encode(canonicalized_query_string[1:])

    h = hmac.new(str(access_key_secret + "&"), string_to_sign, sha1)
    signature = base64.encodestring(h.digest()).strip()
    return percent_encode(signature)


def xml2dict(xml, xml_attribs=True):
    d = xmltodict.parse(xml, xml_attribs=xml_attribs)
    return json.dumps(d, indent=4)


def oss_sign(access_key_secret, verb, expires, canonicalizedResource):
    s = "\n".join([verb,
                   '',
                   '',
                   str(expires),
                   '' + canonicalizedResource])

    h = hmac.new(str(access_key_secret), str(s), sha)

    return urllib.quote(base64.encodestring(h.digest()).strip())


def random_string(digits, characters):
    return ''.join([choice(characters) for i in range(digits)])

# 用户自定义查询结果，转换成字典形式


def row_to_dict(row):
    if isinstance(row, list):
        return [{n: getattr(item, n) for n in item.keys()} for item in row]
    else:
        return {n: getattr(row, n) for n in row.keys()}


def oss_sign(access_key_secret, verb, expires, canonicalizedResource):
    s = "\n".join([verb,
                   '',
                   '',
                   str(expires),
                   '' + canonicalizedResource])

    h = hmac.new(str(access_key_secret), str(s), sha)

    return urllib.quote(base64.encodestring(h.digest()).strip())
