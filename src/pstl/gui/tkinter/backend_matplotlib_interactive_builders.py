import copy
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from matplotlib import pyplot as plt
from matplotlib.widgets import Button
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk  # type: ignore
import tkinter as tk
from tkinter import Frame

from pstl.utls.verify import verify_type
from pstl.utls.helpers import count_placeholders
from backend_matplotlib_interactive_cursor import AnnotatedCursor


class ButtonBaseBuilder:
    def __init__(self, ax, ax_plot_func=None):
        self.name = "Base Builder"
        self.ax = ax
        self._history = []
        self._originals = {'artists': len(ax.artists), 'collections': len(ax.collections), 'images': len(
            ax.images), 'lines': len(ax.lines), 'patches': len(ax.patches), 'texts': len(ax.texts)}

        # adds connetion to button pressed events
        self.cid = None
        #ax.figure.canvas.mpl_connect('button_press_event', self)

    def disconnect(self, val):
        self.ax.figure.canvas.mpl_disconnect(self.cid)

    def connect(self, val):
        self.cid = self.ax.figure.canvas.mpl_connect(
            'button_press_event', self)


class VerticalLineBuilder(ButtonBaseBuilder):
    def __init__(self, ax,
                 ax_plot_func=None,
                 control_panel=False, tk_home=None,
                 ax_plot_kwargs: dict = {}, axvline_kwargs: dict = {},
                 **kwargs):
        ButtonBaseBuilder.__init__(self, ax, ax_plot_func)
        self.name = "Vertical Line Builder"
        self.xs = []
        self.label_format = kwargs.get('label_format', None)
        self._original_number_of_plots = self._originals['lines']
        self._original_index = self._original_number_of_plots - 1
        self._xs_counter = 0
        self.ax_plot_func = ax_plot_func if ax_plot_func is not None else ax.plot
        self.ax_plot_kwargs = ax_plot_kwargs
        self.axvline_kwargs = axvline_kwargs
        self.control_panel = None
        self.tk_home = tk_home

        # If tk_home is a not None, then checks it is correct type, If pass:
        # makes a canvas to edit on tkinter frame/window
        if self.tk_home is not None:
            verify_type(self.tk_home, (tk.Frame, tk.Tk), 'tk_home')
            self.canvas = MatplotlibCanvasFrameTk(self.ax, self.tk_home)

        # if control_panel is True, make the control panel
        # if tk_home is a tk.Frame or tk.Tk object, then tkinter will be used, else matplotlib figure
        if control_panel:
            self._make_control_panel()

    def __call__(self, event):
        if event.inaxes != self.ax.axes:
            return
        self.add_vertical_line(event.xdata)

    def add_vertical_line(self, val):
        self.xs.append(val)
        axvline_kwargs = copy.deepcopy(self.axvline_kwargs)
        # add color default if not given per added line
        axvline_kwargs['color'] = axvline_kwargs.get(
            'color', "C"+str(self._xs_counter+self._original_number_of_plots))
        # check if label needs arguments
        label = axvline_kwargs.get('label', None)
        if label is not None:
            num_ph = count_placeholders(label)
            if num_ph != 0:
                label = label.format(val)
        axvline_kwargs['label'] = label
        self.ax.axvline(val, **axvline_kwargs)
        self.ax.figure.canvas.draw()
        self._xs_counter += 1

    def clear_lines(self):
        num_of_lines = len(self.ax.lines)
        max_index_of_lines = num_of_lines - 1
        for index in range(max_index_of_lines, self._original_index, -1):
            line = self.ax.lines[index]
            line.remove()
        self.xs = []
        self._xs_counter = 0
        self.ax.figure.canvas.draw()

    def undo(self):
        if len(self.xs) == 0:
            print("Nothing to undo")
        else:
            self.ax.lines[-1].remove()
            self._history.append(self.xs.pop())
            self._xs_counter -= 1
            self.ax.figure.canvas.draw()

    def redo(self):
        if len(self._history) == 0:
            print("Nothing to be redo")
        else:
            replot = self._history.pop()
            self.add_vertical_line(replot)

    def clear(self):
        self.clear_lines()

    def _make_control_panel(self):

        if self.tk_home is not None:  # tk control panel
            self.control_panel = VerticalLineControlPanelTk(
                self.tk_home, worker=self)  # type: ignore

        else:  # matplotlib control panel
            self.control_panel = plt.figure(
                FigureClass=VerticalLineControlPanelMatplotlib, worker=self)


class VerticalLineControlPanelMatplotlib(Figure):
    def __init__(self,  *args, worker=VerticalLineBuilder, **kwargs):
        Figure.__init__(self, *args, **kwargs)

        # make and place disconnect button
        btn_disconnect = Button(self.add_axes([0.1, 0.9, 0.15, 0.04]),
                                'disconnect', hovercolor='0.975')  # type: ignore
        btn_disconnect.on_clicked(worker.disconnect)
        # make and place connect button
        btn_connect = Button(self.add_axes([0.1, 0.8, 0.15, 0.04]),
                             'connect', hovercolor='0.975')  # type: ignore
        btn_connect.on_clicked(worker.connect)
        # make and place clear button
        btn_clear = Button(self.add_axes([0.1, 0.7, 0.15, 0.04]),
                           'clear', hovercolor='0.975')  # type: ignore
        btn_clear.on_clicked(worker.clear)

        self.buttons = [btn_disconnect, btn_connect, btn_clear]


