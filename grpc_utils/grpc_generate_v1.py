# *_*coding:utf-8 *_*
# @Author : Reggie
# @Time : 2022/11/17 15:55
import inspect
import os

import django
from jinja2 import Template
from pathlib import Path
from typing import List, AnyStr

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chemical.settings')
django.setup()

from domainServer.service.userAuth.user_service import UserServiceDomain


class Generic:
    @classmethod
    def generate_source_class_data(cls, source_class, dest_class_name, server, server_imports: List[AnyStr] = None):
        server_imports = server_imports or []
        members = inspect.getmembers(source_class)
        data = {
            "class_name": dest_class_name,
            "server": server,
            "BASE": source_class.__name__,
            "class_funcs": [

            ],
            "server_needs": {
                "imports": server_imports,
            },
        }
        for member in members:
            func_name, func_type = member
            if not str(func_type).startswith("<bound method"):
                continue
            temp = {
                "name": func_name,
                "parametes": "",
            }
            parametes = []
            sig = inspect.signature(getattr(source_class, func_name))
            for k, v in sig.parameters.items():
                parametes.append(str(v))
            temp["parametes"] = ", ".join(parametes)
            data["class_funcs"].append(temp)
        return data

    @classmethod
    def generate_server(cls, data):
        with open("grpc_server.template", "r") as f:
            file_data = f.read()
        template = Template(file_data)
        render = template.render(data=data)
        return render

    @classmethod
    def generate_client(cls, data):
        with open("grpc_client.template", "r") as f:
            file_data = f.read()
        template = Template(file_data)
        render = template.render(data=data)
        return render

    @classmethod
    def generate_client_file(cls, data, dest):
        with open(dest, encoding="utf-8", mode="w") as f:
            f.write(cls.generate_client(data))

    @classmethod
    def generate_server_file(cls, data, dest):
        with open(dest, encoding="utf-8", mode="w") as f:
            f.write(cls.generate_server(data))

    @classmethod
    def write_to_file(cls, data, dest):
        with open(dest, encoding="utf-8", mode="w") as f:
            f.write(data)


if __name__ == '__main__':
    BASE = os.getcwd()
    rpc_path = Path(BASE).joinpath("saaS").joinpath("rpc")
    server_imports = [
        "from domainServer.service.userAuth.user_service import UserServiceDomain",
    ]
    data = Generic.generate_source_class_data(UserServiceDomain, "User", "chemical", server_imports=server_imports)
    print(data)
    client_path = rpc_path.joinpath("rpc_client")
    server_path = rpc_path.joinpath("rpc_server")
    client_data = Generic.generate_client(data)
    print(client_data)
    Generic.write_to_file(client_data, client_path.joinpath("user").joinpath("user.py").as_posix())
    server_data = Generic.generate_server(data)
    print(server_data)
    Generic.write_to_file(server_data, server_path.joinpath("user").joinpath("user.py").as_posix())
