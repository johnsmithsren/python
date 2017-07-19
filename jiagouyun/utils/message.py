#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import requests
import json
import time

from jiagouyun import config


def get_year():
    format = '%Y'
    v = int(time.time()) + 3600 * 8
    valuegmt = time.gmtime(v)
    year = time.strftime(format, valuegmt)
    return year


def send_email(to, subject, body, calendar=None):
    params = {
        "to": [to],
        "cc": [],
        "bcc": [],
        "title": subject,
        "content": body,
        "calendar": calendar,
        "html": True
    }
    headers = {
        "Content-Type": "application/json"
    }
    resp = requests.post(config['message']['endpoint'] + "/email", data=json.dumps(params), headers=headers)


def send_sms(to, body):
    params = {
        "to": [to],
        "content": body
    }
    headers = {
        "Content-Type": "application/json"
    }
    resp = requests.post(config['message']['endpoint'] + "/sms", data=json.dumps(params), headers=headers)
    # if resp.status_code >= 400:
    #     logger.error("Request error: %s" % resp.text)
    #     raise exceptions.SMSSendFail()
