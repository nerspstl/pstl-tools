from abc import ABC, abstractmethod, abstractproperty
from typing import Any, Sequence
import tkinter as tk
import pprint
import traceback

import pandas as pd

from pstl.gui import WidgetOrganizer, Widgets
from pstl.gui.langmuir.canvas import LinearSemilogyDoubleCanvasSingleProbeLangmuir
from pstl.gui.langmuir.results import SingleProbeLangmuirResultsFrame
from pstl.gui.langmuir.panel import SingleProbeLangmuirPanelFrame

from pstl.utls.plasmas import setup as plasma_setup
from pstl.utls.data import setup as data_setup
from pstl.utls.objects import setup as object_setup
from pstl.utls.abc import PSTLObject
from pstl.utls import errors as err
from pstl.utls.errors.langmuir import FailedLangmuirAlgorithm

from pstl.diagnostics.probes.langmuir.single import setup as probe_setup
from pstl.diagnostics.probes.langmuir.single.analysis.solvers.solvers import SingleLangmuirProbeSolver, PlasmaProbeSolver
from pstl.diagnostics.probes.langmuir.single.analysis.solvers.solvers import setup as solver_setup


class CombinedDataFrame(tk.Frame, PSTLObject):
    def __init__(self, Solver, Canvas, Panel, *args, 
                 master=None, cnf=None, 
                 **kwargs):
        # get kwargs for individual
        canvas_kwargs = kwargs.pop("canvas_kwargs", {})
        panel_kwargs = kwargs.pop("panel_kwargs", {})
        solver_kwargs = kwargs.pop("solver_kwargs", {})
        super().__init__(master, cnf=cnf, *args, **kwargs)
        PSTLObject().__init__(*args, **kwargs)

        # set defaults for canvas
        canvas_kwargs.setdefault("width", 5)
        canvas_kwargs.setdefault("height", 4)

        # set defaults for panel

        # make plotting canvas
        self._canvas = Canvas(  # LinearSemilogyDoubleCanvasSingleProbeLangmuir(
            self, cnf, **canvas_kwargs)

        # make control panel
        self._panel = Panel(  # SingleProbeLangmuirResultsFrame(
            self, cnf, **panel_kwargs)

        # make solver
        self._solver = Solver(**solver_kwargs)

        # pack Away!!
        self.canvas.grid(row=0, column=1, sticky="NSWE")
        self.panel.grid(row=0, column=0, sticky="NWE")

    @property
    def canvas(self):
        return self._canvas

    @property
    def panel(self):
        return self._panel

    @property
    def solver(self):
        return self._solver
    
class CombinedDataFrame2(tk.Frame, PSTLObject):
    def __init__(
            self, 
            solver: PlasmaProbeSolver, 
            Canvas, 
            Panel, 
            *args, 
                 master=None, cnf=None, name=None,
                 **kwargs):
        # get kwargs for individual
        canvas_kwargs = kwargs.pop("canvas_kwargs", {})
        panel_kwargs = kwargs.pop("panel_kwargs", {})
        super().__init__(master, *args, cnf=cnf,  **kwargs)
        PSTLObject().__init__(*args,name=name,**kwargs)

        # set defaults for canvas
        canvas_kwargs.setdefault("width", 5)
        canvas_kwargs.setdefault("height", 4)

        # set defaults for panel

        # make plotting canvas
        self._canvas = Canvas( #LinearSemilogyDoubleCanvasSingleProbeLangmuir(
            self, cnf, **canvas_kwargs)

        # make control panel
        self._panel =  Panel( #SingleProbeLangmuirResultsFrame(
            master=self, cnf=cnf, **panel_kwargs)

        # make solver
        self._solver = solver

        # make name l
        if name is None:
            name = "None"
        else:
            name = str(name)
        name_lbl = tk.Label(master=self,cnf=cnf, text=name)
        self._name_label = name_lbl

        # pack Away!!
        self.canvas.grid(row=0, column=1, rowspan=2,sticky="NSWE")
        self.panel.grid(row=1, column=0, sticky="NWE")
        self.name_label.grid(row=0, column=0, sticky="NWE")
    

    @property
    def canvas(self):
        return self._canvas

    @property
    def panel(self):
        return self._panel

    @property
    def solver(self):
        return self._solver
    
    @property
    def name_label(self):
        return self._name_label

singe_langmuir_probe_solver_setup_builders = {
    "plasma"    :   plasma_setup,
    "probe"     :   probe_setup,
    "data"      :   data_setup,
}