class VerticalLineControlPanelTk(Frame):
    def __init__(self, root, *args, worker=VerticalLineBuilder, **kwargs):
        Frame.__init__(self, root, *args, **kwargs)

        # put Frame in root Frame
        self.grid(row=0, column=0)

        # make Label title
        title = tk.StringVar()
        title.set("Control Panel:\nVeritcal Line Builder")
        lbl_title = tk.Label(
            self, textvariable=title,
        )
        # make buttons
        btn_disconnect = tk.Button(
            self, text='Disconnect', command=lambda: worker.disconnect(None))  # type: ignore
        btn_connect = tk.Button(
            self, text='Connect', command=lambda: worker.connect(None))  # type: ignore
        btn_clear = tk.Button(self, text='Clear',  # type: ignore
                              command=lambda: worker.clear())  # type: ignore
        btn_undo = tk.Button(
            self, text="Undo", command=lambda: worker.undo())  # type: ignore
        btn_redo = tk.Button(
            self, text="Redo", command=lambda: worker.redo())  # type: ignore

        # pack label "Control Panel" into this Frame
        lbl_title.grid(row=0, column=0, columnspan=3, pady=10)
        # pack buttons into this frame
        btn_undo.grid(row=1, column=0, sticky="NSWE")
        btn_redo.grid(row=1, column=1, sticky="NSWE")
        btn_connect.grid(row=2, column=0, columnspan=2, sticky="NSWE")
        btn_disconnect.grid(row=3, column=0, columnspan=2, sticky="NSWE")
        btn_clear.grid(row=4, column=0, columnspan=2, sticky="NSWE")

        self.widgets = {'labels': {'title': {'object': lbl_title, 'var': title}},
                        'buttons': {'undo': btn_undo, 'redo': btn_redo,
                                    'connect': btn_connect, 'disconnect': btn_disconnect, 'clear': btn_clear},
                        'check_buttons': {}
                        }


class MatplotlibCanvasFrameTk(Frame):
    def __init__(self, worker, root, *args, **kwargs):
        Frame.__init__(self, root, *args, **kwargs)
        self.grid(row=0, column=1)
        self.ax = worker

        # Create the Matplotlib canvas
        self.canvas = FigureCanvasTkAgg(
            self.ax.figure, master=self)
        self.canvas.draw()
        self.widget = self.canvas.get_tk_widget()
        self.widget.pack(
            side=tk.TOP, fill=tk.BOTH, expand=1)
        # pack_toolbar=False will make it easier to use a layout manager later on.
        self.toolbar = NavigationToolbar2Tk(
            self.canvas, self, pack_toolbar=True)
        self.toolbar.update()


class FloatingPotentialBuilder(VerticalLineBuilder):
    def __init__(self, ax, ax_data=None, ax_plot_func=None, control_panel=False, tk_home=None,
                 ax_plot_kwargs: dict = {}, axvline_kwargs: dict = {}, annotated_cursor_kwargs: dict = {},
                 **kwargs):
        axvline_kwargs['label'] = axvline_kwargs.get(
            'label', r"$V_{{f}}$ = {0:.2f}V")
        VerticalLineBuilder.__init__(
            self, ax, ax_plot_func, control_panel, tk_home, ax_plot_kwargs, axvline_kwargs)
        self.ax_data = ax.lines[0] if ax_data is None else ax_data
        # default settings for annotated cursor kwargs
        annotated_cursor_kwargs['ax'] = annotated_cursor_kwargs.get('ax', ax)
        annotated_cursor_kwargs['useblit'] = annotated_cursor_kwargs.get(
            'useblit', True)
        annotated_cursor_kwargs['color'] = annotated_cursor_kwargs.get(
            'color', 'black')
        annotated_cursor_kwargs['linestyle'] = annotated_cursor_kwargs.get(
            'linestyle', '--')
        annotated_cursor_kwargs['linewidth'] = annotated_cursor_kwargs.get(
            'linewidth', 0.8)
        annotated_cursor_kwargs['numberformat'] = annotated_cursor_kwargs.get(
            'numberformat', "{0:.2f}\n{1:.2f}")
        self.cursor = AnnotatedCursor(self.ax_data, **annotated_cursor_kwargs)

        if control_panel:
            # add RadioButton for Legend
            self.control_panel.widgets['labels']['title']['var'].set(
                "Control Panel:\nFloating Potential")
            self._update_control_panel()

    def legend(self):  # , var: bool = True):
        var = self.control_panel.widgets['check_buttons']['legend']['var'].get(
        )
        if var:  # True
            self.ax.legend()
            self.ax.figure.canvas.draw()
        else:
            self.ax.get_legend().remove()
            self.ax.figure.canvas.draw()

    def _update_control_panel(self):
        frame = self.control_panel
        var = tk.BooleanVar()
        cbtn_legend = tk.Checkbutton(
            frame, text='Legend',
            variable=var,
            onvalue=True,
            offvalue=False,
            command=self.legend)
        self.control_panel.widgets['check_buttons']['legend'] = {
            'object': cbtn_legend, 'var': var}
        cbtn_legend.grid(row=5, column=0, columnspan=2, sticky="NWSE")
