#! venv/bin/python

from flask import Flask, Response, json, jsonify, request, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from datetime import datetime, timedelta
import hmac
import hashlib
import time
import re
import os

from gc_exceptions import *
import git_commands
import bash
import log
import jobs
import db

app = Flask(__name__)
Bootstrap(app)
app.config.from_object("config")

ROOT = os.path.dirname(os.path.realpath(__file__))
BUILD_SCRIPT = ROOT + "/build.sh"
SUPPORTED_REPO_TYPES = ["github", "bitbucket"]
git = git_commands.Repository(ROOT + "/repository", app.config["MASTER"])


res = {}

@app.route("/add/<username>/<branch>")
def add_fake_job(username, branch):
    job = jobs.add(branch, username)
    print jobs.get()
    return redirect(url_for("get_jobs"))


@app.route("/job/<id>", methods=["GET"])
def get_job(id):
    job = jobs.get_by_id(id)
    if not job:
        job = db.find_job(id)
    return render_template("job.html", job=job)


@app.route("/jobs", methods=["GET"])
@app.route("/jobs/<int:hours>", methods=["GET"])
def get_jobs(hours=None):
    if not hours: hours = 24
    since = datetime.now() - timedelta(hours=hours)
    jobs = db.find_jobs(since)
    return render_template("jobs.html", jobs=jobs)

@app.route("/", methods=["GET"])
@app.route("/current_jobs", methods=['GET'])
@app.route("/current_jobs/<username>", methods=['GET'])
def get_current_jobs(username=None):
    return render_template("jobs.html", jobs=jobs.get())

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
        if not authenticate(request):
            raise Unauthorized()
        branch = get_from_complex_request(request, "branch_name")
        username = get_from_complex_request(request, "username")
        start_job(branch, username)
        res['payload'] = json.loads(request.form.get('payload',"{}"))
        res['headers'] = dict(request.headers.items())
        return ""
    else:
        return Response(json.dumps(res, indent=None if request.is_xhr else 2),
                        mimetype='application/json')

@app.route("/config", methods=["GET"])
def get_config():
    status = { "remote_problems": git.remote_problems() }
    config = { "remote": git.remote }
    return render_template("config.html", status=status, config=config)

@app.route("/config", methods=["POST"])
def set_config():
    remote = get_from_form(request, "remote")
    repo_type = get_from_form(request, "repo_type", str.lower)

    if repo_type not in SUPPORTED_REPO_TYPES and False: # This is ignored for now
        msg = "Repo type '%s' not supported. Supported types are %s" % (repo_type, SUPPORTED_REPO_TYPES)
        raise BadRequest(msg)
    git.remote = remote

    return redirect(url_for("get_config"))


@app.errorhandler(404)
def not_found(e):
    return bad_request_handler(NotFound("Invalid URL"))

@app.errorhandler(GcException)
def bad_request_handler(error):
    error.log_exception()
    payload = error.to_dict()
    payload["time"] = time.asctime()
    response = jsonify(payload)
    response.status_code = error.status_code
    return render_template("error.html", code=error.status_code, name=type(error).__name__, payload=payload), error.status_code

def authenticate(request):
    digester = hmac.new(app.config["HOOK_KEY"], request.data, hashlib.sha1)
    requestHash = "sha1=%s" % digester.hexdigest()
    requestSecret = request.headers["X-Hub-Signature"]
    diff = sum(i != j for i, j in zip(requestHash, requestSecret))
    return diff == 0

def username_github(payload):
    return payload["pusher"]["name"]

def username_bitbucket(payload):
    return payload["actor"]["username"]

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

def get_from_form(request, field, convert=lambda x:x):
    if not field in request.form:
        raise BadRequest("%s not provided" % field)
    return convert(str(request.form[field]))

def get_from_complex_request(request, field):
    rt = repo_type(request)
    try:
        payload = request.get_json()
        return payload_accessors[rt][field](payload)
    except:
        raise BadRequest("%s not provided" % field)

def start_job(branch, username):
    if not re.match(app.config["BRANCH_PATTERN"], branch):
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
    app.run(host='0.0.0.0', port=8080)
    log.debug("---[ STARTING SERVER ]---")
