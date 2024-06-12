import tkinter as tk
from typing import Any, Callable
import json
import csv

import numpy as np

from pstl.gui import Widgets

from pstl.diagnostics.probes.langmuir.single.helpers import available_plasma_properties

def print_not_yet_implemented():
    print("Not yet implemented")


class SingleProbeLangmuirResultsFrame(tk.Frame):
    def __init__(
            self, 
            master  =   None, 
            cnf     :   dict            =   {}, 
            *args, 
            results :   dict | None     =   None, 
            fname   :   str | None      =   None, 
            ftype   :   str | None      =   None,
            **kwargs):
        
        # pop out ResultOutput kwargs out of kwargs to prevent initialize error in tk.Frame
        result_output_kwargs = kwargs.pop("results_output_kwargs",{})
        btn_kwargs = result_output_kwargs.pop("btn_kwargs",{})

        # initialize tk.Frame
        super().__init__(master, cnf, *args, **kwargs)

        # add widgets organizer
        self.widgets = Widgets()

        # if results are not given
        if results is None:
            results = {}
            for key in available_plasma_properties:
                results[key] = {"value": 1, "other": None}
        elif isinstance(results, dict):
            pass
        else:
            raise ValueError(
                "'results' must be dictionary: {}".format(type(results)))

        # create and save results as an attribute
        self._results = results

        # number of properties to display and grid positions
        grid_positions_list = self.grid_positions(results.keys())

        # loop and create labels to display
        result_frames = {}
        row = 0 
        for k, key in enumerate(results.keys()):
            # Results displayed value on label
            text = self.results[key]["value"]
            # Results units displayed
            unit = self.results[key]["other"]
            unit = self.default_unit_format(key) if unit is None else unit
            # get command for each button based on kwargs["result_output_kwargs"]["btn_kwargs"][key]
            command = btn_kwargs.get(key, print_not_yet_implemented)
            result_output_kwargs["btn_kwargs"] = {"command": command}
            # create One frame to house btn, text result, and unit display
            result_frames[key] = ResultOutput(
                key, text, unit, self, cnf, 
                **result_output_kwargs) # these are frames of btn and label
            # get grid positions 
            row = grid_positions_list[k][0]
            col = grid_positions_list[k][1]
            # pack it away!
            result_frames[key].grid(
                row=row, column=col,
                sticky="NWSE", padx=5, pady=5)
            
        # add export frame (button&entry) to save results
        frame_save = SaveResults(
            self.export_results, 
            fname=fname, ftype=ftype,
            master=self, cnf=cnf,
            *args,**kwargs)
        # pack save away!
        frame_save.grid(row=row+1,column=0,columnspan=3,sticky="NSWE", padx=5,pady=5)

        # save Individual ResultOuput Frame access
        self.widgets.frames["results"] = result_frames
        
        # save SaveResult Frame access
        self.widgets.frames["save"] = frame_save

        # function to update the results
        self.update_texts(results=self.results)

        # Configure the columns to have the same weight/size
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
    
    def save(self):
        self.widgets.frames["save"].save()

    @property
    def results(self):
        return self._results

    @results.setter
    def results(self, val):
        self.update_texts(val)
        self._results = val

    def update_label(self, key, text):
        if key in self.widgets.frames["results"]:
            self.widgets.frames["results"][key].update_text(text=text)
        else:
            table = "\n".join(
                [f"{k}\t{v}" for k, v in enumerate(self.widgets.frames["results"])])
            raise ValueError(
                f"Matching key not found: {key}\nChoose from one of the available options:\n{table}")

    def update_texts(self, results=None):
        if results is None:
            results = self.results

        for key in results.keys():
            text = self.default_text_format(key)
            val = results[key]['value']
            val = 0.0 if val is None else val
            text = text.format(val)
            self.update_label(key, text)

    def export_results(self):
        temp = self.results
        results = {}

        for key in temp.keys():
            value = temp[key]["value"]
            unit = temp[key].get("unit",self.default_unit_string(key))
            results[key] = {"value":value,"unit":unit}
        return results

    def default_text_format(self, key):
        if key == "V_f":
            text = "{0:.2f}"
        elif key == "V_s":
            text = "{0:.2f}"
        elif key == "I_is":
            text = "{0:.2e}"
        elif key == "n_i":
            text = "{0:.2e}"
        elif key == "I_es":
            text = "{0:.2e}"
        elif key == "KT_e":
            text = "{0:.2f}"
        elif key == "n_e":
            text = "{0:.2e}"
        elif key == "J_es":
            text = "{0:.2e}"
        elif key == "J_is":
            text = "{0:.2e}"
        elif key == "lambda_De":
            text = "{0:.2e}"
        elif key == "r_p/lambda_De":
            text = "{0:.2e}"
        elif key == "sheath":
            text = "{0}"
        else:
            text = "{}"

        return text
    
    def default_unit_string(self, key):
        if key == "V_f":
            text = "V"
        elif key == "V_s":
            text = "V"
        elif key == "I_is":
            text = "A"
        elif key == "n_i":
            text = "m^-3"
        elif key == "I_es":
            text = "A"
        elif key == "KT_e":
            text = "eV"
        elif key == "n_e":
            text = "m^-3"
        elif key == "J_es":
            text = "A/m^2"
        elif key == "J_is":
            text = "A/m^2"
        elif key == "lambda_De":
            text = "m"
        elif key == "r_p/lambda_De":
            text = "-"
        elif key == "sheath":
            text = "-"
        else:
            text = "{}"

        return text

    def default_unit_format(self, key):
        if key == "V_f":
            text = "V"
        elif key == "V_s":
            text = "V"
        elif key == "I_is":
            text = "A"
        elif key == "n_i":
            text = "m\u207B\u00B3"
        elif key == "I_es":
            text = "A"
        elif key == "KT_e":
            text = "eV"
        elif key == "n_e":
            text = "m\u207B\u00B3"
        elif key == "J_es":
            text = "A/m\u00B2"
        elif key == "J_is":
            text = "A/m\u00B2"
        elif key == "lambda_De":
            text = "m"
        elif key == "r_p/lambda_De":
            text = ""
        elif key == "sheath":
            text = ""
        else:
            text = "N/A"

        return text


    def grid_positions(self, lst, layout="two"):
        # layout = "square"
        if layout == "two":
            func = self._two_layout
        elif layout == "square":
            func = self._square_layout
        else:
            raise ValueError("layout is not knonw: {layout}")
        return func(lst)

    def _sort_positions(self, num_items, num_rows, num_cols):
        positions = []
        for i in range(num_items):
            row = int(i/num_cols) 
            col = i % num_cols
            positions.append((row, col))

        return positions

    def _two_layout(self, lst):
        num_items = len(lst)
        num_rows = int(np.ceil(num_items/2))
        num_cols = 2
        return self._sort_positions(num_items, num_rows, num_cols)

    def _square_layout(self, lst):
        # Calculate the number of rows and columns needed for the closest square grid
        num_items = len(lst)
        grid_size = int(np.ceil(np.sqrt(num_items)))
        num_rows = grid_size
        num_cols = grid_size

        # If the grid is larger than necessary, reduce the number of columns
        if num_items < num_rows*num_cols:
            num_cols = int(np.ceil(num_items/num_rows))

        return self._sort_positions(num_items, num_rows, num_cols)

