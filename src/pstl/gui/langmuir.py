from abc import ABC, abstractmethod, abstractproperty
from typing import Any, Sequence
import tkinter as tk

import numpy as np
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk  # type: ignore

from pstl.utls import constants as c
from pstl.diagnostics.probes.langmuir.single.classes import available_plasma_properties
from pstl.diagnostics.probes.langmuir.single.analysis.solver import SingleLangmuirProbeSolver


class Widgets:
    # Initialize the class with empty dictionaries for each widget name
    def __init__(self):
        self.buttons = {}
        self.canvases = {}
        self.checkbuttons = {}
        self.entries = {}
        self.frames = {}
        self.labels = {}
        self.labelframes = {}
        self.listboxes = {}
        self.menus = {}
        self.menubuttons = {}
        self.messages = {}
        self.optionmenus = {}
        self.panedwindows = {}
        self.radiobuttons = {}
        self.scales = {}
        self.scrollbars = {}
        self.texts = {}
        self.toplevels = {}


class WidgetOrganizer:
    def __init__(self) -> None:
        self._widgets = Widgets()

    @property
    def widget(self):
        return self._widgets


class MatplotlibCanvas(tk.Frame):
    def __init__(self, master=None, cnf=None, *args, fig: Figure | None = None, ax: Axes | None = None,  **kwargs):
        width = kwargs.pop("width", 8)
        height = kwargs.pop("height", 6)
        dpi = kwargs.pop("dpi", 100)
        super().__init__(master, cnf, *args, **kwargs)

        # add widgets
        self.widgets = Widgets()

        if fig is None:
            # initialize matplotlib figure and axes

            self.fig = Figure(figsize=(width, height), dpi=dpi)
            self.fig.set_tight_layout(True)
        else:
            self.fig = fig

        if ax is None:
            self.ax = self.fig.add_subplot(
                1, 1, 1)  # type: ignore
        else:
            self.ax = ax

        # A tk.DrawingArea.
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()

        # Pack Canvas
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def set_fig_to_linear(self):
        fig = self.fig

        ax = self.ax
        scale = ax.get_yscale()
        if len(ax.lines) == 0:
            ax.set_yscale("linear")
        else:
            ydata = ax.lines[0].get_ydata()
            ydata_minimum = np.min(ydata)
            ydata_maximum = np.max(ydata)
            ylim = ax.get_ylim()

            ypad = 0.05*(np.max(ydata)-np.min(ydata))

            ylim = [ydata_minimum-ypad, ydata_maximum+ypad]

            ax.set_yscale("linear")

            ax.set_ylim(ylim[0], ylim[1])
        fig.canvas.draw()

    def set_fig_to_semilogy(self):
        fig = self.fig

        ax = self.ax
        scale = ax.get_yscale()

        if len(ax.lines) == 0:
            ax.set_yscale("log")
        else:
            ydata = ax.lines[0].get_ydata()

            # Set the y-axis limits with minimum positive value padding
            y_lim = ax.get_ylim()
            y_min = np.floor(np.log10(np.min(ydata[ydata > 0])))
            y_max = np.ceil(np.log10(y_lim[1]))

            ax.set_yscale("log")

            ax.set_ylim(10**(y_min), 10**y_max)
        fig.canvas.draw()


class MatplotlibCanvasWToolbar(MatplotlibCanvas):
    def __init__(self, master=None, cnf=None, *args, **kwargs):
        super().__init__(master, cnf, *args, **kwargs)
        # pack_toolbar=False will make it easier to use a layout manager later on.
        self.toolbar = NavigationToolbar2Tk(
            self.canvas, self, pack_toolbar=False)
        self.toolbar.update()

        # Pack Toolbar
        self.toolbar.pack(side=tk.TOP, fill=tk.X, expand=True)


