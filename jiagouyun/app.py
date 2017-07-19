#!/usr/bin/env python
# coding=utf-8
from __future__ import unicode_literals

import sys

from datetime import timedelta

import redis

from flask import Flask
from flask import request
from flask import jsonify

from jiagouyun import config
from jiagouyun import utils
from jiagouyun.utils.exceptions import HttpException
from jiagouyun.utils.session import RedisSessionInterface
# from crm.models import Session

logger = utils.getLogger(__name__)
app = Flask("crm")

app.secret_key = config['security']['secret_key']

# Session Block
app.permanent_session_lifetime = timedelta(seconds=config['session']['expire'])

app.config['SESSION_COOKIE_DOMAIN'] = config['hostname']
app.config['SESSION_COOKIE_NAME'] = config['session']['cookie_name']

session_redis = redis.Redis(host=config['redis']['host'],
                            port=config['redis']['port'],
                            password=config['redis']['password'],
                            db=config['session']['redis_db'])


app.session_interface = RedisSessionInterface(
    redis=session_redis, prefix=config['session']['prefix'])
# Session Block end

third_party_login_redis = redis.Redis(host=config['redis']['host'],
                                      port=config['redis']['port'],
                                      password=config['redis']['password'],
                                      db=config['third_party']['login_redis_db'])

if config['debug']:
    @app.after_request
    def cors_headers(response):
        origin = request.headers.get('Origin')
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Max-Age"] = sys.maxint
        response.headers[
            "Access-Control-Allow-Headers"] = "authorization,Access-Control-Allow-Origin,Content-Type,Cookie,Cache-Control,Connection,Accept-Language,Accept-Encoding,Accept,Pragma,Referer,User-Agent,DNT,Host,Accept-Charset"
        response.headers[
            "Access-Control-Allow-Methods"] = "GET,POST,HEAD,PATCH,PUT,OPTIONS,DELETE,TRACE,CONNECT,MOVE,PROXY"
        response.headers[
            "Access-Control-Allow-Origin"] = origin
        return response


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "code": "99400",
        "message": "BadRequest"
    })


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "code": "99404",
        "message": "NotFound"
    })


@app.errorhandler(405)
def method_not_support(error):
    return jsonify({
        "code": "99405",
        "message": "MethodNotSupport"
    })


@app.errorhandler(HttpException)
def http_exception(error):
    return jsonify({
        "code": error.code,
        "message": error.message,
        "messageKey": error.messageKey
    })


@app.errorhandler(Exception)
def internel_error(error):
    logger.error(error, exc_info=True)
    return jsonify({
        "code": "99500",
        "message": "Internal Error"
    })
