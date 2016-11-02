from global_data import app, git, ROOT
from gc_exceptions import BuildFailure, DeployFailure, Cancellation, GcException
import jobs
import log
import bash

import time

BUILD_SCRIPT = ROOT + "/build.sh"
DEPLOY_SCRIPT = ROOT + "/deploy.sh"
_cancelled = False

def cancel():
    global _cancelled
    _cancelled = True
    timeout = 10.0
    step = 0.2
    while _cancelled:
        time.sleep(step)
        timeout -= step
        if timeout <= 0.0:
            log.debug("waiting for cancellation to take effect...")
            timeout = 10
            step = 1

class job_step(object):
    def __init__(self, description):
        self.description = description
    def __call__(self, f):
        def decorator(job):
            global _cancelled
            if _cancelled:
                job["progress"].append("Cancelled")
                job["success"] = False
                raise Cancellation()
            job["progress"].append(self.description)
            f(job)
        return decorator

@job_step("Fetching sources")
def _fetch(job):
    git.fetch()
    git.merge(job["branch"], git.master)

@job_step("Building sources")
def _build(job):
    git.checkout(job["branch"])
    bash.execute(BUILD_SCRIPT, BuildFailure)

@job_step("Merging to %s" % app.config["MASTER"])
def _merge(job):
    git.merge_and_push(job["branch"])

@job_step("Deploying")
def _deploy(job):
    _build(job)
    bash.execute(DEPLOY_SCRIPT, DeployFailure)

def execute_job(job):
    global _cancelled
    log.debug("Starts merging %s" % job["branch"])
    log.indent = 1
    git.clean()
    try:
        _fetch(job)
        _build(job)
        _merge(job)
        job["success"] = True
    except GcException as e:
        job["success"] = False
        log.debug("Job was aborted, starting cleanup")
        e.log_exception()
        git.clean()
        raise
    finally:
        try:
            git.delete_remote_branch(job["branch"])
        except: pass
        jobs.finish_current()
        _cancelled = False
        log.indent = 0
    log.debug("merge succesful")

