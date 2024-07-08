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
from scipy.interpolate import interp1d
import pandas as pd

from pstl.utls import constants as c
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

def interpolate(x,X,Y,method=None):
    # find nearest neighbors (no sorting is performed)
    lenX = len(X)
    k = 0
    while X[k] <= x :
        if X[k] != x:
            if k+1 == lenX:
                raise ValueError("'{x}' not in domain of X")
            elif k+1 > lenX:
                raise ValueError("Something really went wrong")
            if X[k+1] > x:
                break
            elif X[k+1] < x:
                k += 1
            elif X[k+1] == x:
                y = Y[k+1]
                method = None
                break
        else:
            # return the value
            y = Y[k]
            method = None
            break
    # Perform interpolation
    if method is None:
        pass
    elif method == 'linear':
        if x != 0:
            f = interp1d(X[k:k+2],Y[k:k+2] )  # type: ignore
            y: float = f(x)
        else:
            pass
    elif method == 'exponential':
        if x != 0:
            xp = np.log(Y)
            f = interp1d(xp, X)
            y: float = f(x)
        else:
            pass
    elif method == 'logarithmic':
        if x != 0:
            xp = np.log(X)
            f = interp1d(Y, xp)
            y: float = np.exp(f(x))
        else:
            pass
    else:
        raise ValueError("Invalid value for interpolate parameter.")
    return y


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


def ideal_gas_law_pressure_to_density(P_gas, T_gas: int | float = 300):
    """
    Returns neutral gas density [Torr]

    Parameters:
    P_gas [Torr]
    T_gas (optional=300) [K]
    """

    P = P_gas
    P = P*101325/760            # unit: J/m^3 <- [Torr]*[101325 Pa/760 Torr]*[1 J/m^3/1 Pa] NOTE: 1 atm = 101325 Pa = 760 Torr
    N = P/(c.K_B*T_gas )        # unit: m^-3 <- [J/m^3]/([J/K]*[K])
    return N                    # unit: m^-3