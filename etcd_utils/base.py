# *_*coding:utf-8 *_*
# @Author : Reggie
# @Time : 2023/3/16 11:28
import abc

import etcd3


class EtcdBase(metaclass=abc.ABCMeta):
    def __init__(self):
        self.client = etcd3.client()

    def get(self, key, value):
        return self.client.put(key, value)

    def list(self, key):
        return self.client.get(key)

    def delete(self, key):
        return self.client.delete(key)

    def lock(self):
        pass

    def watch(self, key, revers):
        return self.client.watch(key, revers)


if __name__ == '__main__':
    c = EtcdBase()
