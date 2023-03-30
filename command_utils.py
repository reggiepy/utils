# *_*coding:utf-8 *_*
# @Author : Reggie
# @Time : 2023/3/21 13:14
import abc
import json
import logging
import os
import shlex
import subprocess
import threading
import time
from pathlib import Path
from typing import List, Union, Callable
from typing import Tuple

from utils.logger_utils import LoggerUtils
from utils.psutil_utils import Psutil

_logger = logging.getLogger("chemical.utils.command_utils")


class Command:
    @classmethod
    def simple_command(cls, command):
        """
        for print
        :param command:
        :return:
        """
        return Path(command).name

    @classmethod
    def handle_command(cls, command, shell):
        if shell:
            if isinstance(command, (list, tuple)):
                command = " ".join([str(i) for i in command])
        else:
            if isinstance(command, str):
                command = shlex.split(command)
            elif isinstance(command, (list, tuple)):
                command = [str(i) for i in command]
        return command

    @classmethod
    def create_popen(
            cls,
            cmd,
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            env=None,
            logger=None,
    ) -> Tuple[Union[subprocess.Popen, None], str, int]:
        logger = logger or _logger
        out, err, rc = None, "", 1

        cmd = cls.handle_command(cmd, shell)

        try:
            p = subprocess.Popen(args=cmd, shell=shell, stdout=stdout, stderr=stderr, stdin=stdin, env=env)
        except Exception as e:
            logger.error("Run Command Error", exc_info=True)
            return out, f"Run Command Error: {e}", 1
        return p, err, 0

    @classmethod
    def run_command(
            cls,
            cmd,
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            input=None,
            cmd_env=None,
            raise_error=False,
            json_out=False,
            timeout=None,
            encode="utf-8",
            logger=None
    ):
        logger = logger or _logger

        out, err, rc = {}, "", 1

        cmd = cls.handle_command(cmd, shell)

        env = dict(os.environ)
        if cmd_env:
            for k in cmd_env.keys():
                env[k] = cmd_env[k]

        try:
            p = subprocess.Popen(args=cmd, shell=shell, stdout=stdout, stderr=stderr, stdin=stdin, env=env)
            try:
                out, err = p.communicate(input=input, timeout=timeout)
                rc = p.returncode
            except subprocess.TimeoutExpired:
                p.terminate()
                outs, errs = p.communicate()
                Psutil.kill(p.pid)
                return outs, errs, rc
        except Exception as e:
            err = f"Run Command Error: {e}"
            logger.error("Run Command Error", exc_info=True)
            if raise_error:
                raise Exception(e)
            return out, err, rc

        if encode:
            out = out.decode(encode)
            err = err.decode(encode)

        logger.info(f"out: {out} err: {err}")

        if json_out:
            try:
                out = json.loads(out)
            except Exception as e:
                logging.error("JSON Loads Error", exc_info=True)
                if raise_error:
                    raise Exception(e)
                return out, err, rc

        return out, err, rc


def _health_check(p: subprocess.Popen) -> bool:
    return True


def _process_stop_callback(self):
    pass


