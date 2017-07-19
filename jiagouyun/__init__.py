#!/usr/bin/env python
# coding=utf-8
"""Initial the project.

Offer config object for all the project.
"""
from __future__ import unicode_literals

import os
import yaml

base_path = os.path.dirname(os.path.abspath(__file__))
config = {}
with open(base_path + "/../config/config.yaml") as f:
    config = yaml.load(f)
