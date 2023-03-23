from utils.etcd_utils import EtcdClient, EtcdData
from types import FunctionType, MethodType


class JobEtcdBase(EtcdClient):

    def get_one(self, key):
        with self.client.lock(key):
            data_ = self.get(key)
            if data_ is not None:
                data_ = data_.value
            real_key = self.real_key(key)
            data = EtcdData(key=key, value={})
            self.client.put(real_key, data.json(ensure_ascii=False))
        return data_

    def delete_k_k(self, key, k):
        with self.client.lock(key):
            data_ = self.get(key).value
            real_key = self.real_key(key)
            data = EtcdData(key=key, value=data_.pop(k))
            self.client.put(real_key, data.json(ensure_ascii=False))


class JobEtcdRecord:
    def __init__(self, task=None, addressee=None, **kwargs):
        self.task = task
        self.addressee = addressee
        self.param_c = JobEtcdBase(f"/config/job/param/")
        self.state_c = JobEtcdBase(f"/config/job/state/")
        # self.jobs_c = JobEtcdBase(f"/config/job/")

    def get_run_state(self, addressee):
        data = self.state_c.get(addressee)
        return data if data is None else data.value.get("state")
        #     data = data.value.get("state")
        # return self.state_c.get(addressee).value.get("state")

    def update_run_state(self, state):
        self.state_c.update(self.addressee, **{"state": state})

    def get_run_param(self):
        return self.param_c.get_one(self.task) or {}

    def update_run_param(self, info, **kwargs):
        self.param_c.update(self.task, **info)

    def record_user_job(self, label, pro, task):
        # 记录用户任务， 记录任务状态， 记录任务属于的项目、运行的地方
        state, data = self.get_user_job()
        self.state_c.set(self.addressee, {"projectId": pro, "calLabel": label, "task": task, "state": "await"})
        return state, {"projectId": None, "calLabel": None, "task": None, "state": "await"} if data is None else data

    def un_record_user_job(self):
        self.state_c.delete(self.addressee)

    def get_user_job(self):
        # 返回状态和数据
        try:
            record_ = self.state_c.get(self.addressee)
            data = {} if record_ is None else record_.value
            return 1 if data else 0, data
        except Exception as e:
            return 0, {}

    def del_run_info(self, addressee):
        self.param_c.delete(self.task)
        self.state_c.delete(addressee)
        # self.un_record_user_job(addressee)


def job_etcd_restart():
    try:
        JobEtcdBase(f"/config/job/").clear()
    except Exception:
        pass

if __name__ == '__main__':
    JobEtcdRecord().state_c.set("local_cslab_15", {"21:25":25})
    print(JobEtcdRecord().state_c.get("local_cslab_15").value)