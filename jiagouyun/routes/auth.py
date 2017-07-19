#!/usr/bin/env python
# coding=utf-8
"""Authentication routes.

Authentication routes
"""
from __future__ import unicode_literals

import time

from flask import session
from flask import request
from flask import jsonify
from flask import Blueprint

from jiagouyun.controllers import user as user_controller
from jiagouyun.utils import getLogger
from jiagouyun.utils import exceptions
from jiagouyun.utils.auth import need_login

logger = getLogger(__name__)
auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    """Register.

    @api {post} /auth/register 注册
    @apiName Register
    @apiGroup Auth

    @apiParam {String} email 用户邮箱。
    @apiParam {String} mobile 用户手机号。
    @apiParam {String} full_name 用户显示名。
    @apiParam {String} password 密码。
    """
    data = request.json
    user = user_controller.create_user(data)
    if user is None:
        raise exceptions.UserCreateFailed()

    return jsonify({
        "code": "0",
        "data": user
    })


@auth_bp.route("/login", methods=["POST"])
def login():
    """Login.

    @api {post} /auth/login 登录
    @apiName Login
    @apiGroup Auth

    @apiParam {String} identifier 用户标识（邮箱或者手机号）。
    @apiParam {String} password 密码。
    """
    ips = request.headers.get(
        'X-Forwarded-For', request.headers.get('X-Real-Ip', request.remote_addr))
    real_ip = ''
    if ips is not None:
        real_ip = ips.split(',')[0].strip()
    data = request.json
    user = user_controller.verify_user(data['identifier'], data['password'])
    if user is None:
        raise exceptions.LoginFailed()

    session["user"] = user

    user_controller.update_user(user['id'], {
        "last_login_ip": real_ip,
        "last_login_time": int(time.time())
    })

    return jsonify({
        "code": "0",
        "data": user
    })


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """Logout.

    @api {post} /auth/logout 登出
    @apiName Logout
    @apiGroup Auth
    """
    session.clear()
    return jsonify({
        "code": "0",
        "data": {}
    })


@auth_bp.route("/current_user", methods=["GET"])
@need_login
def current_user():
    """Current user.

    @api {get} /auth/current_user 当前用户
    @apiName CurrentUser
    @apiGroup Auth
    """
    return jsonify({
        "code": "0",
        "data": session['user']
    })
