# *_*coding:utf-8 *_*
# @Author : Reggie
# @Time : 2023/2/23 13:46
import json
from typing import Any

from utils.message_utils.base import BaseMessage


class LocalMessage(BaseMessage):
    def __init__(self, host="127.0.0.1", port=6600):
        super().__init__()
        self.host = host
        self.port = port

    def send(self, user_id, message, *args, **kwargs) -> (int, str, Any):
        """
        send a message
        :param user_id: user_id
        :param message: message
        :param args:
        :param kwargs:
        :return: ( result, code, message )
        """
        data = {
            "message": message,
        }
        url = f"http://{self.host}:{self.port}/chemical-chaos/v1/ws/send?user_id={user_id}"
        try:
            resp = self.session.post(url, data=json.dumps(data))
        except Exception as e:
            self.logger.error(e)
            return 1, "request failed", None
        return self.handle_response(resp)


if __name__ == '__main__':
    result = LocalMessage().send("wtt", "hello")
    print(result)
