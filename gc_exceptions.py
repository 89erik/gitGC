import log

class GcException(Exception):
    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        self.status_code = status_code if status_code else 500
        self.payload = payload
    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

class BadRequest(GcException):
    def __init__(self, message, payload=None):
        GcException.__init__(self, message, 400, payload)
    def log_exception(self):
        log.warning("BadRequest: " + self.message)

class NotFound(GcException):
    def __init__(self, message, payload=None):
        GcException.__init__(self, message, 404, payload)
    def log_exception(self):
        pass

class Unauthorized(GcException):
    def __init__(self, message, payload=None):
        GcException.__init__(self, message, 401, payload)

    def log_exception(self):
        pass

class BuildFailure(GcException):
    def __init__(self, message, payload=None):
        GcException.__init__(self, message, 409, payload)
    def log_exception(self):
        log.info("BuildFailure: " + self.message)

class DeployFailure(GcException):
    def __init__(self, message, payload=None):
        GcException.__init__(self, message, 409, payload)
    def log_exception(self):
        log.info("DeployFailure: " + self.message)

class MergeFailure(BuildFailure):
    def log_exception(self):
        log.info("MergeFailure: " + self.message)

class Cancellation(GcException):
    def __init__(self, message, payload=None):
        GcException.__init__(self, message, 200, payload)
    def log_exception(self):
        log.info("Job cancelled during '%s'" % self.message)

class Ignore(GcException):
    def __init__(self, message, payload=None):
        GcException.__init__(self, message, 200, payload)
    def log_exception(self):
        log.debug(self.message)

