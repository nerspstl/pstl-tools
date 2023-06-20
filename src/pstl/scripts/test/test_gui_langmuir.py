import tkinter as tk
import argparse

import numpy as np
import pandas as pd
from matplotlib import style

from pstl.gui.langmuir import LinearSemilogyCanvas, LinearSemilogyDoubleCanvas, LinearSemilogyDoubleCanvasSingleProbeLangmuir
from pstl.gui.langmuir import LinearSemilogyDoubleCanvasSingleProbeLangmuir as Canvas
from pstl.gui.langmuir import SingleProbeLangmuirResultsFrame as Panel
from pstl.gui.langmuir import SingleProbeLangmuirResultsFrame
from pstl.gui.langmuir import LinearSemilogySingleLangmuirCombinedData as LSSLCD

from pstl.utls.plasmas import XenonPlasma, ArgonPlasma
from pstl.diagnostics.probes.langmuir.single import SphericalSingleProbeLangmuir as SSPL
from pstl.diagnostics.probes.langmuir.single import CylindericalSingleProbeLangmuir as CSPL
from pstl.diagnostics.probes.langmuir.single.analysis.solver import SingleLangmuirProbeSolver as SLPS

style.use("bmh")

parser = argparse.ArgumentParser(
                    prog='GUI Langmuir',
                    description='Anaylsis on IV-trace',
                    epilog='Text at the bottom of help')
parser.add_argument('-s','--sname', help="save name for plots", default="outpng.png")
parser.add_argument('-f','--fname', help="file name to read in", default="lang_data.txt")
args = parser.parse_args()

def old_main():
    x = np.linspace(-.2, .2, 9)
    y = x*.2

    root = tk.Tk()
    a = LinearSemilogyDoubleCanvasSingleProbeLangmuir(root, width=6, height=5)
    results = None
    b = SingleProbeLangmuirResultsFrame(root, results=results)
    a.add_raw_data(x, y)
    a.add_floating_potential(.2, color="r")
    a.add_electron_retarding_fill(-0.1, .1, color="black", alpha=0.1)
    a.legend()
    # a = LinearSemilogyCanvas(root)
    # a.widgets.frames['semilogy'].ax.relim()
    # a.widgets.frames['semilogy'].ax.autoscale()
    # a.widgets.frames['semilogy'].set_fig_to_semilogy()
    # a.ax2.update_from(a.ax1)
    # a.widgets.frames['semilogy'].fig.canvas.draw()
    # a.widgets.frames['linear'].fig.canvas.draw()

    # pack
    a.grid(row=0, column=1)
    b.grid(row=0, column=0)

    # run loop
    root.mainloop()


def get_lang_data():
    filename = args.fname
    data = pd.read_csv(filename, names=["voltage", "current"])
    data.iloc[:, 1] *= 1
    return data


def main():
    # initiate app
    app = tk.Tk()

    # create page
    page = tk.Frame(app)
    page.pack()

    # create Canvas
    canvas = Canvas(page, saveas=args.sname, width=4, height=3)
    canvas.grid(row=0, column=1, sticky="NSWE", rowspan=2)

    # create Panel
    panel = Panel(page)
    panel.grid(row=0, column=0, sticky="N")

    data = get_lang_data()
    # data = get_test_data()

    # probe = CSPL(2.4e-3, 10e-3)
    probe = SSPL(0.010, 0.0079)
    probe_smaller = SSPL(0.010, 0.009)
    rox_probe = CSPL(0.76e-3,2.54e-3)
    plasma = XenonPlasma()
    # plasma = ArgonPlasma()

    solver = SLPS(plasma, rox_probe, data)

    # pre process data
    solver.preprocess()

    # solve for data
    solver.find_plasma_properties()

    # make plots of solved for plasma parameters
    canvas.make_plot(solver)

    # pass data to results panel
    panel.results = solver.results

    # run mainloop
    app.mainloop()


if __name__ == "__main__":
    main()
