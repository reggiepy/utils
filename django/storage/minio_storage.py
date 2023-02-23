import logging
import mimetypes
import os
import uuid
from pathlib import Path

from django.conf import settings
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible
from minio import Minio, S3Error

logger = logging.getLogger()


def setting(name, default=None):
    """
    Helper function to get a Django setting by name or (optionally) return
    a default (or else ``None``).
    """
    return getattr(settings, name, default)


@deconstructible
class MinioStorage(Storage):
    # TODO: Log errors caused by exceptions
    server = setting('MINIO_SERVER')
    access_key = setting('MINIO_ACCESSKEY')
    secret_key = setting('MINIO_SECRET')
    secure = setting('MINIO_SECURE')
    minio_bucket = setting('MINIO_BUCKET')

    def __init__(self, bucket=None, show_abs_url=False, abs_host=None, *args, **kwargs):
        self._connection = None
        self.bucket = bucket or self.minio_bucket
        self.show_abs_url = show_abs_url
        self.abs_host = abs_host or self.server

    @property
    def connection(self):
        if not self._connection:
            try:
                self._connection = Minio(
                    endpoint=self.server,
                    access_key=self.access_key,
                    secret_key=self.secret_key,
                    secure=self.secure
                )
            except Exception as e:
                logger.error('Exception while connecting to minio server: %s', e)
                self._connection = None
        return self._connection

    def _save(self, name, content):
        name = Path(name).as_posix()
        content_type = content.content_type if hasattr(content, 'content_type') else mimetypes.guess_type(name)[0]

        if self.connection:
            if not self.connection.bucket_exists(self.bucket):
                self.connection.make_bucket(self.bucket)
            try:
                self.connection.put_object(
                    self.bucket,
                    name,
                    content,
                    content.size,
                    content_type=content_type,
                )
            except S3Error as err:
                raise IOError(f'Could not stat file {name} {err}')
        return name

    def exists(self, name):
        try:
            self.connection.stat_object(self.bucket, name)
        except S3Error as err:
            raise IOError(f'Could not stat file {name} {err}')
        else:
            return True

    def size(self, name):
        return self.connection.stat_object(self.bucket, self.bucket_file_path(name)).size

    def get_available_name(self, name, max_length=None):
        return name

    def save(self, name, content, max_length=None):
        """
        文件保存
        :param name: 上传时的文件名称，包含后缀名
        :param content: 文件内容,File对象
        :param max_length: 文件最大二进制长度
        :return: 文件路径
        """
        # todo 处理保存文件逻辑，返回相对文件路径
        return super().save(name, content, max_length)

    def delete(self, name):
        """
        删除文件
        :param name: 相对路径文件名，此处并非上传时的文件名，而是在save()函数中返回的文件名
        :return:
        """
        # todo 处理删除文件逻辑，无返回
        if not self.connection:
            raise Exception("not connection!")
        self.connection.remove_object(self.bucket, name)

    def url(self, name):
        """
        返回文件的url地址
        :param name: 相对路径文件名，此处并非上传时的文件名，而是在save()函数中返回的文件名
        :return:
        """
        # todo 处理返回文件url逻辑，返回文件的url地址
        if self.show_abs_url:
            return f"http{'s' if self.secure else ''}://{self.abs_host}/" \
                   f"{self.bucket}{'' if name.startswith('/') else '/'}{name}"
        return f"/{self.bucket}/{name}"

    def path(self, name):
        """
        返回文件的相对路径地址
        :param name: 相对路径文件名，此处并非上传时的文件名，而是在save()函数中返回的文件名
        :return: 相对路径地址
        """
        # todo 处理返回文件相对路径地址，一般返回name自身或者与url()一致，具体看自身业务逻辑
        return self.url(name)

    def open(self, name, mode='rb'):
        """
        打开文件操作，一般pass即可
        :param name: 相对路径文件名，此处并非上传时的文件名，而是在save()函数中返回的文件名
        :param mode: 打开方式，默认'rb'
        :return:
        """
        pass

    def generate_filename(self, filename):
        dirname, filename = os.path.split(filename)
        uid = uuid.uuid4().hex.lower()
        return Path(dirname).joinpath(f"{uid}-{self.get_valid_name(filename)}").as_posix()

    def get_valid_name(self, name):
        """
        Return a filename, based on the provided filename, that's suitable for
        use in the target storage system.
        """
        return super().get_valid_name(name)
