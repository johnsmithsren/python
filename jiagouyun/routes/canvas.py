#!/usr/bin/env python
# coding=utf-8
"""Canvas routes.

Canvas routes
"""
from __future__ import unicode_literals

from flask import session
from flask import request
from flask import jsonify
from flask import Blueprint

from jiagouyun.controllers import canvas as canvas_controller
from jiagouyun.utils import getLogger
from jiagouyun.utils import exceptions
from jiagouyun.utils.auth import need_login

logger = getLogger(__name__)
canvas_bp = Blueprint("canvas", __name__)


@canvas_bp.route("", methods=["GET"])
@need_login
def list_canvases():
    """List canvases.

    @api {get} /canvas 获取画布列表
    @apiName ListCanvas
    @apiGroup Canvas

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
    count, data = canvas_controller.list_canvases(
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


@canvas_bp.route("/<canvas_id>/share", methods=["GET"])
@need_login
def list_share_canvases(canvas_id):
    """List Share History.

    @api {get} /canvas/:canvas_id/share 获取当前版本分享历史数据
    @apiName ListShareCanvas
    @apiGroup Canvas

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
    count, data = canvas_controller.list_share_canvases(canvas_id, page, results_per_page, user_id=session['user']['id'])
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


@canvas_bp.route("", methods=["POST"])
@need_login
def create_canvas():
    """Create canvas.

    @api {post} /canvas 创建画布
    @apiName CreateCanvas
    @apiGroup Canvas

    @apiParam {String} name 画布名称。
    @apiParam {String} description 画布简介。
    @apiParam {String} draft 画布内容（引入版本后改为当前草稿）。
    """
    data = request.json
    data['user_id'] = session['user']['id']
    canvas = canvas_controller.create_canvas(data)
    if canvas is None:
        raise exceptions.CanvasCreateFailed()

    return jsonify({
        "code": "0",
        "data": canvas
    })


@canvas_bp.route("/<canvas_id>/copy", methods=["POST"])
@need_login
def copy_canvas(canvas_id):
    """Copy canvas.

    @api {post} /canvas 拷贝画布
    @apiName CopyCanvas
    @apiGroup Canvas

    @apiParam {String} name 画布名称。
    """
    data = request.json
    data['user_id'] = session['user']['id']
    canvas = canvas_controller.copy_canvas(data, canvas_id)
    if canvas is None:
        raise exceptions.CopyCanvasFailed()

    return jsonify({
        "code": "0",
        "data": canvas
    })


@canvas_bp.route("/<canvas_id>/share", methods=["POST"])
@need_login
def share_canvas(canvas_id):
    """Share Canvas.

    @api {post} /canvas/:canvas_id/share 分享画布
    @apiName ShareCanvas
    @apiGroup Canvas

    @apiParam {String} to_email 被分享者邮箱。
    @apiParam {String} canvas_version_id 架构版本ID，作判断用处。
    """
    data = request.json
    data['user_id'] = session['user']['id']
    user_email = canvas_controller.verify_email(data)
    if user_email is None:
        raise exceptions.UserNotFound()
    data["owner_id"] = user_email["id"]
    canvas_verify = canvas_controller.verify(canvas_id, data)
    canvas = canvas_controller.share_canvas(data, data["canvas_version_id"], user_email)
    if canvas is None:
        raise exceptions.ShareCanvasFailed()

    return jsonify({
        "code": "0",
        "data": canvas
    })


@canvas_bp.route("/<canvas_id>", methods=["GET"])
@need_login
def get_canvas(canvas_id):
    """Get canvas.

    @api {get} /canvas/:id 获取画布
    @apiName GetCanvas
    @apiGroup Canvas

    @apiParam {Number} id 画布ID。
    """

    canvas = canvas_controller.get_canvas(canvas_id)
    if canvas is None or canvas['user_id'] != session['user']['id']:
        raise exceptions.CanvasNotFound()
    return jsonify({
        "code": "0",
        "data": canvas
    })


