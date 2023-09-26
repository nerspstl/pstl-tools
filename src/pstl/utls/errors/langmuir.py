
class FailedLangmuirAlgorithmConvergence(Exception):
    """Raised when the Single probe Langmuir algorithm cannot converge on a sheath type"""

    def __init__(self, msg="Failed to converge in Langmuir algorithm"):
        self.msg = msg
        Exception.__init__(self, self.msg)