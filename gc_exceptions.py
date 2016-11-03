import log

class GcException(Exception):
    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        self.logstr = "%s: %s" % (type(self).__name__, message)
        self.status_code = status_code if status_code else 500
        self.payload = payload
    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv
    def log_exception(self):
        pass

class BadRequest(GcException):
    def __init__(self, message, payload=None):
        GcException.__init__(self, message, 400, payload)
    def log_exception(self):
        log.warning(self.logstr)

class NotFound(GcException):
    def __init__(self, message, payload=None):
        GcException.__init__(self, message, 404, payload)

class Unauthorized(GcException):
    def __init__(self, message, payload=None):
        GcException.__init__(self, message, 401, payload)

class BuildFailure(GcException):
    def __init__(self, message, payload=None):
        GcException.__init__(self, message, 409, payload)
    def log_exception(self):
        log.info(self.logstr)

class DeployFailure(GcException):
    def __init__(self, message, payload=None):
        GcException.__init__(self, message, 409, payload)
    def log_exception(self):
        log.info(self.logstr)

class MergeFailure(BuildFailure):
    def log_exception(self):
        log.info(self.logstr)

class Cancellation(GcException):
    def __init__(self, message, payload=None):
        GcException.__init__(self, message, 200, payload)
    def log_exception(self):
        log.info("Job cancelled during '%s'" % self.message)

class Ignore(GcException):
    def __init__(self, message, payload=None):
        GcException.__init__(self, message, 200, payload)
    def log_exception(self):
        log.debug(self.logstr)

