from abc import ABC, abstractmethod, abstractproperty
from typing import Dict, Callable, Any
import json
import pprint

import numpy as np
import pandas as pd

from pstl.utls.abc import PSTLObject
from pstl.utls.json import load_build_and_get_parameters
from pstl.utls.plasmas import Plasma
from pstl.utls.plasmas import setup as plasma_setup
from pstl.utls.data import setup as data_setup
from pstl.utls.objects import setup as object_setup
from pstl.diagnostics.probes.langmuir.single import setup as probe_setup
from pstl.diagnostics.probes import Probe

from pstl.utls.preprocessing import preprocessing_filter, preprocess_filter, smooth_filter
from pstl.diagnostics.probes.langmuir.single import SingleProbeLangmuir

from pstl.diagnostics.probes.langmuir.single.analysis.algorithms import topham, lobbia
from pstl.diagnostics.probes.langmuir.single.analysis.floating_potential import get_floating_potential
from pstl.diagnostics.probes.langmuir.single.analysis.ion_saturation_current import get_ion_saturation_current, get_ion_saturation_current_density
from pstl.diagnostics.probes.langmuir.single.analysis.electron_temperaure import get_electron_temperature
from pstl.diagnostics.probes.langmuir.single.analysis.electron_saturation_current import get_electron_saturation_current, get_electron_saturation_current_density
from pstl.diagnostics.probes.langmuir.single.analysis.plasma_potential import get_plasma_potential
from pstl.diagnostics.probes.langmuir.single.analysis.electron_density import get_electron_density
from pstl.diagnostics.probes.langmuir.single.analysis.ion_density import get_ion_density
from pstl.utls.constants import lambda_D
from pstl.utls.helpers import probe_radius_to_debye_length as get_sheath_type
from pstl.utls.helpers import method_function_combiner, method_selector
from pstl.utls.decorators import absorb_extra_args_kwargs, add_empty_dict
get_lambda_D = add_empty_dict(absorb_extra_args_kwargs(lambda_D))
get_sheath_type = add_empty_dict(absorb_extra_args_kwargs(get_sheath_type))

# maybe a concrete class called ProbeData that would jsut be raw_data, deleted_data, filtered_data, smoothed_data
singe_langmuir_probe_solver_setup_builders = {
    "plasma"    :   plasma_setup,
    "probe"     :   probe_setup,
    "data"      :   data_setup,
}


def setup(settings, *args, **kwargs):
    """
    Creates and returns a SingleProbeLangmuirSolver object based on settings dictionary passed in.
    The settings parameter must have keys 'plasma', 'probe', and 'data', where in
    each is a dictionary with either a key being 'define' or 'file_load'. If 'define',
    there is another dictionary that defines all need properties to make the object. In
    the 'file_load' case, the entry is a string that is the file path to load a json file
    that has all the needed properties to make the object.
    
    Keys (mandatory):
        'plasma': dict[dict | str]   ->  Plasma object defining properties or path to json file 
        'probe' : dict[dict | str]   ->  Probe object defining properties or path to json file
        'data'  : dict[dict | str]   ->  Data object defining properties or path to json file
    (optional)
        'name'          : str   ->  name designation for object
        'description'   : str   ->  description of object
        'args'          : tuple ->  addional position arguments
        'kwargs'        : dict  ->  addional keyword arguments
    Returns: Solver Object
    """
    # create new object with parameters (arguments)
    output_object: SingleLangmuirProbeSolver = object_setup(
        *args,
        settings=settings,
        builders=singe_langmuir_probe_solver_setup_builders,
        Builder=SingleLangmuirProbeSolver,
        **kwargs,
    )

    return output_object


