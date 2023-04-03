# *_*coding:utf-8 *_*
# @Author : Reggie
# @Time : 2023/4/3 8:49
import os
import pathlib
import sys


def get_home_dir_2():
    """
    获得当前用户家目录，支持windows，linux和macosx
    更新方法，更加简单
    :return:
    """
    homedir = str(pathlib.Path.home())
    return homedir


def get_home_dir():
    """
    获得家目录
    :return:
    """
    if sys.platform == 'win32':
        homedir = os.environ['USERPROFILE']
    elif sys.platform == 'linux' or sys.platform == 'darwin':
        homedir = os.environ['HOME']
    else:
        raise NotImplemented(f'Error! Not this system. {sys.platform}')
    return homedir


