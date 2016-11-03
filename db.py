import pymongo
from datetime import datetime
import gc_exceptions
import log

_client = pymongo.MongoClient("localhost", 8081)
_db = _client.gitGC

def create_job(branch, username):
    return { "username": username, 
             "branch": branch, 
             "progress": ["In queue"], 
             "success": None,
             "log": [], 
             "start":  datetime.now() }

def insert_job(job):
    job["end"] = datetime.now()
    _db.jobs.insert_one(job)

def find_jobs(since):
    jobs = _db.jobs.find({"start": {"$gt": since}}).sort("start", pymongo.DESCENDING)
    return map(_without_id, jobs)

def find_job(branch):
    job = _db.jobs.find_one({"branch": branch})
    if not job: raise gc_exceptions.NotFound("Job for branch '%s' does not exist" % branch)
    return _without_id(job)

def delete_job_if_exist(branch):
    if not branch: raise Exception("Bad call to db")
    res = _db.jobs.delete_many({"branch": branch})
    if res.deleted_count:
        log.debug("Deleted %d jobs matching branch '%s'" % (res.deleted_count, branch))


def _without_id(job):
    del job["_id"]
    return job
