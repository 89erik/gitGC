import pymongo
from datetime import datetime

_client = pymongo.MongoClient("localhost", 8081)
_db = _client.gitGC

def create_job(branch, username):
    return { "username": username, 
             "branch": branch, 
             "progress": [], 
             "log": [], 
             "start":  datetime.now() }

def insert_job(job):
    job["end"] = datetime.now()
    _db.jobs.insert_one(job)

def find_jobs(since):
    jobs = _db.jobs.find({"start": {"$gt": since}})
    def without_id(d):
        del d["_id"]
        return d
    return map(without_id, jobs)

