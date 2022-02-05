import os
import shutil
import tempfile
import subprocess
from io import BytesIO

import magic
from sqlalchemy import create_engine, and_
from celery import Celery, Task
from celery.signals import worker_init

from vobla.db import models
from vobla.db.engine import get_engine_params
from vobla.settings import config
from vobla.storage import get_storage
from vobla.utils.mimetypes import get_mimetype_preview


celery_app = Celery(__name__)
celery_app.config_from_object(config["celery"])


class BaseTask(Task):
    @classmethod
    def create_engine(cls):
        params = get_engine_params()
        cls.engine = create_engine(
            "postgresql://{user}:{password}@{host}/{database}".format(
                user=params["user"],
                password=params["password"],
                host=params["host"],
                database=params["database"],
            )
        )

    @classmethod
    def create_storage_client(cls):
        cls.storage = get_storage()


@worker_init.connect
def configure_workers(*args, **kwargs):
    BaseTask.create_engine()
    BaseTask.create_storage_client()


def get_drop_file_images(*, temp_folder, rows, storage):
    for drop_file in (models.DropFile._construct_from_row(row) for row in rows):
        drop_file_path = os.path.join(temp_folder, drop_file.hash)
        if drop_file.mimetype.startswith("image/"):
            with open(drop_file_path, "wb+") as f:
                for d in drop_file.get_from_storage(storage).iter_chunks(32 * 1024):
                    f.write(d)
        else:
            drop_file_path = get_mimetype_preview(drop_file.mimetype)
        yield drop_file_path


@celery_app.task(base=BaseTask, bind=True)
def generate_previews(self, drop_id: int):
    with self.engine.begin() as conn:
        rows = conn.execute(
            models.DropFile.t.select().where(
                and_(
                    models.DropFile.c.drop_id == drop_id,
                    models.DropFile.c.uploaded_at.isnot(None),
                )
            )
        ).fetchall()
        if rows:
            temp_folder = tempfile.mkdtemp()
            try:
                images = get_drop_file_images(
                    temp_folder=temp_folder, rows=rows, storage=self.storage
                )
                if len(rows) == 1:
                    image = str(next(images))
                    if not int(config["vobla"]["animated_previews"]):
                        image += "[0]"
                    cmd = [
                        "convert",
                        image,
                        "-thumbnail",
                        "150x100^",
                        "-gravity",
                        "center",
                        "-extent",
                        "150x100",
                        "-",
                    ]
                else:
                    cmd = [
                        "montage",
                        # [0] should be added otherwise all gif frames will be displayed
                        *map(lambda im: f"{im}[0]", images),
                        "-geometry",
                        "150x100^",
                        "-",
                    ]
                process = subprocess.Popen(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                data, error = process.communicate()
                content_type = magic.from_buffer(data, mime=True)
                self.storage.put_object(
                    bucket_name=models.Drop.bucket,
                    object_name=models.Drop.encode(drop_id),
                    data=BytesIO(data),
                    content_type=content_type,
                    length=len(data),
                )
                conn.execute(
                    models.Drop.t.update()
                    .values(is_preview_ready=True)
                    .where(models.Drop.c.id == drop_id)
                )
            finally:
                shutil.rmtree(temp_folder)
