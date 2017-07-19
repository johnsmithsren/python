#!/usr/bin/env python
# coding=utf-8
from __future__ import unicode_literals

from jiagouyun import config
from jiagouyun.utils import getLogger
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
# from flask import session

logger = getLogger(__name__)


engine = create_engine(config['database']['connection'].replace("mysql://", "mysql+pymysql://"),
                       pool_size=5, max_overflow=5, pool_recycle=3600, poolclass=QueuePool)
Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.exception(e)
        raise
    finally:
        session.close()
