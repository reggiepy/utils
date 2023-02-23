# *_*coding:utf-8 *_*
# @Author : Reggie
# @Time : 2022/9/20 10:35
import time
from functools import wraps


def timer(sys_out=None):
    if sys_out is None:
        sys_out = print

    def _inner(func):
        @wraps(func)
        def __inner(*args, **kwargs):
            start = time.time()
            out = func(*args, **kwargs)
            sys_out(f"Call {func.__name__} Cost {time.time() - start}")
            return out

        return __inner

    return _inner
