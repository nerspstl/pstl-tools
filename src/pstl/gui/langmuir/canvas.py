import tkinter as tk

import pandas as pd
import numpy as np
from scipy.signal import savgol_filter
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk  # type: ignore

from pstl.gui import WidgetOrganizer, Widgets
from pstl.gui.langmuir.results import SaveResults

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
                 cnf={}, *args,
                 fig: Figure | None = None, ax: Axes | None = None,
                 saveas: str = "figure1.png", stype="png",
                 **kwargs):
        super().__init__(master, cnf, *args, fig=fig, ax=ax, **kwargs)

        self.saveas = saveas
        self.args = args
        self.kwargs = kwargs

        # add save default button
        btn = SaveResults(self.save,fname=saveas,ftype=stype,master=self,cnf=cnf)
        self.widgets.frames['save'] = btn
        #    self, text="Save", command=self.save)
        #self.widgets.buttons['save'].pack(
        btn.pack(side=tk.TOP, fill=tk.X, expand=True)
        

    def save(self, **kwargs):#, saveas: str | None = None, **kwargs):
        #if saveas is None:
        #    saveas = self.widgets.frames['save'].get()
        saveas = self.widgets.frames["save"].get()
        self.fig.savefig(saveas, **kwargs)
        print("save to '%s'"%(saveas))


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

class FirstDerivativeSingleProbeLangmuir(MatplotlibCanvasWToolbarSave):
    def __init__(self, master=None, cnf={}, *args, fig: Figure | None = None, ax: Axes | None = None, saveas: str = "first_derivative.png", stype="png", **kwargs):
        kwargs.setdefault("width", 5)
        kwargs.setdefault("height", 4)
        kwargs.setdefault("dpi", 100)
        
        super().__init__(master, cnf, *args, fig=fig, ax=ax, saveas=saveas, stype=stype, **kwargs)

        self._state = False

    def solve(self,solver):

        try:
            voltage = solver.data.voltage
            current = solver.data.current

            win_len = 3
            polyorder = 1

            gradient_1D = np.gradient(current, voltage)
            smoothed_1D = savgol_filter(
                current,
                window_length=win_len,
                polyorder=polyorder)
            smoothed_1D = np.gradient(smoothed_1D, voltage)
            smoothed_1D_savgol = savgol_filter(
                current, 
                window_length=win_len,
                polyorder=polyorder,
                deriv=1
            )
            self.ax.plot(voltage, gradient_1D, "-",label="np.gradient")
            self.ax.plot(voltage, smoothed_1D,"-",label="savgol, then gradiend")
            self.ax.plot(voltage, smoothed_1D_savgol,"-",label="sp.signal.savgol_filter")
            self.ax.legend()
    
        except:
            print("unable to make first derivative plot")
            pass
    
    @property
    def state(self):
        return self._state
    @state.setter
    def state(self, change_to):
        if isinstance(change_to, bool):
            self._state = change_to
        else:
            raise TypeError("Must be a bool")

class LinearSemilogyDoubleCanvas(tk.Frame):
    def __init__(self, master=None, cnf=None, saveas="figures.png", sappends=["_linear", "_semilogy"], n=2, sharex=True, **kwargs):
        width = kwargs.pop("width", 5)
        height = kwargs.pop("height", 4)
        dpi = kwargs.pop("dpi", 100)
        stype = kwargs.pop("stype", "png")
        figure_kw = {'width': width, 'height': height, 'dpi': dpi, 'stype':stype}

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

    def save(self):
        self.save_both()

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

        # make 1der plot show hide buttons
        canvas_1der = FirstDerivativeSingleProbeLangmuir(self,cnf, **kwargs)
        canvas_1der.grid(row=0, column=0, sticky="NWSE")
        self.widgets.frames["1der"] = canvas_1der
        show_hide_btn = tk.Button(self,cnf,text="Show/Hide",command=self.show_hide)
        show_hide_btn.grid(row=2, column=0,columnspan=2,sticky="NSEW")
        self.widgets.frames["linear"].tkraise()
        self.ax3 = canvas_1der.ax
    def show_hide(self):
        canvas_1der = self.widgets.frames["1der"]
        canvas_linear = self.widgets.frames["linear"]
        state = canvas_1der.state
        if state is True: # is showing thus hide
            canvas_linear.tkraise()
            state = False
        elif state is False: # not showing
            canvas_1der.tkraise()
            state = True

        canvas_1der.state = state


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

    def add_semilogy_trace(self, voltage, current, *args, label=None,**kwargs):
        kwargs.setdefault("label", "Experimental Data")
        kwargs.setdefault("color", "C0")
        kwargs.setdefault("marker", "^")
        kwargs.setdefault("markerfacecolor", "none")
        # save data
        #self.electron_trace = pd.DataFrame({'voltage': voltage, 'current': current})
        self.add_plot(self.ax2.plot,
                      voltage, current, *args, **kwargs)
        label = r"$I_{probe}\ [A]$" if label is None else label
        self.set_xlabel_semilogy()
        self.set_ylabel_semilogy(label=label)

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
    def add_1derivative(self, solver):
        self.widgets.frames["1der"].solve(solver)

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

        # add 1der plot
        app.add_1derivative(solver)
    def make_plot_basic(self, solver):
        app = self
        # make xdomain for fit plotting
        xdomain = [np.min(solver.data.voltage), np.max(solver.data.voltage)]

        # Make Plots ###
        # add probe trace
        app.add_probe_trace(solver.data.voltage, solver.data.current)
        # add electron current
        app.add_semilogy_trace(solver.data.voltage, solver.data.current)
        # mark deleted points
        app.add_deleted_points(solver.deleted_data.voltage,
                               solver.deleted_data.current)

        # Add to Plasma Properties to Plots
        #app.add_floating_potential(solver.results["V_f"]["value"])
        #app.add_plasma_potential(solver.results["V_s"]["value"])

        # turn on legend
        app.legend()
        # add 1der plot
        app.add_1derivative(solver)
    
    def clear_plots(self):
        self.ax1.cla()
        self.ax2.cla()
        self.ax3.cla()



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