class SaveResults(tk.Frame):
    def __init__(self, command, fname=None, ftype=None, master=None, cnf={}, *args,**kwargs):
        super().__init__(master,cnf, *args, **kwargs)

        # create widgets
        self.widgets = Widgets()

        # create save button
        btn_kwargs = kwargs.get("btn_kwargs", {})
        btn_kwargs.setdefault("text", "Save")
        btn_kwargs.setdefault("command",self.export_results)
        btn = tk.Button(self, cnf, **btn_kwargs)

        # create entry for filename and populate with default
        entry_kwargs = kwargs.get("entry_kwargs", {})
        #entry_kwargs.setdefault()
        entry = tk.Entry(self, cnf,**entry_kwargs)

        # pack away!
        btn.grid(row=0, column=0, sticky="NSWE")
        entry.grid(row=0, column=1, sticky="NSWE")

        # change column weights
        self.columnconfigure(1,weight=1)

        # store
        self.widgets.buttons["save"] = btn
        self.widgets.entries["save"] = entry

        # store command
        self.command = command

        # store file type to save to 
        self.ftype = ftype

        # store fname default
        if fname is None:
            fname = "output.txt"
        entry.insert(0,fname)

    def save(self):
        self.export_results()

    def export_results(self):
        command = self.command
        if callable(command):
            results = command()
        else:
            results = command
        ftype = self.ftype


        # get current entry filename
        fname = self.widgets.entries["save"].get()

        if ftype is None or ftype.upper() == "CSV":
            if fname is None:
                fname = "output.csv"

            with open(fname, "w") as outfile:
                header = []
                values = []
                for key in results.keys():
                    unit = results[key]["unit"]
                    string = key+" - ["+unit+"]"
                    header.append(string)
                for key in results.keys():
                    value = str(results[key]["value"])
                    values.append(value)

                writer = csv.writer(outfile)

                writer.writerow(header)
                writer.writerow(values)

        elif ftype.upper() == "JSON":
            if fname is None:
                fname = "output.json"

            with open(fname, "w") as outfile:
                json.dump(results, outfile) 
        else:
            raise ValueError("Not supported export type. Try:\n") # add list of types
        
        # print
        print("saved to '%s'"%(fname))
    
    def get(self):
        return self.widgets.entries["save"].get()



