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

from utils.command_utils import Command
from utils.logger_utils import common_logger
from utils.psutil_utils import Psutil


def _health_check(p: subprocess.Popen) -> bool:
    return True


def _process_stop_callback(self):
    pass


class HealthCheck(metaclass=abc.ABCMeta):
    @classmethod
    @abc.abstractmethod
    def check(cls, p) -> bool:
        return True


class CommandProcessManager(object):
    def __init__(
            self,
            cmd,
            env: Union[dict, None] = None,
            shell=False,
            health_checks: Union[List[Union[Callable, _health_check, HealthCheck]], None] = None,
            logger=None,
            process_stop_callback: Callable = None,
            process_logger=None,
    ):
        self.cmd = cmd
        self.process_logger = process_logger
        if isinstance(self.process_logger, str):
            self.process_logger = logging.getLogger(self.process_logger)
        if not isinstance(self.process_logger, logging.Logger):
            self.process_logger = logging.getLogger("command_process_manager.process_logger")
        self.shell = shell
        self.cmd_env = dict(os.environ)
        self.env = env or {}
        if env is not None:
            for k, v in env.items():
                self.cmd_env[k] = v
        self._stop_event = threading.Event()
        self._is_stop_event = threading.Event()
        self._logger = logger or logging.getLogger()
        self.health_checks: List = health_checks or []
        self.is_running = True
        self.process_stop_callback: Union[Callable, _process_stop_callback] = process_stop_callback

    def stop(self):
        self._stop_event.set()
        self._is_stop_event.wait(2)
        return True

    def thread_read(self, p):
        def handle():
            while not self._is_stop_event.is_set():
                line = p.stderr.readline()  # blocking read
                self.process_logger.info(line.rstrip().decode('utf-8'))

        t = threading.Thread(target=handle)
        t.daemon = True
        t.start()

    def run(self):
        self._logger.info(f"Running command: {self.cmd} {' '.join([f'{k}:{v}' for k, v in self.env.items()])}")
        p, err, rc = Command.create_popen(self.cmd, self.shell, env=self.cmd_env)
        if rc != 0:
            self._logger.info(f"command: {self.cmd} start failed.")
            return
        self._logger.info(f"command: {self.cmd} [{p.pid}] start success.")
        self.is_running = True
        self.thread_read(p)
        while self.is_running:
            if self._stop_event.is_set():
                self._logger.info(f"stop running command: {self.cmd}")
                p.terminate()
                break
            if not Psutil.is_active_pid(p.pid):
                if callable(self.process_stop_callback):
                    self.process_stop_callback(self)
                self._logger.info(f"command: {self.cmd} process [{p.pid}] is killed.")
                break
            for health_check in self.health_checks:
                if isinstance(health_check, HealthCheck):
                    health_check = HealthCheck.check
                if callable(health_check):
                    status_ok = health_check(p)
                    if not status_ok:
                        self._logger.info(f"command: {self.cmd} health check failed.")
            time.sleep(1)
        self._logger.info(f"stop command: {self.cmd} process [{p.pid}] manager.")
        self._is_stop_event.set()

    def run_backend(self):
        t = threading.Thread(target=self.run)
        t.daemon = True
        t.start()


if __name__ == '__main__':
    def health_check(p):
        try:
            return psutil.Process(p.pid).is_running()
        except:
            return False


    cmd = r"C:/Users/wt/Desktop/etcd-v3.4.24-windows-amd64/etcd.exe --data-dir C:/Users/wt/Desktop/etcd-v3.4.24-windows-amd64/default.etcd"
    m = CommandProcessManager(cmd=cmd, health_checks=[health_check], logger=common_logger())
    m.run_backend()
    while 1:
        c = input()
        if c == "1":
            print(m.stop())
