#!/usr/bin/env python
# coding=utf-8
"""Utilizations.

Jiagouyun utilizations like logger and encrypt.
"""
from __future__ import unicode_literals

import logging
import logging.handlers
from hashlib import sha256

from jiagouyun import config


def getLogger(name):
    """Get a logger.

    Get a logger for "name"
    """
    logger = logging.getLogger(name)
    watched_file_handler = logging.handlers.WatchedFileHandler(config['logging']['file'])
    watched_file_handler.setLevel(config['logging']['level'])
    watched_file_handler.setFormatter(logging.Formatter('%(name)s %(asctime)s %(levelname)8s %(message)s'))
    logger.addHandler(watched_file_handler)
    logger.setLevel(config['logging']['level'])
    return logger


def encrypt(password, salt):
    """Encrypt passwords.

    Encrypt the password using salt
    """
    _sha = sha256(password)
    _sha.update(str(salt))
    _sha.update(config['security']['secret_key'])
    return _sha.hexdigest()