class HealthCheck(metaclass=abc.ABCMeta):
    @classmethod
    @abc.abstractmethod
    def check(cls, manager) -> bool:
        """
        :param CommandProcessManager manager:
        :return:
        """
        return True

    @classmethod
    @abc.abstractmethod
    def failed_callback(cls, manager):
        """
        :param CommandProcessManager manager:
        :return:
        """

    @classmethod
    @abc.abstractmethod
    def success_callback(cls, manager):
        """
        :param CommandProcessManager manager:
        :return:
        """


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
            logger_encoding="utf-8",
            initializer=None,
            initargs=None,
    ):
        self.cmd = cmd
        self._logger = logger or _logger
        self.process_logger = process_logger
        if isinstance(self.process_logger, str):
            self.process_logger = logging.getLogger(self.process_logger)
        if not isinstance(self.process_logger, logging.Logger):
            self.process_logger = logging.getLogger("command_process_manager.process_logger")
            self.process_logger.propagate = False
        self.shell = shell
        self.cmd_env = dict(os.environ)
        self.env = env or {}
        if env is not None:
            for k, v in env.items():
                self.cmd_env[k] = v
        self._stop_prev_event = threading.Event()
        self._stop_end_event = threading.Event()
        self.health_checks: List[HealthCheck] = health_checks or []
        self.process_stop_callback: Union[Callable, _process_stop_callback] = process_stop_callback
        self.logger_encoding = logger_encoding
        self.initializer = initializer
        self.initargs = initargs or ()
        self.process: Union[subprocess.Popen, None] = None

    def stop(self, timeout=5):
        self._stop_prev_event.set()
        self._stop_end_event.wait(timeout)
        return True

    @property
    def process_pid(self):
        if self.process:
            return self.process.pid
        return None

    @property
    def is_running(self):
        if self.process_pid:
            return Psutil.is_active_pid(self.process_pid)
        return False

    def process_logger_handler(self):
        while not self._stop_end_event.is_set():
            line = self.process.stderr.readline()  # blocking read
            if not line:
                continue
            self.process_logger.info(line.rstrip().decode(self.logger_encoding))

    def health_check_handler(self):
        while not self._stop_end_event.is_set():
            simple_cmd = Command.simple_command(self.cmd)
            for health_check in self.health_checks:
                if not isinstance(health_check, HealthCheck):
                    print(1)
                    self._logger.warning(f"health check {health_check} must be a HealthCheck subclass")
                    continue
                status_ok = health_check.check(self)
                print(status_ok)
                if not status_ok:
                    health_check.failed_callback(self)
                    self._logger.info(f"command: {simple_cmd} health check failed.")
                else:
                    health_check.success_callback(self)
            time.sleep(1)

    def run(self):
        if self.initializer is not None:
            try:
                self.initializer(*self.initargs)
            except BaseException:
                self._logger.critical('Exception in initializer:', exc_info=True)
                # The parent will notice that the process stopped and
                # mark the pool broken
                return

        simple_cmd = Command.simple_command(self.cmd)

        self._logger.info(f"Running command: {simple_cmd} {' '.join([f'{k}:{v}' for k, v in self.env.items()])}")
        self.process, err, rc = Command.create_popen(self.cmd, self.shell, env=self.cmd_env)
        if rc != 0:
            self._logger.info(f"command: {simple_cmd} start failed.")
            return
        self._logger.info(f"command: {simple_cmd} [{self.process.pid}] start success.")

        t = threading.Thread(target=self.process_logger_handler, daemon=True)
        t.start()
        t = threading.Thread(target=self.health_check_handler, daemon=True)
        t.start()
        while 1:
            if self._stop_prev_event.is_set():
                self._logger.info(f"stop running command: {simple_cmd}")
                self.process.terminate()
                break
            if not Psutil.is_active_pid(self.process.pid):
                self._logger.info(f"command: {simple_cmd} process [{self.process.pid}] is killed.")
                break
            time.sleep(1)
        self._logger.info(f"stop command: {simple_cmd} process [{self.process.pid}] manager.")
        self._stop_end_event.set()
        if callable(self.process_stop_callback):
            self.process_stop_callback(self)

    def run_backend(self):
        t = threading.Thread(target=self.run)
        t.daemon = True
        t.start()


if __name__ == '__main__':
    import psutil


    def health_check(p):
        try:
            return psutil.Process(p.pid).is_running()
        except:
            return False


    cmd = r"C:/Users/wt/Desktop/etcd-v3.4.24-windows-amd64/etcd.exe --data-dir C:/Users/wt/Desktop/etcd-v3.4.24-windows-amd64/default.etcd"
    m = CommandProcessManager(cmd=cmd, health_checks=[health_check], logger=LoggerUtils.common_console_logger())
    m.run_backend()
    while 1:
        c = input()
        if c == "1":
            print(m.stop())
