# *_*coding:utf-8 *_*
# @Author : Reggie
# @Time : 2023/3/21 15:12
from typing import Any

import psutil


class Psutil:
    @classmethod
    def is_active_pid(cls, pid):
        try:
            return psutil.Process(pid).is_running()
        except:
            return False

    @classmethod
    def kill(cls, proc_pid):
        process = psutil.Process(proc_pid)
        for proc in process.children(recursive=True):
            proc.kill()
        process.kill()

    @classmethod
    def kill_by_name(cls, proc_name) -> (psutil.Process, str, int):
        proc, msg, rc = cls.get_process_by_name(proc_name)
        if rc != 0:
            return None, msg, rc
        if proc:
            proc.kill()
            return proc, "success", 0
        return None, "proc not found", 1

    @classmethod
    def get_process_by_name(cls, proc_name) -> (psutil.Process, str, int):
        for proc in psutil.process_iter():
            # check whether the process name matches
            if proc.name() == proc_name:
                return proc, "success", 0
        return None, "proc not found", 1
