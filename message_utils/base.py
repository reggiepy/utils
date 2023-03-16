# *_*coding:utf-8 *_*
# @Author : Reggie
# @Time : 2023/2/8 16:04
import json
import logging
from abc import ABCMeta, abstractmethod
from typing import Any, Callable, Union

import requests
import six
from pydantic import BaseModel, Field
from requests.models import Response

from utils.message_utils.constants import Platform, SourceModel, DestinationModel


class MessageModel(BaseModel):
    source: SourceModel = Field(..., description="发送方")
    destination: DestinationModel = Field(..., description="接收方")
    version: str = Field(..., description="版本信息")
    flag: str = Field(..., description="推送标识")
    data: Any = Field(..., description="推送数据")


class BaseMessage(six.with_metaclass(ABCMeta)):
    VERSION = "1.0.0"
    PLATFORM = Platform.UNDEFINED
    SOURCE = SourceModel.UNDEFINED
    DESTINATION = DestinationModel.UNDEFINED

    def __init__(self, logger=None, destination=None, source=None):
        self.session: requests.Session = requests.Session()
        self.logger = logging.getLogger("chemical-chaos.message") \
            if logger is None else logging.getLogger(logger)
        if destination:
            self.Destination = destination
        if source:
            self.SOURCE = source

    @classmethod
    def handle_response(cls, response: Response, is_json=True):
        if response.status_code != 200:
            logging.error(f"response status code failed: {response.status_code} response: {response.text}")
            return 1, f"response status code failed: {response.status_code}", None
        if is_json:
            return 0, "success", response.json()
        else:
            return 0, "success", response.text

    @classmethod
    def gen_message_model(cls, source, destination, version, flag, data):
        return MessageModel(
            source=source,
            destination=destination,
            version=version,
            flag=flag,
            data=data
        )

    def message_model(self, flag, data):
        return self.gen_message_model(
            source=self.source,
            destination=self.destination,
            version=self.version,
            flag=flag,
            data=data,
        )

    @property
    def url(self):
        return f"http://{self.host}:{self.port}/chemical-chaos/v1/ws/send"

    @property
    def version(self):
        return self.VERSION

    @property
    def platform(self):
        if isinstance(self.PLATFORM, Platform):
            return self.PLATFORM.value
        return self.PLATFORM

    @platform.setter
    def platform(self, value):
        self.PLATFORM = value

    @property
    def destination(self):
        if isinstance(self.DESTINATION, DestinationModel):
            return self.DESTINATION.value
        return self.DESTINATION

    @destination.setter
    def destination(self, value):
        self.DESTINATION = value

    @property
    def source(self):
        if isinstance(self.SOURCE, SourceModel):
            return self.SOURCE.value
        return self.SOURCE

    @source.setter
    def source(self, value):
        self.SOURCE = value

    def post(
            self,
            message: str,
            params: dict,
            message_handle: Union[Callable, None] = None,
            **kwargs
    ) -> (Any, int, str):
        """
        send a message
        :param message_handle:
        :param message:message
        :param params:params
        :param args:args
        :param kwargs:kwargs
        :return: ( result, code, message )
        """
        params.update({
            "platform": self.platform,
            "version": self.version,
        })
        if message_handle and callable(message_handle):
            _message = message_handle(message)
        else:
            _message = message
        data = {
            "message": _message,
        }
        try:
            resp = self.session.post(self.url, params=params, data=json.dumps(data), **kwargs)
        except Exception as e:
            self.logger.error(e)
            return 1, "request failed", None
        return self.handle_response(resp)

    @abstractmethod
    def send(self, *args, **kwargs) -> (Any, int, str):
        pass


class ChemicalMessageHandle:
    def handle_message(self, flag, message: str) -> str:
        """
        :param flag: flag
        :param message: message
        :return:
        """
        message = self.message_model(
            flag=flag,
            data=message
        )
        return message.json()
