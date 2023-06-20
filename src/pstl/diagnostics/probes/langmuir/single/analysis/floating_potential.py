"""

Testing get_floating_potential func - funcs_floating_potential.py


"""
from dataclasses import dataclass
from typing import Tuple, Any, Dict

import numpy as np
from scipy.interpolate import interp1d

from pstl.utls.verify import verify_type


class FloatingData:
    def __init__(self, vf: float,
                 label_format: str = r"$V_{{f}}$ = {0:.2f}V",
                 label: str | None = None,
                 ):

        self._vf = vf
        self._label_format = label_format
        self._label = label

    @property
    def vf(self):
        return self._vf

    # @vf.setter
    # def set_vf(self, vf_: float):
    #    self._vf = vf_
    def set_vf(self, vf):
        self._vf = vf

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, *args):
        self._label = self._label_format.format(*args)

    @property
    def label_format(self):
        return self._label_format

    @label_format.setter
    def label_format(self, label_format: str):
        self._label_format = label_format


def get_floating_potential(*args, method=0, **kwargs) -> Tuple[float, Dict[str, Any]]:
    # Declare available methods
    available_methods = {
        0: 'consecutive',
    }

    # Converts method: str -> method: int if method is a str
    if isinstance(method, str):
        reversed_methods = {v: k for k, v in available_methods.items()}
        method = reversed_methods.get(method, None)

    # check for match and get which function to use
    # raises value error with options if failed to match
    if method == 0:  # default
        func = consecutive_method
    else:  # makes a table of options if error occurs
        table = "\n".join([f"{k}\t{v}" for k, v in available_methods.items()])
        raise ValueError(
            f"Matching method not found: {method}\nChoose from one of the available options:\n{table}")

    # Call funtion and return result
    return func(*args, **kwargs)


def check_for_floating_potential(V_f, voltage, current, **kwargs):
    # determine starting point (all positive after vf) if not given
    if V_f is None:
        # determine starting point (all positive after V_f)
        floating_kwargs = kwargs.pop('V_f_kwargs', {})
        floating_kwargs.setdefault('method', "consecutive")
        # get floating potential
        V_f, _ = get_floating_potential(
            voltage, current, **floating_kwargs)
    # verify V_f
    verify_type(V_f, (int, float, np.int64, np.float64, np.ndarray), 'V_f')

    return V_f


def get_above_floating_potential(V_f, voltage, current, **kwargs):
    # Once floating Potential is found, find its index w.r.t. data
    istart = np.where(voltage < V_f)[0][-1]+1
    # Get data from positive current values (above floating)
    xdata = voltage[istart:]
    ydata = current[istart:]

    return istart, xdata, ydata


def get_below_floating_potential(V_f, voltage, current, **kwargs):
    # Once floating Potential is found, find its index w.r.t. data
    iend = np.where(voltage < V_f)[0][-1]+1
    # Get data from positive current values (above floating)
    xdata = voltage[:iend]
    ydata = current[:iend]

    return iend, xdata, ydata


def consecutive_method(
        voltage, current, *args,
        min_points=5, threshold=None, interpolate=None,
        **kwargs) -> Tuple[float, Dict[str, Any]]:
    """
    Solves for the floating potential on a Langmuir probe trace by determining
    the voltage at which the current is always positive following a transition
    from negative to positive or zero current over a minimum number of points.

    Parameters
    ----------
    voltage : array_like
        A 1D array containing the voltage data.
    current : array_like
        A 1D array containing the current data.
    min_points : int, optional
        The minimum number of consecutive points with positive current required
        to determine the floating potential. Defaults to 5.
    threshold : int, optional
        The maximum number of points left to check in the data if the current
        is not continuously positive after the transition point. Defaults to
        the value of `min_points`.
    interpolate : str or None, optional
        The type of interpolation to use to determine the floating potential.
        Must be one of 'linear', 'exponential', or 'logarithmic'. If None, no
        interpolation is performed. Defaults to None.

    Returns
    -------
    float
        The floating potential in volts, or np.nan if no floating potential
        could be found. For example, if `get_floating_potential` is called on
        a set of voltage and current data, the function may return a floating
        potential value of -4.2 V.

    Raises
    ------
    ValueError
        If voltage and current arrays have different lengths.

    ValueError
        If an invalid value is passed for the `interpolate` parameter.

    Examples
    --------
    >>> voltage = np.array([-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5])
    >>> current = np.array([-0.3, -0.2, -0.1, 0, 0, 0, 0.1, 0.2, 0.3, 0.4, 0.5])
    >>> get_floating_potential(voltage, current, min_points=2)
    -3.0

    >>> voltage = np.array([-5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5])
    >>> current = np.array([-0.6, -0.5, -0.4, -0.3, -0.2, -0.1, 0.1, 0.2, 0.3, 0.4, 0.5])
    >>> get_floating_potential(voltage, current,min_points = 4, interpolate='linear')
    0.5
    """
    if len(voltage) != len(current):
        raise ValueError(
            "Voltage and current arrays must have the same length.")

    if threshold is None:
        threshold = min_points

    n = len(voltage)
    start = min_points // 2
    end = n - start
    V_f = np.nan
    I_f = np.nan

    for i in range(start, end):
        # Find the first transition point from negative to positive or zero current
        if current[i] >= 0:
            continue
        j = i + 1
        while j < n and current[j] < 0:
            j += 1
        if j - i < min_points:
            continue

        # Check if the current is continuously positive after the transition point
        k = j
        while k < n and current[k] >= 0:
            k += 1
        if k - j >= min_points:
            V_f: float = voltage[j]
            I_f = current[j]
            break

        # Check if there are enough points left to test
        if n - k < threshold:
            break

    # does interpolation between points if 'interpolate' is a matching string
    # will not do interpolation if float current is exactly zero to avoid error
    if interpolate is None:
        pass
    elif interpolate == 'linear':
        if I_f != 0:
            f = interp1d(current[j-1:j+1], voltage[j-1:j+1])  # type: ignore
            V_f: float = f(0)
        else:
            pass
    elif interpolate == 'exponential':
        if I_f != 0:
            x = np.log(current)
            f = interp1d(x, voltage)
            V_f: float = f(0)
        else:
            pass
    elif interpolate == 'logarithmic':
        if I_f != 0:
            x = np.log(voltage)
            f = interp1d(current, x)
            V_f: float = np.exp(f(0))
        else:
            pass
    else:
        raise ValueError("Invalid value for interpolate parameter.")

    # to return format (value, extras: Dict[str,Any])
    others: dict = {"interpolate": interpolate}
    floating_potential: float = V_f
    return floating_potential, others
