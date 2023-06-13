from abc import ABC, abstractmethod, abstractproperty
from typing import Dict

import numpy as np
import pandas as pd

from pstl.utls.plasmas import Plasma
from pstl.utls.preprocessing import preprocessing_filter, preprocess_filter, smooth_filter
from pstl.diagnostics.probes.langmuir.single import SingleProbeLangmuir

from pstl.diagnostics.probes.langmuir.single.analysis.algorithm import topham, lobbia
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


class DiagnosticData:
    def __init__(self, data, deleted_data=None, filtered_data=None, smoothed_data=None, *args, **kwargs):
        # set different data versions
        self.set_data(
            data,
            deleted_data=deleted_data,
            filtered_data=filtered_data,
            smoothed_data=smoothed_data,
        )

    def set_data(self, raw_data, source=0, deleted_data=None, filtered_data=None, smoothed_data=None):
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
        if source == 0:
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

        elif source == 1:
            data = raw_data
        elif source == 2:
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

    def preprocess(self, *args, source=0, **kwargs):
        filtered_data, deleted_data = preprocess_filter(
            self._data, *args, **kwargs)
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

    @abstractmethod
    def set_default_methods(self, methods: Dict) -> Dict:
        pass
        # return {}

    @abstractmethod
    def set_available_plasma_properties(self, properties: Dict) -> Dict:
        pass


class PlasmaLangmuirProbeSolver(PlasmaProbeSolver):
    def __init__(self, Plasma: Plasma, Probe, Data, *args, **kwargs) -> None:
        super().__init__(Plasma, Probe, Data, *args, **kwargs)

        self._data_e = self.data.copy()

    def update_current_e(self, curret_i):
        self.data_e.current = np.subtract(self.data.current, curret_i)

    @property
    def data_e(self):
        return self._data_e


