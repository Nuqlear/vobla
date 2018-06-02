import os
import shutil
import subprocess

from sqlalchemy import create_engine, and_
from celery import Celery
from celery.task import Task
from celery.signals import worker_init

from vobla.db import models
from vobla.db.engine import get_engine_params
from vobla.settings import config


celery_app = Celery(__name__)
celery_app.config_from_object(config['celery'])


class BaseTask(Task):

    @classmethod
    def create_engine(cls):
        params = get_engine_params()
        cls.engine = create_engine(
            'postgresql://{user}:{password}@{host}/{database}'.format(
                user=params['user'],
                password=params['password'],
                host=params['host'],
                database=params['database'],
            )
        )


@worker_init.connect
def configure_workers(*args, **kwargs):
    BaseTask.create_engine()


@celery_app.task(base=BaseTask)
def rmtree(*paths):
    for path in paths:
        if os.path.isfile(path):
            os.unlink(path, dir_fd=None)
        else:
            shutil.rmtree(path)


@celery_app.task(base=BaseTask, bind=True)
def generate_previews(self, drop_id: int):
    with self.engine.begin() as conn:
        rows = conn.execute(
            models.DropFile.t.select()
            .where(and_(
                models.DropFile.c.drop_id == drop_id,
                models.DropFile.c.uploaded_at.isnot(None),
                models.DropFile.c.mimetype.ilike('image/%')
            ))
        ).fetchall()
        if rows:
            images = (
                models.DropFile._construct_from_row(row).file_path
                for row in rows
            )
            destination = models.Drop._construct_from_row(
                conn.execute(
                    models.Drop.t.select()
                    .where(models.Drop.c.id == drop_id)
                ).fetchone()
            ).preview_path
            if len(rows) == 1:
                cmd = [
                    'convert', next(images), '-thumbnail', '150x100^',
                    '-gravity', 'center', '-extent', '150x100', destination
                ]
            else:
                cmd = [
                    'montage', *images, '-geometry', '150x100^', destination
                ]
            try:
                subprocess.check_call(cmd, stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as e:
                raise
            conn.execute(
                models.Drop.t.update()
                .values(is_preview_ready=True)
                .where(models.Drop.c.id == drop_id)
            )
