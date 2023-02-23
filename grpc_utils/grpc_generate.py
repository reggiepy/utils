# *_*coding:utf-8 *_*
# @Author : Reggie
# @Time : 2022/11/17 15:55
import copy
import inspect
from dataclasses import dataclass
from pathlib import Path
from typing import List, AnyStr, Any, Union

import yaml
from jinja2 import Template

_BASE = Path(__file__).parent


class Generic:
    @classmethod
    def generate_source_class_data(
            cls,
            source_class: type,
            dest_class_name: str,
            server: str,
            server_imports: List[AnyStr] = None,
    ):
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
    def generate_server(cls, data, template_path=None):
        template_path = template_path or _BASE.joinpath("grpc_server.template")
        with open(template_path, "r") as f:
            file_data = f.read()
        template = Template(file_data)
        render = template.render(data=data)
        return render

    @classmethod
    def generate_client(cls, data, template_path=None):
        template_path = template_path or _BASE.joinpath("grpc_client.template")
        with open(template_path, "r") as f:
            file_data = f.read()
        template = Template(file_data)
        render = template.render(data=data)
        return render

    @classmethod
    def generate_client_file(cls, data, dest):
        Path(dest).parent.mkdir(parents=True, exist_ok=True)
        with open(dest, encoding="utf-8", mode="w") as f:
            f.write(cls.generate_client(data))

    @classmethod
    def generate_server_file(cls, data, dest):
        Path(dest).parent.mkdir(parents=True, exist_ok=True)
        with open(dest, encoding="utf-8", mode="w") as f:
            f.write(cls.generate_server(data))

    @classmethod
    def write_to_file(cls, data, dest):
        Path(dest).parent.mkdir(parents=True, exist_ok=True)
        with open(dest, encoding="utf-8", mode="w") as f:
            f.write(data)


@dataclass()
class GenericHelper:
    source_module: type
    rpc_path: str
    dest_file_path: str
    dest_class_name: str
    rcp_server_name: str
    client_path: str = None
    server_path: str = None
    client_template_path: str = None
    server_template_path: str = None
    server_imports: List = None
    verbose: bool = True

    def __post_init__(self):
        self.client_path = self.client_path or Path(self.rpc_path).joinpath("rpc_client").as_posix()
        self.server_path = self.server_path or Path(self.rpc_path).joinpath("rpc_server").as_posix()
        for k, v in self.__dict__.items():
            if k == "dest_file_path":
                continue
            if not k.endswith("_path"):
                continue
            if not v:
                continue
            setattr(self, k, Path(v).absolute())

    def log(self, *args, **kwargs):
        if self.verbose:
            print(f"{' '.join([f'{i}' for i in args])} {' '.join([f'{k}: {v}' for k, v in kwargs.items()])}")

    @classmethod
    def from_file(cls, file_path: str):
        return from_file(file_path)

    def generate(self):
        data = Generic.generate_source_class_data(
            self.source_module,
            self.dest_class_name,
            self.rcp_server_name,
            server_imports=self.server_imports
        )

        client_data = Generic.generate_client(data, template_path=self.client_template_path)
        client_file_path = Path(self.client_path).joinpath(self.dest_file_path).as_posix()
        self.log(client_file_path, client_data)
        Generic.write_to_file(client_data, client_file_path)
        server_data = Generic.generate_server(data, template_path=self.server_template_path)
        server_file_path = Path(self.server_path).joinpath(self.dest_file_path).as_posix()
        self.log(server_file_path, server_data)
        Generic.write_to_file(server_data, server_file_path)


def from_file(
        file_path: str,
        client_template_path: Union[str, Any] = None,
        server_template_path: Union[str, Any] = None
):
    with open(file_path, encoding="utf-8", mode="r") as f:
        data = f.read()
    kwargs = yaml.safe_load(data)
    if client_template_path is not None:
        kwargs['client_template_path'] = client_template_path
    if server_template_path is not None:
        kwargs['server_template_path'] = server_template_path
    gh = GenericHelper
    sig = inspect.signature(gh)
    source_module = kwargs.get("source_module")
    new_kwargs = copy.deepcopy(kwargs)
    if isinstance(source_module, str):
        module_name, class_name = source_module.rsplit(".", 1)
        # source_module = eval(f"from {module_name} import {class_name}")
        source_module = __import__(module_name, fromlist=[class_name])
        source_class = getattr(source_module, class_name)
        if inspect.ismodule(source_class):
            raise ValueError("source_module must not be a module")
        new_kwargs["source_module"] = source_class
    bind = sig.bind(**new_kwargs).arguments
    if bind.get("verbose"):
        print(bind)
    return GenericHelper(
        **new_kwargs
    )
