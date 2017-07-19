#!/usr/bin/env python
# coding=utf-8
"""Canvas Controller.

Canvas controller functions
"""
from __future__ import unicode_literals

import time

from jiagouyun.models import session_scope
from jiagouyun.models.entities import Canvas
from jiagouyun.models.entities import CanvasVersion
from jiagouyun.models.entities import User
from jiagouyun.models.entities import ShareHistory
from jiagouyun.utils import exceptions
from jiagouyun.utils import templates
from jiagouyun.utils import message
from jiagouyun.utils import config


def verify_email(data):
    with session_scope() as db_session:
        existsUid = db_session.query(User).filter(User.email == data["to_email"]).first()
        if existsUid is None:
            raise exceptions.UserNotFound()
        user_verity = db_session.query(User).get(data["user_id"])
        user_verity = user_verity.to_dict()
        if user_verity["email"] == data["to_email"]:
            raise exceptions.CanNotShareToYourself()
        return existsUid.to_dict()
    return None


def upate_canvas_owner(canvas_id, user_id):
    # 新增字段，在照顾老数据没有此字段，需要设置默认值，做的处理函数
    with session_scope() as db_session:
        canvas = db_session.query(Canvas).get(canvas_id)
        canvas.set_update_table_base()
        canvas.canvas_owner = user_id
        db_session.commit()


def upate_canvas_edit(canvas_id):
    # 新增字段，在照顾老数据没有此字段，需要设置默认值，做的处理函数
    with session_scope() as db_session:
        canvas = db_session.query(Canvas).get(canvas_id)
        canvas.set_update_table_base()
        canvas.canvas_edited = True
        db_session.commit()


def list_share_canvases(canvas_id, page, results_per_page, user_id=None):
    with session_scope() as db_session:
        start = (page - 1) * results_per_page
        end = start + results_per_page
        query = db_session.query(ShareHistory)
        if user_id is not None:
            query = query.filter(ShareHistory.user_id == user_id, ShareHistory.canvas_id == canvas_id)
        count = query.count()
        histories = query.order_by(ShareHistory.create_time.desc()).slice(start, end).all()
        history_list = []
        for item in [history.to_dict() for history in histories]:
            canvas_version = db_session.query(ShareHistory, CanvasVersion, User).join(CanvasVersion, CanvasVersion.id == ShareHistory.canvas_version_id).join(User, User.id == ShareHistory.user_id).filter(ShareHistory.canvas_version_id == item["canvas_version_id"]).first()
            item["email"] = [item1.to_dict() for item1 in canvas_version][2]["email"]
            item["info"] = [item1.to_dict() for item1 in canvas_version][1]
            item["to_email"] = db_session.query(User).get([item1.to_dict() for item1 in canvas_version][0]["owner_id"]).email
            history_list.append(item)
        return count, history_list


def get_user_info(user_id):
    with session_scope() as db_session:
        user_info = db_session.query(User).get(user_id)
        return user_info.to_dict()
    return None


def get_canvas_list(canvase, user_id):
    with session_scope() as db_session:
        canvas_list = []
        test = [canvas.to_dict() for canvas in canvase]
        for item in test:
            # 这个有点问题，前面一个函数已经对None的情况做了处理，不知道为啥这个处理生效速度有延迟，导致这里依然会出现这个情况
            if item["canvas_owner"] is None:
                item["canvas_owner"] = user_id
            if item["canvas_edited"] is None:
                item["canvas_edited"] = True
            owner_info = get_user_info(item["canvas_owner"])
            item["owner_name"] = owner_info["full_name"]
            item["owner_email"] = owner_info["email"]
            canvas_list.append(item)
        return canvas_list


def list_canvases(page, results_per_page, user_id=None):
    with session_scope() as db_session:
        start = (page - 1) * results_per_page
        end = start + results_per_page
        query = db_session.query(Canvas)
        if user_id is not None:
            query = query.filter(Canvas.user_id == user_id, Canvas.deleted == 0)
        count = query.count()
        canvases = query.order_by(Canvas.create_time.desc()).slice(start, end).all()
        canvas_dict = [canvas.to_dict() for canvas in canvases]
        for item in canvas_dict:
            if item["canvas_owner"] is None:
                upate_canvas_owner(item["id"], user_id)
            if item["canvas_edited"] is None:
                upate_canvas_edit(item["id"])
        canvase = query.order_by(Canvas.create_time.desc()).slice(start, end).all()
        canvas_list = get_canvas_list(canvase, user_id)
        return count, canvas_list


