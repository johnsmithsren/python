#!/usr/bin/env python
# coding=utf-8

from jinja2 import Environment, PackageLoader
env = Environment(loader=PackageLoader('jiagouyun', 'templates'))


def render(template_name, params):
    template = env.get_template(template_name)

    return template.render(**params)
