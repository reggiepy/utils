import shutil
from pathlib import Path
from utils.cal_job_record.read_write import FileHandle


class JobFileRecord:
    def __init__(self, task=None, addressee=None):
        from chemical_chaos.settings import RUN_INFO_PATH
        self.RUN_INFO_PATH = RUN_INFO_PATH
        if addressee:
            self.addressee = addressee
            self.state_f = FileHandle(f"{RUN_INFO_PATH}/state_{addressee}.txt", is_dir=False)
        if task:
            self.param_f = FileHandle(f"{RUN_INFO_PATH}/info_{task}.txt", is_dir=False)

    def get_run_state(self):
        try:
            return self.state_f.read_json().get("state")
        except FileNotFoundError:
            return ""

    def get_run_param(self):
        try:
            return_ = self.param_f.read_json()
            self.param_f.write_json({}, mode="w")
            return return_
        except FileNotFoundError:
            return {}

    def update_run_state(self, state):
        self.state_f.write(state)

    def update_run_param(self, info, mode="a", deep=True):
        self.param_f.write_json(info, mode=mode, deep=deep)

    def del_run_info(self):
        self.param_f.rm()
        self.state_f.rm()

    def record_user_job(self, label, pro, task):
        # 记录用户任务， 记录任务状态， 记录任务属于的项目、运行的地方
        self.update_run_state("await")
        state, data = self.get_user_job()
        self.state_f.write_json({"projectId": pro, "calLabel": label, "task": task, "state": "await"}, mode="w")
        return state, {"projectId": None, "calLabel": None, "task": None, "state": "await"} if data is None else data

    def un_record_user_job(self):
        self.state_f.rm()

    def get_user_job(self):
        # 返回状态和数据
        try:
            job_state = self.state_f.read_json()
            return 1 if job_state else 0, job_state
        except Exception as e:
            return 0, None


def rm_run_info():
    from chemical_chaos.settings import RUN_INFO_PATH
    f = Path(RUN_INFO_PATH)
    shutil.rmtree(f)
    f.mkdir(parents=True, exist_ok=True)