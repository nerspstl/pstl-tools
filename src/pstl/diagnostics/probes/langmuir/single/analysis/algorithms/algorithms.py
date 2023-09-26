from typing import Dict, Any

import numpy as np
import pandas as pd

from pstl.utls import constants as c
from pstl.utls.constants import lambda_D as get_lambda_D
from pstl.utls.decorators import absorb_extra_args_kwargs, add_empty_dict
get_lambda_D = add_empty_dict(absorb_extra_args_kwargs(get_lambda_D))
from pstl.utls.errors.langmuir import FailedLangmuirAlgorithmConvergence
from pstl.utls.plasmas.sheath import get_probe_to_sheath_ratio

from .algorithm_helpers import(
    get_plasma_property_sorter,
    print_results,
    topham_configure,
    topham_get_ion_current_and_density
)
from .algorithm_helpers import(
    default_methods,
    default_plasma_properties_to_get,
    topham_get_ion_current_and_density
)

from ..ion_density import get_ion_density
from ..electron_density import get_electron_density
from ..plasma_potential import get_plasma_potential
from ..electron_saturation_current import get_electron_saturation_current, get_electron_saturation_current_density
from ..electron_temperaure import get_electron_temperature
from ..ion_saturation_current import get_ion_saturation_current, get_ion_saturation_current_density
from ..floating_potential import get_floating_potential
from ..ion_current import get_ion_current

def lobbia():
    return



######################################################################
######################################################################
######################################################################


