

class MonolithError(Exception):

    def __init__(self, message, code=-1):
        self.message = message
        self.code = code


class CLIError(MonolithError):
    pass


class CommandError(CLIError):
    pass


class AlreadyRegistered(CLIError):
    pass

