# *_*coding:utf-8 *_*
# @Author : Reggie
# @Time : 2023/3/15 13:58
import enum


class Platform(enum.Enum):
    WEB = "web"
    WINDOWS = "windows"
    ANDROID = "android"
    IOS = "ios"
    ALL = "all"
    UNDEFINED = "undefined"


class SourceModel(enum.Enum):
    UNDEFINED = "undefined"


class DestinationModel(enum.Enum):
    WEB = "web"
    WINDOWS = "windows"
    ANDROID = "android"
    IOS = "ios"
    ALL = "all"
    UNDEFINED = "undefined"
