# *_*coding:utf-8 *_*
# @Author : Reggie
# @Time : 2023/3/16 11:28
import json
import logging
from pathlib import Path
from typing import Any

import etcd3
from etcd3.client import KVMetadata
from pydantic import BaseModel, Field

from utils.logger_utils import LoggerUtils


class AlreadyExistsException(Exception):
    def __str__(self):
        return "key already exists"


class EtcdMetadata(BaseModel):
    meta: KVMetadata = Field(None, exclude=True)

    class Config:
        arbitrary_types_allowed = True


class EtcdClearData(EtcdMetadata):
    key: str = Field(..., description="key")
    status: bool = Field(False, description="delete status")


class EtcdData(EtcdMetadata):
    key: Any = Field(..., description="key")
    value: Any = Field(..., description="value")


class EtcdClient:
    def __init__(self, prefix, logger=None):
        self.client = etcd3.client(host="127.0.0.1")
        self.prefix = prefix
        self.lock_prefix = ""
        self._logger = logging.getLogger("etcd3.client")
        if isinstance(logger, str):
            logger = logging.getLogger(logger)
            if logger is not logging.root:
                self._logger = logger
        elif isinstance(logger, logging.Logger):
            self._logger = logger

    def real_key(self, key):
        return Path(self.prefix).joinpath(key).as_posix()

    def set(self, key, value, force=True):
        real_key = self.real_key(key)
        with self.client.lock(key):
            data = self.get(real_key)
            if data and not force:
                raise AlreadyExistsException()
            data = EtcdData(key=key, value=value)
            self.client.put(real_key, data.json(ensure_ascii=False))
            return data

    def get(self, key, default=None):
        real_key = self.real_key(key)
        value, meta = self.client.get(real_key)
        try:
            value = json.loads(value).get('value')
            return EtcdData(key=key, value=value, meta=meta)
        except Exception as e:
            return default

    def list(self):
        result = []
        for value, meta in self.client.get_prefix(self.prefix):
            try:
                key = meta.key.decode("utf-8")
                k = key.replace(f"{self.prefix}/", "")
                value = json.loads(value)
                v = value.get("value")
                data = EtcdData(key=k, value=v, meta=meta)
            except:
                self._logger.error(f"Unable to parse {meta.key} value: {value}.")
            else:
                result.append(data)
        return result

    def list_dict_result(self):
        result = {}
        for item in self.list():
            result[item.key] = item.value
        return result

    def delete(self, key):
        with self.client.lock(key):
            return self.client.delete(self.real_key(key))

    def update(self, key, *args, **kwargs):
        real_key = self.real_key(key)
        with self.client.lock(real_key):
            data = self.get(key)
            if data is not None:
                if args:
                    data.value = args[0]
                else:
                    for k, v in kwargs.items():
                        if not isinstance(data.value, dict):
                            raise Exception(f"{k} value not is dict. {data.value}")
                        data.value[k] = v
            else:
                if args:
                    value = args[0]
                else:
                    value = kwargs
                data = EtcdData(key=real_key, value=value)
            self.client.put(real_key, value=data.json(ensure_ascii=False))
            return data

    def pop(self, key, default_value=None, value_callback=None):
        default_value = default_value or {}
        real_key = self.real_key(key)
        with self.client.lock(real_key):
            data = self.get(key)
            if value_callback and callable(value_callback):
                value = value_callback(data.value)
            else:
                value = default_value
            self.client.put(
                real_key,
                value=EtcdData(
                    key=data.key,
                    value=value
                ).json(ensure_ascii=False)
            )
            return data

    def watch(self, key):
        """
        :example:
            c = EtcdBase("/test")
            events_iterator, cancel = c.watch("1")
            for event in events_iterator:
                print(event)
        :param key:
        :return: events_iterator, cancel
        """
        real_key = self.real_key(key)
        self._logger.debug(f"watch key: {real_key}")
        return self.client.watch_prefix(self.real_key(key))

    def watch_prefix(self, prefix=None):
        """
        :example:
            c = EtcdBase("/test")
            events_iterator, cancel = c.watch_prefix("/")
            for event in events_iterator:
                print(event)
        :param prefix:
        :return: events_iterator, cancel
        """
        prefix = prefix or self.prefix
        self._logger.debug(f"watch key: {prefix}")
        return self.client.watch_prefix(prefix)

    def clear(self):
        result = []
        for v, meta in self.client.get_prefix(self.prefix):
            key = meta.key.decode("utf-8")
            k = key.replace(f"{self.prefix}/", "")
            result.append(EtcdClearData(key=k, status=self.delete(key), meta=meta))
        return result

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()


def t_watch_prefix():
    c = EtcdClient("/config")
    events_iterator, cancel = c.watch_prefix("/")
    for event in events_iterator:
        print(event)


def t_curd():
    import time
    start = time.time()
    c = EtcdClient("/config")
    print(1, time.time() - start)
    ret = c.get("t")
    print(2, time.time() - start)
    print("get", ret)
    start = time.time()
    ret = c.get("t")
    print(3, time.time() - start)
    print("get", ret)
    ret = c.update("v", test=1)
    print(3, time.time() - start)
    print("get", ret)
    ret = c.update("v", {"dddd": 3})
    print(3, time.time() - start)
    print("get", ret)
    # ret = c.delete("t")
    # print("delete", ret)
    # ret = c.set("key3", 1)
    # print("set", ret)
    # ret = c.set("key4", {"test": 1})
    # print("set", ret)
    # ret = c.update("key4", **{"test": 2})
    # print("update", ret)
    # ret = c.set("key3/t", 1)
    # print("set", ret)
    # ret = c.get("key3")
    # print("get", ret)
    # ret = c.list()
    # print("list", ret)
    # ret = c.list_dict_result()
    # print("list_dict_result", ret)
    # ret = c.pop("key4")
    # print("pop", ret)
    # ret = c.delete("key4")
    # print("delete", ret)
    # ret = c.clear()
    # print("clear", ret)


if __name__ == '__main__':
    LoggerUtils.common_console_logger()
    t_curd()
