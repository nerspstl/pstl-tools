import string
from typing import Any, Optional, Union, Tuple, Sequence, Callable
import traceback

import numpy as np
import numpy.typing as npt
from numpy.polynomial import Polynomial as P
from numpy.linalg import LinAlgError
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.signal import savgol_filter, find_peaks
import pandas as pd

from pstl.utls.errors import FitConvergenceError, MissingReturnError, FunctionFitError
from pstl.utls.verify import verify_iterables, verify_1D_array, verify_type


class FunctionFit:
    def __init__(
            self,
            func: Callable[[npt.ArrayLike, tuple[int | float, ...]], int | float],
            coef: Sequence,
            poly: P,
            domain: Sequence,
            stats: dict,
    ) -> None:

        self.func = func
        self.coef = coef
        self.poly = poly
        self.domain = domain
        self.stats = stats

    def __call__(self, x: npt.ArrayLike, *args: Any, **kwds: Any) -> Any:
        return self.func(x, *self.coef)

    def xrange(self, n: int | None = None, domain: Optional[Sequence] = None):
        if domain is None:
            domain = self.domain  # type: ignore
        if n is None:
            n = int((domain[1]-domain[0])/1e-3)

        return np.linspace(domain[0], domain[1], n)  # type: ignore

    def yrange(self, n: int | None = None, domain: Optional[Sequence] = None):
        if domain is None:
            domain = self.domain  # type: ignore
        if n is None:
            n = int((domain[1]-domain[0])/1e-3)

        # type: ignore
        return self.__call__(np.linspace(domain[0], domain[1], n))


class ExponentialFit(FunctionFit):
    def __init__(self, poly: P, domain: npt.ArrayLike, stats: dict = {}) -> None:
        func = _fit_exponential_func
        coef = poly.convert().coef
        super().__init__(func, coef, poly, domain, stats)  # type: ignore


class PolynomialFit(FunctionFit):
    def __init__(self, poly: P, domain: npt.ArrayLike, stats: dict = {}) -> None:
        func = _fit_polynomial_func
        coef = poly.convert().coef
        super().__init__(func, coef, poly, domain, stats)  # type: ignore


class PowerFit(FunctionFit):
    def __init__(self, power: int | float, poly: P, domain: Sequence, stats: dict = {}, polarity: int = 1) -> None:
        func = _fit_power_func
        coef = poly.convert().coef
        self.power = power
        self._polarity = polarity
        super().__init__(func, coef, poly, domain, stats)

    def __call__(self, x: npt.ArrayLike, *args: Any, **kwds: Any) -> Any:
        result = self.func(
            self.power,
            x,  # type: ignore
            *self.coef)*self._polarity
        return result


class CustomFit(FunctionFit):
    def __init__(self, func, coef, domain, fit_xrange, stats={}):
        poly = P([0, 1], domain=fit_xrange)
        super().__init__(func, coef, poly, domain, stats)  # type: ignore


def make_CustomFit(func, voltage, current, coefs):
    domain = [np.min(voltage), np.max(voltage)]
    # make fit function
    indexs = np.where(current != 0)[0]
    vmin = voltage[indexs[0]]
    vmax = voltage[indexs[-1]]
    fit_xrange = [vmin, vmax]

    fit = CustomFit(func, coefs, domain, fit_xrange)
    return fit


def safe_sqrt(x):
    mask = x < 0
    sqrt_x = np.sqrt(np.abs(x))
    sqrt_x[mask] = np.nan
    return sqrt_x


def method_not_found(method, available_methods):

    # make table string to print
    table = "\n".join([f"{k}\t{v}" for k, v in available_methods.items()])

    # raise error and make table
    raise ValueError(
        f"Matching method not found: {method}\nChoose from one of the available options:\n{table}")


