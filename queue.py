from collections import deque
import db

_queue = deque([])


def add(branch, username):
    job = db.create_job(branch, username)
    _queue.append(job)
    return job

def get():
    return list(_queue)

def append_log(msg):
    _queue[0]["log"].append(msg)

def is_current(queue_item):
    return _queue[0] == queue_item

def index(queue_item):
    return _queue.index(queue_item)

def finish():
    db.insert_job(_queue.popleft())

