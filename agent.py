from start_server import app, git, ROOT
from gc_exceptions import BuildFailure
import jobs
import log
import bash

BUILD_SCRIPT = ROOT + "/build.sh"

class JobStep:
    def __init__(self, job, description):
        self.job = job
        self.description = description

    def log(self):
        print self.description
        self.job["progress"].append(self.description)

class Fetch(JobStep):
    def __init__(self, job):
        JobStep.__init__(self, job, "Fetching sources")

    def execute(self):
        git.checkout(self.job["branch"])

class Build(JobStep):
    def __init__(self, job):
        JobStep.__init__(self, job, "Building sources")

    def execute(self):
        bash.execute(BUILD_SCRIPT, BuildFailure)

class Merge(JobStep):
    def __init__(self, job):
        JobStep.__init__(self, job, "Merging to %s" % app.config["MASTER"])

    def execute(self):
        git.merge(self.job["branch"])

def execute_step(step):
    step.log()
    step.execute()

def execute_job(job):
    log.debug("Starts merging %s" % job["branch"])
    log.indent = 1
    git.clean()
    try:
        execute_step(Fetch(job))
        execute_step(Build(job))
        execute_step(Merge(job))
    except:
        log.debug("Exception during merge, starting cleanup")
        git.clean()
        raise
    finally:
        git.delete(job["branch"])
        jobs.finish_current()
        log.indent = 0
    log.debug("merge succesful")

