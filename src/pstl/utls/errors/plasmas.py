class FailedPlasmaClassBuild(Exception):
    """Raised when a Plasma class is tried to be made but something fails"""

    def __init__(self, msg="Failed to make Plasma class"):
        self.msg = msg
        Exception.__init__(self, self.msg)