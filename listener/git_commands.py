import bash
from gc_exceptions import MergeFailure

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

class Repository(object):
    def __init__(self, path):
        self.prefix = "git -C %s " % path
        self.master = "master"

    def checkout(self, branch):
        self.execute(FETCH)
        self.execute(CHECKOUT % self.master)
        self.execute(PULL % self.master)
        self.execute(CHECKOUT % branch)
        self.execute(MERGE % self.master)
        
    def merge(self, branch):
        self.execute(CHECKOUT % self.master)
        self.execute(MERGE % branch)
        self.execute(PUSH % self.master)

    def delete(self, branch):
        self.execute(DELETE_BRANCH_LOCAL % branch)
        self.execute(DELETE_BRANCH_REMOTE % branch)

    def clean(self):
        self.execute(RESET)
        self.execute(CLEAN)

    def status(self):
        return self.get(STATUS)

    def tree(self):
        return self.get(TREE)

    def execute(self, command):
        bash.execute(self.prefix + command, MergeFailure)
        
    def get(self, command):
        rv = bash.execute_without_log(self.prefix + command)
        return rv["stdout"]
