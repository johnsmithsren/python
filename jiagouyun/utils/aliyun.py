#!/usr/bin/env python
# coding=utf-8

import jiagouyun.utils.params as params_utils
from jiagouyun.utils import exceptions
from jiagouyun.utils import getLogger
from uuid import uuid4
from jiagouyun import config

import time
import requests
import base64
import hmac
import sha
import urllib
from hashlib import sha1
from hashlib import sha256
import httplib

logger = getLogger(__name__)


def _generate_api_url(ak, resource_type, parameters):
    params = {}

    for key, value in parameters.iteritems():
        params[key] = value

    api_endpoint = config['aliyun_open_api'][resource_type]

    params['Format'] = "json"
    params['Version'] = api_endpoint['version']
    params['SignatureNonce'] = str(uuid4())
    params['SignatureMethod'] = "HMAC-SHA1"
    params['SignatureVersion'] = "1.0"
    params['AccessKeyId'] = ak['access_key_id']
    params['Timestamp'] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    signature = params_utils.sign(ak['access_key_secret'], params)
    print params
    params['Signature'] = signature
    text_parameters = "&".join(
        map(lambda x: "=".join(x), params.iteritems()))

    # 这五个region的endpoint需要动态感知
    url = None  # api_endpoint['url']
    if resource_type != 'server' and 'RegionId' in parameters and parameters['RegionId'] in ['ap-northeast-1', 'eu-central-1', 'me-east-1', 'ap-southeast-2', 'cn-zhangjiakou']:
        url = "{0}://{1}.{2}.{3}".format(api_endpoint['protocol'], api_endpoint['product'], parameters['RegionId'], api_endpoint['url'])
    else:
        url = "{0}://{1}.{2}".format(api_endpoint['protocol'], api_endpoint['product'], api_endpoint['url'])

    full_url = url + "?" + text_parameters

    return full_url


def invoke_api(info, resource_type, parameters):
    retry = 0
    resp = None
    full_url = None
    ak = {
        "access_key_id": info["akid"],
        "access_key_secret": info["aksecret"]
    }
    while retry < 5:
        try:
            full_url = _generate_api_url(ak, resource_type, parameters)
            resp = requests.get(full_url, headers={"Accept-Encoding": ""}, timeout=15)
            retry = 9999

        except Exception as e:
            logger.exception(e)
            retry = retry + 1
            print 'retry times: {0}, url: {1} '.format(str(retry), full_url)

            if retry >= 5:
                raise exceptions.SyncResourceError()

    return resp.text, resp.status_code


def oss_invoke_api(ak, canonicalizedResource, parameters, action=None, bucket=None, region='oss'):
    params = {}
    for key, value in parameters.iteritems():
        params[key] = value

    endpoint = config['aliyun_open_api']['objectstorage']

    # date = http_date()
    expires = int(time.time()) + 300

    sign = params_utils.oss_sign(ak['aksecret'], 'GET', expires, canonicalizedResource)

    params['OSSAccessKeyId'] = ak['akid']
    params['Expires'] = str(expires)
    params['Signature'] = sign

    text_parameters = "&".join(
        map(lambda x: "=".join(x), params.iteritems()))

    url = endpoint['url']
    if bucket is not None:
        url = "http://{0}.{1}.{2}".format(bucket, region, url)
    else:
        url = "http://{0}.{1}".format(region, url)

    if action is None:
        full_url = "{0}/?{1}".format(url, text_parameters)  # url + "?" + text_parameters
    else:
        full_url = "{0}/?{1}&{2}".format(url, action, text_parameters)  # url + "?" + text_parameters

    print full_url
    resp = requests.get(full_url)

    dictResp = params_utils.xml2dict(resp.text)
    return dictResp, resp.status_code