def get_method_options(method, available_methods) -> tuple[int, str]:
    imethod: int | None = None
    vmethod: str | None = None
    if isinstance(method, int) and method in available_methods:
        # perform action using list of strings tied to the integer key
        imethod = method
        vmethod = available_methods[method][0]

    elif isinstance(method, str):
        # perform action using the string as the method name
        # check if the string matches any of the available_methods
        for key, value in available_methods.items():
            if method.lower() in value:
                imethod = key
                vmethod = value[0]
    else:
        imethod = None
        vmethod = None

    # make returns
    if imethod is None or vmethod is None:
        returns: tuple[int, str] = (0, "")
        # will raise error below
        method_not_found(method, available_methods)
    else:
        returns: tuple[int, str] = (imethod, vmethod)

    return returns


def method_selector(method, available_methods, available_functions):
    imethod, _ = get_method_options(method, available_methods)
    func = available_functions[imethod]
    return func


def method_function_combiner(dict1, dict2):
    if set(dict1.keys()) != set(dict2.keys()):
        raise ValueError("The two dictionaries do not have the same keys!")
    new_dict = {}

    for key in dict1.keys():
        new_dict[key] = (dict1[key], dict2[key])

    return new_dict


def probe_radius_to_debye_length(lambda_D, radius_probe):
    l = np.abs(lambda_D)  # Debye length [m]
    rp = np.abs(radius_probe)  # radius of probe [m]

    ratio = np.divide(rp, l)

    if ratio <= 3:
        sheath = "thick/OML"
    elif ratio >= 50:
        sheath = "thin"
    else:
        sheath = "transitional"

    other = {"sheath_type": sheath}
    return ratio, other


def find_intersection(coefs1, coefs2):
    m1, b1 = coefs1
    m2, b2 = coefs2
    # check if lines are parallel
    if m1 == m2:
        return None

    # calculate intersection point
    x_intersect = (b2 - b1) / (m1 - m2)
    y_intersect = m1 * x_intersect + b1

    return np.array([x_intersect, y_intersect])


def count_placeholders(fmt):
    count = 0
    L = string.Formatter().parse(fmt)
    for x in L:
        if x[1] is not None:
            count += 1
    return count


def get_rsquared(yexperimental, ypredicted):
    if len(yexperimental) != len(ypredicted):
        raise ValueError(
            "Vector 1 and Vector 2 arrays must have the same length.")

    corr_matrix = np.corrcoef(yexperimental, ypredicted)
    corr = corr_matrix[0, 1]
    rsq = corr**2

    return rsq


def determine_step(step: int | float, step_type: str, len_x: int) -> int:
    if step_type == 'index':
        istep = int(step)
    elif step_type == "percent":
        istep = int(step*len_x)
    elif step_type == "distance":
        raise NotImplementedError
    else:
        raise ValueError(
            "'step_type' does not match 'index' or 'percent': %s" % (str(step_type)))

    # make istep at least one
    if istep == 0:
        istep += 1
    return istep


