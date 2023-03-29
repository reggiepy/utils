# *_*coding:utf-8 *_*
# @Author : Reggie
# @Time : 2023/3/29 10:40
import logging

from PyQt5 import QtWidgets


class QTextEditLogger(logging.Handler):
    def __init__(self, parent):
        super().__init__()
        self.widget = QtWidgets.QPlainTextEdit(parent)
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)
