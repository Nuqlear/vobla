#!/usr/bin/env python
import argparse
import sys

import alembic.config
from celery.bin import worker
import pytest
import tornado.platform
import tornado.httpserver
import tornado.ioloop
import tornado.web

from vobla.settings import config
from vobla.app import TornadoApplication
from vobla.tasks import celery_app
from vobla.db.engine import create_engine
from vobla.db.models import UserInvite


TESTS_FOLDER = 'tests'


def run_server():
    tornado.platform.asyncio.AsyncIOMainLoop().install()
    app = TornadoApplication()
    app.listen(config['vobla']['port'])
    loop = tornado.ioloop.IOLoop.current()
    loop.start()


def run_migrations():
    alembic_args = [
        '--raiseerr',
        'upgrade', 'head',
    ]
    alembic.config.main(argv=alembic_args)


def run_tests():
    sys.exit(pytest.main(['-vv', TESTS_FOLDER]))


def create_invite():
    tornado.platform.asyncio.AsyncIOMainLoop().install()
    loop = tornado.ioloop.IOLoop.current().asyncio_loop

    async def _create_invite():
        eng = await create_engine(loop)
        async with eng.acquire() as pgc:
            ui = await UserInvite.create(pgc)
            print(ui.code)

    loop.run_until_complete(_create_invite())


def run_worker():
    worker.worker(app=celery_app).run(**config['celery'])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-m", "--migrate", help="run migrations", action="store_true"
    )
    parser.add_argument(
        "command", type=str, choices=[
            'migrate', 'runserver', 'runworker', 'runtests', 'createinv'
        ]
    )
    args = parser.parse_args()
    if args.command == 'migrate' or args.migrate:
        run_migrations()
    if args.command == 'runserver':
        run_server()
    elif args.command == 'createinv':
        create_invite()
    elif args.command == 'runtests':
        run_tests()
    elif args.command == 'runworker':
        run_worker()
