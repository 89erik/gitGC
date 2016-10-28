import bash
from gc_exceptions import GcException, MergeFailure

import re
import os
import os.path
import shutil

FETCH = "fetch"
PULL = "pull origin %s"
PUSH = "push origin %s"
CHECKOUT = "checkout %s"
MERGE = "merge %s"
STATUS = "status"
TREE = "--no-pager log --oneline --abbrev-commit --all --graph --decorate"
RESET = "reset --hard"
CLEAN = "clean -f"
DELETE_BRANCH_REMOTE = "push origin --delete %s"
DELETE_BRANCH_LOCAL = "branch -D %s"
ADD_REMOTE = "remote add origin %s"


def _get(command):
    return bash.execute_inner(command)["stdout"]

def _merge_step(command):
    bash.execute(command, MergeFailure)

def _general_action(command):
    bash.execute(command, GcException)

def _stderr(command):
    rv = bash.execute_inner(command)
    if rv["rc"] == 0:
        return ""
    else:
        return rv["stderr"]

class Repository(object):
    def __init__(self, path, master):
        self.prefix = "git -C %s " % path
        self.master = master
        self.path = path
        self._remote = None
        self._remote_problems = None

    @property
    def remote(self):
        if not self._remote:
            self._remote = self._load_remote()
        return self._remote
    
    @remote.setter
    def remote(self, remote):
        print("setting remote to: %s" % remote)
        active_repo = self.path
        backup_repo = active_repo + ".backup"

        shutil.move(active_repo, backup_repo)
        try:
            os.mkdir(active_repo)
            self.init(remote)
        except:
            shutil.move(backup_repo, active_repo)
            raise
        shutil.rmtree(backup_repo)
        self._remote = remote
        self._remote_problems = None

    def remote_problems(self):
        if self._remote_problems == None:
            self._remote_problems = self._execute("ls-remote", _stderr)
        return self._remote_problems

    def init(self, remote):
        self._execute("init", _general_action)
        self._execute(ADD_REMOTE % remote, _general_action)

    def checkout(self, branch):
        self._execute(FETCH)
        self._execute(CHECKOUT % self.master)
        self._execute(MERGE % "origin/"+self.master)
        self._execute(CHECKOUT % branch)
        self._execute(MERGE % self.master)
        
    def merge(self, branch):
        self._execute(CHECKOUT % self.master)
        self._execute(MERGE % branch)
        self._execute(PUSH % self.master)

    def delete(self, branch):
        self._execute(CHECKOUT % self.master)
        try:
            self._execute(DELETE_BRANCH_LOCAL % branch)
            self._execute(DELETE_BRANCH_REMOTE % branch)
        except: pass

    def clean(self):
        self._execute(RESET)
        self._execute(CLEAN)

    def status(self):
        return self._execute(STATUS, _get)

    def tree(self):
        return self._execute(TREE, _get)

    def _execute(self, command, execute_inner=_merge_step):
        return execute_inner(self.prefix + command)
    
    def _load_remote(self):
        config_file = "%s/.git/config" % self.path
        if os.path.isfile(config_file):
            with open(config_file, "r") as f:
                content = f.read()
            m = re.search("\[remote \"origin\"\][^\[]*url = ([^\n]+)", content)
            if m:
                return m.group(1)
        return ""

