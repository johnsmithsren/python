#!/usr/bin/env python
# coding=utf-8
"""Cloudaccount routes.

Cloudaccount routes
"""
from __future__ import unicode_literals

from flask import session
from flask import request
from flask import jsonify
from flask import Blueprint
from jiagouyun.controllers import cloud_account as cloud_account_controller
from jiagouyun.utils import getLogger
from jiagouyun.utils import exceptions
from jiagouyun.utils.auth import need_login
from jiagouyun.utils import aliyun
from jiagouyun.utils import params
import json
# from jiagouyun.utils import xml2dict

logger = getLogger(__name__)
cloud_account_bp = Blueprint("cloud_acount", __name__)
resource_map = {'ecs': "server", 'rds': "database", 'slb': 'loadbalancer', 'sts': 'sts', "ram": "ram", 'vpc': 'vpc'}


@cloud_account_bp.route("", methods=["GET"])
@need_login
def list_cloud_accounts():
    """List cloud account.

    @api {get} /cloud_account 获取阿里云账号信息列表
    @apiName ListCloudAccount
    @apiGroup CloudAccount

    @apiParam {Number} page 页码。
    @apiParam {Number} results_per_page 每页显示的数量
    """
    page = 1
    results_per_page = 10
    try:
        page = int(request.args["page"])
    except:
        pass
    try:
        results_per_page = int(request.args["results_per_page"])
    except:
        pass
    count, data = cloud_account_controller.list_cloud_account(
        page, results_per_page, user_id=session['user']['id'])
    total_pages = count / \
        results_per_page if count % results_per_page == 0 else count / results_per_page + 1
    return jsonify({
        "code": 0,
        "data": {
            "objects": data,
            "total_pages": total_pages,
            "current_page": page,
            "num_results": count
        }
    })


@cloud_account_bp.route("/<cloud_account_id>", methods=["GET"])
@need_login
def get(cloud_account_id):
    """Get cloud account.

    @api {get} /cloud_account/:id 获取阿里云账号信息
    @apiName GetCloudAccount
    @apiGroup CloudAccount
    """
    cloud_account = cloud_account_controller.get_cloud_account(cloud_account_id)
    if cloud_account is None:
        raise exceptions.CloudAccountError()
    return jsonify({
        "code": "0",
        "data": cloud_account
    })


@cloud_account_bp.route("/<cloud_account_id>", methods=["DELETE"])
@need_login
def delete(cloud_account_id):
    """Delete cloud account.

    @api {delete} /cloud_account/:id 删除阿里云账号信息
    @apiName DeleteCloudAccount
    @apiGroup CloudAccount
    """
    cloud_account = cloud_account_controller.get_cloud_account(cloud_account_id)
    if cloud_account is None or cloud_account['user_id'] != session['user']['id']:
        raise exceptions.DeleteAccountFailed()
    cloud_account_controller.delete_cloud_account(cloud_account_id)
    return jsonify({
        "code": "0",
        "data": {}
    })


@cloud_account_bp.route("/<cloud_account_id>", methods=["PATCH"])
@need_login
def update(cloud_account_id):
    """Update cloud account.

    @api {patch} /cloud_account/:id 更新阿里云账号信息
    @apiName UpdateCloudAccount
    @apiGroup CloudAccount

    @apiParam {String} account_name 账号名称。
    @apiParam {String} info AK secret详细信息，可以进行加密存储。
    @apiParam {String} description AK信息解释。
    @apiParam {int} status cloudaccount状态（0,启用，1，禁用）。
    """
    data = request.json
    cloud_account = cloud_account_controller.get_cloud_account(cloud_account_id)
    if cloud_account is None:
        raise exceptions.CloudAccountNotFound()
    cloud_account_result = cloud_account_controller.update_cloud_account(cloud_account_id, data)
    if cloud_account_result is None or cloud_account_result['user_id'] != session['user']['id']:
        raise exceptions.UpadteAccountFailed()
    return jsonify({
        "code": "0",
        "data": cloud_account_result
    })


@cloud_account_bp.route("", methods=["POST"])
@need_login
def create():
    """Create one ak info.
    @api {post} /cloud_account 创建阿里云账号信息
    @apiName CreateCloudAccount
    @apiGroup CloudAccount
    @apiParam {String} platform .平台介绍，描述AK所属平台，当前主要为阿里云，后期会增加其他平台AK信息。
    @apiParam {String} account_name .账号信息别名。
    @apiParam {String} info .cloudaccout secret详细信息，可以进行加密存储。
    @apiParam {String} description cloudaccount 信息解释。
    @apiParam {String} corporate_name cloudaccount 公司名称。
    """
    data = request.json
    cloud_account = cloud_account_controller.create_cloud_account(session['user']['id'], data)
    if cloud_account is None:
        raise exceptions.InsertAccountFailed()
    return jsonify({
        "code": "0",
        "data": cloud_account
    })


@cloud_account_bp.route("/<cloud_account_id>/invoke", methods=["GET"])
@need_login
def invoke_api(cloud_account_id):
    """Invoke Cloud API.
    Invoke cloud api for aliyun etc.

    @api {get}  /cloud_account/:id/invoke 请求平台实例信息
    @apiName GetResourceInfo
    @apiGroup CloudAccount

    @apiParam {String} requestArgs 直接传参数对象即可.

    """
    cloud_account = cloud_account_controller.get_invoke_ak(cloud_account_id)
    resource_type = request.args.get('resource_type')
    if resource_type is None:
        raise SourceTypeNotFount()
    resource_type = resource_map[resource_type]
    info = json.loads(cloud_account['info'].replace("'", "\""))
    invoke_result = aliyun.invoke_api(info, resource_type, request.args)
    invoke_result = json.loads(invoke_result[0])
    return jsonify({
        "code": '0',
        "data": invoke_result
    })


@cloud_account_bp.route("/<cloud_account_id>/oss_invoke", methods=["GET"])
@need_login
def oss_invoke_api(cloud_account_id):
    """Invoke Cloud Oss API.
    oss Invoke cloud api for aliyun etc.

    @api {get} /cloud_account/:id/oss_invoke 请求平台oss实例信息
    @apiName GetOssResourceInfo
    @apiGroup CloudAccount

    @apiParam {String} resource oss资源.
    @apiParam {String} params 请求参数.
    @apiParam {String} action oss请求方法.
    @apiParam {String} bucket bucket 名称.

    """

    cloud_account = cloud_account_controller.get_invoke_ak(cloud_account_id)
    info = json.loads(cloud_account['info'].replace("'", "\""))
    # param = {
    #     "max-keys": "100",
    #     "encoding-type": "url"
    # }
    # action = 'listBuckets'
    # bucket = ''
    # resource = 'liuyltest4'
    invoke_result = aliyun.oss_invoke_api(info, resource, param, action, bucket)
    oss_invoke_result = json.loads(invoke_result[0])
    return jsonify({
        "code": '0',
        "data": oss_invoke_result
    })
