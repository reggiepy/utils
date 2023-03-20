# *_*coding:utf-8 *_*
# @Author : Reggie
# @Time : 2023/3/16 11:28
import abc
import logging
from pathlib import Path

import etcd3


class EtcdBase(metaclass=abc.ABCMeta):
    def __init__(self, prefix, logger=None):
        self.client = etcd3.client()
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

    def set(self, key, value):
        real_key = self.real_key(key)
        with self.client.lock(key):
            return self.client.put(real_key, value)

    def get(self, key):
        real_key = self.real_key(key)
        return self.client.get(real_key)

    def list(self):
        result = []
        for v, _ in self.client.get_prefix(self.prefix):
            result.append(v)
        return result

    def list_key_kv(self, key):
        real_key = self.real_key(key)
        result = {}
        for v, KVMetadata in self.client.get_prefix(real_key):
            k = KVMetadata.key
            for k in k.decode("utf-8").rsplit("/", 1)[-1:]:
                result[k] = v
        return result

    def gen_key_k(self, key, k):
        return Path(self.real_key(key)).joinpath(k).as_posix()

    def set_key_k(self, key, k, v):
        real_key_k = self.gen_key_k(key, k)
        with self.client.lock(real_key_k):
            return self.client.put(real_key_k, v)

    def delete_key_k(self, key, k):
        real_key_k = self.gen_key_k(key, k)
        return self.delete(real_key_k)

    def delete_key_all_k(self, key):
        result = []
        real_key = self.real_key(key)
        for v, KVMetadata in self.client.get_prefix(real_key):
            key = KVMetadata.key
            for k in key.decode("utf-8").rsplit("/", 1)[-1:]:
                break
            else:
                continue
            result.append(self.delete(k))
        return result

    def delete(self, key):
        with self.client.lock(key):
            return self.client.delete(self.real_key(key))

    def delete_prev_kv(self, key):
        return self.client.delete(self.real_key(key), prev_kv=True, return_response=True)

    def watch(self, key):
        real_key = self.real_key(key)
        self._logger.debug(f"watch key: {real_key}")
        return self.client.watch_prefix(self.real_key(key))

    def clear(self):
        result = []
        for v, KVMetadata in self.client.get_prefix(self.prefix):
            key = KVMetadata.key
            for k in key.decode("utf-8").rsplit("/", 1)[-1:]:
                break
            else:
                continue
            result.append(self.delete(k))
        return result

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()


if __name__ == '__main__':
    root_logger = logging.getLogger()
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s (%(funcName)s in %(filename)s %(lineno)d)")
    stream_handle = logging.StreamHandler()
    stream_handle.setFormatter(formatter)
    root_logger.addHandler(stream_handle)
    root_logger.setLevel("DEBUG")

    c = EtcdBase("/config")
    # for i in c.watch("/"):
    #     print(i)

    ret = c.set("key", "1")
    print("set", ret)
    ret = c.get("key")
    print("get", ret)
    ret = c.list()
    print("list", ret)
    ret = c.list_key_kv("key")
    print("list_kv", ret)
    ret = c.delete_prev_kv("key")
    print("delete_prev_kv", ret)
