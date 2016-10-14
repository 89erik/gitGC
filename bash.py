from subprocess import Popen, PIPE
import log

def execute(command, failure):
    log.debug(command)
    rv = execute_inner(command)
    if rv["rc"] != 0:
        raise failure("Command \"%s\" failed: \n%s%s" % (command, rv["stdout"], rv["stderr"]))

def execute_inner(command):
    p = Popen(command.split(" "), stdout=PIPE, stderr=PIPE)
    rv = p.communicate()
    return { 'stdout': rv[0], 'stderr': rv[1], 'rc': p.returncode }

