# *_*coding:utf-8 *_*
# @Author : Reggie
# @Time : 2023/3/29 10:40
import logging

from PyQt5 import QtWidgets


class QTextEditLogger(logging.Handler):
    def __init__(self, widget: QtWidgets.QPlainTextEdit):
        super().__init__()
        self.widget = widget
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)


class QTextBrowserLogger(logging.Handler):
    def __init__(self, browser: QtWidgets.QTextBrowser):
        super().__init__()
        self.browser = browser
        self.browser.document().setMaximumBlockCount(1000)

    def emit(self, record):
        msg = self.format(record)
        self.browser.append(msg)