class MatplotlibCanvasWToolbarSave(MatplotlibCanvasWToolbar):
    def __init__(self, master=None,
                 cnf=None, *args,
                 fig: Figure | None = None, ax: Axes | None = None,
                 saveas: str = "figure1.png",
                 **kwargs):
        super().__init__(master, cnf, *args, fig=fig, ax=ax, **kwargs)

        self.saveas = saveas

        # add save default button
        self.widgets.buttons['save'] = tk.Button(
            self, text="Save", command=self.save)
        self.widgets.buttons['save'].pack(
            side=tk.TOP, fill=tk.X, expand=True)

    def save(self, saveas: str | None = None, **kwargs):
        if saveas is None:
            saveas = self.saveas
        self.fig.savefig(saveas, **kwargs)


class LinearSemilogyCanvas(MatplotlibCanvasWToolbarSave):
    def __init__(self, master=None,
                 cnf={}, fig: Figure | None = None, ax: Axes | None = None,
                 saveas: str = "figure1.png",
                 **kwargs):
        super().__init__(master, cnf, fig=fig, ax=ax, saveas=saveas, **kwargs)

        self.widgets.buttons['linear'] = tk.Button(
            self, text="Linear", command=self.set_fig_to_linear
        )
        self.widgets.buttons['semilogy'] = tk.Button(
            self, text="Semilogy", command=self.set_fig_to_semilogy
        )

        # pack linear and semilogy buttons
        self.widgets.buttons['linear'].pack(
            side=tk.LEFT, fill=tk.BOTH, expand=True
        )
        self.widgets.buttons['semilogy'].pack(
            side=tk.RIGHT, fill=tk.BOTH, expand=True
        )


