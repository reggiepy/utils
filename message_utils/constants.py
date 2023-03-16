# *_*coding:utf-8 *_*
# @Author : Reggie
# @Time : 2023/3/15 13:58
import enum


class PlatformEnum(enum.Enum):
    WEB = "web"
    WINDOWS = "windows"
    ANDROID = "android"
    IOS = "ios"
    ALL = "all"
    UNDEFINED = "undefined"


class SourceEnum(enum.Enum):
    UNDEFINED = "undefined"


class DestinationEnum(enum.Enum):
    WEB = "web"
    WINDOWS = "windows"
    ANDROID = "android"
    IOS = "ios"
    ALL = "all"
    UNDEFINED = "undefined"


class FlagEnum(enum.Enum):
    CHEMICAL = "chemical"