def topham(voltage, current, shape, r_p, area, m_i, m_e=c.m_e,
           methods={},
           smooth=False, itmax=9, convergence_percent=1,
           *args, **kwargs) -> tuple[pd.DataFrame,Dict]:

    # initialize configuration
    (   convergence_decimal,
        methods_to_use,
        properties_to_get,
        results,
        func_kwargs,
    ) = topham_configure(convergence_percent,methods,*args, **kwargs)
    rmse = float()
    V_f = float()
    V_f_extras = {}
    V_s = float()
    V_s_extras = {}
    n_e = float()
    n_e_extras = {}
    n_i = float()
    n_i_extras = {}
    KT_e = float()
    KT_e_extras = {}
    I_es = float()
    I_es_extras = {}
    I_is = float()
    I_is_extras = {}
    lambda_De = float()
    lambda_De_extras = {}
    ratio = float()
    ratio_extras = {}
    I_e = float()




    # inialize sheath method
    sheath_method = "thin"

    # Zero Step (optional):
    # smooth data for find better fit region

    # First Step:
    # Get Floating Potential
    # -> V_f
    key = "V_f"
    V_f, V_f_extras = get_floating_potential(
        voltage, current, method="consecutive", interpolate="linear",
    )

    # Intermediate Step (optional for convergence speedup):
    # Do Either @ V_bias << V_f:
    # 1) Fit a linear line in Ion Saturation Region
    # 2) Take the resonable minimum value of the Ion Saturation Region
    # 3) Fit a power term (i.e. 1/2) to the Ion Saturation Region
    # Then either use the fits to subtract out ion current from the total probe current
    # to get a approximate electron only current, or a flat value across the board of the
    # minimum ion current (may lead to artifcial bi-Maxwellian)
    # Ie = Iprobe - Ii  --or-- Iprobe = Ie+Ii (note: Ii convention is negative)
    # -> temp I_i
    I_i, I_i_extras = get_ion_current(
        shape,
        voltage, current,
        method=sheath_method, V_f=V_f,  
    )
    I_i_fit = I_i_extras["fit"]


    # Initialize convergence and loop counters/exit-criteria
    convergence = False
    it = 0
    old = float("inf")

    # Start Convergence loop 
    # First step is thin sheath assumption, 
    # then continues with new sheath type (either transitional or thick (OML)) 
    # till within convergence percent using this iteration compared to last iteration
    # the last iteration values are sourced as the results, not the new as new is just used to show convergence
    # Thus if not thin sheath, the loop will run at for the new sheath type at least twice
    while not convergence and it < itmax:
        # number of iterations
        it += 1
        print("\nIteration %i: (%s)"%(it,sheath_method))

    
        # Calculate electron current (I_e) from probe current (current) using determined ion current (I_i)
        I_e = np.subtract(current, I_i)

        # Second Step:
        # Find Rough Exponential Fit after Floating Potential in the Electron Retarding Region
        # Note: Ii is removed this should be only Ie
        # -> KT_e
        KT_e, KT_e_extras = get_electron_temperature(
            voltage, I_e, method="fit", V_f=V_f,
        )
        KT_e_poly = KT_e_extras["fit"].poly.convert()

        # Third Step:
        # Find Electron Saturation Exponential Fit
        # @ V_bias >> V_s (plasma or space potential) before probe breakdown (plasma created due to accelerated elcectrons),
        # There should be no ion current.
        # Note: Theory says I_es =
        # -> I_es = I_e(@V_s) = exp(m*V_s+b)
        I_es, I_es_extras = get_electron_saturation_current(
            voltage, I_e, method="fit", elec_ret_poly=KT_e_poly, V_f=V_f,
        )
        I_es_poly = I_es_extras["fit"].poly.convert()

        # Fourth Step:
        # Find Plasma Potential via intersection point of Electron Retarding and Saturation Regions
        # May also be done using first or second derivate to locate like in lobbia but requries smoothed data
        # and often inconclusive
        # -> V_s
        V_s, V_s_extras = get_plasma_potential(
            voltage, I_e, method="intersection", V_f=V_f, elec_ret_poly=KT_e_poly, elec_sat_poly=I_es_poly,
        )

        # Fifth Step:
        # Find Ion Saturation Current
        # Either:
        # 1) Thin Sheath:
        #   Linear Ion Saturation Fit @ V_bias << V_f that intersects the x-axis at a V_bias > V_s
        #   -> I_is = I_i(@V_s) = m*V_s + b
        # 2) Thick Sheath/Orbital Motion Limited (OML):
        #   Power 1/2 Fit in the Ion Saturation Region @ V_bias << V_f
        #   I_i^2 = alpha*V_bias + beta
        #       Where: alpha = -(q_e*area*ni)^2*(2.1*q_e/(pi^2*m_i))
        #               beta = (q_e*area*ni)^2*(2.1*q_e/(pi^2*m_i))*V_s
        #   Note: in theory I_es = -I_is*exp(0.5)*sqrt(m_i/(2*pi*m_e))
        # questionable below:
        #   -> I_is = -I_es*exp(-0.5)*sqrt(2*pi*m_e/m_i) --or-- I_is = -exp(-0.5)*area*q_e*n_i*sqrt(KT_e/m_i)
        # Last Step:
        # Once convergence is made, get n_i and n_e (ion and electron densities) and J_es and J_is (electorn and ion saturation current densities)
        # Electrons:
        # -> n_e = I_es/(area*q_e)*sqrt(2*pi*m_e/KT_e)
        # -> J_es = I_es/area
        # Ions:
        # if thin sheath:
        # n_i = I_is/(area*q_e)*sqrt(m_i/KT_e)
        # if thick sheath:
        # n_i = ((alpha*pi^2*m_i)/(2*q_e^3*area^2))^(0.5)

        # Debye Length
        # -> lambda_De = sqrt(KT_e*epsilon_0/(n_e*q_e^2))

        n_e, n_e_extras = get_electron_density(
            I_es, area=area, KT_e=KT_e, m_e=c.m_e, method="I_es",
        )
        # get ionsaturation value at V_f based on V_s, I_es, n_e, KT_e, V_f (need V_s to solve)
        I_is, I_is_extras = get_ion_saturation_current(
            voltage, current, V_f=V_f, method=3,
            I_i_fit=I_i_fit, I_i_method=sheath_method,
            V_s=V_s, n_e=n_e,T_e=KT_e, area=area,
        )
        # temp ion density
        n_i, n_i_extras = get_ion_density(
            I_is=I_is, voltage=voltage, current=current, area=area, KT_e=KT_e, m_i=m_i, method=sheath_method, shape=shape,
        )
        # lambda_D
        lambda_De, lambda_De_extras = get_lambda_D(n_e, KT_e)

        # ratio
        ratio, ratio_extras = get_probe_to_sheath_ratio(r_p, lambda_De)
        # sheath_method = ratio_extras["sheath"]

        # Repeat till Convergence on V_s from Intermediate Step to Last Step
        # using Ion Saturation Current fit to correct orginal probe current data to electron only current
        # i.e. I_probe,orginal - I_i,new = I_e,next_iteration_data
        if ratio <= 3:
            sheath_method = "thick"
        elif ratio > 3 and ratio < 50:
            sheath_method = "transitional"
        elif ratio >= 50 and it == 1:
            #sheath_method = "thin"
            break
        elif ratio >= 50:
            errmsg = "Back to thin"
            raise ValueError(errmsg)
        else:
            errmsg = "WHa???!!!"
            raise ValueError(errmsg)

        if it == itmax and it==1:
            break
        elif it == itmax and it !=1:
            errmsg = "No convergence in Langmuir Topham algorithm was made after %i iterations"%(itmax)
            raise FailedLangmuirAlgorithmConvergence(errmsg)

        # get updated n_i
        # <<enter here>>
        I_i, I_i_extras, n_i, n_i_extras = topham_get_ion_current_and_density(
            voltage=voltage, current=current, shape=shape, sheath_method=sheath_method,
            area=area, m_i=m_i, KT_e=KT_e, r_p=r_p, lambda_De=lambda_De,
            V_f=V_f, V_s=V_s, n_e=n_e, n_i=n_i,
        )

        # update I_is and I_is extras ## NEEEEEEEEDS ATTENETION
        I_i_fit = I_i_extras["fit"]
        # how to do ion saturation current for thick and transitional (i think below works)
        # get ionsaturation value at V_f based on V_s, I_es, n_e, KT_e, V_f (need V_s to solve)
        I_is, I_is_extras = get_ion_saturation_current(
            voltage, current, V_f=V_f, method=3,
            I_i_fit=I_i_fit, I_i_method=sheath_method,
            V_s=V_s, n_e=n_e,T_e=KT_e, area=area,
        )



        results["V_f"]["value"] = V_f
        results["V_f"]["other"] = V_f_extras
        results["V_s"]["value"] = V_s
        results["V_s"]["other"] = V_s_extras
        results["I_is"]["value"] = I_is
        results["I_is"]["other"] = I_is_extras
        results["n_i"]["value"] = n_i
        results["n_i"]["other"] = n_i_extras
        results["I_es"]["value"] = I_es
        results["I_es"]["other"] = I_es_extras
        (results["J_es"]["value"], 
        results["J_es"]["other"]) = get_electron_saturation_current_density(area, I_es=I_es)
        (results["J_is"]["value"], 
        results["J_is"]["other"]) = get_ion_saturation_current_density(area, I_is=I_is)
        results["KT_e"]["value"] = KT_e
        results["KT_e"]["other"] = KT_e_extras
        results["n_e"]["value"] = n_e
        results["n_e"]["other"] = n_e_extras
        results["lambda_De"]["value"] = lambda_De
        results["lambda_De"]["other"] = lambda_De_extras
        results["r_p/lambda_De"]["value"] = ratio
        results["r_p/lambda_De"]["other"] = ratio_extras
        results["sheath"]["value"] = ratio_extras['sheath']
        results["sheath"]["other"] = {}
        print_results(results)

        new = lambda_De
        if it != 1:
            difference = old-new
            realtive_difference = difference/old
            rmse = np.sqrt(np.sum(np.power(realtive_difference, 2)))
        else:
            rmse = float("inf")
        old = new

        convergence = True if rmse <= convergence_decimal else False

    ##### REMOVE AFTER DEBUG ######

    print("\nNumber of iterations: %i"%(it))
    print("Convergence %f"%(rmse))
    ###############################

    results["V_f"]["value"] = V_f
    results["V_f"]["other"] = V_f_extras
    results["V_s"]["value"] = V_s
    results["V_s"]["other"] = V_s_extras
    results["I_is"]["value"] = I_is
    results["I_is"]["other"] = I_is_extras
    results["n_i"]["value"] = n_i
    results["n_i"]["other"] = n_i_extras
    results["I_es"]["value"] = I_es
    results["I_es"]["other"] = I_es_extras
    (results["J_es"]["value"], 
    results["J_es"]["other"]) = get_electron_saturation_current_density(area, I_es=I_es)
    (results["J_is"]["value"], 
     results["J_is"]["other"]) = get_ion_saturation_current_density(area, I_is=I_is)
    results["KT_e"]["value"] = KT_e
    results["KT_e"]["other"] = KT_e_extras
    results["n_e"]["value"] = n_e
    results["n_e"]["other"] = n_e_extras
    results["lambda_De"]["value"] = lambda_De
    results["lambda_De"]["other"] = lambda_De_extras
    results["r_p/lambda_De"]["value"] = ratio
    results["r_p/lambda_De"]["other"] = ratio_extras
    results["sheath"]["value"] = ratio_extras['sheath']
    results["sheath"]["other"] = {}
    data = {'voltage': voltage, 'current': current,
            'current_e': I_e, 'current_i': I_i}
    data = pd.DataFrame(data)
    print("DATA:\n",data)
    print()
    print("RESULTS:")
    print_results(results)
    return data, results