def create_canvas(data):
    with session_scope() as db_session:
        canvas = Canvas()
        canvas.set_create_table_base()
        support_columns = ("name", "description", "draft", "user_id")
        for column in support_columns:
            if column in data:
                setattr(canvas, column, data[column])
        canvas.draft_time = int(time.time())
        canvas.canvas_owner = data["user_id"]
        canvas.canvas_edited = True
        db_session.add(canvas)
        db_session.commit()
        return canvas.to_dict()

    return None


def share_canvas_history(canvas_version_id, user_id, owner_id, canvas_id):
    with session_scope() as db_session:
        share_history = ShareHistory()
        share_history.set_create_table_base()
        share_history.owner_id = owner_id
        share_history.user_id = user_id
        share_history.canvas_id = canvas_id
        share_history.canvas_version_id = canvas_version_id
        db_session.add(share_history)
        db_session.commit()
        return share_history.to_dict()


def copy_canvas_version(new_canvas_id, canvas_version_id):
    with session_scope() as db_session:
        new_canvas_version = CanvasVersion()
        new_canvas_version.set_create_table_base()
        old_canvas_version = db_session.query(CanvasVersion).get(canvas_version_id)
        old_canvas_version = old_canvas_version.to_dict()
        support_columns = ("content", "version_number", "title", "description")
        for column in support_columns:
            if column in old_canvas_version:
                setattr(new_canvas_version, column, old_canvas_version[column])
        new_canvas_version.canvas_id = new_canvas_id
        db_session.add(new_canvas_version)
        db_session.commit()


def share_canvas_version(new_canvas_id, canvas_version_id):
    with session_scope() as db_session:
        new_canvas_version = CanvasVersion()
        new_canvas_version.set_create_table_base()
        old_canvas_version = db_session.query(CanvasVersion).get(canvas_version_id)
        old_canvas_version = old_canvas_version.to_dict()
        support_columns = ("content", "version_number", "title", "description")
        for column in support_columns:
            if column in old_canvas_version:
                setattr(new_canvas_version, column, old_canvas_version[column])
        new_canvas_version.canvas_id = new_canvas_id
        db_session.add(new_canvas_version)
        db_session.commit()


def copy_canvas(data, canvas_id):
    with session_scope() as db_session:
        new_canvas = Canvas()
        new_canvas.set_create_table_base()
        old_canvas = db_session.query(Canvas).get(canvas_id)
        old_canvas = old_canvas.to_dict()
        support_columns = ("description", "draft", "user_id")
        for column in support_columns:
            if column in old_canvas:
                setattr(new_canvas, column, old_canvas[column])
        new_canvas.draft_time = int(time.time())
        new_canvas.name = data["name"]
        db_session.add(new_canvas)
        db_session.commit()
        old_canvas_version = db_session.query(CanvasVersion).filter(CanvasVersion.canvas_id == canvas_id, CanvasVersion.deleted == 0).all()
        old_canvas_version = [canvas_version.to_dict() for canvas_version in old_canvas_version]
        for column in old_canvas_version:
            copy_canvas_version(new_canvas.id, column['id'])
        return new_canvas.to_dict()


def share_canvas(data, canvas_version_id, user_message):
    with session_scope() as db_session:
        new_canvas = Canvas()
        new_canvas.set_create_table_base()
        old_canvas_version = db_session.query(CanvasVersion).filter(CanvasVersion.id == canvas_version_id, CanvasVersion.deleted == 0).first()
        if old_canvas_version is None:
            raise exceptions.CanvasVersionNotFound()
        old_canvas_version = old_canvas_version.to_dict()
        old_canvas = db_session.query(Canvas).get(old_canvas_version['canvas_id'])
        old_canvas = old_canvas.to_dict()
        old_canvas_owner = db_session.query(User).get(old_canvas['user_id'])
        old_canvas_owner = old_canvas_owner.to_dict()
        new_canvas.draft = old_canvas_version["content"]
        new_canvas.name = old_canvas_version["title"]
        new_canvas.description = old_canvas_version["description"]
        new_canvas.draft_time = int(time.time())
        new_canvas.user_id = user_message["id"]
        new_canvas.canvas_edited = False
        new_canvas.canvas_owner = data["user_id"]
        db_session.add(new_canvas)
        db_session.commit()
        share_canvas_version(new_canvas.id, canvas_version_id)
        share_canvas_history(canvas_version_id, data["user_id"], user_message['id'], old_canvas_version["canvas_id"])
        content = templates.render("email/share_canvas.html", {
            "username": old_canvas_owner["full_name"],
            "hostname": config['hostname'],
            "canvas_version": old_canvas_version["title"],
            "name": user_message["full_name"],
            "year": message.get_year()
        })
        message.send_email(data["to_email"], '分享架构通知', content)
        return new_canvas.to_dict()
    return None