def LSSLCD_setup(settings, *args, **kwargs):
    """
    Creates and returns a LinearSemilogySingleLangmuirCombinedData object based on settings dictionary passed in.
    The settings parameter must have keys 'plasma', 'probe', and 'data', where in
    each is a dictionary with either a key being 'define' or 'file_load'. If 'define',
    there is another dictionary that defines all need properties to make the object. In
    the 'file_load' case, the entry is a string that is the file path to load a json file
    that has all the needed properties to make the object.
    
    Keys (mandatory):
        'plasma': dict[dict | str]   ->  Plasma object defining properties or path to json file 
        'probe' : dict[dict | str]   ->  Probe object defining properties or path to json file
        'data'  : dict[dict | str]   ->  Data object defining properties or path to json file
        'solver_kwargs' : dict[dict | str]  ->  kwargs for solver class either
    (optional)
        'name'          : str   ->  name designation for object
        'description'   : str   ->  description of object
        'args'          : tuple ->  addional position arguments
        'kwargs'        : dict  ->  addional keyword arguments
    Returns: Solver Object
    """
    def raise_missing_key_error(key):
        raise KeyError("'%s' is not a defined key but needs to be"%(key))
    # check if plasma, probe, and data are either given here or a part of solver_kwargs
    key = "solver_kwargs"
    solver_kwargs = settings[key] if key in settings else raise_missing_key_error(key)
    to_args = {
        "plasma"    :   ["solver_kwargs", "plasma"],
        "probe"     :   ["solver_kwargs", "probe"],
        "data"      :   ["solver_kwargs", "data"]
        }
    
    # create new object with parameters (arguments)
    output_object:LinearSemilogySingleLangmuirCombinedData = object_setup(
        *args,
        settings=settings,
        builders=singe_langmuir_probe_solver_setup_builders,
        Builder=LinearSemilogySingleLangmuirCombinedData,
        to_args=to_args,
        **kwargs,
    )

    return output_object

solver_setup_builders = {
    "plasma"    :   plasma_setup,
    "probe"     :   probe_setup,
    "data"      :   data_setup,
    "solver"    :   solver_setup,
}
def LSSLCD2_setup(settings, *args, **kwargs):
    """
    Creates and returns a LinearSemilogySingleLangmuirCombinedData object based on settings dictionary passed in.
    The settings parameter must have keys 'plasma', 'probe', and 'data', where in
    each is a dictionary with either a key being 'define' or 'file_load'. If 'define',
    there is another dictionary that defines all need properties to make the object. In
    the 'file_load' case, the entry is a string that is the file path to load a json file
    that has all the needed properties to make the object.
    
    Keys (mandatory):
        'solver' : dict[str,dict | str]  ->  Path or dict for creating solver class either
        'canvas_kwargs' : dict[str,dict | str]  ->  kwargs for canvas creating either
        'panel_kwargs' : dict[str,dict | str]  ->  kwargs for solver class either
    (optional)
        'name'          : str   ->  name designation for object
        'description'   : str   ->  description of object
        'args'          : tuple ->  addional position arguments
        'kwargs'        : dict  ->  addional keyword arguments
    Returns:  Object
    """
    
    # create new object with parameters (arguments)
    output_object:LinearSemilogySingleLangmuirCombinedData2 = object_setup(
        *args,
        settings=settings,
        builders=solver_setup_builders,
        Builder=LinearSemilogySingleLangmuirCombinedData2,
        **kwargs,
    )

    return output_object

class LinearSemilogySingleLangmuirCombinedData(CombinedDataFrame):
    def __init__(self, plasma, probe, data: pd.DataFrame, *args, master=None, cnf={}, **kwargs):
        Canvas = LinearSemilogyDoubleCanvasSingleProbeLangmuir
        Panel = SingleProbeLangmuirResultsFrame
        Solver = SingleLangmuirProbeSolver
        kwargs.setdefault("solver_kwargs",{})
        kwargs["solver_kwargs"].update({'Plasma':plasma,'Probe':probe,'Data':data})
        super().__init__(Solver, Canvas, Panel,*args, master=master, cnf=cnf, **kwargs)
        # can call self.canvas, self.panel, self.property

        # solve Trace
        self.solve()

        # make save and exit button
        btn_save_n_close = tk.Button(self,cnf=cnf,command=self.save_n_close,text="Save and Close")
        # make exit button
        btn_close = tk.Button(self,cnf=cnf,command=self.close,text="Close")

        # pack away!
        btn_save_n_close.grid(row=2,column=0,columnspan=2,sticky="NSWE")
        btn_close.grid(row=3,column=0,columnspan=2,sticky="NSWE")

        # store
        self.widgets = Widgets()
        self.widgets.buttons["save_n_close"] = btn_save_n_close
        self.widgets.buttons["close"] = btn_close
    
    def solve(self,*args, **kwargs):
        # solve for data
        self.solver.solve(*args, **kwargs)

        # make plots of solved for plasma parameters
        self.canvas.make_plot(self.solver)

        # pass data to results panel
        self.panel.results = self.solver.results

    def solve_with_preprocessing(self,*args, **kwargs):
        # pre process data
        self.solver.preprocess()

        # solve for data
        self.solver.solve(*args, **kwargs)

        # make plots of solved for plasma parameters
        self.canvas.make_plot(self.solver)

        # pass data to results panel
        self.panel.results = self.solver.results

    def save_n_close(self):
        self.panel.save()
        self.canvas.save()
        self.close()

    def close(self):
        self.destroy()

