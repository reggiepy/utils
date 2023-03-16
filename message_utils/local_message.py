# *_*coding:utf-8 *_*
# @Author : Reggie
# @Time : 2023/2/23 13:46
from typing import Any

from utils.message_utils.base import BaseMessage
from utils.message_utils.constants import PlatformEnum


class LocalMessage(BaseMessage):
    PLATFORM = PlatformEnum.ALL

    def __init__(self, host="127.0.0.1", port=6600, **kwargs):
        super().__init__(**kwargs)
        self.host = host
        self.port = port

    def send(
            self,
            user_id,
            message,
            **kwargs
    ) -> (int, str, Any):
        """
        send a message
        :param user_id: user_id
        :param message: message
        :param kwargs:
        :return: ( result, code, message )
        """
        params = {
            "user_id": user_id
        }
        return super().send(message, params, **kwargs)


if __name__ == '__main__':
    result = LocalMessage().send("online", "hello")
    print(result)
