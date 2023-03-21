# *_*coding:utf-8 *_*
# @Author : Reggie
# @Time : 2023/3/21 10:39
import abc
import logging
import os
import subprocess
import threading
import time
from typing import List, Union, Callable

import psutil

from utils.command_utils import create_popen
from utils.logger_utils import common_logger


def _health_check(p: subprocess.Popen) -> bool:
    return True


class HealthCheck(metaclass=abc.ABCMeta):
    @classmethod
    @abc.abstractmethod
    def check(cls, p) -> bool:
        return True


class CommandProcessManager(object):
    def __init__(self, health_checks: Union[List[Union[Callable, _health_check, HealthCheck]], None] = None,
                 logger=None):
        self.env = dict(os.environ)
        self._stop_event = threading.Event()
        self._logger = logger or logging.getLogger()
        self.health_checks: List = health_checks or []

    def stop(self):
        self._stop_event.set()

    def run(self, cmd, shell=False):
        self._logger.info(f"Running command: {cmd}")
        p, err, rc = create_popen(cmd, shell, env=self.env)
        if rc != 0:
            self._logger.info(f"command start failed.")
            return
        self._logger.info(f"command start success. Pid: {p.pid}")
        status_ok = True
        while status_ok:
            if self._stop_event.is_set():
                self._logger.info("stop running command.")
                p.terminate()
                break
            for health_check in self.health_checks:
                if isinstance(health_check, HealthCheck):
                    health_check = HealthCheck.check
                if callable(health_check):
                    status_ok = health_check(p)
                    if not status_ok:
                        self._logger.info(f"command health check failed.")
            time.sleep(1)
        self._logger.info(f"stop command process manager.")

    def run_backend(self, cmd, shell=False):
        t = threading.Thread(target=self.run, args=(cmd, shell,))
        t.daemon = True
        t.start()


if __name__ == '__main__':
    def health_check(p):
        try:
            return psutil.Process(p.pid).is_running()
        except:
            return False

    m = CommandProcessManager(health_checks=[health_check], logger=common_logger())
    m.run_backend(r"C:/Users/wt/Desktop/etcd-v3.4.24-windows-amd64/etcd.exe --data-dir C:/Users/wt/Desktop/etcd-v3.4.24-windows-amd64/default.etcd")
    while 1:
        c = input()
        if c == "1":
            m.stop()
