import tkinter as tk

from PIL import Image, ImageTk

from pstl.extras.images import pstl_ico_path, pstl_png_path


def main():
    root = tk.Tk()
    img_16 = tk.PhotoImage(file="/home/tyjoto/temp/tkinter-icons/icon-16.png")
    img_32 = tk.PhotoImage(file="/home/tyjoto/temp/tkinter-icons/icon-32.png")
    #img = tk.PhotoImage(file=pstl_ico_path)
    #img = tk.PhotoImage(file=pstl_png_path)
    #root.tk.call('wm', 'iconphoto', root._w, img)

    img = Image.open(pstl_ico_path)
    img.save('/home/tyjoto/github-work/pstl-tools/src/pstl/extras/images/pstl-16.ico',format = 'ICO', sizes=[(16,16)])
    img.save('/home/tyjoto/github-work/pstl-tools/src/pstl/extras/images/pstl-32.ico',format = 'ICO', sizes=[(32,32)])
    tkimage_16 = ImageTk.PhotoImage(Image.open("/home/tyjoto/github-work/pstl-tools/src/pstl/extras/images/pstl-16.ico"))
    tkimage_32 = ImageTk.PhotoImage(Image.open("/home/tyjoto/github-work/pstl-tools/src/pstl/extras/images/pstl-32.ico"))
    #label=tk.Label(root,image=tkimage)

    #label.pack()
    root.iconphoto(False,tkimage_32, img_16)
    root.mainloop()

if __name__ == "__main__":
    main()