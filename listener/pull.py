#! venv/bin/python

from flask import Flask, Response, json, jsonify, request
from time import asctime
import re
import os

from gc_exceptions import *
import git_commands
import bash
import log

ROOT = os.path.dirname(os.path.realpath(__file__))
BUILD_SCRIPT = ROOT + "/build.sh"
git = git_commands.Repository(ROOT + "/repository")
BRANCH_PATTERN = re.compile(r"GC_\d{4}-\d{2}-\d{2}_\d{4}\.\d{2}\.\d+")
log.debug("---[ STARTING SERVER ]---")

app = Flask(__name__)
res = {}


@app.errorhandler(404)
def not_found(e):
    return "NOT FOUND: %s" % request.path, 404

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
        branch = get_branch_name(request)
        try_merge(branch)
        res['time'] = asctime()
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
    payload["time"] = asctime()
    response = jsonify(payload)
    response.status_code = error.status_code
    return response


def get_branch_name(request):
    try:
        content = request.get_json()
        return content["push"]["changes"][0]["new"]["name"]
    except:
        raise BadRequest("Branch name not provided")


def try_merge(branch):
    if not re.match(BRANCH_PATTERN, branch):
        raise Ignore("Ignoring push to branch %s" % branch)
    log.debug("Starts merging %s" % branch)
    log.indent = 1
    git.clean()
    try:
        git.checkout(branch)
        bash.execute(BUILD_SCRIPT)
        git.merge(branch)
    except:
        log.debug("Exception during merge, starting cleanup")
        git.clean()
        raise
    finally:
        git.delete(branch)

    log.indent = 0
    log.debug("merge succesful")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
