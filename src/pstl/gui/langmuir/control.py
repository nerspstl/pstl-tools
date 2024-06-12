import tkinter as tk
from typing import Any
from tkinter import Misc
from typing_extensions import Literal

import numpy as np

from pstl.gui import Widgets

from pstl.diagnostics.probes.langmuir.single.helpers import available_plasma_properties

class SingleProbeLangmuirResultsControlFrame(tk.Frame):
    def __init__(
            self, 
            controls:dict[str,Any]={}, 
            *args, 
            master=None, cnf={}, 
            **kwargs):
        control_frames_kwargs = kwargs.pop("control_frames_kwargs",{})
        super().__init__(master, cnf, *args, **kwargs)

        # add widgets organizer
        self.widgets = Widgets()
        
        # if controls are not given
        control_frames = {}
        if isinstance(controls, dict):
            for key in available_plasma_properties:
                # get individual control_frame kwargs for keyed value
                control_frame_key_kwargs = control_frames_kwargs.get(key, {})
                # set master and cnf
                control_frame_key_kwargs.setdefault("master", self)
                control_frame_key_kwargs.setdefault("cnf", cnf)
                # creates the control frame either the default or probided function to make a framif key not in controls else controls[key](cnf=cnf,**)e and then packs it onto this frame
                if key not in controls:
                    control_frame_key_kwargs.setdefault("txt", key)
                    control_frames[key] = self.create_default_frame(key, **control_frame_key_kwargs) 
                else:
                    # may need to verify that controls value element for key is a callable function that makes and returns a frame
                    control_frames[key] = controls[key](**control_frame_key_kwargs)
        else:
            raise ValueError(
                "'controls' must be dictionary: {}".format(type(controls)))
        
        # Once all control frames are made, they must be packed
        # all can be in the same spot as tk.raise will overide which is on top
        for key in control_frames:
            frame = control_frames[key]
            frame.grid(
                row=0,
                column=0,
                columnspan=5,
                sticky="NWSE",
            )

        # save function controls
        self._controls = controls

        # save control_frames  
        self.widgets.frames["controls"] = control_frames

        # save control buttons
        #self.widgets.buttons["save"] = frame_save
        #self.widgets.buttons["back"]
        #self.widgets.buttons["update"]
        #self.widgets.buttons["cancel"]

        # save display status label
        #self.widgets.labels["status"]

        #self.update_texts(results=self.results)

        # set size of columns (prob not needed for now)
        self.columnconfigure(0, weight=1, uniform="fred")
    
    def save(self):
        self.widgets.buttons["save"].save()

    @property
    def controls(self):
        return self._controls
    
    def get_all_controls_entries(self):
        """
        Returns dict of i.e. {"V_f_kwargs: value, ...}
        """
        returns = {}
        for key,frame in self.widgets.frames["controls"].items():
            key_kwargs = key + "_kwargs"
            kwargs_values = frame.get_entries()
            returns[key_kwargs] = kwargs_values
        return returns

    def create_default_frame(self, key, *args, cnf={},**kwargs):
#ResultControl(key=key, create_func=None,**control_frame_key_kwargs)     #
        if key == "V_f":
            control_frame = ResultControl(key=key,cnf=cnf,**kwargs)
        elif key == "V_s":
            control_frame = ResultControl(key=key,cnf=cnf,**kwargs)
        elif key == "I_is":
            #control_frame = ResultControl(key=key,cnf=cnf,**kwargs)
            control_frame = ControlFunctionFit(cnf=cnf,**kwargs)
        elif key == "n_i":
            control_frame = ResultControl(key=key,cnf=cnf,**kwargs)
        elif key == "I_es":
            control_frame = ControlFunctionFit(cnf=cnf,**kwargs)
        elif key == "KT_e":
            control_frame = ControlFunctionFit(cnf=cnf,**kwargs)
        elif key == "n_e":
            control_frame = ResultControl(key=key,cnf=cnf,**kwargs)
        elif key == "J_es":
            control_frame = ResultControl(key=key,cnf=cnf,**kwargs)
        elif key == "J_is":
            control_frame = ResultControl(key=key,cnf=cnf,**kwargs)
        elif key == "lambda_De":
            control_frame = ResultControl(key=key,cnf=cnf,**kwargs)
        elif key == "r_p/lambda_De":
            control_frame = ResultControl(key=key,cnf=cnf,**kwargs)
        elif key == "sheath":
            control_frame = ResultControl(key=key,cnf=cnf,**kwargs)
        else:
            control_frame = ResultControl(key=key,cnf=cnf,**kwargs)

        return control_frame

    def create_electron_temperature(self, cnf, *args, **kwargs):
        print("Electron Temperature")

    def create_electron_saturation(self, cnf, *args, **kwargs):
        print("Electron saturation")


