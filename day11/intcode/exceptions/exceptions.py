class IntCodeNotImplemented(Exception):
    def __init__(self, error_string: str):
        super(error_string)


class HaltException(Exception):
    pass


class WaitingForInputException(Exception):
    pass


class YieldAfterOutputException(Exception):
    pass