class DiagnosticData(PSTLObject):
    def __init__(self, data, deleted_data=None, filtered_data=None, smoothed_data=None, *args, **kwargs):
        # set different data versions
        self.set_data(
            data,
            deleted_data=deleted_data,
            filtered_data=filtered_data,
            smoothed_data=smoothed_data,
        )

    def set_data(self, raw_data, source=0, deleted_data=None, filtered_data=None, smoothed_data=None):
        """
        Takes raw_data
        """
        self._raw_data = raw_data
        self._deleted_data = deleted_data
        self._filtered_data = filtered_data
        self._smoothed_data = smoothed_data

        # available sources
        available_sources = {
            0: "best",
            1: "raw_data",
            2: "filtered_data",
            3: "smoothed_data",
        }

        # Converts method: str -> method: int if method is a str
        if isinstance(source, str):
            reversed_sources = {v: k for k, v in available_sources.items()}
            source = reversed_sources.get(source, None)

        # choose data source
        if source == 0: # Best
            if smoothed_data is True:
                # get smoothed of filtered data
                raise NotImplementedError
                data = smoothed_data
            elif isinstance(smoothed_data, pd.DataFrame):
                data = smoothed_data
            elif filtered_data is True:
                # get filtered data
                raise NotImplementedError
                data = filtered_data
            elif isinstance(filtered_data, pd.DataFrame):
                data = filtered_data
            else:
                data = raw_data

        elif source == 1:   # raw data
            data = raw_data

        elif source == 2:   # filtered data
            if filtered_data is True:
                filtered_data = pd.DataFrame
            elif filtered_data is False or filtered_data is None:
                filtered_data = raw_data
            elif isinstance(filtered_data, pd.DataFrame):
                filtered_data = filtered_data
            else:
                raise TypeError(
                    "'filtered_data' can only type pd.DataFrame, bool, None: ", type(filtered_data))
            data = filtered_data

        elif source == 3:   # tecniquely filtered and and smoothed if filtered is True and smoothed is True
            if smoothed_data is True:
                smoothed_data = pd.DataFrame
            elif smoothed_data is False or smoothed_data is None:
                smoothed_data = raw_data
            elif isinstance(smoothed_data, pd.DataFrame):
                smoothed_data = smoothed_data
            else:
                raise TypeError(
                    "'smoothed_data' can only type pd.DataFrame, bool, None: ", type(smoothed_data))
            data = smoothed_data

        else:  # makes a table of options if error occurs
            table = "\n".join(
                [f"{k}\t{v}" for k, v in available_sources.items()])
            raise ValueError(
                f"Matching source not found: {source}\nChoose from one of the available options:\n{table}")

        # based on data argument set data variable to use
        self._data = data

    def preprocess(self, *args, source=0, delete=True, **kwargs):
        filtered_data, deleted_data = preprocess_filter(
            self._data, *args, delete=delete, **kwargs)
        self.set_data(self._data, source=source,
                      deleted_data=deleted_data, filtered_data=filtered_data)

    def smooth(self, *args, source=0, **kwargs):
        smoothed_data = smooth_filter(self._data, *args, **kwargs)
        self.set_data(self._data, source=source, smoothed_data=smoothed_data)


class PlasmaProbeSolver(DiagnosticData, ABC):
    def __init__(self, Plasma: Plasma, Probe, Data: pd.DataFrame,
                 methods: Dict = {}, properties: Dict = {},
                 deleted_data: pd.DataFrame | bool | None = None,
                 filtered_data: pd.DataFrame | bool | None = None,
                 smoothed_data: pd.DataFrame | bool | None = None,
                 name: str | None = None, description: str | None = None,
                 *args, **kwargs) -> None:
        # super(ABC, self).__init__()
        DiagnosticData.__init__(
            self, Data,
            deleted_data=deleted_data, filtered_data=filtered_data, smoothed_data=smoothed_data)

        # add verification here
        self._plasma = Plasma
        self._probe = Probe

        # create results dictionary
        self._results = self.set_available_plasma_properties(properties)

        # set defeult methods (abstract)
        self._methods = self.set_default_methods(methods)

        # set defeult methods (abstract)
        self._methods_args = self.set_default_methods_args(kwargs)
        
        # set defeult methods (abstract)
        self._methods_kwargs = self.set_default_methods_kwargs(kwargs)
    @property
    def plasma(self):
        return self._plasma

    @property
    def probe(self):
        return self._probe

    @property
    def data(self):
        return self._data

    @property
    def raw_data(self):
        return self._raw_data

    @property
    def deleted_data(self):
        return self._deleted_data

    @property
    def results(self):
        return self._results

    @property
    def methods(self):
        return self._methods

    @property
    def methods_args(self):
        return self._methods_args
    
    @property
    def methods_kwargs(self):
        return self._methods_kwargs

    @abstractmethod
    def set_default_methods(self, methods: dict) -> dict:
        pass
        # return {}

    @abstractmethod
    def set_default_methods_args(self, methods: dict) -> tuple:
        pass

    @abstractmethod
    def set_default_methods_kwargs(self, methods: dict) -> dict:
        pass

    @abstractmethod
    def set_available_plasma_properties(self, properties: dict) -> dict:
        pass

    @abstractmethod
    def solve(self, *args, methods: dict={}, **kwargs):
        pass