def get_canvas(canvas_id):
    with session_scope() as db_session:
        canvas = db_session.query(Canvas, User).join(User, Canvas.canvas_owner == User.id).filter(Canvas.id == canvas_id).first()
        if canvas is not None:
            canvas_info = [canvases.to_dict(exclude_columns=["password", "last_login_ip"]) for canvases in canvas][0]
            canvas_info["owner_info"] = [canvases.to_dict(exclude_columns=["password", "last_login_ip"]) for canvases in canvas][1]
            print canvas_info
            return canvas_info
    return None


def verify(canvas_id, data):
    with session_scope() as db_session:
        canvas_verify = db_session.query(Canvas).filter(Canvas.id == canvas_id, Canvas.user_id == data["user_id"]).first()
        if canvas_verify is None:
            raise exceptions.CanvasNotFound()
        canvas_version_verify = db_session.query(CanvasVersion).filter(CanvasVersion.id == data["canvas_version_id"], CanvasVersion.canvas_id == canvas_id).first()
        if canvas_version_verify is None:
            raise exceptions.CanvasVersionNotFound()
        canvas_version_share_verify = db_session.query(ShareHistory).filter(ShareHistory.canvas_version_id == data["canvas_version_id"], ShareHistory.owner_id == data["owner_id"]).first()
        if canvas_version_share_verify is not None:
            raise exceptions.CanvasVersionAlreadyShared()
        return None


def update_canvas(canvas_id, data):
    with session_scope() as db_session:
        canvas = db_session.query(Canvas).get(canvas_id)
        if canvas is not None:
            canvas.set_update_table_base()
            support_columns = ("name", "description", "draft")
            for column in support_columns:
                if column in data:
                    setattr(canvas, column, data[column])
            if "draft" in data:
                canvas.draft_time = int(time.time())
            db_session.commit()
            return canvas.to_dict()

    return None


def delete_canvas(canvas_id):
    with session_scope() as db_session:
        account = db_session.query(Canvas).get(canvas_id)
        account.set_update_table_base()
        account.deleted = 1
        # db_session.query(Canvas).filter(Canvas.id == canvas_id).delete(False)
        db_session.commit()


def get_canvas_versions(canvas_id):
    with session_scope() as db_session:
        canvas_versions = db_session.query(CanvasVersion).filter(CanvasVersion.canvas_id == canvas_id, CanvasVersion.deleted == 0).order_by(CanvasVersion.version_number.desc()).all()

        def _to_dict(canvas_version):
            _dict = canvas_version.to_dict()
            del _dict['content']
            return _dict
        return [_to_dict(canvas_version) for canvas_version in canvas_versions]

    return None


def get_canvas_version(canvas_id, version_id):
    with session_scope() as db_session:
        canvas_version = db_session.query(CanvasVersion)\
            .filter(CanvasVersion.canvas_id == canvas_id)\
            .filter(CanvasVersion.id == version_id)\
            .first()
        if canvas_version is not None:
            return canvas_version.to_dict()

    return None


def create_canvas_version(canvas_id, title, description):
    with session_scope() as db_session:
        canvas = db_session.query(Canvas).get(canvas_id)
        if canvas is not None:
            most_recent_canvas_version = db_session.query(CanvasVersion)\
                .filter(CanvasVersion.canvas_id == canvas_id)\
                .order_by(CanvasVersion.version_number.desc())\
                .first()

            version_number = 1
            if most_recent_canvas_version is not None and most_recent_canvas_version.version_number is not None:
                version_number = most_recent_canvas_version.version_number + 1

            canvas_version = CanvasVersion()
            canvas_version.set_create_table_base()
            canvas_version.canvas_id = canvas_id
            canvas_version.content = canvas.draft
            canvas_version.title = title
            canvas_version.description = description
            canvas_version.version_number = version_number
            db_session.add(canvas_version)

            db_session.commit()

            return canvas_version.to_dict()

    return None


def delete_canvas_version(canvas_id, version_id):
    with session_scope() as db_session:
        account = db_session.query(CanvasVersion).get(version_id)
        account.set_update_table_base()
        account.deleted = 1
        # db_session.query(CanvasVersion).filter(CanvasVersion.canvas_id == canvas_id).filter(CanvasVersion.id == version_id).delete(False)
        db_session.commit()