class LinearSemilogyDoubleCanvas(tk.Frame):
    def __init__(self, master=None, cnf=None, saveas="figures.png", sappends=["_linear", "_semilogy"], n=2, sharex=True, **kwargs):
        width = kwargs.pop("width", 5)
        height = kwargs.pop("height", 4)
        dpi = kwargs.pop("dpi", 100)
        figure_kw = {'width': width, 'height': height, 'dpi': dpi}

        super().__init__(master, cnf, **kwargs)

        if isinstance(saveas, list):
            self.saveass = saveas
        elif isinstance(saveas, str):
            slist = saveas.split('.')
            if len(slist) == 1:
                path = saveas
                ext = str()
            elif len(slist) >= 2:
                num_ext_char = len(slist[-1])
                iend = -(num_ext_char+1)
                ext = saveas[iend:]
                path = saveas[:iend]
            elif len(slist) == 0:
                raise ValueError("Something went wrong")
            else:
                raise ValueError("Lenth of list cannot be negative")

            saveas = []
            for i in range(n):
                if i == 0:
                    sappend = "_linear"
                elif i == 1:
                    sappend = "_semilogy"
                else:
                    sappend = str(i)
                saveas.append(path+sappend+ext)

        self.widgets = Widgets()

        self.widgets.frames['linear'] = MatplotlibCanvasWToolbarSave(
            self, saveas=saveas[0], **figure_kw)

        self.widgets.frames['semilogy'] = MatplotlibCanvasWToolbarSave(

            self, saveas=saveas[1], **figure_kw)
        # remap ax for plotting
        self.frame1 = self.widgets.frames['linear']
        self.ax1 = self.frame1.ax
        self.frame2 = self.widgets.frames['semilogy']
        self.ax2 = self.frame2.ax
        # set frame2 to semilogy
        self.widgets.frames['semilogy'].set_fig_to_semilogy()

        if sharex:
            self.ax2.sharex(self.ax1)

        # pack
        self.frame1.grid(row=0, column=0, sticky="NSWE")
        self.frame2.grid(row=0, column=1, sticky="NSWE")

        # add save default button
        self.widgets.buttons['save_both'] = tk.Button(
            self, text="Save Both", command=self.save_both)
        self.widgets.buttons['save_both'].grid(
            row=1, column=0, columnspan=2, sticky="NSEW")

    def save_both(self, **kwargs):

        self.frame1.save()
        self.frame2.save()

    @staticmethod
    def update_both(func, *args, **kwargs):
        def decorator(self, *args, **kwargs):
            func(*args, **kwargs)
            self.frame1.set_fig_to_linear()
            self.frame2.set_fig_to_semilogy()
        return decorator  # (*args, **kwargs)

    @update_both
    @staticmethod
    def add_plot(ax_func, *args, **kwargs):
        ax_func(*args, **kwargs)

    @update_both
    @staticmethod
    def add_to_both(ax1_func, ax2_func, *args, **kwargs):
        ax1_func(*args, **kwargs)
        ax2_func(*args, **kwargs)

    def legend(self, ax1_bool=True, ax2_bool=True, *args, **kwargs):
        if ax1_bool:
            self.ax1.legend(*args, **kwargs)
        if ax2_bool:
            self.ax2.legend(*args, **kwargs)

    def add_raw_data(self, voltage, current, *args, **kwargs):
        # set defaults
        kwargs.setdefault("label", "Raw Data")
        kwargs.setdefault("color", "C0")
        kwargs.setdefault("marker", "s")
        kwargs.setdefault("markerfacecolor", "none")
        kwargs.setdefault("alpha", 0.5)

        # save data
        self.raw_data = pd.DataFrame({'voltage': voltage, 'current': current})

        # add plot
        self.add_to_both(self.ax1.plot, self.ax2.plot,
                         voltage, current, *args, **kwargs)

    def add_data(self, voltage, current, *args, **kwargs):
        # set defaults
        kwargs.setdefault("label", "Experimental Data")
        kwargs.setdefault("color", "C0")
        kwargs.setdefault("marker", "^")
        kwargs.setdefault("markerfacecolor", "none")

        # save data
        self.data = pd.DataFrame({'voltage': voltage, 'current': current})

        # add plot
        self.add_to_both(self.ax1.plot, self.ax2.plot,
                         voltage, current, *args, **kwargs)

    def add_deleted_points(self, voltage, current, *args, **kwargs):
        kwargs.setdefault("label", "Removed Data")
        kwargs.setdefault("color", "C1")
        kwargs.setdefault("linestyle", "none")
        kwargs.setdefault("marker", "x")
        self.deleted_points = pd.DataFrame(
            {'voltage': voltage, 'current': current})
        self.add_to_both(self.ax1.plot, self.ax2.plot,
                         voltage, current, *args, **kwargs)

    def add_filtered_data(self, voltage, current, *args, **kwargs):
        kwargs.setdefault("label", "Filtered Data")
        kwargs.setdefault("color", "C7")
        kwargs.setdefault("marker", "v")
        kwargs.setdefault("markerfacecolor", "none")
        self.filtered_data = pd.DataFrame(
            {'voltage': voltage, 'current': current})
        self.add_to_both(self.ax1.plot, self.ax2.plot,
                         voltage, current, *args, **kwargs)

    def add_smoothed_data(self, voltage, current, *args, **kwargs):
        kwargs.setdefault("label", "Smoothed Data")
        kwargs.setdefault("color", "C8")
        kwargs.setdefault("marker", "o")
        kwargs.setdefault("markerfacecolor", "none")
        self.smoothed_data = pd.DataFrame(
            {'voltage': voltage, 'current': current})
        self.add_to_both(self.ax1.plot, self.ax2.plot,
                         voltage, current, *args, **kwargs)