class SingleLangmuirProbeSolver(PlasmaLangmuirProbeSolver):
    def __init__(self, Plasma: Plasma, Probe: SingleProbeLangmuir, Data: pd.DataFrame,
                 methods: Dict = {}, properties: Dict = {},
                 *args, **kwargs) -> None:
        super().__init__(Plasma, Probe, Data,
                         methods=methods, properties=properties,
                         *args, **kwargs)

    def set_available_plasma_properties(self, properties: Dict) -> Dict:
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
            "V_f": 0,
            "V_s": 0,
            "I_is": 0,
            "n_i": 0,
            "I_es": 0,
            "KT_e": 0,
            "n_e": 0,
            "J_es": 0,
            "J_is": 0,
            "lambda_De": 0,
            "sheath": 0,
        }
        default_methods.update(methods)
        return default_methods

    def find_plasma_properties(self, algo=0, methods={}, *args, **kwargs):
        # algo is the default algo to use i.e. topham, lobia, etc.
        # verify methods is a dictionary
        # methods should not be modified unless you want to modify which methods are being used during the alogrythm.
        if not isinstance(methods, dict):
            raise ValueError(
                "'methods' must be a dictionary not: ", type(methods))

        # overwrite methods if passed in
        methods_to_use = dict(self.methods)
        methods_to_use.update(methods)

        # loop through plasma properties to get and perform each in given order
        # HARD CODEDIN
        func = method_selector(algo, available_algorithms,
                               available_algorithm_functions)
        data, results = func(
            self.data.voltage, self.data.current,
            self.probe.shape, self.probe.radius, self.probe.area,
            self.plasma.m_i, m_e=self.plasma.m_e,
        )
        self._results = results
        self._data = data

    def find_plasma_property(self, key, method=None, **kwargs):
        # choose which property
        if key == "V_f":
            func = get_floating_potential
            kwargs.setdefault("voltage", self.data.iloc[:, 0])  # type: ignore
            kwargs.setdefault("current", self.data.iloc[:, 1])  # type: ignore
        elif key == "V_s":
            func = get_plasma_potential
            kwargs.setdefault("voltage", self.data.iloc[:, 0])  # type: ignore
            kwargs.setdefault(
                "current", self.data_e.iloc[:, 1])  # type: ignore
            elec_ret_poly = self.results["KT_e"]["other"]["fit"].poly.convert(
            ) if "fit" in self.results["KT_e"]["other"] else None
            elec_sat_poly = self.results["I_es"]["other"]["fit"].poly.convert(
            ) if "fit" in self.results["I_es"]["other"] else None
            kwargs.setdefault("elec_ret_poly", elec_ret_poly)
            kwargs.setdefault("elec_sat_poly", elec_sat_poly)
        elif key == "I_is":
            func = get_ion_saturation_current
            kwargs.setdefault("voltage", self.data.iloc[:, 0])  # type: ignore
            kwargs.setdefault("current", self.data.iloc[:, 1])  # type: ignore
        elif key == "n_i":
            func = get_ion_density
            kwargs.setdefault("voltage", self.data.iloc[:, 0])  # type: ignore
            kwargs.setdefault("current", self.data.iloc[:, 1])  # type: ignore
            kwargs.setdefault("area", self.probe.area)
            kwargs.setdefault("KT_e", self.results["KT_e"]["value"])
            kwargs.setdefault("I_is", self.results["I_is"]["value"])
            kwargs.setdefault("m_i", self.plasma.m_i)
            kwargs.setdefault("m_e", self.plasma.m_e)
        elif key == "I_es":
            func = get_electron_saturation_current
            kwargs.setdefault("voltage", self.data.iloc[:, 0])  # type: ignore
            kwargs.setdefault(
                "current", self.data_e.iloc[:, 1])  # type: ignore
        elif key == "KT_e":
            func = get_electron_temperature
            kwargs.setdefault("voltage", self.data.iloc[:, 0])  # type: ignore
            kwargs.setdefault(
                "current", self.data_e.iloc[:, 1])  # type: ignore
            kwargs.setdefault("V_f", self.results["V_f"]["value"])
            kwargs.setdefault("V_s", self.results["V_s"]["value"])
        elif key == "n_e":
            func = get_electron_density
            kwargs.setdefault("voltage", self.data.iloc[:, 0])  # type: ignore
            kwargs.setdefault(
                "current", self.data_e.iloc[:, 1])  # type: ignore
            kwargs.setdefault("area", self.probe.area)
            kwargs.setdefault("KT_e", self.results["KT_e"]["value"])
            kwargs.setdefault("I_es", self.results["I_es"]["value"])
            kwargs.setdefault("m_e", self.plasma.m_e)
        elif key == "J_es":
            func = get_electron_saturation_current_density
            kwargs.setdefault("voltage", self.data.iloc[:, 0])  # type: ignore
            kwargs.setdefault(
                "current", self.data_e.iloc[:, 1])  # type: ignore
            kwargs.setdefault("area", self.probe.area)
            kwargs.setdefault("I_es", self.results["I_es"]["value"])
        elif key == "J_is":
            func = get_ion_saturation_current_density
            kwargs.setdefault("voltage", self.data.iloc[:, 0])  # type: ignore
            kwargs.setdefault("current", self.data.iloc[:, 1])  # type: ignore
            kwargs.setdefault("area", self.probe.area)
            kwargs.setdefault("I_is", self.results["I_is"]["value"])
        elif key == "lambda_De":
            func = get_lambda_D
            kwargs.setdefault("area", self.probe.area)
            kwargs.setdefault("KT_e", self.results["KT_e"]["value"])
            kwargs.setdefault("n", self.results["n_e"]["value"])
        elif key == "sheath":
            func = get_sheath_type
            kwargs.setdefault("lambda_D", self.results["lambda_De"]["value"])
            kwargs.setdefault("radius_probe", self.probe.diameter/2)
        else:
            table = "\n".join(
                [f"{k}\t{v}" for k, v in enumerate(self.results)])
            raise ValueError(
                f"Matching key not found: {key}\nChoose from one of the available options:\n{table}")

        # check for set method
        if method is None:
            method = self.methods[key]

        # solve and return a tuple
        kwargs.setdefault("method", method)
        value, other = func(**kwargs)

        # store values and other returns
        self.results[key]['value'] = value
        self.results[key]['other'] = other

    def find_floating_potential(self, method=None, **kwargs):
        # key for method and saving indexing
        key = 'V_f'
        self.find_plasma_property(key, method, **kwargs)

    def find_plasma_potential(self, method=None, **kwargs):
        # key for method and saving indexing
        key = 'V_s'
        self.find_plasma_property(key, method, **kwargs)

    def find_ion_saturation_current(self, method=None, **kwargs):
        # key for method and saving indexing
        key = 'I_is'
        self.find_plasma_property(key, method, **kwargs)

    def find_ion_density(self, method=None, **kwargs):
        # key for method and saving indexing
        key = 'n_i'
        self.find_plasma_property(key, method, **kwargs)

    def find_electron_saturation_current(self, method=None, **kwargs):
        # key for method and saving indexing
        key = 'I_es'
        self.find_plasma_property(key, method, **kwargs)

    def find_electron_density(self, method=None, **kwargs):
        # key for method and saving indexing
        key = 'n_e'
        self.find_plasma_property(key, method, **kwargs)

    def find_electron_temperature(self, method=None, **kwargs):
        # key for method and saving indexing
        key = 'KT_e'
        self.find_plasma_property(key, method, **kwargs)

    def find_electron_saturation_current_density(self, method=None, **kwargs):
        # key for method and saving indexing
        key = 'J_es'
        self.find_plasma_property(key, method, **kwargs)

    def find_ion_saturation_current_density(self, method=None, **kwargs):
        # key for method and saving indexing
        key = 'J_is'
        self.find_plasma_property(key, method, **kwargs)

    def find_electron_debye_length(self, method=None, **kwargs):
        # key for method and saving indexing
        key = 'lambda_De'
        self.find_plasma_property(key, method, **kwargs)

    def find_sheath_type(self, method=None, **kwargs):
        # key for method and saving indexing
        key = 'sheath'
        self.find_plasma_property(key, method, **kwargs)


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