def find_fit(
        xdata: npt.ArrayLike, ydata: npt.ArrayLike, deg: int = 1, power: int | float = 1, polarity: int = 1,
        reverse: bool = False, return_best: bool = False, fit_type: str = "polynomial",
        min_points: int = 5, istart: int | None = None, iend: int | None = None, invalid: str = "ignore",
        fstep: int | float | None = None, fstep_type: str | None = None, fstep_adjust: bool = True, fitmax: int | None = None,
        bstep: int | float | None = None, bstep_type: str | None = None, bstep_adjust: bool = True, bitmax: int | None = None,
        threshold_residual: int | float | None = None, threshold_rmse: int | float = 0.30,
        threshold_rsq: int | float = 0.95, threshold_method: str | None = None,
        convergence_residual_percent: int | float = 1.0, convergence_rmse_percent: int | float = 1.0,
        convergence_rsq_percent: int | float = 1.0, convergence_method: str | None = None,
        strict: bool = False, full: bool = False, printlog: bool = False) -> FunctionFit:
    # Convert xdata and ydata to numpy arrays
    xdata = np.array(xdata)
    ydata = np.array(ydata)

    # Set Defaults for threshold residual if not given
    threshold_residual = 0 if threshold_residual is None else threshold_residual

    # Set Defeaults for if reverse or standard direction
    if reverse:
        fstep = 0.1 if fstep is None else fstep
        fstep_type = "percent" if fstep_type is None else fstep_type
        bstep = 1 if bstep is None else bstep
        bstep_type = "index" if bstep_type is None else bstep_type
        fitmax = None if fitmax is None else (
            None if fitmax == "none" else fitmax)
        bitmax = None if bitmax is None else (  # changed 1 -> None
            None if bitmax == "none" else bitmax)
    else:
        bstep = 0.1 if bstep is None else bstep
        bstep_type = "percent" if bstep_type is None else bstep_type
        fstep = 1 if fstep is None else fstep
        fstep_type = "index" if fstep_type is None else fstep_type
        fitmax = None if fitmax is None else (  # changed 1 -> None
            None if fitmax == "none" else fitmax)
        bitmax = None if bitmax is None else (
            None if bitmax == "none" else bitmax)

    # verify keyword argument 'deg' is int
    verify_type(deg, int, 'deg')

    # verify keyword argument 'power' is int or float
    verify_type(power, (int, float), 'power')

    # verify keyword argument 'fit_type' is str
    verify_type(fit_type, str, 'fit_type')

    # correct deg if 'fit_type' == linear
    if fit_type == "linear":
        deg = 1

    # Set Defaults for threshold_method and convergence_method based on fit_type and deg
    if fit_type == "linear" or (fit_type == "polynomial" and deg == 1):
        threshold_method = "rsq" if threshold_method is None else threshold_method
        convergence_method = "rsq" if convergence_method is None else convergence_method
    else:
        threshold_method = "rmse" if threshold_method is None else threshold_method
        convergence_method = "rmse" if convergence_method is None else convergence_method

    # verify keyword arguments with bools are bool s.t. the loops below will not contiue if not True
    verify_type(reverse, bool, 'reverse')
    verify_type(return_best, bool, 'return_best')
    verify_type(fstep_adjust, bool, 'fstep_adjust')
    verify_type(bstep_adjust, bool, 'bstep_adjust')
    verify_type(strict, bool, 'strict')
    verify_type(full, bool, 'full')
    verify_type(printlog, bool, 'printlog')

    # Verify that these are arrays/iterable
    # and get lengths of data and check they are the same length
    verify_iterables(xdata, ydata)
    verify_1D_array(xdata)
    verify_1D_array(ydata)
    len_x = len(xdata)

    # convert convergence values from percent -> decimal for comparison later
    convergence_residual_percent_decimal = np.divide(
        convergence_residual_percent, 100)
    convergence_rmse_percent_decimal = np.divide(
        convergence_rmse_percent, 100)
    convergence_rsq_percent_decimal = np.divide(
        convergence_rsq_percent, 100)

    # convergence criteria
    if printlog:
        print("Fit Type: {}".format(fit_type))
        print("Strict Candidate: {0}".format(strict))
        print("Threshold Method: %s" % (threshold_method))
        print("Threshold Absolute Residual: {0:0.2e}".format(
            threshold_residual))
        print("Threshold RMSE %: {0:0.2%}".format(threshold_rmse))
        print("Threshold Rsquared: {0:.2f}".format(threshold_rsq))
        print("Convergence Method: %s" % (convergence_method))
        print("Convergence Residual Percent: {0:.2%}".format(
            convergence_residual_percent/100))
        print("Convergence RMSE Percent: {0:.2%}".format(
            convergence_rmse_percent/100))
        print("Convergence Rsquared Percent: {0:.2%}".format(
            convergence_rsq_percent/100))
        print(f"Reverse: {reverse}")
        print(f"Iteration Max: Forward: {fitmax}; Backward: {bitmax}")

    # initialize best trackers
    best_residual = float("inf")
    best_rmse = float("inf")
    best_rsq = float("-inf")
    best_fit = None

    # Initialize Exit, Threshold, and Convergence flags to finish
    threshold = False
    convergence = False
    exit = False

    # inintialize Return fit
    fit = None

    # initialize x,y arrays
    x = xdata[istart:iend]
    y = ydata[istart:iend]

    # if reverse direction
    if reverse:
        # initialize counter index backward
        jend = int(len_x) if iend is None else int(iend) if int(iend)>=0 else int(len_x)+int(iend)
        # initiailize counter index forward
        jstart = 0 if istart is None else int(istart) if int(istart)>=0 else int(len_x)+int(istart)
    else:
        # initialize counter index forward
        jstart = 0 if istart is None else int(istart) if int(istart)>=0 else int(len_x)+int(istart)
        # initiailize counter index backward
        jend = int(len_x) if iend is None else int(iend)if int(iend)>=0 else int(len_x)+int(iend)

    # initialize jfstep, jbstep index advancement counters
    jfstep = 0
    jbstep = 0

    # initialize inner and outer loop counters
    # initialize forward loop counter
    fiteration = 0
    # initialize backward loop counter
    biteration = 0

    # function for returning a fit class

    def create_fit():
        stats = {'rmse': rmse, 'residual': residual}
        stats.update(
            {'rsq': rsq}) if fit_type == "linear" or (fit_type == "polynomial" and deg == 1) else stats

        # if all components are wanted, added them to status dictionary
        stats.update({'rel_err': rel_diff_err,
                     'residuals': diff_err}) if full else stats

        # Create fit class depending on fit_type
        xrange = [np.min(x), np.max(x)]
        if fit_type == "linear" or fit_type == "polynomial":
            fit = PolynomialFit(poly, xrange, stats)
        elif fit_type == "exponential":
            fit = ExponentialFit(poly, xrange, stats)
        elif fit_type == "power":
            fit = PowerFit(power, poly, xrange, stats, polarity)
        else:
            raise ValueError("something went wrong in creating fit class")
        return fit

    # outer loop helper function
    def outer():
        step_bool = ((jend >= min_points if istart is None else istart+min_points) if reverse else (jstart <= len_x-min_points if iend is None else iend-min_points)) 
        iteration_num_bool = ((biteration < bitmax if bitmax is not None else True) if reverse else (fiteration < fitmax if fitmax is not None else True))
        out = step_bool and  iteration_num_bool
        return out

    # inner loop helper function
    def inner():
        step_bool = (jstart <= jend-min_points) if reverse else (jend >= jstart+min_points)
        iteration_num_bool= ((fiteration < fitmax if fitmax is not None else True) if reverse else (biteration < bitmax if bitmax is not None else True))
        out =  step_bool and iteration_num_bool

        return out

    # Start outer loop to continue till the length of array from start index to end is less than minimum points
    while outer():

        # Restart residual and rsme convergence trackers because the outerloop restarted and would not be a fair comparison
        last_residual = float("inf")
        last_rmse = float("inf")
        last_rsq = float("inf")

        # Start inner loop to continue till the length of the array between start index and to end index is less than minimum points
        while inner():
            # Grab the arrays with specified start indexes
            x = xdata[jstart:jend]
            y = ydata[jstart:jend] * polarity

            try:

                if fit_type == "linear" or (fit_type == "polynomial" and deg == 1):
                    # Determine the Coefs for linear (same as polynomial but deg is automatically set to 1 no matter what
                    # This uses  ~numpy.polonomial.Polonomial.fit (note: this is least squares fit )
                    poly = P.fit(x, y, deg=deg)
                    # y-values on standared plot using x-values of actual data area of interest
                    yp = poly.convert()(x)

                elif fit_type == "polynomial":
                    # Determine the Coefs for polynomial using regression fit using ~numpy.polonomial.Polonomial.fit (note: this is least squares fit )
                    poly = P.fit(x, y, deg=deg)
                    # y-values on standared plot using x-values of actual data area of interest
                    yp = poly.convert()(x)

                elif fit_type == "exponential":
                    # Take natural log of data
                    logy = np.log(y)
                    # Determine the Coefs for semilogy using linear regression fit in semilogy space (note: this is non-linear regression)
                    poly = P.fit(x, logy, 1, w=np.sqrt(y))
                    # poly = P.fit(x, logy, 1)
                    # popt, opt = curve_fit(_fit_exponential_func, x,
                    #                      y, p0=poly.convert().coef)
                    # poly.coef = np.polynomial.polyutils.mapdomain(
                    #    popt, [-1, 1], poly.domain)
                    # poly.domain = [-1, 1]

                    # y-values on standared plot using x-values of actual data area of interest
                    yp = np.exp(poly.convert()(x))

                elif fit_type == "power":
                    # Take inverse power of data
                    mody = np.power(y, 1/power)
                    # Determine the Coefs for fit using linear regression fit in mod power space (note: this is non-linear regression)
                    poly = P.fit(x, mody, 1)

                    # y-values on standared plot using x-values of actual data area of interest
                    temp = poly.convert()(x)
                    if invalid == "ignore":
                        with np.errstate(invalid='ignore'):
                            yp = np.power(temp, power)
                    else:
                        yp = np.power(temp, power)

                    # correct for polarity
                    # yp *= polarity

                    # check for nan because of the root
                    inan = np.argwhere(np.isnan(yp))

                    # remove nans for comparisons
                    # y = np.delete(y, inan)
                    # yp = np.delete(yp, inan)

                else:
                    raise ValueError("'fit_type' is not a known value of 'linear', 'polynomial', 'exponential', or 'power': {}".format(
                        fit_type
                    ))
                    
            except ValueError as err:
                print("ValueError Fail: functionfit")
                traceback.print_exc()
                raise ValueError(err)
            except LinAlgError as err:
                print("General Fail: functionfit")
                traceback.print_exc()
                print("X-data:")
                print(x)
                print("Y-data:")
                print(y)
                raise FunctionFitError
            # The following are used to determine if the fit is good
            # Two criteria maybe used to determine the goodness of fit
            # Root Mean Square Error (RMSE) of the Relative Difference Error -> rmse_rel_diff_err
            # Absolute Residual (Residual) - The sum of the absolute difference between input (experimental) and the fitted (theoretical) -> residual
            # Difference Error -> diff_err
            diff_err = np.subtract(y, yp)
            # Absolue Difference Error -> abs_diff_err
            abs_diff_err = np.abs(diff_err)
            # Relative Difference Percent Error (decimal form) -> rel_diff_err
            rel_diff_err = np.divide(diff_err, yp)
            # Relative Difference Percent Error (percent from) -> rel_per_diff_err (not used currently, maybe removed)
            rel_per_diff_err = np.multiply(rel_diff_err, 100)
            # Root Mean Square of Relative Differnece Percent Error (decimal form) -> rmse_rel_diff_err
            rmse_rel_diff_err = np.sqrt(np.mean(np.power(rel_diff_err, 2)))
            # Root Mean Square of Relative Differnece Percent Error (percent form) -> rmse_rel_per_diff_err (not used currently, maybe removed)
            rmse_rel_per_diff_err = np.multiply(rmse_rel_diff_err, 100)

            # rmse value used for comparison (convience only)
            rmse = rmse_rel_diff_err.copy()

            # total absolute residual -> residual
            residual = np.sum(abs_diff_err)

            # correlation coefs for Rsquared (not really used outside of 'linear' fit_type)
            corr_matrix = np.corrcoef(y, yp)
            corr = corr_matrix[0, 1]
            rsq = corr*corr

            # Calculate convergence for both Residual and RMSE
            # get the decimal form of relative difference of residual from last point
            convergence_residual = np.abs(np.divide(np.subtract(
                last_residual, residual), last_residual)) if last_residual != float("inf") else float("inf")
            # get the difference of in decimal form of the last two rmse
            convergence_rmse = np.abs(np.subtract(
                last_rmse, rmse)) if last_rmse != float("inf") else float("inf")
            # get the difference of in decimal form of the last two Rsquared
            convergence_rsq = np.abs(np.subtract(
                last_rsq, rsq)) if last_rsq != float("-inf") else float("-inf")

            # After last point was a possible candidate for a solution, check for convergence by checking this point to see the magnitude of the change in solution
            # test this point for convergence, if converges, breaks here so last point is returned and this point is disregared as criteria were meet on last point
            # the input arg 'convergence_method' determines if residual or rmse are used for determining convergence
            if threshold:
                if convergence_method == "both":
                    convergence = convergence_residual <= convergence_residual_percent_decimal and convergence_rmse <= convergence_rmse_percent_decimal
                elif convergence_method == "rmse":
                    convergence = convergence_rmse <= convergence_rmse_percent_decimal
                elif convergence_method == "threshold_residual":
                    convergence = convergence_residual <= convergence_residual_percent_decimal
                elif convergence_method == "rsq" or convergence_method == "rsquared":
                    convergence = convergence_rsq <= convergence_rsq_percent_decimal
                else:
                    raise ValueError("'convergence_method' can only be 'both', 'rmse', 'residual' or 'rsq': %s" % (
                        str(convergence_method)))

            # check if residual is less than threshold and RMSE is less
            if threshold_method == "both":
                threshold = residual <= threshold_residual and rmse <= threshold_rmse
            elif threshold_method == "rmse":
                threshold = rmse_rel_diff_err <= threshold_rmse
            elif threshold_method == "residual":
                threshold = residual <= threshold_residual
            elif threshold_method == "rsq" or threshold_method == "rsquared":
                threshold = rsq >= threshold_rsq
            else:
                raise ValueError("'threshold_method' can only be 'both', 'rmse', 'residual', or 'rsq': %s" % (
                    str(threshold_method)))

            # If strict, threshold and convergence must both be meet for both canidite point and convergence test point
            # else, only convergence has to be made between the two points since threshold was meet on the canidite point
            # Then, exit is set to true to break
            exit = threshold and convergence if strict else convergence

            # If printlog is True, show steps in printed log
            if printlog:
                print("----------------------------------------------")
                print("jstart: {0}\tjend: {1}\tforward step: {2}\tbackward step: {3}".format(
                    jstart, jend, jfstep, jbstep))
                print("fiteration: {0}\tbiteration: {1}".format(fiteration,biteration))
                print("Absolute Residual: {0:.2e}\tBest Abs. Residual: {1:.2e}\tLast Abs. Residual: {2:.2e}".format(
                    residual, best_residual, last_residual))
                print("RMSE: {0:.2%}\tBest RMSE: {1:.2%}\tLast RMSE: {2:.2%}".format(
                    rmse_rel_diff_err, best_rmse, last_rmse))
                print("Relative Difference: Max Rel Diff: {0:.2%};\tMin Rel Diff: {1:.2%}".format(
                    np.max(rel_diff_err), np.min(rel_diff_err)))
                print("Rsquared: {0:.2f}\tBest Rsquared: {1:.2f}\tLast Rsquared: {2:.2f}".format(
                    rsq, best_rsq, last_rsq))
                print("Convergence Abs. Residual: {0:.2%}\tConvergence RMSE: {1:.2%}\tConvergence Rsquared: {2:.2%}".format(
                    convergence_residual, convergence_rmse, convergence_rsq))
                print("Candidate:\tThreshold: {0}\tConvergence: {1}\nExit: {2}".format(
                    threshold, convergence, exit))
                # if exit, should quit and add this extra line below
                if exit:
                    print("----------------------------------------------")

            # Exit Loop
            if exit:
                break

            # Have not meet exit criteria, keep updating last interation data if candidate (threshold==True)
            if threshold:
                # Returned Dictionary depending if input keyword arg is True
                # These values are good as they were saved before the next loop, therefore they will only besaved for candidate
                # adds rsq if linear
                fit = create_fit()

            # if the best fit option is given, the best fit is also stored temporarly and returned if convergence is not made
            if return_best:
                if threshold:
                    best_fit = fit
                else:

                    if threshold_method == "both" or threshold_method == "residual":
                        # Keep track of best residual (not neccessarily the best fit)
                        if residual <= best_residual:
                            best_residual = residual.copy()
                            best_fit = create_fit()

                    elif threshold_method == "both" or threshold_method == "rmse":
                        # Keep track of best RMSE (not neccessarily the best fit)
                        if rmse <= best_rmse:
                            best_rmse = rmse.copy()
                            best_fit = create_fit()

                    elif threshold_method == "rsq" or threshold_method == "rsquared":
                        # Keep track of best Rsquared (not neccessarily the best fit)
                        if rsq >= best_rsq:
                            best_rsq = rsq.copy()
                            best_fit = create_fit()

                    else:
                        raise ValueError("something went wrong in return_best")

            # Update the last residual and rmse (must be after printlog)
            last_residual = residual.copy()
            last_rmse = rmse.copy()
            last_rsq = rsq.copy()

            # If reverse, move forward, else move backward
            if reverse:
                # If break does not happen yet, determine forward step size
                jfstep = determine_step(fstep, fstep_type, len(
                    x)) if fstep_adjust else determine_step(fstep, fstep_type, len_x)
                # Forward counter index is advanced with step
                jstart += jfstep
                # advance interation
                fiteration += 1
            else:
                # If the break did not happen yet, determine the backward step size
                jbstep = determine_step(bstep, bstep_type, len(
                    x)) if bstep_adjust else determine_step(bstep, bstep_type, len_x)
                # the backward counter index is advanced with step
                jend -= jbstep
                # advance interation
                biteration += 1

        # Exits the outerloop if criteria meet
        if exit:
            break

        # Restart conter index for inner loop
        if reverse:
            # initiailize or restart counter index forward
            jstart = 0 if istart is None else int(istart)
            # restart inner loop couter
            fiteration = 0
        else:
            # initiailize or restart counter index backward
            jend = int(len_x) if iend is None else int(iend)
            # restart inner loop couter
            biteration = 0

        # For Outer loop: If reverse, move backward, else move forward
        if reverse:
            # If the break did not happen yet, determine the backward step size
            jbstep = determine_step(bstep, bstep_type, len(
                x)) if bstep_adjust else determine_step(bstep, bstep_type, len_x)
            # the backward counter index is advanced with step
            jend -= jbstep
            # advance outer interation
            biteration += 1
        else:
            # If break does not happen yet, determine forward step size
            jfstep = determine_step(fstep, fstep_type, len(
                x)) if fstep_adjust else determine_step(fstep, fstep_type, len_x)
            # Forward counter index is advanced with step
            jstart += jfstep
            # advance outer interation
            fiteration += 1

    # if exit is True, then criteria meet and can exit
    if exit:
        if fit:
            return fit
        else:
            raise MissingReturnError
    elif return_best:
        if best_fit:
            return best_fit
        else:
            raise FitConvergenceError
    else:
        raise FitConvergenceError