class LinearSemilogyDoubleCanvasSingleProbeLangmuir(LinearSemilogyDoubleCanvas):
    def __init__(self, master=None, cnf=None, saveas="figures.png", sappends=["_linear", "_semilogy"], n=2, sharex=True, **kwargs):
        super().__init__(master, cnf, saveas, sappends, n, sharex, **kwargs)

        self.raw_data = None
        self.filtered_data = None
        self.deleted_points = None
        self.smoothed_data = None

        self.vf = None
        self.vs = None

        self.electron_retarding_fits = []
        self.electron_retarding_fills = []

        self.electron_saturation_fit = None
        self.electron_saturation_fill = None

        self.ion_saturation_fit = None
        self.ion_saturation_fill = None

    def set_xlabel_linear(self, label=None, *args, **kwargs):
        label = r"$V_{bias}\ [V]$" if label is None else label
        self.ax1.set_xlabel(label)

    def set_xlabel_semilogy(self, label=None, *args, **kwargs):
        label = r"$V_{bias}\ [V]$" if label is None else label
        self.ax2.set_xlabel(label)

    def set_xlabel(self, label_linear=None, label_semilogy=None, *args, **kwargs):
        self.set_xlabel_linear(label=label_linear)
        self.set_xlabel_semilogy(label=label_semilogy)

    def set_ylabel_linear(self, label=None, *args, **kwargs):
        label = r"$I_{probe}\ [A]$" if label is None else label
        self.ax1.set_ylabel(label)

    def set_ylabel_semilogy(self, label=None, *args, **kwargs):
        label = r"$I_{e}\ [A]$" if label is None else label
        self.ax2.set_ylabel(label)

    def set_ylabel(self, label_linear=None, label_semilogy=None, *args, **kwargs):
        self.set_ylabel_linear(label=label_linear)
        self.set_ylabel_semilogy(label=label_semilogy)

    def add_probe_trace(self, voltage, current, *args, **kwargs):
        kwargs.setdefault("label", "Experimental Data")
        kwargs.setdefault("color", "C0")
        kwargs.setdefault("marker", "^")
        kwargs.setdefault("markerfacecolor", "none")
        # save data
        self.probe_trace = pd.DataFrame(
            {'voltage': voltage, 'current': current})
        self.add_plot(self.ax1.plot,
                      voltage, current, *args, **kwargs)
        self.set_xlabel_linear()
        self.set_ylabel_linear()

    def add_electron_trace(self, voltage, current, *args, **kwargs):
        kwargs.setdefault("label", "Experimental Data")
        kwargs.setdefault("color", "C0")
        kwargs.setdefault("marker", "^")
        kwargs.setdefault("markerfacecolor", "none")
        # save data
        self.electron_trace = pd.DataFrame(
            {'voltage': voltage, 'current': current})
        self.add_plot(self.ax2.plot,
                      voltage, current, *args, **kwargs)
        self.set_xlabel_semilogy()
        self.set_ylabel_semilogy()

    def add_floating_potential(self, V_f, *args, **kwargs):
        kwargs.setdefault("label", rf"$V_{{f}} = {V_f:.2f}V$")
        kwargs.setdefault("color", "C2")
        self.V_f = V_f
        self.add_to_both(self.ax1.axvline, self.ax2.axvline,
                         V_f, *args, **kwargs)

    def add_plasma_potential(self, V_s, *args, **kwargs):
        kwargs.setdefault("label", rf"$V_{{s}} = {V_s:.2f}V$")
        kwargs.setdefault("color", "C4")
        self.V_s = V_s
        self.add_to_both(self.ax1.axvline, self.ax2.axvline,
                         V_s, *args, **kwargs)

    def add_electron_retarding_fit(self, voltage, current, KT_e, *args, **kwargs):
        kwargs.setdefault("label", rf"$KT_{{e}} = {KT_e:.2f}eV$")
        kwargs.setdefault("color", "C3")
        kwargs.setdefault("linestyle", "--")
        self.electron_retarding_fits.append(
            pd.DataFrame({'voltage': voltage, 'current': current}))
        self.add_plot(self.ax2.plot,
                      voltage, current, *args, **kwargs)

    def add_ion_saturation_fit(self, voltage, current, I_is, *args, **kwargs):
        kwargs.setdefault("label", rf"$I_{{is}} = {I_is:.2e}A$")
        kwargs.setdefault("color", "C6")
        kwargs.setdefault("linestyle", "--")
        self.ion_saturation_fit = pd.DataFrame(
            {'voltage': voltage, 'current': current})
        self.add_plot(self.ax1.plot,
                      voltage, current, *args, **kwargs)

    def add_electron_saturation_fit(self, voltage, current, I_es, *args, **kwargs):
        kwargs.setdefault("label", rf"$I_{{es}} = {I_es:.2e}A$")
        kwargs.setdefault("color", "C5")
        kwargs.setdefault("linestyle", "--")
        self.electron_saturation_fit = pd.DataFrame(
            {'voltage': voltage, 'current': current})
        self.add_plot(self.ax2.plot,
                      voltage, current, *args, **kwargs)

    def add_electron_retarding_fill(self, xstart, xstop, *args, **kwargs):
        kwargs.setdefault("color", "C3")
        kwargs.setdefault("alpha", 0.3)
        self.electron_retarding_fills.append([xstart, xstop])
        self.add_to_both(self.ax1.axvspan, self.ax2.axvspan,
                         xstart, xstop, *args, **kwargs)

    def add_electron_saturation_fill(self, xstart, xstop, *args, **kwargs):
        kwargs.setdefault("color", "C5")
        kwargs.setdefault("alpha", 0.3)
        self.electron_saturation_fill = [xstart, xstop]
        self.add_to_both(self.ax1.axvspan, self.ax2.axvspan,
                         xstart, xstop, *args, **kwargs)

    def add_ion_saturation_fill(self, xstart, xstop, *args, **kwargs):
        kwargs.setdefault("color", "C6")
        kwargs.setdefault("alpha", 0.3)
        self.ion_saturation_fill = [xstart, xstop]
        self.add_to_both(self.ax1.axvspan, self.ax2.axvspan,
                         xstart, xstop, *args, **kwargs)

    def make_plot(self, solver):
        app = self
        # make xdomain for fit plotting
        xdomain = [np.min(solver.data.voltage), np.max(solver.data.voltage)]

        # solve for KT_e fit data
        KT_e_fit = solver.results["KT_e"]["other"]["fit"]
        voltage_KT_e_fit = KT_e_fit.xrange(domain=xdomain)
        current_KT_e_fit = KT_e_fit(voltage_KT_e_fit)
        # solve for I_es fit data
        I_es_fit = solver.results["I_es"]["other"]["fit"]
        voltage_I_es_fit = I_es_fit.xrange(domain=xdomain)
        current_I_es_fit = I_es_fit(voltage_I_es_fit)

        # solve for I_is fit data
        I_is_fit = solver.results["I_is"]["other"]["fit"]
        voltage_I_is_fit = I_is_fit.xrange(domain=xdomain)
        current_I_is_fit = I_is_fit(voltage_I_is_fit)

        # Make Plots ###
        # add probe trace
        app.add_probe_trace(solver.data.voltage, solver.data.current)
        # add electron current
        app.add_electron_trace(solver.data.voltage, solver.data.current_e)
        # mark deleted points
        app.add_deleted_points(solver.deleted_data.voltage,
                               solver.deleted_data.current)

        # Add to Plasma Properties to Plots
        app.add_floating_potential(solver.results["V_f"]["value"])
        app.add_plasma_potential(solver.results["V_s"]["value"])

        # Electron Retarding fit and fill for region of fit
        app.add_electron_retarding_fit(
            voltage_KT_e_fit, current_KT_e_fit, solver.results["KT_e"]["value"])
        app.add_electron_retarding_fill(*KT_e_fit.poly.domain)

        # Electron Saturation fit and fill for region of fit
        app.add_electron_saturation_fit(
            voltage_I_es_fit, current_I_es_fit, solver.results["I_es"]["value"])
        app.add_electron_saturation_fill(*I_es_fit.poly.domain)

        # Ion Saturation fit and fill for region of fit or domain area
        app.add_ion_saturation_fit(
            voltage_I_is_fit, current_I_is_fit, solver.results["I_is"]["value"],
        )
        app.add_ion_saturation_fill(*I_is_fit.poly.domain)

        # turn on legend
        app.legend()


