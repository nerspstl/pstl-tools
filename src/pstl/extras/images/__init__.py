import os 
import tkinter as tk

from PIL import ImageTk, Image

path = os.path.dirname(__file__)

pstl_ico_path = os.path.join(path, "pstl.ico")
pstl_png_path = os.path.join(path, "pstl.png")
pstl_16_ico_path = os.path.join(path, "pstl-16.ico")
pstl_32_ico_path = os.path.join(path, "pstl-32.ico")

#pstl_png = tk.PhotoImage(file=pstl_png_path)

pstl_ico = ImageTk.PhotoImage(Image.open(pstl_ico_path))
pstl_16_ico = ImageTk.PhotoImage(Image.open(pstl_16_ico_path))
pstl_32_ico = ImageTk.PhotoImage(Image.open(pstl_32_ico_path))
pstl_png = ImageTk.PhotoImage(Image.open(pstl_png_path))