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

from pstl.utls.plasmas import XenonPlasma, ArgonPlasma, NeonPlasma, Plasma
from pstl.utls.errors.plasmas import FailedPlasmaClassBuild

from pstl.diagnostics.probes.langmuir.single import SphericalSingleProbeLangmuir as SSPL
from pstl.diagnostics.probes.langmuir.single import CylindericalSingleProbeLangmuir as CSPL
from pstl.diagnostics.probes.langmuir.single import PlanarSingleProbeLangmuir as PSPL
from pstl.diagnostics.probes.langmuir.single.analysis.solver import SingleLangmuirProbeSolver as SLPS

style.use("bmh")

parser = argparse.ArgumentParser(
                    prog='GUI Langmuir',
                    description='Anaylsis on IV-trace',
                    epilog='Text at the bottom of help')
parser.add_argument('-s','--sname', help="save name for plots", default="outpng.png")
parser.add_argument('-f','--fname', help="file name to read in", default="lang_data.txt")
parser.add_argument('-c','--convergence', help="convergence rmse threshold for electron retarding fit", default=25,type=float)
parser.add_argument('-n','--negative', help="if electron current is negative",action="store_true")
parser.add_argument('-p','--plasma', help="define plasma composition i.e. Xenon, Argon, Neon",default="",type=str)
parser.add_argument('-d','--delimiter', help="sets delimiter of csv file, default is ',' use '\t' for tab",default=",",type=str)
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
    data = pd.read_csv(filename, names=["voltage", "current"],header=1,delimiter=args.delimiter)
    if args.negative:
        data.iloc[:, 1] *= -1
    else:
        data.iloc[:, 1] *= 1
    return data

def get_settings():
    filename = args.sname # Change this
    thershold_rmse = args.convergence
    # filename (no extentsion) to open
    fname_split = args.fname.split(".")

    # canvas kwargs
    ptype = "png"
    sname = fname_split[0]+"_plot."+ptype
    canvas_kwargs = {
        'saveas': sname,
        'stype': ptype,
        'width': 5,
        'height': 4,
    }

    # panel kwargs
    ftype = "csv"
    fname = fname_split[0]+"_results."+ftype
    panel_kwargs = {
        'fname': fname,
        'ftype': ftype,
    }

    # solver kwargs
    # solver = SLPS(plasma, probe, data)
    solver_kwargs = {
    }


    settings = {
        'canvas_kwargs':canvas_kwargs,
        'panel_kwargs': panel_kwargs,
        'solver_kwargs': solver_kwargs,
    }
    return settings

"""
WLP: Cylinderical Downstream
Diameter: 0.1230 inches -> 0.31242 cm
Length: 0.6105 inches -> 1.55067 cm

PLP: Planer Down stream
Diameter: 0.1570 inches -> 0.39878 cm

NLP: Cylinderial @ Neutral
Diameter: 0.0155 inches -> 0.03937 cm
Lenth: 0.1170 inches -> 0.29718 cm

Farday:
Diameter inner: 0.6925 inches -> 1.175895 cm
Diameter outer: 1.120 inches -> 2.8448 cm
"""
def wlp():
    return CSPL(0.31242e-2,1.55067e-02)
def plp():
    return PSPL(0.39878e-02)
def NLP():
    return CSPL(0.03937e-02,0.29718e-02)
def blp():
    return SSPL(0.010, 0.0079)
def blp_smaller():
    return SSPL(0.010, 0.009) # BLP6
def rox():
    return CSPL(0.76e-3,2.54e-3)

def set_plasma_type(string,*args, **kwargs):
    plasma = None
    while plasma is None:
        plasma = logic_plasma_type(string, *args, **kwargs)
        if plasma is not None:
            break
        else:
            plasma = choose_plasma_type()
            
    return plasma

    
        

def choose_plasma_type():
    string = input("Please enter Xenon, Argon, Neon\nor define using '-p' flag when initializing>>")
    plasma = logic_plasma_type(string)
    return plasma

def logic_plasma_type(string, *args, **kwargs):
    string = string.upper()
    if string == "":
        plasma = choose_plasma_type()
    elif string == "XENON":
        plasma = XenonPlasma(*args, **kwargs)
    elif string == "ARGON":
        plasma = ArgonPlasma(*args, **kwargs)
    elif string == "NEON":
        plasma = NeonPlasma(*args, **kwargs)
    else:
        try:
            plasma = Plasma(*args,**kwargs)
        except:
            print("'%s' does not match known options.")
            raise FailedPlasmaClassBuild()

    return plasma




def main():
    # initiate app
    app = tk.Tk()
    
    # load settings
    settings = get_settings()

    # solver args
    solver_args = {
        #'plasma': XenonPlasma(),
        'plasma': set_plasma_type(args.plasma), # use -p <plasma-string-name>
        #'probe': SSPL(0.010, 0.0079),
        'probe': blp(),
        'data': get_lang_data(),                # use -f <file-path\file-name.csv>
        }

    # create page
    # create combined langmuir frame that sits on one page
    page = LSSLCD(**solver_args,master=app,**settings)
    # pack it on
    page.pack()

    # close button
    btn = tk.Button(app,text="Close App",command=app.destroy)
    btn.pack()

    # run loop
    app.mainloop()
    




def old_main_2():
    # initiate app
    app = tk.Tk()

    # create page
    page = tk.Frame(app)
    page.pack()
    
    # filename (no extentsion) to open
    fname_split = args.fname.split(".")

    # create Canvas
    ptype = "png"
    sname = fname_split[0]+"_plot."+ptype
    #canvas = Canvas(page, saveas=args.sname, width=4, height=3)
    canvas = Canvas(page, saveas=sname, width=5, height=4)
    canvas.grid(row=0, column=1, sticky="NSWE", rowspan=2)

    # create Panel
    ftype = "csv"
    fname = fname_split[0]+"_results."+ftype
    panel = Panel(page,fname=fname,ftype=ftype)
    panel.grid(row=0, column=0, sticky="N")

    data = get_lang_data()
    # data = get_test_data()

    # probe = CSPL(2.4e-3, 10e-3)
    probe = SSPL(0.010, 0.0079)
    probe_smaller = SSPL(0.010, 0.009) # probe 5 (plasma screen)
    rox_probe = CSPL(0.76e-3,2.54e-3)
    plasma = XenonPlasma()
    # plasma = ArgonPlasma()

    solver = SLPS(plasma, probe, data)

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
