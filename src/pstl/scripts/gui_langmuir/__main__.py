import tkinter as tk
import argparse
import json
import traceback

import numpy as np
import pandas as pd
from matplotlib import style
from PIL import Image, ImageTk

from pstl.gui.langmuir.canvas import LinearSemilogyCanvas, LinearSemilogyDoubleCanvas, LinearSemilogyDoubleCanvasSingleProbeLangmuir
from pstl.gui.langmuir import LinearSemilogyDoubleCanvasSingleProbeLangmuir as Canvas
from pstl.gui.langmuir import LinearSemilogySingleLangmuirCombinedData as LSSLCD
from pstl.gui.langmuir import LinearSemilogySingleLangmuirCombinedData2 as LSSLCD2
from pstl.gui.langmuir import LSSLCD_setup
from pstl.gui.langmuir import LSSLCD2_setup

from pstl.gui.langmuir import SingleProbeLangmuirResultsFrame as Panel
from pstl.gui.langmuir import SingleProbeLangmuirResultsFrame
from pstl.gui.langmuir import gui_langmuir

from pstl.utls.plasmas import XenonPlasma, ArgonPlasma, NeonPlasma, KryptonPlasma, Plasma
from pstl.utls.plasmas import setup as plasma_setup
from pstl.utls.errors.plasmas import FailedPlasmaClassBuild
from pstl.utls.errors.langmuir import Flagged

from pstl.utls.data import setup as data_setup

from pstl.extras.images import pstl_png_path, pstl_ico_path, pstl_16_ico_path, pstl_32_ico_path

from pstl.diagnostics.probes.langmuir.single import SphericalSingleProbeLangmuir as SSPL
from pstl.diagnostics.probes.langmuir.single import CylindericalSingleProbeLangmuir as CSPL
from pstl.diagnostics.probes.langmuir.single import PlanarSingleProbeLangmuir as PSPL
from pstl.diagnostics.probes.langmuir.single import setup as probe_setup

from pstl.diagnostics.probes.langmuir.single.analysis.solvers.solvers import SingleLangmuirProbeSolver as SLPS
from pstl.diagnostics.probes.langmuir.single.analysis.solvers.solvers import SingleLangmuirProbeSolver as SLPS

#style.use("bmh")

parser = argparse.ArgumentParser(
                    prog='GUI Langmuir',
                    description='Anaylsis on IV-trace',
                    epilog='Text at the bottom of help')
parser.add_argument('-o','--sname', help="save name for plots", default="outpng.png")
parser.add_argument('-f','--fname', help="file name to read in", default="lang_data.txt")
parser.add_argument('-c','--convergence', help="convergence rmse threshold for electron retarding fit", default=25,type=float)
parser.add_argument('-n','--negative', help="if electron current is negative",action="store_true")
parser.add_argument('-s','--delimiter', help="sets sep or delimiter of tabular data file, default is ',' use '\t' for tab",default=",",type=str)
parser.add_argument('-g','--neutral_gas', help="define gas composition i.e. Xenon, Argon, Neon",default="",type=str)
parser.add_argument('-p','--probe', help="define probe shape diameter length* where *only for spherical",nargs="*")

#parser.add_argument('-O','--output_settings_file', help="location of output results defining json file",type=str)
parser.add_argument('-G',   '--neutral_gas_settings_file',  help="location of neutral gas (and plasma) defining json file",  type=str)
parser.add_argument('-P',   '--probe_settings_file',        help="location of probe defining json file",                     type=str)
parser.add_argument('-D',   '--data_settings_file',         help="location of data defining json file",                      type=str)
parser.add_argument('-L',   '--solver_settings_file',       help="location of solver settings json file",                    type=str)

parser.add_argument('-S',   '--settings_file',              help="location of whole gui settings json file",                 type=str)
args = parser.parse_args()



available_shapes = {
    0: ['cylinderical', 'cylindrical'],
    1: ['spherical'],
    2: ['planar', 'planer'],
}

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

    
def choose_probe_type():
    shape = args.probe[0]
    shape = shape.lower()
    if shape in available_shapes[0]: #"cylinderical"
        Probe = CSPL
    elif shape in available_shapes[1]:  #"spherical":
        Probe = SSPL
    elif shape in available_shapes[2]:  #"planer"
        Probe = PSPL
    else:
        raise ValueError("First argument of probe does not match available shapes '%s'"%(shape))
    other_args = args.probe[1:]
    new_args:list[None|int|float] = [None]*len(other_args)
    for k, value in enumerate(other_args):
        try:
            new_args[k] = float(value)  
        except:
            raise ValueError("Argument %i of Probe is not a float %s"%(k+1,other_args[k]))
    tuple_args: tuple[float] = tuple(new_args)  # type: ignore

    probe = Probe(*tuple_args) # type: ignore
    return probe

    

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
            print("'%s' does not match known options."%(string))
            raise FailedPlasmaClassBuild()

    return plasma