class ResultControl(tk.Frame):
    """
    This creates a frame that houses the controls and buttons for a control panel
    that is raised when the button on the ResultOutputs frame has.
    """
    def __init__(
            self, 
            key,
            create_func=None,
            *args, 
            master=None, cnf={}, 
            **kwargs):
        lbl_kwargs = kwargs.pop("label_kwargs",{})
        btn_kwargs = kwargs.pop("btn_kwargs",{})
        txt = kwargs.pop("txt","")
        super().__init__(master, cnf, *args, **kwargs)

        # create widgets
        self.widgets = Widgets()

        # create frame and populate with either default or call to create_func 
        kwargs.setdefault("key",key)
        kwargs.setdefault("txt",txt)
        self.create_place_holder(cnf, *args, **kwargs) if create_func is None else create_func(*args,cnf=cnf,**kwargs)
        
    def create_place_holder(self, cnf, *args, **kwargs):
        key = kwargs.pop("key")
        # create label
        lbl = create_label_place_holder(self,cnf, *args, **kwargs,)
        
        # pack away!
        lbl.grid(row=0,column=0,sticky="NSWE")

        # save access
        self.widgets.labels["not-implemented"] = lbl

        # set column size 
        self.columnconfigure(0, weight=1, uniform="fred")
    
    def get_entries(self):
        """
        Returns a empty dictionary for Control.get_all_controls_enteries()
        """
        return {}

# module functions
def create_label_place_holder(master, cnf, txt="",*args,**kwargs):
    # set defaults
    text = "Not yet implemented\n"+txt
    kwargs.setdefault("text", text)

    # create place holder label
    lbl = tk.Label(
        master = master,
        cnf = cnf,
        *args,
        **kwargs,
    )
    return lbl

class ControlEntryLabelFrame(tk.Frame):
    def __init__(self, lbl_txt, *args, master=None, cnf={},**kwargs):
        label_kwargs = kwargs.pop("label_kwargs",{})
        entry_kwargs = kwargs.pop("entry_kwargs",{})
        super().__init__(master, cnf, *args,**kwargs)

        # add widgets organizer
        self.widgets = Widgets()

        # creat label
        lbl = tk.Label(self, cnf,text=lbl_txt,**label_kwargs)
        # packit
        lbl.grid(row=0,column=0,sticky="NSEW")
        # creat label
        ent = tk.Entry(self, cnf,**label_kwargs)
        # packit
        ent.grid(row=0,column=1,sticky="NSEW")

        # save them
        self.widgets.labels["label"] = lbl
        self.widgets.entries["entry"] = ent

        # create short handel
        self._label = lbl
        self._entry = ent

        # column weight
        self.columnconfigure(0, weight=1, uniform="fred")
        self.columnconfigure(1, weight=1, uniform="ted")

    @property
    def label(self):
        return self._label
    
    @property
    def entry(self):
        return self._entry
    
    def clear_entry(self):
        self.widgets.entries["entry"].delete(0,tk.END)
    
    def get_entry(self) -> int | None:
        value = self.widgets.entries["entry"].get()
        if value.lower() == "none" or value == "":
            value = None
        else:
            value = int(value)
        return value
    def get_label_text(self) -> str | None:
        value = self.widgets.labels["label"]["text"]
        return value


