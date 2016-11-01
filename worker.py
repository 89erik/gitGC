import jobs
import agent
import log

import threading
import time

worker = None

def _listen():
    while True:
        try:
            job = jobs.get_next()
            if job:
                agent.execute_job(job)
            else:
                time.sleep(1)
        except Exception as e:
            log.error("%s in worker thread:\n%s" % (type(e), str(e)))

def start():
    global worker
    if worker != None:
        raise Exception("Only one worker supported")

    worker = threading.Thread(target=_listen)
    worker.setDaemon(True)
    log.debug("Starting worker thread")
    worker.start()

