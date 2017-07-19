#!/usr/bin/env python
# coding=utf-8
from __future__ import unicode_literals

from flask import Blueprint
from flask import request
from flask import session
from flask import jsonify
from flask import redirect
from flask import g

import jiagouyun.controllers.user as user_controller
import jiagouyun.controllers.third_party as third_party_controller

from jiagouyun.utils.auth import token_verify
from jiagouyun.utils.validator import validate

third_party_bp = Blueprint("third_party", __name__)


@third_party_bp.route("/token", methods=["POST"])
def create_token():
    username = request.json.get("username")
    password = request.json.get("password")

    third_party_account = third_party_controller.verify_third_party_account(
        username, password)
    token = third_party_controller.create_token(third_party_account)
    return jsonify({
        "code": 0,
        "data": token
    })


@third_party_bp.route("/refresh_token", methods=["POST"])
def refresh_token():
    refresh_token = request.json.get("refresh_token")
    token = third_party_controller.refresh_token(refresh_token)
    return jsonify({
        "code": 0,
        "data": token
    })


@third_party_bp.route("/user", methods=["POST"])
@token_verify
def create_user():
    '''
    {
        "full_name": "full name",
        "email": "email",
        "mobile": "mobile",
        "password": "password"
        "company_name": "company name"
    }
    '''
    validate('user_create', request.json)
    data = {key: value for key, value in request.json.iteritems()}
    data['third_party_account_id'] = g.third_party_account['id']

    user = user_controller.create_user(data)
    return jsonify({
        "code": 0,
        "data": user
    })


@third_party_bp.route("/user/<user_id>/key", methods=["GET"])
@token_verify
def third_party_user_login(user_id):
    key = third_party_controller.user_third_party_key(
        user_id, g.third_party_account)
    return jsonify({
        "code": 0,
        "data": {
            "key": key
        }
    })


@third_party_bp.route("/login/<key>", methods=["GET"])
def user_login(key):
    ips = request.headers.get(
        'X-Forwarded-For', request.headers.get('X-Real-Ip', request.remote_addr))
    real_ip = ''
    if ips is not None:
        real_ip = ips.split(',')[0].strip()

    user = third_party_controller.user_third_party_login(key, real_ip)
    if user is not None:
        session['user'] = user

    return redirect("/")