def other():
    # Make save all button
    # btn_save_all = tk.Button(master=self, text="Save Both and Next",
    #                         command=lambda: save_figures(fig, saveas, root))
    # btn_save_all.pack(side=tk.BOTTOM, expand=1, fill=tk.BOTH)

    if None:
        canvas.mpl_connect(
            "key_press_event", lambda event: print(f"you pressed {event.key}"))
        canvas.mpl_connect("key_press_event", key_press_handler)

        # Make quit button
        button_quit = tk.Button(master=root, text="Quit", command=root.destroy)
        button_quit.pack(side=tk.BOTTOM, expand=1, fill=tk.BOTH)


class SingleProbeLangmuirResultsFrame(tk.Frame):
    def __init__(self, master=None, cnf={}, *args, results=None, **kwargs):
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

        # creat instance
        self._results = results

        # number of properties to display
        grid_positions_list = self.grid_positions(results.keys())

        # loop and create labels to display
        labels = {}
        for k, key in enumerate(results.keys()):
            text = self.results[key]["value"]
            unit = self.results[key]["other"]
            unit = self.default_unit_format(key) if unit is None else unit
            labels[key] = ResultOutput(key, text, unit, self, cnf)
            row = grid_positions_list[k][0]
            col = grid_positions_list[k][1]
            labels[key].grid(row=row, column=col,
                             sticky="NWSE", padx=5, pady=5)

        self.widgets.frames.update(labels)

        self.update_texts(results=self.results)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

    @property
    def results(self):
        return self._results

    @results.setter
    def results(self, val):
        self.update_texts(val)
        self._results = val

    def update_label(self, key, text):
        if key in self.widgets.frames:
            self.widgets.frames[key].update_text(text=text)
        else:
            table = "\n".join(
                [f"{k}\t{v}" for k, v in enumerate(self.widgets.frames)])
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
        elif key == "sheath" or key == "r_p/lambda_De":
            text = "{0:.2e}"
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
        elif key == "sheath" or key == "r_p/lambda_De":
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


