import os
import shutil

from celery import Celery

from vobla.settings import config


celery_app = Celery(__name__)
celery_app.config_from_object(config['celery'])


@celery_app.task
def rmtree(*paths):
    for path in paths:
        if os.path.isfile(path):
            os.unlink(path, dir_fd=None)
        else:
            shutil.rmtree(path)