def normalize(x: np.ndarray) -> np.ndarray:
    """
    Returns the normalized ndarray of input array

    Parameters
    ----------
    x : arraylike
        A 1D array to be normalized.

    Returns
    -------
    np.ndarray
        Normalized np.ndarray.
    """
    return (x-np.min(x))/(np.max(x)-np.min(x))


def residual(xdata: np.ndarray, xdata_mean: np.ndarray):
    """
    Returns the residual (difference) between the two arrays

    Parameters
    ----------
    xdata :  arraylike
        A 1D array of experimental data
    xdata_mean : arraylike
        A 1D array of mean of the experimental data

    Returns
    -------
    np.ndarray
        Residual
    """
    # verify same length


def preproces_data(xdata: np.ndarray) -> np.ndarray:

    # initialize and set default
    outdata = np.ndarray(np.size(xdata), dtype=None)
    return outdata


def _fit_linear_func(x, b, m):
    return m*x+b


def _fit_exponential_func(x, *args):
    total = _fit_polynomial_func(x, *args)
    return np.exp(total)


def _fit_power_func(power, x, *args, invalid="ignore"):
    total = _fit_polynomial_func(x, *args)
    # print(total) if np.any(np.isnan(total)) else None
    # print(power)
    if invalid == "ignore":
        with np.errstate(invalid="ignore"):
            res = np.power(total, power)
    else:
        res = np.power(total, power)
    # print(res) if np.any(np.isnan(res)) else None
    return res


def _fit_polynomial_func(x, *args):
    total = 0.0
    for k, arg in enumerate(args):
        total = np.add(
            total,
            np.multiply(
                arg,
                np.power(
                    x,
                    k
                )
            )
        )

    return total
