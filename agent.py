from start_server import app, git, ROOT
from gc_exceptions import BuildFailure, DeployFailure, GcException
import jobs
import log
import bash

BUILD_SCRIPT = ROOT + "/build.sh"
DEPLOY_SCRIPT = ROOT + "/deploy.sh"

class job_step(object):
    def __init__(self, description):
        self.description = description
    def __call__(self, f):
        def f_wrapper(job):
            job["progress"].append(self.description)
            f(job)
        return f_wrapper

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
    log.debug("Starts merging %s" % job["branch"])
    log.indent = 1
    git.clean()
    try:
        _fetch(job)
        _build(job)
        _merge(job)
        job["success"] = True
    except GcException as e:
        log.debug("Exception during merge, starting cleanup")
        log.info(e.message)
        git.clean()
        raise
    finally:
        try:
            git.delete_remote_branch(job["branch"])
        except: pass
        jobs.finish_current()
        log.indent = 0
    log.debug("merge succesful")