def gui_langmuir_from_file(settings_file:str):
    # initiate app
    app = tk.Tk()
    app.title("PSTL GUI Langmuir")

    with open(settings_file) as f: 
        settings = json.load(f)
    page = LSSLCD2_setup(settings, master=app)

    # pack it on
    page.pack()

    # close button
    btn = tk.Button(app,text="Close App",command=app.destroy)
    btn.pack()

    # run loop
    app.mainloop()
    



def main():
    if args.settings_file is None:
        if args.probe_settings_file is None and args.probe is None:
            raise ValueError("either probe_settings_file or probe must be defined")

        if args.neutral_gas_settings_file is None and args.plasma is None:
            raise ValueError("either neutral_gas_settings_file or plasma must be defined")
        
        if args.data_settings_file is None and args.fname is None:
            raise ValueError("either data_settings_file or fname must be defined")

    
    # load settings
    if args.settings_file is None:
        settings = get_settings()

        # probe settings
        if args.probe_settings_file is None: 
            probe = choose_probe_type()         
        else:
            with open(args.probe_settings_file) as f: 
                probe_settings = json.load(f)
            probe = probe_setup(probe_settings)

        # plasma settings
        if args.neutral_gas_settings_file is None: 
            plasma = choose_plasma_type() if args.gas is None else set_plasma_type(args.gas)
        else:
            with open(args.neutral_gas_settings_file) as f: 
                plasma_settings = json.load(f)
            plasma = plasma_setup(plasma_settings)
        
        # data settings
        if args.data_settings_file is None: 
            try:
                data = pd.read_csv(args.fname)
            except:
                raise ValueError("fname unable to load, must specify data_file or fix fname")
        else:
            with open(args.data_settings_file) as f:
                data_settings = json.load(f)
            data = data_setup(data_settings)
        # if negative
        if args.negative:
            data.iloc[:, 1] *= -1
        else:
            data.iloc[:, 1] *= 1

        # solver settings
        if args.solver_settings_file is None: 
            # solver args
            solver_args = {
                #'plasma': XenonPlasma(),
                'plasma': plasma,
                #'probe': SSPL(0.010, 0.0079),
                'probe': probe,
                'data': data,                # use -f <file-path\file-name.csv>
                }
            # create page
            # create combined langmuir frame that sits on one page
            print(solver_args,"\n",settings)
            #page = LSSLCD(**solver_args,master=app,**settings)
        else:
            with open(args.solver_settings_file) as f:
                solver_settings = json.load(f)
            solver = data_setup(solver_settings)
            settings["solver"] = solver
            #page = LSSLCD2_setup(settings, master=app)

    else:
        print("All settings present")
        with open(args.settings_file) as f: 
            settings = json.load(f)
    try:
        gui_langmuir(settings)
    except Flagged as e:
        print(e)

def olde_main(settings, app):
    # initiate app
    app = tk.Tk()
    app.title("PSTL GUI Langmuir")
    #pstl_png = tk.PhotoImage(file=pstl_png_path)
    app.iconphoto(
        True, 
        ImageTk.PhotoImage(Image.open(pstl_32_ico_path)),
        ImageTk.PhotoImage(Image.open(pstl_16_ico_path))
    )

    # Indented 1
    try:
        page = LSSLCD2_setup(settings, master=app)
    except:
        traceback.print_exc()
        file = settings["name"]+".tab"
        print("\nFAILED: ",file,"\n")
        #with open("/home/tyjoto/janus/temp/fail.tab") as f:
        #    f.write(file+"\n")

        pass
    else:
        def save_n_close():
            page.save_n_close()
            app.destroy()
        # save and close
        btn_savenclose = tk.Button(app,text="Save and Close app", command=save_n_close)
        btn_savenclose.pack()
    finally:
        # close button
        btn = tk.Button(app,text="Close App",command=app.destroy)
        btn.pack()

        # flag button
        btn_flag = tk.Button(app,text="Flag",command=lambda: print(repr("Flagged: {0}".format(str(settings.get("name","Unknown"))))))
        btn_flag.pack()

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
    solver.solve()

    # make plots of solved for plasma parameters
    canvas.make_plot(solver)

    # pass data to results panel
    panel.results = solver.results

    # run mainloop
    app.mainloop()


if __name__ == "__main__":
    main()
