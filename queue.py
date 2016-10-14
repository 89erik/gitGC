from collections import deque

_queue = deque([])


def add(branch, username):
    me = { "username": username, "branch": branch, "progress": [], "log": [] }
    _queue.append(me)
    return me

def get():
    return list(_queue)

def append_log(msg):
    _queue[0]["log"].append(msg)

def is_current(queue_item):
    return _queue[0] == queue_item

def index(queue_item):
    return _queue.index(queue_item)

def go_to_next():
    finished = _queue[0]
    with open(finished["branch"], "w") as f:
        f.write(str(finished)) # TODO insert to database instead
    _queue.popleft()

