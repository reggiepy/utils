# *_*coding:utf-8 *_*
# @Author : Reggie
# @Time : 2023/3/21 13:14
import logging
import shlex
import subprocess
from typing import Union, Tuple


def create_popen(
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

    if shell:
        if isinstance(cmd, (list, tuple)):
            cmd = " ".join([str(i) for i in cmd])
    else:
        if isinstance(cmd, str):
            cmd = shlex.split(cmd)
        elif isinstance(cmd, (list, tuple)):
            cmd = [str(i) for i in cmd]

    try:
        p = subprocess.Popen(args=cmd, shell=shell, stdout=stdout, stderr=stderr, stdin=stdin, env=env)
    except Exception as e:
        logger.error("Run Command Error", exc_info=True)
        return out, f"Run Command Error: {e}", 1
    return p, err, 0
