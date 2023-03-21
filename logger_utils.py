# *_*coding:utf-8 *_*
# @Author : Reggie
# @Time : 2023/3/21 12:58
import logging


def common_logger():
    root_logger = logging.getLogger()
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s (%(funcName)s in %(filename)s %(lineno)d)")
    stream_handle = logging.StreamHandler()
    stream_handle.setFormatter(formatter)
    root_logger.addHandler(stream_handle)
    root_logger.setLevel("DEBUG")
    return root_logger
