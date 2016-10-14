#! venv/bin/python

from flask import Flask, Response, json, jsonify, request, render_template
from flask_bootstrap import Bootstrap
from datetime import datetime, timedelta
import time
import re
import os

from gc_exceptions import *
import git_commands
import bash
import log
import jobs
import db

ROOT = os.path.dirname(os.path.realpath(__file__))
BUILD_SCRIPT = ROOT + "/build.sh"
MASTER = "master"
git = git_commands.Repository(ROOT + "/repository", MASTER)
BRANCH_PATTERN = re.compile(r"GC_\d{4}-\d{2}-\d{2}_\d{4}\.\d{2}\.\d+")
log.debug("---[ STARTING SERVER ]---")

app = Flask(__name__)
Bootstrap(app)

res = {}

@app.errorhandler(404)
def not_found(e):
    return "NOT FOUND: %s" % request.path, 404

@app.route("/job/<id>", methods=["GET"])
def get_job(id):
    return render_template("job.html", job=db.find_job(id))


@app.route("/jobs", methods=["GET"])
@app.route("/jobs/<int:hours>", methods=["GET"])
def get_jobs(hours=None):
    if not hours: hours = 24
    since = datetime.now() - timedelta(hours=hours)
    jobs = db.find_jobs(since)
    return render_template("jobs.html", jobs=jobs)

@app.route("/progress", methods=['GET'])
@app.route("/progress/<username>", methods=['GET'])
def progress(username=None):
    return jsonify({"queue": jobs.get()})

@app.route("/status", methods=['GET'])
def status():
    rv = git.status()
    return Response(rv["stdout"], mimetype="text/plain")

@app.route("/tree", methods=['GET'])
def tree():
    content = git.tree()
    return Response(content, mimetype="text/plain")

@app.route("/log", methods=['GET'])
@app.route("/log/<n>", methods=['GET'])
def getlog(n="500"):
    log_content = log.get_lines(n)
    return Response(log_content, mimetype="text/plain")

@app.route('/pull', methods=['POST', 'GET'])
def handle_pull():
    if request.method == 'POST':
        branch = get_from_request(request, "branch_name")
        username = get_from_request(request, "username")
        start_job(branch, username)
        res['payload'] = json.loads(request.form.get('payload',"{}"))
        res['headers'] = dict(request.headers.items())
        return ""
    else:
        return Response(json.dumps(res, indent=None if request.is_xhr else 2),
                        mimetype='application/json')

@app.errorhandler(GcException)
def bad_request_handler(error):
    error.log_exception()
    payload = error.to_dict()
    payload["time"] = time.asctime()
    response = jsonify(payload)
    response.status_code = error.status_code
    return response


def username_github(payload):
    return payload["pusher"]["name"]

def username_bitbucket(payload):
    return payload["push"]["changes"][0]["commits"][0]["author"]["raw"]

def branch_name_github(payload):
    return payload["ref"][len("refs/heads/"):]

def branch_name_bitbucket(payload):
    return payload["push"]["changes"][0]["new"]["name"]

payload_accessors = {
    "github": { "username": username_github, "branch_name": branch_name_github },
    "bitbucket": { "username": username_bitbucket, "branch_name": branch_name_bitbucket }
}

def repo_type(request):
    user_agent = request.headers.get("User-Agent").lower()
    if "bitbucket" in user_agent:
        return "bitbucket"
    if "github" in user_agent:
        return "github"
    raise Exception("Could not determine repo type")

def get_from_request(request, field):
    rt = repo_type(request)
    try:
        payload = request.get_json()
        return payload_accessors[rt][field](payload)
    except:
        raise BadRequest("%s not provided" % field)

def start_job(branch, username):
    if not re.match(BRANCH_PATTERN, branch):
        raise Ignore("Ignoring push to branch %s" % branch)
    
    me = jobs.add(branch, username)
    while not jobs.is_current(me):
        log.debug("Waiting in queue, current position is %d" % jobs.index(me))
        time.sleep(5)
        pass

    log.debug("Starts merging %s" % branch)
    log.indent = 1
    git.clean()
    try:
        me["progress"].append("Getting sources")
        git.checkout(branch)
        me["progress"].append("Building sources")
        bash.execute(BUILD_SCRIPT, BuildFailure)
        me["progress"].append("Merging to %s" % MASTER)
        git.merge(branch)
        me["progress"].append("Done")
    except:
        log.debug("Exception during merge, starting cleanup")
        git.clean()
        raise
    finally:
        git.delete(branch)
        jobs.finish_current()
        log.indent = 0

    log.debug("merge succesful")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
