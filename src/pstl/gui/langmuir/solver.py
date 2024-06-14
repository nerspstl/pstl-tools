import tkinter as tk
import traceback
from PIL import Image, ImageTk
from matplotlib import style
import matplotlib.pyplot as plt

from pstl.extras.images import pstl_png_path, pstl_ico_path, pstl_16_ico_path, pstl_32_ico_path
from pstl.gui.langmuir import LSSLCD2_setup
from pstl.utls.errors.langmuir import Flagged


def gui_langmuir(settings:dict):
    style.use("bmh")
    plt.rcParams.update({"font.size": 10})

    # initiate app
    app = tk.Tk()
    app.title("PSTL GUI Langmuir")
    app.iconphoto(
        True, 
        ImageTk.PhotoImage(Image.open(pstl_32_ico_path)),
        ImageTk.PhotoImage(Image.open(pstl_16_ico_path))
    )
    
    # Try to run the solver
    try: 
        page = LSSLCD2_setup(settings, master=app)
        # pack it on
        page.pack()
    except Exception as e:
        file = settings["name"]
        print("\nFAILED in gui_langmuir: ",file,"\n")
        print(e)
        traceback.print_exc()
        #with open("/home/tyjoto/janus/temp/fail.tab") as f:
        #    f.write(file+"\n")
        pass
    except:
        file = settings["name"]
        print("\nFAILED in gui_langmuir: ",file,"\n")
        traceback.print_exc()
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
        def raise_flagged(app,msg=""):
            app.destroy()
            #print("FLAGGED: ",msg)
            raise Flagged(msg)
        # close button
        btn = tk.Button(app,text="Close App",command=app.destroy)
        btn.pack()

        # flag button
        flag_str = repr("{0}".format(str(settings.get("name","Unknown"))))
        btn_flag = tk.Button(app,text="Flag",command=lambda: raise_flagged(app, flag_str))
        btn_flag.pack()
        try:
            # run loop
            app.mainloop()
        except Flagged as e:
            app.destroy()
            raise Flagged
