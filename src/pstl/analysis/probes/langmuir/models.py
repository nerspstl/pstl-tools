
class langmuir():
    def __init__(self):
        self.probe = None
        self.name = None

class single(langmuir):
    def __init__(self,methods=None:dict):
        self.model = "single"

        ## NOTE
        # review order of methods
        # i beleive elctron temp must go first

        # method for ionSatCurrent
        # 0) (default) Fitted Line value at 
        # intersect with vertical at 
        # floating potential
        # 1) Fitted Line slope zero
        # 2) lowest acceptable value
        # self.methods['ionSat']

        # method for elecSatCurrent
        # 0) (default) Fitted Line value at 
        # intersect with line from  
        # electron temperature
        # 1) @ plasma potential (bend)
        # 2) Fitted Line slope zero
        # self.methods['ionSat']

        _methods(methods=methods)

    def _methods(self,methods=None):
        """Sets up methods for solving single probe langmuir data.
        passed 'methods' are a dictionary of choosen values."""
        if methods is None:
            # All defaults
            methods = {
                    'ionSat':       0,
                    'elecSat':      0,
                    'elecTemp':     0,
                    'floatPot':     0,
                    'plasmaPot':    0
                    }
            self.methods = methods

        ## NOTE
        # Define the _func's

        # set functions based on methods
        for key, num in methods.items():

            # set func for Ion Sat
            if key == 'ionSat':
                if num == 0:    # Fitted @ intersection
                    solve_ionSat = _func_ionSat_intersection 
                elif num == 1:    # Fitted slope equal to zero
                    solve_ionSat = _func_ionSat_slope 
                elif num == 2:    # Minimum
                    solve_ionSat = _func_ionSat_minimum
                else:
                    raise ValueError("'%s' is not accepted for '%s'"%(str(num),key))

            # set func for Electron Sat

