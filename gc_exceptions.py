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

class BuildFailure(GcException):
    def __init__(self, message, payload=None):
        GcException.__init__(self, message, 409, payload)

    def log_exception(self):
        log.warning("BuildFailure: " + self.message)

class MergeFailure(BuildFailure):
    def log_exception(self):
        log.warning("MergeFailure: " + self.message)

class Ignore(GcException):
    def __init__(self, message, payload=None):
        GcException.__init__(self, message, 200, payload)

    def log_exception(self):
        log.debug(self.message)