@canvas_bp.route("/<canvas_id>", methods=["DELETE"])
@need_login
def delete_canvas(canvas_id):
    """Delete canvas.

    @api {delete} /canvas/:id 删除画布
    @apiName DeleteCanvas
    @apiGroup Canvas

    @apiParam {Number} id 画布ID。
    """
    canvas = canvas_controller.get_canvas(canvas_id)
    if canvas is None or canvas['user_id'] != session['user']['id']:
        raise exceptions.CanvasNotFound()
    canvas_controller.delete_canvas(canvas_id)
    return jsonify({
        "code": "0",
        "data": {}
    })


@canvas_bp.route("/<canvas_id>", methods=["PATCH"])
@need_login
def update_canvas(canvas_id):
    """Update canvas.

    @api {patch} /canvas/:id 更新画布
    @apiName UpdateCanvas
    @apiGroup Canvas

    @apiParam {Number} id 画布ID。
    @apiParam {String} name 画布名称。
    @apiParam {String} description 画布简介。
    @apiParam {String} draft 画布内容（引入版本后改为当前草稿）。
    """
    data = request.json
    canvas = canvas_controller.get_canvas(canvas_id)
    if canvas is None or canvas['user_id'] != session['user']['id']:
        raise exceptions.CanvasNotFound()
    canvas = canvas_controller.update_canvas(canvas_id, data)

    if canvas is None:
        raise exceptions.CanvasUpdateFailed()

    return jsonify({
        "code": "0",
        "data": canvas
    })


@canvas_bp.route("/<canvas_id>/versions", methods=["GET"])
@need_login
def get_canvas_versions(canvas_id):
    """Get All Canvas versions.

    @api {get} /canvas/:canvas_id/versions 获取画布版本列表
    @apiName GetCanvasVersions
    @apiGroup CanvasVersion

    @apiParams {Number} canvas_id 画布ID
    """
    canvas = canvas_controller.get_canvas(canvas_id)
    if canvas is None:
        raise exceptions.CanvasNotFound()

    versions = canvas_controller.get_canvas_versions(canvas_id)

    return jsonify({
        "code": "0",
        "data": versions
    })


@canvas_bp.route("/<canvas_id>/versions/<version_id>", methods=["GET"])
@need_login
def get_canvas_version(canvas_id, version_id):
    """Get a Canvas version.

    @api {get} /canvas/:canvas_id/versions/:version_id 获取单个画布版本
    @apiName GetCanvasVersion
    @apiGroup CanvasVersion

    @apiParams {Number} canvas_id 画布ID
    @apiParams {Number} version_id 版本ID
    """
    version = canvas_controller.get_canvas_version(canvas_id, version_id)
    if version is None:
        raise exceptions.CanvasVersionNotFound()

    return jsonify({
        "code": "0",
        "data": version
    })


@canvas_bp.route("/<canvas_id>/versions/<version_id>", methods=["DELETE"])
@need_login
def delete_canvas_version(canvas_id, version_id):
    """Delete a Canvas version.

    @api {delete} /canvas/:canvas_id/versions/:version_id 删除画布版本
    @apiName DeleteCanvasVersion
    @apiGroup CanvasVersion

    @apiParams {Number} canvas_id 画布ID
    @apiParams {Number} version_id 版本ID
    """
    canvas_controller.delete_canvas_version(canvas_id, version_id)
    return jsonify({
        "code": "0",
        "data": {}
    })


@canvas_bp.route("/<canvas_id>/versions", methods=["POST"])
@need_login
def create_canvas_version(canvas_id):
    """Create a Canvas version.

    @api {post} /cavnas/:canvas_id/version 创建画布版本
    @apiName CreateCavansVersion
    @apiGroup CanvasVersion

    @apiParams {Number} canvas_id 画布ID
    @apiParams {String} title 版本标题
    @apiParams {String} description 版本描述
    """
    title = request.json['title']
    description = request.json.get("description", "")
    canvas_version = canvas_controller.create_canvas_version(canvas_id, title, description)
    if canvas_version is None:
        raise exceptions.CanvasVersionCreateFailed()
    return jsonify({
        "code": "0",
        "data": canvas_version
    })
