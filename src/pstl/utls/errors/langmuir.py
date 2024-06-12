
class FailedLangmuirAlgorithmConvergence(Exception):
    """Raised when the Single probe Langmuir algorithm cannot converge on a sheath type"""

    def __init__(self, msg="Failed to converge in Langmuir algorithm"):
        self.msg = msg
        Exception.__init__(self, self.msg)
class FailedLangmuirAlgorithm(Exception):
    """Raised when the Single probe Langmuir algorithm has a general error"""

    def __init__(self, msg="General Langmuir algorithm error"):
        self.msg = msg
        Exception.__init__(self, self.msg)

class Flagged(Exception):
    """
    Raises this error when something has been flagged so it can be handeled
    """
    def __init__(self, msg=""):
        self.msg = "FLAGGED: "+ msg
        Exception.__init__(self, self.msg)
