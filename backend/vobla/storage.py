import io
from typing import List

import boto3
from botocore.client import Config

# from minio import Minio
# from minio.error import BucketAlreadyOwnedByYou, BucketAlreadyExists

from vobla.db import models
from vobla.settings import config


class VoblaStorage:
    def get_object(self, bucket: str, hash: str):
        raise NotImplementedError

    def put_object(
        self,
        bucket_name: str,
        object_name: bytes,
        data: io.RawIOBase,
        content_type: str,
        length: int,
    ):
        raise NotImplementedError

    def remove_objects(self, bucket: str, hashes: List[str]):
        raise NotImplementedError

    def remove_object(bucket: str, hash: str):
        raise NotImplementedError


class MinioStorage(VoblaStorage):
    def __init__(self):
        self._s3 = boto3.resource(
            "s3",
            endpoint_url=f"http://{config['minio']['host']}:{config['minio']['port']}",
            aws_access_key_id=config["minio"]["access_key"],
            aws_secret_access_key=config["minio"]["secret_key"],
            config=Config(signature_version="s3v4"),
            region_name="us-east-1",
        )
        self._create_buckets()

    def _create_buckets(self):
        for model in (models.Drop, models.DropFile):
            try:
                self._s3.create_bucket(Bucket=model.bucket)
            except (
                self._s3.meta.client.exceptions.BucketAlreadyOwnedByYou,
                self._s3.meta.client.exceptions.BucketAlreadyExists,
            ):
                pass

    def get_object(self, bucket: str, key: str) -> io.RawIOBase:
        obj = self._s3.Object(bucket, key).get()
        obj_data = obj["Body"]
        return obj_data

    def put_object(
        self,
        bucket_name: str,
        object_name: bytes,
        data: io.RawIOBase,
        content_type: str,
        length: int,
    ):
        self._s3.Bucket(bucket_name).put_object(
            Key=object_name,
            Body=data.read(),
            ContentType=content_type,
        )

    def remove_object(self, bucket: str, hash: str):
        self.remove_objects(bucket, [hash])

    def remove_objects(self, bucket: str, hashes: List[str]):
        if not hashes:
            return
        self._s3.meta.client.delete_objects(
            Bucket=bucket, Delete={"Objects": [{"Key": key for key in hashes}]}
        )


def get_storage() -> VoblaStorage:
    storage_class = {
        "minio": MinioStorage,
    }[config["vobla"]["storage"]]
    return storage_class()
