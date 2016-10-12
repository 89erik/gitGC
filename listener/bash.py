from subprocess import Popen, PIPE, call
from gc_exceptions import BuildFailure
import log

def execute(command, failure):
    p = Popen(command.split(" "), stdout=PIPE, stderr=PIPE)
    rv = p.communicate()
    rc = p.returncode
    log.debug("%s -> %d" % (command, rc))
    if rc != 0:
        raise failure("Command \"%s\" failed: \n%s%s" % (command, rv[0], rv[1]))

def execute_without_log(command):
    p = Popen(command.split(" "), stdout=PIPE, stderr=PIPE)
    rv = p.communicate()
    return { 'stdout': rv[0], 'stderr': rv[1], 'exit': p.returncode }

def get_log(n):
    r = execute_without_log("tail -n %s %s" % (n, LOG_FILE))
    return r["stdout"]
