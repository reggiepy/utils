# *_*coding:utf-8 *_*
# @Author : Reggie
# @Time : 2023/3/21 16:25
import sys
from pathlib import Path


class PyinstallerUtils:
    @classmethod
    def is_build(cls):
        if getattr(sys, 'frozen', False) and getattr(sys, '_MEIPASS', None):
            return True
        return False

    @classmethod
    def run_path(cls):
        return Path(sys._MEIPASS)
