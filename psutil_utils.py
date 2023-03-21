# *_*coding:utf-8 *_*
# @Author : Reggie
# @Time : 2023/3/21 15:12
import logging

import psutil


def is_active_pid(pid):
    try:
        return psutil.Process(pid).is_running()
    except:
        return False


def kill(proc_pid, logger=None):
    logger = logger or logging.getLogger()
    process = psutil.Process(proc_pid)
    for proc in process.children(recursive=True):
        logger.info(f"kill {proc.pid}")
        proc.kill()
    logger.info(f"kill {process.pid}")
    process.kill()
