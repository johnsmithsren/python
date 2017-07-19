#!/usr/bin/env python
# coding=utf-8
"""Entry of the program

Example:
python web.py start_dev --host 127.0.0.1 --port 5000 --wokers=1
"""
from __future__ import unicode_literals

import argparse

from gevent import monkey
from gevent.pywsgi import WSGIServer
from gevent.pool import Pool


from jiagouyun.app import app
from jiagouyun.utils import getLogger
import werkzeug.serving


def register_blueprints():
    from jiagouyun.routes.auth import auth_bp
    from jiagouyun.routes.canvas import canvas_bp
    from jiagouyun.routes.third_party import third_party_bp
    from jiagouyun.routes.cloud_account import cloud_account_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(canvas_bp, url_prefix="/canvas")
    app.register_blueprint(cloud_account_bp, url_prefix="/cloud_account")
    app.register_blueprint(third_party_bp, url_prefix="/third_party")


def db_sync():
    from jiagouyun.models import entities
    from jiagouyun.models import engine
    entities.Base.metadata.create_all(engine)


def start_dev(host="127.0.0.1", port=5000, workers=1):
    # werkzeug.serving.run_with_reloader()
    # register blueprints
    register_blueprints()
    # set debug mode
    app.debug = True

    @werkzeug.serving.run_with_reloader
    def run_server():
        "Start gevent WSGI server"
        monkey.patch_all()
        # use gevent WSGI server instead of the Flask
        http = WSGIServer((host, port), app.wsgi_app,
                          spawn=Pool(1), log=getLogger("wsgi"))
        # TODO gracefully handle shutdown
        http.serve_forever()

    run_server()


def start(host="127.0.0.1", port=5000, workers=1):
    register_blueprints()
    # set debug mode
    app.debug = False
    "Start gevent WSGI server"
    from gevent import monkey

    monkey.patch_all()
    # use gevent WSGI server instead of the Flask
    http = WSGIServer((host, port), app.wsgi_app,
                      spawn=Pool(workers), log=getLogger("wsgi"))
    # TODO gracefully handle shutdown
    http.serve_forever()


def main():
    parser = argparse.ArgumentParser(description='Start web server.')
    parser.add_argument('action', metavar='action', type=str,
                        help='start_dev or start')

    parser.add_argument('--host', dest='host',
                        default="127.0.0.1",
                        help='bind host(default: 127.0.0.1)')
    parser.add_argument('--port', dest='port', type=int,
                        default=5000,
                        help='bind port(default: 5000)')

    parser.add_argument('--workers', dest='workers', type=int,
                        default=1,
                        help='bind port(default: 5000)')
    args = parser.parse_args()
    if args.action == "start":
        start(args.host, args.port, args.workers)
    elif args.action == "start_dev":
        start_dev(args.host, args.port, args.workers)
    elif args.action == 'db_sync':
        db_sync()


if __name__ == "__main__":
    main()
