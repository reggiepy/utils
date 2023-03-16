import json
from enum import Enum, unique
from utils.message_utils.chemical_message import ChemicalMessage


@unique
class NoteStatus(Enum):
    NOTE = 21000
    CAL_DATA = 53486  # 计算结果

    @property
    def code(self):
        return self.value


@unique
class CalStatus(Enum):
    CALCULATE_ANOMALY = (36000, "计算异常")  # 参数非法
    MODULE_INSTANCE_ERROR = (37000, "模块实例化失败")  # 参数非法
    MODULE_ERROR = (37100, "加载模块异常")  # 参数非法
    DATA_ERROR = (37200, "加载数据异常")  # 参数非法

    PARAM_IS_NULL = (34001, "参数为空")  # 参数为空
    PARAM_ILLEGAL = (34002, "参数非法")  # 参数非法
    UNKNOWN_ERROR = (35000, "未知异常")  # 未知异常

    @property
    def code(self):
        return self.value


class INFOFeedback:

    def __init__(self, addressee=None, task=None, cal_label=None):
        self.LocalMessage = ChemicalMessage()
        self.addressee = addressee
        if task:
            self.task = task
        self.cal_label = cal_label or "cal"

    @staticmethod
    def json_info(msg=None, code=None):
        code_, msg_ = None, None
        try:
            if isinstance(code, Enum):
                code_, msg_ = code.value
            elif isinstance(code, str):
                code_, msg_ = CalStatus[code].value
            elif isinstance(code, (int, str)) and str(code).isdigit():
                code_, msg_ = int(code), msg
        except (AttributeError, ValueError):
            pass

        def _info_data(info_type_, code1, msg1, msg2):
            # info_ = {"code": code1, "msg": msg2 or msg1}
            info_ = {"code": code1, "msg": msg1, "data": msg2} if msg2 and msg1 != msg2 else {"code1": code, "msg": msg1}
            return {"info_type": f"{info_type_}", "info_msg": info_}
        if str(code_).startswith("3"):
            return _info_data("warn", code_, msg_, msg)
        elif str(code_).startswith("4"):
            return _info_data("error", code_, msg_, msg)
        else:
            return _info_data("rest", code_, msg_, msg)

    def feedback(self, msg=None, code=None):
        if code == "note":
            info_data = {"info_type": "note", "info_msg": msg}
        elif code == "result":
            info_data = {"info_type": "result", "info_msg": "计算结果", "info_data": msg}
        elif code == "exit":
            info_data = {"info_type": "exit", "info_msg": "退出计算"}
        else:
            info_data = self.json_info(msg, code)
        if info_data and hasattr(self, "task"):
            info_data["task"] = self.task
            self.LocalMessage.send(self.addressee, self.info_message(info_data))

    def info_message(self, info_data):
        return {"msg_class": self.cal_label, "msg_data": info_data}



if __name__ == '__main__':
    # a = json.loads("""{"info_code": 21000, "info_type": "NOTE", "info_data": "手动阀", "task": "ad1e32929af2408db30f14e49322db3e"}""")
    # print(a)
    # LocalMessage().send("online", "asdasd")
    print(CalStatus["PARAM_IS_NULL"].value)
