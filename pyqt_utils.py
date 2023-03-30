# *_*coding:utf-8 *_*
# @Author : Reggie
# @Time : 2023/3/29 10:40
import logging

from PyQt5 import QtWidgets

from utils.command_utils import CommandProcessManager


class QTextEditLogger(logging.Handler):
    def __init__(self, widget: QtWidgets.QPlainTextEdit):
        super().__init__()
        self.widget = widget
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.appendPlainText(msg)


class QTextBrowserLogger(logging.Handler):
    def __init__(self, browser: QtWidgets.QTextBrowser, max_block_count=1000):
        super().__init__()
        self.browser = browser
        self.browser.document().setMaximumBlockCount(max_block_count)

    def emit(self, record):
        msg = self.format(record)
        self.browser.append(msg)


class QtCommandProcessManager(CommandProcessManager):
    def process_logger_handler(self, p):
        pass
