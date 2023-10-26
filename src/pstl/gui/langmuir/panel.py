import tkinter as tk

from pstl.gui import Widgets
from pstl.gui.langmuir.results import SingleProbeLangmuirResultsFrame as SPLResultFrame
from pstl.gui.langmuir.control import SingleProbeLangmuirResultsControlFrame as SPLControlFrame

from pstl.diagnostics.probes.langmuir.single.helpers import available_plasma_properties


class SingleProbeLangmuirPanelFrame(tk.Frame):
    """
    This class creates one frame that contains the results page and the page
    that contains subframes of controls for each results button
    """
    def __init__(
            self,
            *args,
            master  :   tk.Frame | None =   None,
            cnf     :   dict            =   {},
            **kwargs):
        controls_frame_kwargs = kwargs.pop("controls_kwargs",{})
        results_frame_kwargs = kwargs.pop("displays_kwargs",{})
        super().__init__(master,cnf,*args,**kwargs)

        # add widgets organizer
        self.widgets = Widgets()

        # create controls
        controls_frame_kwargs.setdefault("master", self)
        controls_frame_kwargs.setdefault("cnf", cnf)
        controls_frame = SPLControlFrame(**controls_frame_kwargs)
        # pack it away!
        controls_frame.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="NWSE",
        )

        # create results
        results_frame_kwargs.setdefault("master", self)
        results_frame_kwargs.setdefault("cnf", cnf)
        results_frame = SPLResultFrame(**results_frame_kwargs)
        # pack it away!
        results_frame.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="NWSE",
        )

        # create display and contrl frame buttons
        display_btn = tk.Button(self,cnf,text="Displays",command=self.raise_display_frame)
        display_btn.grid(row=1,column=0,sticky="WSE")
        control_btn = tk.Button(self,cnf,text="Controls",command=self.raise_control_frame)
        control_btn.grid(row=1,column=1,sticky="WSE")

        # save to widgets
        self.widgets.frames["control"] = controls_frame
        self.widgets.frames["display"] = results_frame
        self.widgets.buttons["control"] = control_btn
        self.widgets.buttons["display"] = display_btn

        # save handle access
        self._controls = controls_frame
        self._displays = results_frame

        # configure buttons to ew
        self.set_display_btn_default()

    @property
    def controls(self):
        return self._controls
    
    @property
    def displays(self):
        return self._displays
    
    def save(self):
        self.displays.save()

    def get_updated_algorithm_kwargs_from_control_panel(self):
        """
        Returns dict of i.e. {"V_f_kwargs: value, ...}
        """
        algorithm_kwargs = self.controls.get_all_controls_entries()
        return algorithm_kwargs

    def set_display_btn_default(self):
        for key in available_plasma_properties:
            raise_func=self.get_raise_func(key)
            #self.displays.widgets.frames["results"][key].widgets.buttons["key"].configure(command=self.controls.widgets.frames["controls"][key].tkraise)
            #self.displays.widgets.frames["results"][key].widgets.buttons["key"].configure(command=self.raise_control_frame)
            self.displays.widgets.frames["results"][key].widgets.buttons["key"].configure(command=raise_func)


    def get_raise_func(self, key):
        if key == "V_f":
            raise_func = self.raise_func_floating_potential
        elif key == "V_s":
            raise_func = self.raise_func_plasma_potential
        elif key == "I_is":
            raise_func = self.raise_func_ion_saturation_current
        elif key == "n_i":
            raise_func = self.raise_func_ion_density
        elif key == "I_es":
            raise_func = self.raise_func_electron_saturation_current
        elif key == "KT_e":
            raise_func = self.raise_func_electron_temperature
        elif key == "n_e":
            raise_func = self.raise_func_electron_density
        elif key == "J_es":
            raise_func = self.raise_func_electron_saturation_current_density
        elif key == "J_is":
            raise_func = self.raise_func_ion_saturation_current_density
        elif key == "lambda_De":
            raise_func = self.raise_func_lambda_De
        elif key == "r_p/lambda_De":
            raise_func = self.raise_func_ratio
        elif key == "sheath":
            raise_func = self.raise_func_sheath
        else:
            raise_func = self.raise_control_frame

        return raise_func



    def raise_control_frame_keyed(self, key):
        self.raise_control_frame()
        self.controls.widgets.frames["controls"][key].tkraise()

    def raise_control_frame(self):
        self.controls.tkraise()
    def raise_display_frame(self):
        self.displays.tkraise()

    def raise_func_floating_potential(self):
        key="V_f"
        self.raise_control_frame()
        self.controls.widgets.frames["controls"][key].tkraise()
    def raise_func_plasma_potential(self):
        key="V_s"
        self.raise_control_frame()
        self.controls.widgets.frames["controls"][key].tkraise()
    def raise_func_ion_saturation_current(self):
        key="I_is"
        self.raise_control_frame()
        self.controls.widgets.frames["controls"][key].tkraise()
    def raise_func_ion_saturation_current_density(self):
        key="J_is"
        self.raise_control_frame()
        self.controls.widgets.frames["controls"][key].tkraise()
    def raise_func_electron_saturation_current(self):
        key="I_es"
        self.raise_control_frame()
        self.controls.widgets.frames["controls"][key].tkraise()
    def raise_func_electron_saturation_current_density(self):
        key="J_es"
        self.raise_control_frame()
        self.controls.widgets.frames["controls"][key].tkraise()
    def raise_func_electron_density(self):
        key="n_e"
        self.raise_control_frame()
        self.controls.widgets.frames["controls"][key].tkraise()
    def raise_func_ion_density(self):
        key="n_i"
        self.raise_control_frame()
        self.controls.widgets.frames["controls"][key].tkraise()
    def raise_func_electron_temperature(self):
        key="KT_e"
        self.raise_control_frame()
        self.controls.widgets.frames["controls"][key].tkraise()
    def raise_func_lambda_De(self):
        key="lambda_De"
        self.raise_control_frame()
        self.controls.widgets.frames["controls"][key].tkraise()
    def raise_func_ratio(self):
        key="r_p/lambda_De"
        self.raise_control_frame()
        self.controls.widgets.frames["controls"][key].tkraise()
    def raise_func_sheath(self):
        key="sheath"
        self.raise_control_frame()
        self.controls.widgets.frames["controls"][key].tkraise()