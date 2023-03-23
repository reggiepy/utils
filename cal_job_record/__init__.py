JobEtcdRecord = None
JobFileRecord = None
job_etcd_restart = None
rm_run_info = None
try:
    from .etcd_jobRecord import JobEtcdRecord, job_etcd_restart
except Exception:
    pass
try:
    from .file_jobRecord import JobFileRecord, rm_run_info
except Exception:
    pass

JOBRecord = JobEtcdRecord or JobFileRecord
rm_run_info = job_etcd_restart or rm_run_info
if JOBRecord is None:
    raise Exception("丢失任务记录模块")