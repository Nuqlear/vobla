import os
import shutil

from sqlalchemy import create_engine
from celery import Celery
from celery.task import Task
# from celery.signals import worker_init

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


#
# @worker_init.connect
# def configure_workers(*args, **kwargs):
#     BaseTask.engine = create_engine(**get_engine_params())


@celery_app.task(base=BaseTask)
def rmtree(*paths):
    for path in paths:
        if os.path.isfile(path):
            os.unlink(path, dir_fd=None)
        else:
            shutil.rmtree(path)

#
# @celery_app.task(base=BaseTask, bind=True)
# def generate_previews(
#     self, drop_id
# ):
#     pass