class ControlFunctionFit(tk.Frame):
    def __init__(
            self, 
            master: Misc | None = None, 
            cnf: dict[str, Any] | None = {},
            *args,
            **kwargs): 
        istart_kwargs = kwargs.get("istart_kwargs",{})
        iend_kwargs = kwargs.get("iend_kwargs",{})
        fitmax_kwargs = kwargs.get("fitmax_kwargs",{})
        bitmax_kwargs = kwargs.get("bitmax_kwargs",{})
        min_points_kwargs = kwargs.get("min_points_kwargs",{})
        threshold_rmse = kwargs.get("threshold_rmse_kwargs",{})
        update_kwargs = kwargs.get("update_kwargs",{})
        cancel_kwargs = kwargs.get("cancel_kwargs",{})
        txt = kwargs.pop("txt","")

        super().__init__(master, cnf, *args, **kwargs)

        # add widgets organizer
        self.widgets = Widgets()

        # create four ControlLabelEntryFrames
        istart = ControlEntryLabelFrame(lbl_txt="istart",master=self,cnf=cnf,**istart_kwargs)
        iend = ControlEntryLabelFrame(lbl_txt="iend",master=self,cnf=cnf,**iend_kwargs)
        fitmax = ControlEntryLabelFrame(lbl_txt="fitmax",master=self,cnf=cnf,**fitmax_kwargs)
        bitmax = ControlEntryLabelFrame(lbl_txt="bitmax",master=self,cnf=cnf,**bitmax_kwargs)
        min_points = ControlEntryLabelFrame(lbl_txt="min_points",master=self,cnf=cnf,**bitmax_kwargs)
        # create update and clear
        update_btn = tk.Button(self,cnf,text="Update",**update_kwargs)
        cancel_kwargs.setdefault("command", self.clear_enteries)
        cancel_btn = tk.Button(self,cnf,text="Cancel",**cancel_kwargs)

        # pack away
        istart.grid(row=0,column=0,sticky="NSEW")
        iend.grid(
            row=0,
            column=1,
            sticky="NSWE",
        )
        fitmax.grid(
            row=1,
            column=0,
            sticky="NSWE",
        )
        bitmax.grid(
            row=1,
            column=1,
            sticky="NSWE",
        )
        min_points.grid(
            row=2,
            column=0,
            sticky="NSWE",
        )
        # pack away
        update_btn.grid(
            row=5,
            column=0,
            sticky="NSEW",
        )
        cancel_btn.grid(
            row=5,
            column=1,
            sticky="NSEW",
        )

        # save them
        self.widgets.frames["istart"] = istart
        self.widgets.frames["iend"] = iend
        self.widgets.frames["fitmax"] = fitmax
        self.widgets.frames["bitmax"] = bitmax
        self.widgets.frames["min_points"] = min_points

        self.widgets.buttons["update"] = update_btn
        self.widgets.buttons["cancel"] = cancel_btn

        # create short handel
        self._istart = istart
        self._iend = iend
        self._fitmax = fitmax
        self._bitmax = bitmax

        # column weight
        self.columnconfigure(0, weight=1, uniform="fred")
        self.columnconfigure(1, weight=1, uniform="fred")
        #self.rowconfigure(0, weight=1, uniform="fred")
        #self.rowconfigure(1, weight=1, uniform="fred")

    @property
    def istart(self):
        return self._istart
    
    @property
    def iend(self):
        return self._iend

    @property
    def fitmax(self):
        return self._fitmax
    
    @property
    def bitmax(self):
        return self._bitmax
    
    def clear_enteries(self):
        for key in self.widgets.frames:
            #self.widgets.frames[key].widgets.entries["entry"].delete(0,tk.END)
            self.widgets.frames[key].clear_entry()
    def get_entries(self):
        fit_kwargs = {}
        for key in self.widgets.frames:
            label_text = self.widgets.frames[key].get_label_text()
            entry_value = self.widgets.frames[key].get_entry()
            if entry_value is None:
                _ = fit_kwargs.pop(label_text,None)
            else:
                fit_kwargs[label_text] = entry_value
        returns = {"fit_kwargs": fit_kwargs}
        return returns

