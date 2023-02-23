# *_*coding:utf-8 *_*
# @Author : Reggie
# @Time : 2023/2/8 16:04
import logging
from abc import ABCMeta, abstractmethod
from typing import Any

import requests
import six
from requests.models import Response


class BaseMessage(six.with_metaclass(ABCMeta)):

    def __init__(self, logger=None):
        self.session: requests.Session = requests.Session()
        self.logger = logging.getLogger("chemical-chaos.message") \
            if logger is None else logging.getLogger(logger)

    @classmethod
    def handle_response(cls, response: Response, is_json=True):
        if response.status_code != 200:
            logging.error(f"response status code failed: {response.status_code} response: {response.text}")
            return 1, f"response status code failed: {response.status_code}", None
        if is_json:
            return 0, "success", response.json()
        else:
            return 0, "success", response.text

    @abstractmethod
    def send(self, *args, **kwargs) -> (Any, int, str):
        """
        send a message
        :param args:
        :param kwargs:
        :return: ( result, code, message )
        """
        pass
