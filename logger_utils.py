# *_*coding:utf-8 *_*
# @Author : Reggie
# @Time : 2023/3/21 12:58
import logging


class LoggerUtils:
    LONG_FORMATTER = logging.Formatter(
        "%(asctime)s -- %(levelname)s -- %(message)s (%(funcName)s in %(filename)s):%(lineno)d]")
    STANDARD_FORMATTER = logging.Formatter("%(asctime)s -- %(levelname)s -- %(message)s")
    SHORT_FORMATTER = logging.Formatter("%(levelname)s -- %(message)s")
    FREE_FORMATTER = logging.Formatter("%(message)s")

    @classmethod
    def common_console_logger(
            cls,
            log_name=None,
            formatter: logging.Formatter = LONG_FORMATTER
    ):
        logger = logging.getLogger(log_name)
        handle = logging.StreamHandler()
        handle.setFormatter(formatter)
        logger.addHandler(handle)
        logger.setLevel("DEBUG")
        return logger

    @classmethod
    def common_file_logger(
            cls,
            filename,
            log_name=None,
            formatter: logging.Formatter = LONG_FORMATTER,
            mode='a',
            encoding=None
    ):
        logger = logging.getLogger(log_name)
        handle = logging.FileHandler(filename, mode=mode, encoding=encoding)
        handle.setFormatter(formatter)
        logger.addHandler(handle)
        logger.setLevel("DEBUG")
        return logger
