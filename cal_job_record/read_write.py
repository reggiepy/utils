import json
import shutil
from pathlib import Path
import portalocker


class FileHandle:

    def __init__(self, file_path, is_path=True, is_dir=True, is_create=False):
        self.f = Path(file_path) if is_path else Path.cwd().joinpath(file_path)
        self.f.parent.mkdir(parents=True, exist_ok=True)
        # if is_create:
        #     if is_dir:
        #         self.f.mkdir(parents=True, exist_ok=True)
        #     else:
        #         self.f.parent.mkdir(parents=True, exist_ok=True)

    def read(self):
        with open(self.f, mode="r") as f:
            portalocker.lock(f, portalocker.LOCK_EX)
            text__ = f.read() or ""
            portalocker.unlock(f)
            return text__

    def _read(self):
        return self.f.read_text() or ""

    def read_json(self):
        with open(self.f, mode="r") as f:
            portalocker.lock(f, portalocker.LOCK_EX)
            text__ = json.loads(f.read() or "{}") or {}
            portalocker.unlock(f)
            return text__

    def _read_json(self):
        return json.loads(self.f.read_text() or "{}") or {}

    def write(self, text_: str, mode="w"):
        text__ = ""
        if mode == "a":
            try:
                with open(self.f, mode="r") as f:
                    portalocker.lock(f, portalocker.LOCK_EX)
                    text__ = f.read() or ""
                    portalocker.unlock(f)
            except FileNotFoundError:
                pass
            else:
                text__ = text__ + "\n"

        with open(self.f, mode="w") as f:
            portalocker.lock(f, portalocker.LOCK_EX)
            f.write(text__ + text_)
            portalocker.unlock(f)

    def _write(self, text_: str, mode="w"):
        if mode == "w":
            self.f.write_text(text_)
        elif mode == "a":
            try:
                self.f.write_text(self.read() + "\n" + text_)
            except FileNotFoundError:
                self.f.write_text(text_)

    def write_json(self, json_: dict, mode="w", deep=False):
        def join_(dict_1: dict, dict_2):
            for k, v in dict_2.items():
                v_ = dict_1.get(k)
                if isinstance(v, dict) and isinstance(v_, dict):
                    new_v = join_(v_, v)
                elif isinstance(v, list) and isinstance(v_, list):
                    new_v = v_ + v
                else:
                    new_v = v
                dict_1[k] = new_v
            return dict_1
        json__ = {}
        if mode == "a":
            try:
                with open(self.f, mode="r") as f:
                    portalocker.lock(f, portalocker.LOCK_EX)
                    json__ = json.loads(f.read() or {}) or {}
                    portalocker.unlock(f)
            except FileNotFoundError:
                pass
        try:
            with open(self.f, mode="w") as f:
                portalocker.lock(f, portalocker.LOCK_EX)
                join_(json__, json_ or {}) if deep else json__.update(json_ or {})
                f.write(json.dumps(json__))
                portalocker.unlock(f)
        except Exception as e:
            print(e)


    def _write_json(self, json_: dict, mode="w", deep=False):
        if mode == "w":
            self.f.write_text(json.dumps(json_))
        elif mode == "a":
            try:
                json__ = self.read_json()

                def join_(dict_1: dict, dict_2):
                    print(dict_1, dict_2)
                    for k, v in dict_2.items():
                        v_ = dict_1.get(k)
                        if isinstance(v, dict) and isinstance(v_, dict):
                            new_v = join_(v_, v)
                        elif isinstance(v, list) and isinstance(v_, list):
                            new_v = v_ + v
                        else:
                            new_v = v
                        dict_1[k] = new_v
                    return dict_1
                join_(json__, json_) if deep else json__.update(json_)
            except FileNotFoundError:
                json__ = json_
            self.f.write_text(json.dumps(json__))

    def rm(self):
        if self.f.exists():
            self.f.unlink() if self.f.is_file() else shutil.rmtree(self.f)


if __name__ == '__main__':
    pass
    # a = f"{RUN_INFO_PATH}/b/a.txt"
    # FileHandle("dd/a.txt").write_json({"a": 5}, mode="a")
    # a = FileHandle("dd")
    # a.rm()
    # print(a)
    # print(Path(a).is_file())
    # a.rmdir()
    # print(FileHandle("a.txt").read_json(), type(FileHandle("a.txt").read_json()))