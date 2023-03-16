# *_*coding:utf-8 *_*
# @Author : Reggie
# @Time : 2023/3/15 16:16
from functools import partial
from typing import Any

from utils.message_utils.base import BaseMessage, ChemicalMessageHandle
from utils.message_utils.constants import Platform, DestinationModel


class ChemicalMessage(ChemicalMessageHandle, BaseMessage):
    PLATFORM = Platform.WEB
    DESTINATION = DestinationModel.WEB

    def __init__(self, host="127.0.0.1", port=6600, **kwargs):
        super().__init__(**kwargs)
        self.host = host
        self.port = port

    def send(
            self,
            user_id,
            message,
            flag,
            **kwargs
    ) -> (Any, int, str):
        params = {
            "user_id": user_id
        }
        message_handle = partial(self.handle_message, flag)
        return self.post(message, params, message_handle=message_handle, **kwargs)


if __name__ == '__main__':
    ChemicalMessage().send("wtt", {"info": "test"}, "chemical")
