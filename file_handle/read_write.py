import json
from pathlib import Path


class FileHandle:
    def __init__(self, file_path):
        self.f = Path.cwd().joinpath(file_path)
        self.f.parent.mkdir(parents=True, exist_ok=True)

    def read(self):
        return self.f.read_text() or ""

    def read_json(self):
        return json.loads(self.f.read_text() or "{}") or {}

    def write(self, text_: str, mode="w"):
        if mode == "w":
            self.f.write_text(text_)
        elif mode == "a":
            try:
                self.f.write_text(self.read() + "\n" + text_)
            except FileNotFoundError:
                self.f.write_text(text_)

    def write_json(self, json_: dict, mode="w"):
        if mode == "w":
            self.f.write_text(json.dumps(json_))
        elif mode == "a":
            try:
                json__ = self.read_json()
                json__.update(json_)
            except FileNotFoundError:
                json__ = json_
            self.f.write_text(json.dumps(json__))

    def rmdir(self):
        self.f.parent.rmdir()

    def unlink(self):
        self.f.unlink()


class RunInfo:
    def __init__(self, task):
        from chemical_chaos.settings import RUN_INFO_PATH
        self.state_f = FileHandle(f"{RUN_INFO_PATH}/run_info_{task}/state.txt")
        self.info_f = FileHandle(f"{RUN_INFO_PATH}/run_info_{task}/info.txt")

    def get_run_state(self):
        return self.state_f.read()

    def get_run_info(self):
        return self.info_f.read_json()

    def update_run_state(self, state):
        self.state_f.write(state)

    def update_run_info(self, info):
        self.info_f.write_json(info, mode="a")

    def del_run_info(self):
        self.info_f.unlink()
        self.state_f.unlink()
        self.state_f.rmdir()

if __name__ == '__main__':
    pass
    # FileHandle("dd/a.txt").write_json({"a": 5}, mode="a")
    # a = FileHandle("dd/a.txt")
    # a.unlink()
    # a.rmdir()
    # print(FileHandle("a.txt").read_json(), type(FileHandle("a.txt").read_json()))