class PlasmaLangmuirProbeSolver(PlasmaProbeSolver):
    def __init__(self, Plasma: Plasma, Probe, Data, *args, **kwargs) -> None:
        super().__init__(Plasma, Probe, Data, *args, **kwargs)

        self._data_e = self.data.copy() # type: ignore

    def update_current_e(self, curret_i):
        self.data_e.current = np.subtract(self.data.current, curret_i)  # type: ignore

    @property
    def data_e(self):
        return self._data_e


class SingleLangmuirProbeSolver(PlasmaLangmuirProbeSolver):
    def __init__(self, plasma: Plasma, probe: SingleProbeLangmuir, data: pd.DataFrame,
                 methods: Dict = {}, properties: Dict = {},
                 *args, **kwargs) -> None:
        super().__init__(plasma, probe, data,
                         methods=methods, properties=properties,
                         *args, **kwargs)


    def set_available_plasma_properties(self, properties: dict) -> dict:
        super().set_available_plasma_properties(properties)
        available_plasma_properties = {
            "V_f": {'value': None, 'other': None},
            "V_s": {'value': None, 'other': None},
            "KT_e": {'value': None, 'other': None},
            "n_e": {'value': None, 'other': None},
            "I_es": {'value': None, 'other': None},
            "J_es": {'value': None, 'other': None},
            "n_i": {'value': None, 'other': None},
            "I_is": {'value': None, 'other': None},
            "J_is": {'value': None, 'other': None},
            "lambda_De": {'value': None, 'other': None},
            "sheath": {'value': None, 'other': None},
        }
        return available_plasma_properties

    def set_default_methods(self, methods: Dict):
        # methods = super().setdefault_methods(methods)
        super().set_default_methods(methods)
        default_methods = {
            "algorithm" : 0,
        }
        default_methods.update(methods)
        return default_methods
    
    def set_default_methods_args(self, kwargs: dict) -> dict:
        super().set_default_methods_args(kwargs)
        return kwargs.pop("algorithm_args",())
    
    def set_default_methods_kwargs(self, kwargs: dict) -> dict:
        super().set_default_methods_kwargs(kwargs)
        return kwargs.pop("algorithm_kwargs",{})

    def solve(self, *args,methods={}, **kwargs):
        super().solve(methods,*args,**kwargs)
        # algo is the default algo to use i.e. topham, lobia, etc.
        # verify methods is a dictionary
        # methods should not be modified unless you want to modify which methods are being used during the alogrythm.
        if not isinstance(methods, dict):
            raise ValueError(
                "'methods' must be a dictionary not: ", type(methods))

        # overwrite methods if passed in
        methods_to_use = dict(self.methods)
        methods_to_use.update(methods)

        # grab algorithm args and kwargs from kwargs
        new_algorithm_args = kwargs.get("algorithm_args",tuple())
        new_algorithm_kwargs = kwargs.get("algorithm_kwargs",{})
        

        # update defaults with new
        algorithm_args = new_algorithm_args
        algorithm_kwargs = self.methods_kwargs | new_algorithm_kwargs

        # Choose which alogrithm to solve for results
        algorithm_func = method_selector(methods_to_use["algorithm"], 
                               available_algorithms,
                               available_algorithm_functions,
        )

        # run selected algorithm
        data, results = algorithm_func(   
            self.data.voltage, self.data.current,   # type: ignore
            self.probe.shape, self.probe.radius, self.probe.area,
            self.plasma.m_i, 
            *algorithm_args,
            m_e=self.plasma.m_e,
            **algorithm_kwargs,
        )

        # save results and data to solver object
        self._results = results
        self._data = data

# Declare available methods
available_algorithms = {
    0: ['topham'],
    1: ['lobbia'],
}
# Declare correspondin functions for available_methods
available_algorithm_functions = {
    0: topham,
    1: lobbia,
}

# combines available_methods and available_methods and must have the same keys
# such that the new dictionary has the same keys but value is a tuple(list(str),functions)
options = method_function_combiner(
    available_algorithms, available_algorithm_functions)
