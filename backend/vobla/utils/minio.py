from minio import Minio
from minio.error import (
    BucketAlreadyOwnedByYou, BucketAlreadyExists
)

from vobla.db import models
from vobla.settings import config


def get_minio_client():
    client = Minio(
        f'''{config['minio']['host']}:{config['minio']['port']}''',
        access_key=config['minio']['access_key'],
        secret_key=config['minio']['secret_key'],
        secure=False
    )
    try:
        for model in (models.Drop, models.DropFile):
            client.make_bucket(model.bucket)
    except (BucketAlreadyExists, BucketAlreadyOwnedByYou) as e:
        pass
    return client
