# *_*coding:utf-8 *_*
# @Author : Reggie
# @Time : 2023/3/21 13:14
import json
import logging
import os
import shlex
import subprocess
from typing import Union, Tuple

from utils.psutil_utils import kill


class Command:
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
        logger = logger or logging.getLogger()
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
        logger = logger or logging.getLogger()

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
                kill(p.pid)
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
