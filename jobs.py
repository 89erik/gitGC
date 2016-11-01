from collections import deque
from helpers import *
import db

_jobs = deque([])

def add(branch, username):
    job = db.create_job(branch, username)
    _jobs.append(job)
    return job

def get_by_id(branch):
    jobs = get()
    return single(jobs, lambda j: j["branch"] == branch)

def get():
    return list(_jobs)

def append_log(msg):
    if len(_jobs) > 0:
        _jobs[0]["log"].append(msg)

def is_current(job):
    return _jobs[0] == job

def index(job):
    return _jobs.index(job)

def finish_current():
    db.insert_job(_jobs.popleft())

def get_next():
    if len(_jobs) > 0:
        return _jobs[0]
    else:
        return None
