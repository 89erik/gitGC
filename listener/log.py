from datetime import datetime

LOG_FILE = "log"
indent = 0

def _write(msg):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = "%s    %s%s" % (now, " " * indent * 4, msg)
    msg = msg.replace("\n", "\n" + (" " * (4 + len(now) + indent * 4)))


    print msg
    with open(LOG_FILE, "a") as log_file:
        log_file.write(msg + "\n")

def debug(msg, extra_indent=0):
    global indent
    indent += extra_indent
    _write(msg)
    indent -= extra_indent

error = debug
warning = debug
