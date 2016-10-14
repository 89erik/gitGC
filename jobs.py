from collections import deque
import db

_jobs = deque([])

def add(branch, username):
    job = db.create_job(branch, username)
    _jobs.append(job)
    return job

def get():
    return list(_jobs)

def append_log(msg):
    _jobs[0]["log"].append(msg)

def is_current(job):
    return _jobs[0] == job

def index(job):
    return _jobs.index(job)

def finish_current():
    db.insert_job(_jobs.popleft())

