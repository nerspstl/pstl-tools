import tkinter as tk

from pstl.gui.langmuir.control import SingleProbeLangmuirResultsControlFrame
from pstl.gui.langmuir.control import ControlFunctionFit, ControlEntryLabelFrame


def main():
    app = tk.Tk()

    control = SingleProbeLangmuirResultsControlFrame(master=app)
    #control=ControlFunctionFit(master=app)
    #control=ControlEntryLabelFrame(lbl_txt="HELO",master=app)


    control.grid(row=0,column=0,sticky="NSEW")
    control.tkraise()

    app.mainloop()


if __name__ == "__main__":
    main()