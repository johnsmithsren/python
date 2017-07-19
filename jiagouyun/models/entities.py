#!/usr/bin/env python
# coding=utf-8
"""Entities for jiagouyun

All database entities for jiagouyun
"""
from __future__ import unicode_literals

import time

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import SMALLINT
from sqlalchemy import BigInteger
from sqlalchemy import Boolean
from sqlalchemy import Unicode
from sqlalchemy import Text
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy import CHAR
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

Base = declarative_base()


class BaseMixin:
    """Base Mixin for all entities.

    All common entities functions
    """

    def to_dict(self, exclude_columns=None):
        """Entity to dict.

        Entity to dict for all columns
        """
        if exclude_columns is None:
            exclude_columns = []
        d = {}
        for column in self.__table__.columns:
            if unicode(column.name) in exclude_columns:
                continue
            d[column.name] = getattr(self, column.name)

        return d


# 所有表公共字段
class TableBase:
    """Table base columns.

    Including columns like id, create time and update time
    """

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    create_time = Column(BigInteger)
    update_time = Column(BigInteger)

    def set_create_table_base(self):
        """Set base parameters for object.

        Set create / update time for object
        """
        now = int(time.time())
        self.create_time = now
        self.update_time = now

    def set_update_table_base(self):
        """Set base parameters for object update.

        Set update time for object
        """
        now = int(time.time())
        self.update_time = now


class User(Base, BaseMixin, TableBase):
    """User.

    User for jiagouyun
    """

    __tablename__ = "users"

    email = Column(Unicode(64), nullable=False, unique=True)
    mobile = Column(Unicode(20), nullable=False, unique=True)
    password = Column(CHAR(128), nullable=False)
    email_verified = Column(Boolean, nullable=False, default=False)
    mobile_verified = Column(Boolean, nullable=False, default=False)
    full_name = Column(Unicode(20))
    company_name = Column(Unicode(64))
    third_party_account_id = Column(
        BigInteger, ForeignKey("third_party_accounts.id"))
    last_login_time = Column(BigInteger)
    last_login_ip = Column(Unicode(64))
    canvases = relationship("Canvas")


class Canvas(Base, BaseMixin, TableBase):
    """Canvas.

    Architecture Canvas data
    """

    __tablename__ = "canvases"
    name = Column(Unicode(64), nullable=False)
    description = Column(Text)
    draft = Column(LONGTEXT)
    draft_time = Column(BigInteger)
    user_id = Column(BigInteger, ForeignKey("users.id"))
    deleted = Column(Boolean, nullable=False, default=0)
    canvas_owner = Column(BigInteger)
    canvas_edited = Column(Boolean, nullable=False, default=1)
    user = relationship("User", back_populates="canvases")
    versions = relationship("CanvasVersion")


class CanvasVersion(Base, BaseMixin, TableBase):
    """Canvas Version.

    Canvas history version
    """

    __tablename__ = "canvas_versions"
    content = Column(LONGTEXT)
    version_number = Column(Integer)
    title = Column(Unicode(64))
    description = Column(Text)
    canvas_id = Column(BigInteger, ForeignKey("canvases.id"))
    deleted = Column(Boolean, nullable=False, default=0)
    canvas = relationship("Canvas", back_populates="versions")


class ShareHistory(Base, BaseMixin, TableBase):
    """Canvas Share History.

    Canvas share history 
    """

    __tablename__ = "canvas_share_history"
    canvas_version_id = Column(BigInteger, ForeignKey("canvas_versions.id"))
    owner_id = Column(BigInteger, ForeignKey("users.id"))
    user_id = Column(BigInteger, ForeignKey("users.id"))
    canvas_id = Column(BigInteger, ForeignKey("canvases.id"))


class CloudAccount(Base, BaseMixin, TableBase):
    """CloudAccount table.

    Table where to store cloud account information 

    status:
    '''
    0: 禁用
    1: 启用
    '''
    """
    __tablename__ = "cloud_account"
    account_name = Column(Unicode(255))
    unique_id = Column(Unicode(255))
    info = Column(Text)
    platform = Column(Unicode(60))
    description = Column(Text)
    status = Column(Integer)
    user_id = Column(BigInteger, ForeignKey("users.id"))


class ThirdPartyAccount(Base, BaseMixin, TableBase):
    """Third Party Account.

    Third party account for creating user and login
    """

    __tablename__ = 'third_party_accounts'

    username = Column(Unicode(255), nullable=False)
    password = Column(CHAR(128), nullable=False)
    company = Column(Unicode(128))

    '''
    0: 禁用
    1: 启用
    2: 锁定
    3: 删除
    '''
    status = Column(SMALLINT, default=0)
    last_login_time = Column(BigInteger)
    last_login_ip = Column(Unicode(64))
