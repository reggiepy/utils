# *_*coding:utf-8 *_*
# @Author : Reggie
# @Time : 2022/12/6 10:26
from django.core.files.storage import Storage


class OssStorage(Storage):
    path = ""

    def __init__(self, path: str = "", *args, **kwargs):
        self.path = path
        if not path.endswith("/"):
            self.path = self.path + "/"

    def save(self, name, content, max_length=None):
        """
        文件保存
        :param name: 上传时的文件名称，包含后缀名
        :param content: 文件内容,File对象
        :param max_length: 文件最大二进制长度
        :return: 文件路径
        """
        # todo 处理保存文件逻辑，返回相对文件路径
        pass

    def delete(self, name):
        """
        删除文件
        :param name: 相对路径文件名，此处并非上传时的文件名，而是在save()函数中返回的文件名
        :return:
        """
        # todo 处理删除文件逻辑，无返回
        pass

    def url(self, name):
        """
        返回文件的url地址
        :param name: 相对路径文件名，此处并非上传时的文件名，而是在save()函数中返回的文件名
        :return:
        """
        # todo 处理返回文件url逻辑，返回文件的url地址

    def path(self, name):
        """
        返回文件的相对路径地址
        :param name: 相对路径文件名，此处并非上传时的文件名，而是在save()函数中返回的文件名
        :return: 相对路径地址
        """
        # todo 处理返回文件相对路径地址，一般返回name自身或者与url()一致，具体看自身业务逻辑

    def open(self, name, mode='rb'):
        """
        打开文件操作，一般pass即可
        :param name: 相对路径文件名，此处并非上传时的文件名，而是在save()函数中返回的文件名
        :param mode: 打开方式，默认'rb'
        :return:
        """
