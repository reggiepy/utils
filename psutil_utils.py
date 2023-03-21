# *_*coding:utf-8 *_*
# @Author : Reggie
# @Time : 2023/3/21 15:12
import logging

import psutil


class Psutil:
    @classmethod
    def is_active_pid(cls, pid):
        try:
            return psutil.Process(pid).is_running()
        except:
            return False

    @classmethod
    def kill(cls, proc_pid, logger=None):
        logger = logger or logging.getLogger()
        process = psutil.Process(proc_pid)
        for proc in process.children(recursive=True):
            logger.info(f"kill {proc.pid}")
            proc.kill()
        logger.info(f"kill {process.pid}")
        process.kill()

    @classmethod
    def kill_by_name(cls, proc_name, logger=None):
        logger = logger or logging.getLogger()
        for proc in psutil.process_iter():
            # check whether the process name matches
            if proc.name() == proc_name:
                logger.info(f"kill {proc_name}")
                proc.kill()