class ResultOutput(tk.Frame):
    def __init__(self, key, value=None, unit=None, master=None, cnf=None, *args, latex=True, **kwargs):
        super().__init__(master, cnf, *args, **kwargs)

        # create widgets
        self.widgets = Widgets()

        # create button/label of property name to display
        btn_kwargs = kwargs.get("btn_kwargs", {})
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
        self.widgets.buttons["key"] = btn
        self.widgets.labels["value"] = value_lbl
        self.widgets.labels["unit"] = unit_lbl

        # configure columns same size
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
        input_string = input_string.replace("sheath", "r_p/\u03BB_De")

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


class CombinedDataFrame(tk.Frame):
    def __init__(self, Data, Solver, Canvas, Panel, master=None, cnf=None, *args, **kwargs):
        super().__init__(master, cnf=cnf, *args, **kwargs)
        # get kwargs for individual
        canvas_kwargs = kwargs.pop("canvas_kwargs", {})
        panel_kwargs = kwargs.pop("panel_kwargs", {})
        solver_kwargs = kwargs.pop("solver_kwargs", {})

        # set defaults for canvas
        canvas_kwargs.setdefault("width", 5)
        canvas_kwargs.setdefault("height", 4)

        # set defaults for panel

        # set defaults for solver
        solver_kwargs.setdefault("Data", Data)

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


class LinearSemilogySingleLangmuirCombinedData(CombinedDataFrame):
    def __init__(self, Data: pd.DataFrame, master=None, cnf=None, *args, **kwargs):
        Canvas = LinearSemilogyDoubleCanvasSingleProbeLangmuir
        Panel = SingleProbeLangmuirResultsFrame
        Solver = SingleLangmuirProbeSolver
        super().__init__(Data, Solver, Canvas, Panel, master, cnf=cnf, *args, **kwargs)


class MultipleDataFrame(tk.Frame):
    def __init__(self, num, DataFrame, master=None, cnf=None, *args, **kwargs):
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