class LinearSemilogySingleLangmuirCombinedData2(CombinedDataFrame2):
    def __init__(
            self, 
            solver: SingleLangmuirProbeSolver, 
            *args,
            master=None, cnf={}, name=None, preprocess=True, **kwargs):
        Canvas = LinearSemilogyDoubleCanvasSingleProbeLangmuir
        Panel = SingleProbeLangmuirPanelFrame
        super().__init__(solver, Canvas, Panel, *args, master=master,cnf=cnf, name=name,**kwargs)
        # can call self.canvas, self.panel, self.property

        # solve Trace
        self.solve(*args,preprocess=preprocess,**kwargs)

        # make save and exit button
        btn_save_n_close = tk.Button(self,cnf=cnf,command=self.save_n_close,text="Save and Close")
        # make exit button
        btn_close = tk.Button(self,cnf=cnf,command=self.close,text="Close")

        # pack away!
        btn_save_n_close.grid(row=2,column=0,columnspan=2,sticky="NSWE")
        btn_close.grid(row=3,column=0,columnspan=2,sticky="NSWE")

        # store
        self.widgets = Widgets()
        self.widgets.buttons["save_n_close"] = btn_save_n_close
        self.widgets.buttons["close"] = btn_close

        # set the update buttons on the panel.control to pass retrieved algorithm_kwargs and to resolve if pushed
        for key, control_frame in self.panel.controls.widgets.frames["controls"].items():
            if "update" in control_frame.widgets.buttons:
                control_frame.widgets.buttons["update"].configure(command=self.updated_solve)

    def solve(self, *args, preprocess=True, **kwargs):
        # pre process data
        self.solver.preprocess(delete=preprocess)

        self.solve_no_preprocessing(self, *args, **kwargs)
    
    def solve_no_preprocessing(self, *args, **kwargs):

        try:
            # solve for data
            self.solver.solve(*args, **kwargs)

            # make plots of solved for plasma parameters
            self.canvas.make_plot(self.solver)
        except (err.FunctionFitError, err.FitConvergenceError) as e:
            print("Failed in functionfit: langmuir.solve")
            print(e)
            traceback.print_exc()
            # make basic plot
            self.canvas.make_plot_basic(self.solver)
            #raise e

        except FailedLangmuirAlgorithm as F:
            print("Failed in algorithm: langmuir.solve")
            print(F)
            traceback.print_exc()
            # make basic plot
            self.canvas.make_plot_basic(self.solver)
            #raise F
        except Exception as e:
            print("General Fail: langmuir.solve")
            print(e)
            traceback.print_exc()
            # make basic plot
            try:
                self.canvas.make_plot_basic(self.solver)
            except Exception as e2:
                print("Could not make basic plot: langmuir.solve")
                print(e2)
                traceback.print_exc()
                raise e2
            #pass
        except:
            print("Catch all Fail: langmuir.solve")
            traceback.print_exc()
            # make basic plot
            self.canvas.make_plot_basic(self.solver)
            #raise

        # pass data to results panel
        self.panel.displays.results = self.solver.results

    def updated_solve(self, *args, **kwargs):

        print("Updating")
        # get what already exists
        algorithm_kwargs = kwargs.get("algorithm_kwargs", {})
        # update algorthim_kwargs is dict of i.e. {"V_f_kwargs: value, ...} with retrieved from entries
        algorithm_kwargs.update(self.panel.get_updated_algorithm_kwargs_from_control_panel())
        # reset into kwargs
        kwargs["algorithm_kwargs"] = algorithm_kwargs
        
        # before passing into resolve, clear canvas
        self.canvas.clear_plots()

        # pass in and resolve
        self.solve_no_preprocessing(*args, **kwargs)

    def save_n_close(self):
        self.panel.save()
        self.canvas.save()
        self.close()

    def close(self):
        self.destroy()


class MultipleDataFrame(tk.Frame):
    def __init__(self, num, DataFrame, master=None, cnf={}, *args, **kwargs):
        super().__init__(master, cnf=cnf, *args, **kwargs)

        self._pages = [None]*num

    def create_pages(self, num, DataFrame, *args, **kwargs):
        for k in range(num):
            self.pages[k] = DataFrame(*args, **kwargs)

    @property
    def pages(self):
        return self._pages

    def show_page(self, n):
        n -= 1

        self.pages[n].tkraise()
