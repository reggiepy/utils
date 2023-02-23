# *_*coding:utf-8 *_*
# @Author : Reggie
# @Time : 2022/12/13 11:07
from rest_framework import serializers


class MyImageField(serializers.ImageField):
    def to_representation(self, value):
        try:
            url = value.url
        except AttributeError:
            return value.name
        except ValueError:
            return ""
        else:
            return url
