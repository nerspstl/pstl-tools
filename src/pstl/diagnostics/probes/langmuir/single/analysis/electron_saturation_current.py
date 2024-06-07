"""

Testing get_electron_saturation_current func - funcs_electon_saturation_current.py


"""
from typing import Tuple, Dict, Any

import numpy as np
import numpy.typing as npt
from numpy.polynomial import Polynomial as P

from pstl.utls.verify import verify_type, verify_array_polarity
#from pstl.utls.helpers import interpolate
from pstl.utls.helpers import interpolate
from pstl.utls.functionfit.helpers import find_fit
from pstl.diagnostics.probes.langmuir.single.analysis.floating_potential import get_floating_potential, check_for_floating_potential
from pstl.diagnostics.probes.langmuir.single.analysis.electron_temperaure import get_electron_temperature
# from funcs_plasma_potential import get_plasma_potential

default_fit_kwargs = {
    'deg': 1, 'power': 1, 'polarity': 1,
    'reverse': True, 'return_best': True, 'fit_type': "exponential",
    'min_points': 5, 'istart': None, 'iend': None, 'invalid': "ignore",
    'fstep': 0.1, 'fstep_type': 'percent', 'fstep_adjust': True, 'fitmax': None,
    'bstep': 1, 'bstep_type': 'index', 'bstep_adjust': True, 'bitmax': None,
    'threshold_residual': None, 'threshold_rmse': 0.30,
    'threshold_rsq': 0.95, 'threshold_method': None,
    'convergence_residual_percent': 1.0, 'convergence_rmse_percent': 1.0,
    'convergence_rsq_percent': 1.0, 'convergence_method': None,
    'strict': False, 'full': True, 'printlog': False,
}


def get_electron_saturation_current(*args, method: int | str | None = 0, **kwargs) -> Tuple[float, Dict[str, Any]]:
    # Declare available methods
    available_methods = {
        0: 'fit',
    }

    # Converts method: str -> method: int if method is a str
    if isinstance(method, str):
        reversed_methods = {v: k for k, v in available_methods.items()}
        method = reversed_methods.get(method, None)

    # check for match and get which function to use
    # raises value error with options if failed to match
    if method == 0:  # default
        func = get_electron_saturation_current_fit
    else:  # makes a table of options if error occurs
        table = "\n".join([f"{k}\t{v}" for k, v in available_methods.items()])
        raise ValueError(
            f"Matching method not found: {method}\nChoose from one of the available options:\n{table}")

    # Call funtion and return result
    return func(*args, **kwargs)


def get_electron_saturation_current_density(
        area, *args,
        method=0, I_es=None,
        **kwargs) -> Tuple[float, Dict[str, Any]]:

    # if electron saturation currint is None solve with defaults
    if I_es is None:
        value, other = get_electron_saturation_current(
            *args, method=method, **kwargs)
        I_es = value
    else:
        other = {}
    # then get electron saturatin current density
    J_es = np.divide(I_es, area)
    return J_es, other


def get_electron_saturation_current_fit(
        voltage, current, *args,
        V_f=None, V_s=None, elec_ret_poly=None, min_points=5, find_V_s=False,
        **kwargs) -> Tuple[float, Dict[str, Any]]:

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

    # make sure have Electron Retarding Region Polynomial of tpye ~np.polynomial.Polynomial
    if elec_ret_poly is None:
        KT_e_kwargs = kwargs.get("KT_e_kwargs", {})
        # set defaults for getting temperature
        KT_e_kwargs.setdefault('V_f', V_f)
        KT_e_kwargs.setdefault('V_s', V_s)
        KT_e_kwargs.setdefault('method', 'fit')
        # overide fit kwargs defaults for electron temperaure fit (exponential)
        KT_e_kwargs.setdefault('fit_kwargs',
                               {
                                   'full': False,
                               }
                               )
        print(KT_e_kwargs)
        _, KT_e_others = get_electron_temperature(
            voltage, current, **KT_e_kwargs)
        elec_ret_poly = KT_e_others["fit"].poly.convert()
    verify_type(elec_ret_poly, P)

    # use vs as a short cut if given
    if V_s is not None:
        verify_type(V_s, (int, float, np.int64, np.float64, np.ndarray), 'V_s')
        istart = np.where(voltage < V_s)[0][-1]+1
    else:  # uses vf
        istart = np.where(voltage > V_f)[0][0]

    # get stoping splicing index of data (aka length of data)
    iend = len(voltage)

    # set some defaults for routine
    fit_kwargs = dict(default_fit_kwargs)
    fit_kwargs.update(kwargs.pop('fit_kwargs', {}))

    # initialiaze for search of electron saturation region
    electron_saturation_current = None
    elec_sat_fit = None
    intersection = None
    # the while loop checks to make sure the determined electron saturation fit
    # is indeed reasonable by taking the total residual by taking the differnece between fit line and
    # experimental data in the semilogy plane for all voltages between istart to iend (gets less relaiable if V_s is given.
    # The total residual should be negative as a good fit will have the electron saturation fit almost always be either much
    # greater (magnitudes difference) than experimental or almost exactly the same. However a bad fit will be the inverse
    while electron_saturation_current is None and iend >= min_points:

        # get search area data
        xdata = voltage[istart:iend]
        ydata = current[istart:iend]

        # find potential electron saturation region fit
        elec_sat_fit = find_fit(xdata, ydata, **fit_kwargs)
        # convert the fit to polynomial of type ~np.polynomial.Polynomial with satandared coefs
        elec_sat_poly = elec_sat_fit.poly.convert()

        # go from start of floating to end of electron saturation region
        # float point cuz want all the way to the end for most residual change
        # end of elec sat cuz want to not take into account the breakdown current if that occurs
        jend = np.where(xdata <= elec_sat_fit.domain[1])[0][-1]
        x = xdata[istart:jend]
        y = ydata[istart:jend]

        # covnvert to semilogy space (experimental)
        logy = np.log(y)

        # covnvert to semilogy space (fit)
        logyp = elec_sat_fit(x)

        # calculate total residual
        residuals = np.subtract(logy, logyp)
        residual = np.sum(residuals)

        # means the fit is below experimental data (may have found probe breakdown current)
        if residual > 0:
            iend -= 1
            continue
        elif residual <= 0:  # the fit is above experimental and intersection could be Vs
            # find intersection
            p = elec_sat_poly-elec_ret_poly
            intersection = p.roots()

            # Check if intersection has a value and break if it does or continue if it doesnt
            if intersection is None:
                iend -= 1
                continue
            else:
                break
        else:
            raise ValueError(
                "'residiual' is unexpected value: %s" % (str(residual)))

    # Checks that the intersection is found
    if intersection is None:
        raise ValueError("Intersection not found")
    else:
        # Determine new V_s based on intersection point
        # future work: maybe add check here that only one vs is found
        V_s = intersection[0]

    # checks that an elec_sat_fit was made
    if elec_sat_fit is None:
        raise ValueError("'elec_sat_fit' not found")

    # calculate electron saturation current
    #electron_saturation_current = elec_sat_fit(V_s)
    electron_saturation_current = interpolate(V_s,voltage,current,method="linear")

    # determine returns based on input arguments
    others: dict[str, Any] = {"fit": elec_sat_fit}
    if find_V_s:
        others["V_s"] = V_s

    # return as (value, Dict[str,Any])
    return electron_saturation_current, others
