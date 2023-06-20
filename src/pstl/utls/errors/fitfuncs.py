class FitConvergenceError(Exception):
    """Raised when Convergence of fit routine could not be found. 
    This was created so that a try and except could be used to account for convergence error such that 
    another method maybe used to achieve same result as this fit routine."""


class MissingReturnError(Exception):
    """Raised when a return argument was not suppose to be empty, but was being returned empty. 
    This is most likely a bug in the code"""

    def __init__(self, msg="Missing Return argument. Maybe a bug in the code"):
        self.msg = msg
        Exception.__init__(self, self.msg)

