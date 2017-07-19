#!/usr/bin/env python
# coding=utf-8
"""User controller.

User controller functions
"""
from __future__ import unicode_literals

from sqlalchemy import or_

from jiagouyun.models import session_scope
from jiagouyun.models.entities import User

from jiagouyun.utils import encrypt


def verify_user(identifier, password):
    """Verify user.

    identifier is mobile or email
    """
    with session_scope() as db_session:
        user = db_session.query(User).filter(
            or_(User.email == identifier, User.mobile == identifier)).first()
        if user is not None and user.password == encrypt(password, user.create_time):
            return user.to_dict(exclude_columns=["password"])

    return None


def create_user(data):
    """Create User.

    create user.
    """
    with session_scope() as db_session:
        user = User()
        user.set_create_table_base()
        user.email = data['email']
        user.mobile = data['mobile']
        user.full_name = data['full_name']
        user.company_name = data['company_name']
        user.password = encrypt(data['password'], user.create_time)
        user.third_party_account_id = data.get("third_party_account_id")
        db_session.add(user)
        db_session.commit()
        return user.to_dict(exclude_columns=["password"])

    return None


def update_user(user_id, data):
    """Update User.

    update user.
    """
    with session_scope() as db_session:
        supported_keys = ("email", "mobile", "full_name",
                          "company_name", "last_login_time", "last_login_ip")
        user = db_session.query(User).get(user_id)
        for key in supported_keys:
            if key in data:
                setattr(user, key, data[key])

        db_session.commit()
        return user.to_dict(exclude_columns=["password"])
