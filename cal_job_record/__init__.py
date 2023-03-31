JobEtcdRecord = None
JobFileRecord = None
job_etcd_restart = None
rm_run_info = None
try:
    from utils.cal_job_record.etcd_jobRecord import JobEtcdRecord, job_etcd_restart
except Exception as e:
    raise e

try:
    from utils.cal_job_record.file_jobRecord import JobFileRecord, rm_run_info
except Exception:
    pass

JOBRecord = JobEtcdRecord or JobFileRecord
JOBRecordInfoRestart = job_etcd_restart or rm_run_info
if JOBRecord is None or JOBRecordInfoRestart is None:
    raise Exception("丢失任务记录模块")