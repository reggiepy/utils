import hashlib
import uuid


def gen_task_id():
    return f"task_{uuid.uuid4().hex.lower()}"


def gen_uuid():
    return uuid.uuid4().hex.lower()


def gen_upper_uuid():
    return uuid.uuid4().hex.upper()


def begin_letter_uuid():
    u_id = gen_uuid()
    while u_id[0].isdigit() or any([u_id.startswith(f"c{i}")  for i in range(10)]):
        u_id = gen_uuid()
    return u_id


# hashlib简单使用
def md5(arg):  # 这是加密函数，将传进来的函数加密
    md5_pwd = hashlib.md5(bytes('uds', encoding='utf-8'))
    md5_pwd.update(bytes(arg, encoding='utf-8'))
    return md5_pwd.hexdigest()  # 返回加密的数据


if __name__ == '__main__':
    print(begin_letter_uuid())
    # print(gen_uuid())
    # print(md5("fafdsafdsaf"))