class ResultOutput(tk.Frame):
    def __init__(self, key, value=None, unit=None, master=None, cnf=None, *args, latex=True, **kwargs):
        btn_kwargs = kwargs.pop("btn_kwargs", {})
        super().__init__(master, cnf, *args, **kwargs)

        # create widgets
        self.widgets = Widgets()

        # create button/label of property name to display
        if latex is True:
            key = self.convert_to_latex(key)
        btn_kwargs.setdefault("text", key)
        # define later to call new window with settings
        btn_kwargs.setdefault("command", None)
        btn = tk.Button(self, cnf, **btn_kwargs)

        # create label of value
        value_lbl_kwargs = kwargs.get("value_lbl_kwargs", {})
        value_lbl_kwargs.setdefault("text", value)
        value_lbl_kwargs.setdefault("bg", "white")
        value_lbl = tk.Label(self, cnf, **value_lbl_kwargs)

        # create unit label
        unit_lbl_kwargs = kwargs.get("unit_lbl_kwargs", {})
        unit_lbl_kwargs.setdefault("text", unit)
        unit_lbl = tk.Label(self, cnf, **unit_lbl_kwargs)

        # pack away!
        btn.grid(row=0, column=0, sticky="NSWE")
        value_lbl.grid(row=0, column=1, sticky="NSWE")
        unit_lbl.grid(row=0, column=2, sticky="NSWE")

        # save to self
        self.widgets.buttons["key"] = btn   # not sure why its a str
        self.widgets.labels["value"] = value_lbl
        self.widgets.labels["unit"] = unit_lbl

        # configure columns size
        self.columnconfigure(0, weight=2, uniform="fred")
        self.columnconfigure(1, weight=2, uniform="fred")
        self.columnconfigure(2, weight=1, uniform="fred")

    def update_text(self, text):
        self.widgets.labels["value"].config(text=text)

    def updata_value_label(self, key, value):
        kwargs = {key: value}
        self.widgets.labels["value"].config(**kwargs)

    def convert_to_latex(self, input_string: str):

        input_string = input_string.replace("lambda", "\u03BB")
        #input_string = input_string.replace("sheath", "r_p/\u03BB_De")

        split_string = input_string.split("_")
        if len(split_string) > 1:
            text = []
            for k, string in enumerate(split_string):
                if k == 0:
                    text.append(string)
                else:
                    text.append(string)
            text = "".join(text)
        else:
            text = split_string[0]

        return text
