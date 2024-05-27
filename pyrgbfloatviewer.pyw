#!/usr/bin/python3.10
# -*- mode: python; Encoding: utf-8; coding: utf-8 -*-
# Last updated: <2024/05/27 09:05:30 +0900>
"""
RGB float viewer

This tool can display and check RGB Float colors.
RGB Float indicates RGB values from 0.0 to 1.0.

Middle Mouse Button : Paste clipboard contents
Ctrl + "+" / "-" : Change font fize
Ctrl+q : Exit

Windows10 x64 22H2 + Python 3.10.10 64bit + tkinter
License : CC0 / Public Domain
Author : mieki256
"""

import tkinter as tk
from tkinter import colorchooser
from tkinter import font
from tkinter import simpledialog
import pyautogui
from pynput import mouse
import re


# number of decimal places
nod = 4

font_name = "Courier New"
# font_name = "Consolas"
font_size = 14
fonts = None

DEF_MSG = "Drag here. Get color"
listener = None
getting = False


class FontChooser(simpledialog.Dialog):
    """Font select dialog"""

    def body(self, master):
        self.title("Font Chooser")
        self.listbox = tk.Listbox(master, width=30, height=25)
        self.listbox.grid(row=0, column=0, sticky="nsew")

        # get font families
        if True:
            # get fixed font
            fonts = sorted(self.get_monospace_fonts())
        else:
            fonts = sorted(font.families())

        # register fontname to Listbox
        for f in fonts:
            self.listbox.insert("end", f)

        self.scrollbar = tk.Scrollbar(master, command=self.listbox.yview)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        self.listbox.config(yscrollcommand=self.scrollbar.set)

        master.grid_rowconfigure(0, weight=1)
        master.grid_columnconfigure(0, weight=1)
        master.grid_columnconfigure(1, weight=0)

        return self.listbox

    def apply(self):
        try:
            self.result = self.listbox.get(self.listbox.curselection())
        except tk.TclError:
            self.result = None

    def get_monospace_fonts(self):
        """Get a list of monospace fonts"""
        global fonts
        if fonts:
            return fonts

        fonts = []
        all_fonts = font.families()
        for fn in all_fonts:
            if fn[0] == "@":
                continue
            if font.Font(family=fn).metrics("fixed"):
                fonts.append(fn)
        return fonts


def get_rgb_float_str(r, g, b):
    """Returns a string described by RGB Float."""
    if nod == 1:
        s = "%.1f, %.1f, %.1f" % (r, g, b)
    elif nod == 2:
        s = "%.2f, %.2f, %.2f" % (r, g, b)
    elif nod == 3:
        s = "%.3f, %.3f, %.3f" % (r, g, b)
    elif nod == 4:
        s = "%.4f, %.4f, %.4f" % (r, g, b)
    elif nod == 5:
        s = "%.5f, %.5f, %.5f" % (r, g, b)
    elif nod == 6:
        s = "%.6f, %.6f, %.6f" % (r, g, b)
    else:
        s = "%f, %f, %f" % (r, g, b)
    return s


def add_rgb_to_text(r, g, b):
    """Add RGB Float string to the end of the text widget."""
    s = get_rgb_float_str(r, g, b)
    txtw.insert(tk.END, "%s,\n" % (s))


def get_line_str(s):
    """Remove characters not associated with RGB floats from the string."""
    s = s.replace("\n", "")
    s = s.translate(str.maketrans({" ": None, "{": None, "}": None}))
    s = s.translate(str.maketrans({"[": None, "]": None}))
    s = s.translate(str.maketrans({"(": None, ")": None}))
    return s


def change_color_panel(r, g, b):
    """Change background color of color display panel based on RGB Float."""
    ri = int(r * 255)
    gi = int(g * 255)
    bi = int(b * 255)
    rgbfloat = get_rgb_float_str(r, g, b)
    rgbint = "%d, %d, %d" % (ri, gi, bi)
    # rgbf_ent.delete(0, tk.END)
    # rgbf_ent.insert(0, "%s" % (rgbfloat))
    # rgb_ent.delete(0, tk.END)
    # rgb_ent.insert(0, "%s" % (rgbint))
    rgbf_str.set(rgbfloat)
    rgb_str.set(rgbint)
    color_preveiw.config(bg="#%02x%02x%02x" % (ri, gi, bi))


def click_middle_button():
    """paste clipboard by middle mouse button is clicked."""
    s = txtw.clipboard_get()
    txtw.insert(tk.INSERT, str(s))


def change_cursor_pos(e):
    root.after(50, get_cursor_pos)


def get_cursor_pos():
    """Processing when the cursor position is changed."""
    pos = txtw.index(tk.INSERT)
    status_var.set("pos=%s" % (pos))
    s = txtw.get("insert linestart", "insert lineend")
    r, g, b = get_rgb_float_values(get_line_str(s.strip()))
    if r is not None:
        change_color_panel(r, g, b)


def get_rgb_float_values(s):
    """Get RGB Float values from a string."""
    m = re.search(r"([01]?\.\d+)\s*,\s*([01]?\.\d+)\s*,\s*([01]?\.\d+)", s)
    if m:
        rs, gs, bs = m.groups()
        r = float(rs)
        g = float(gs)
        b = float(bs)
        if r >= 0.0 and r <= 1.0 and g >= 0.0 and g <= 1.0 and b >= 0.0 and b <= 1.0:
            return (r, g, b)
    return (None, None, None)


def clear_all_text():
    """Clear in text widget."""
    txtw.delete("0.0", tk.END)


def rgb2y(r, g, b):
    return 0.299 * float(r) + 0.587 * float(g) + 0.114 * float(b)


def rgbfloat2rgbint(r, g, b):
    """RGB Float to RGB int."""
    ri = int(float(r) * 255.0)
    gi = int(float(g) * 255.0)
    bi = int(float(b) * 255.0)
    return (ri, gi, bi)


def insert_coloring_line(s):
    """Set background color for one line."""
    r, g, b = get_rgb_float_values(s)
    if r is not None:
        ri, gi, bi = rgbfloat2rgbint(r, g, b)
        y = rgb2y(r, g, b)
        bgcolor = "#%02x%02x%02x" % (ri, gi, bi)
        fgcolor = "#000000" if y > 0.5 else "#ffffff"
        txtw.tag_config(bgcolor, background=bgcolor, foreground=fgcolor)
        txtw.insert(tk.END, f"{s}\n", bgcolor)
    else:
        txtw.insert(tk.END, f"{s}\n")


def coloring(e=None):
    """Set the background color of each row."""
    all_text = txtw.get(0.0, tk.END)
    lines = all_text.split("\n")
    txtw.delete(0.0, tk.END)  # clear all text
    for s in lines:
        insert_coloring_line(s)


def open_color_chooser():
    """Open color choose dialog."""
    old_col = color_preveiw.cget("bg")
    color = colorchooser.askcolor(color=old_col, parent=root)
    if color[0]:
        r, g, b = color[0]
        r = float(int(r)) / 255.0
        g = float(int(g)) / 255.0
        b = float(int(b)) / 255.0
        change_color_panel(r, g, b)
        add_rgb_to_text(r, g, b)


def open_font_chooser():
    """Open font family choose dialog."""
    global font_name
    chooser = FontChooser(root)
    fontname = chooser.result
    if fontname is not None:
        font_name = fontname
        fnt = (font_name, font_size)
        txtw.config(font=fnt)
        rgbf_ent.configure(font=fnt)
        rgb_ent.configure(font=fnt)
        status_var.set("Font : %s" % (font_name))


def set_font_size(fntsize):
    """Set font size."""
    global font_name, font_size
    font_size = fntsize
    if font_size < 6:
        font_size = 6
    txtw.config(font=(font_name, font_size))
    status_var.set("Font size : %d" % (font_size))


def inc_font_size():
    """Increment font size"""
    set_font_size(font_size + 1)


def dec_font_size():
    """Decrement font size"""
    set_font_size(font_size - 1)


def start_get_desktop_color(e):
    """Start getting RGB from desktop."""
    global listener, getting, picker_lbl, rgblbl
    listener = mouse.Listener(on_click=on_click, on_move=on_move)
    listener.start()
    picker_lbl.config(text="Please release on desktop")
    getting = True


def on_move(x, y):
    """Moving mouse cursor"""
    get_rgb_from_mouse_pos(x, y)


def get_rgb_from_mouse_pos(x, y):
    """Get the color of the mouse cursor position"""
    global rgblbl, rgbflbl, collbl
    ri, gi, bi = pyautogui.screenshot().getpixel((x, y))
    rf = float(ri) / 255.0
    gf = float(gi) / 255.0
    bf = float(bi) / 255.0
    change_color_panel(rf, gf, bf)
    return (rf, gf, bf)


def on_click(x, y, button, pressed):
    """Processing when the mouse button is released."""
    global listener, getting, picker_lbl, root
    if button == mouse.Button.left:
        if not pressed:
            # button release
            listener.stop()
            getting = False
            picker_lbl.config(text=DEF_MSG)
            r, g, b = get_rgb_from_mouse_pos(x, y)
            add_rgb_to_text(r, g, b)


# ----------------------------------------
# main

# initialize tkinter
root = tk.Tk()
root.title("RGB Float viewer")
# root.geometry("600x400")

root.attributes("-topmost", True)
root.configure(cursor="arrow")

fnt = font.Font(family=font_name, size=font_size)

color_preveiw = tk.Label(root, text="", borderwidth=1, relief=tk.SOLID, height=5)

rgbfrm = tk.Frame(root)
picker_lbl = tk.Label(
    rgbfrm, text=DEF_MSG, width=25, borderwidth=3, relief=tk.GROOVE, cursor="target"
)
colsel_btn = tk.Button(rgbfrm, text="Choose color", command=open_color_chooser)

rgbf_str = tk.StringVar()
rgb_str = tk.StringVar()
rgbf_lbl = tk.Label(rgbfrm, text="RGB Float")
rgbf_ent = tk.Entry(rgbfrm, font=fnt, textvariable=rgbf_str)
rgb_lbl = tk.Label(rgbfrm, text="RGB")
rgb_ent = tk.Entry(rgbfrm, font=fnt, textvariable=rgb_str)

btnfrm = tk.Frame(root)
fontsel_btn = tk.Button(btnfrm, text="Font", command=open_font_chooser)
fontinc_btn = tk.Button(btnfrm, text="+", command=inc_font_size)
fontdec_btn = tk.Button(btnfrm, text="-", command=dec_font_size)
clear_btn = tk.Button(btnfrm, text="Clear", command=clear_all_text)
coloring_btn = tk.Button(btnfrm, text="Coloring", command=coloring)

status_var = tk.StringVar()
status_lbl = tk.Label(
    btnfrm, textvariable=status_var, borderwidth=3, relief=tk.GROOVE, anchor=tk.W
)

txtfrm = tk.Frame(root)
txtw = tk.Text(txtfrm, font=fnt, width=80, height=10, undo=True, wrap=tk.CHAR)
scrlbary = tk.Scrollbar(txtfrm, orient=tk.VERTICAL, command=txtw.yview)
txtw["yscrollcommand"] = scrlbary.set

# ----------------------------------------
# layout
color_preveiw.grid(row=0, column=0, columnspan=2, sticky="nsew")

rgbfrm.grid(row=1, column=0, sticky="nsew", padx=8, pady=8)
picker_lbl.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=4)
colsel_btn.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=4)
rgbf_lbl.grid(row=0, column=2, padx=4)
rgb_lbl.grid(row=1, column=2, padx=4)
rgbf_ent.grid(row=0, column=3, sticky="nsew", padx=4)
rgb_ent.grid(row=1, column=3, sticky="nsew", padx=4)
rgbfrm.grid_rowconfigure(0, weight=0)
rgbfrm.grid_rowconfigure(1, weight=0)
rgbfrm.grid_columnconfigure(0, weight=0)
rgbfrm.grid_columnconfigure(1, weight=0)
rgbfrm.grid_columnconfigure(2, weight=0)
rgbfrm.grid_columnconfigure(3, weight=1)

btnfrm.grid(row=3, column=0, sticky="ew", padx=4, pady=4)
coloring_btn.pack(side=tk.LEFT, padx=4)
fontsel_btn.pack(side=tk.LEFT, padx=4)
fontinc_btn.pack(side=tk.LEFT, padx=4)
fontdec_btn.pack(side=tk.LEFT, padx=4)
clear_btn.pack(side=tk.LEFT, padx=4)
status_lbl.pack(side=tk.LEFT, padx=4, fill=tk.X, expand=True)

txtfrm.grid(row=4, column=0, sticky="nsew")
scrlbary.pack(side=tk.RIGHT, fill=tk.Y, expand=False)
txtw.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

root.grid_rowconfigure(0, weight=0)
root.grid_rowconfigure(1, weight=0)
root.grid_rowconfigure(2, weight=0)
root.grid_rowconfigure(3, weight=0)
root.grid_rowconfigure(4, weight=1)
root.grid_columnconfigure(0, weight=1)

# ----------------------------------------
# bind

# middle click to paste
txtw.bind("<Button-2>", lambda e: click_middle_button())

txtw.bind("<Button-1>", change_cursor_pos)
txtw.bind("<Key>", change_cursor_pos)

# Ctrl + "+" / "-"" : change font size
txtw.bind("<Control-Key-plus>", lambda e: inc_font_size())
txtw.bind("<Control-Key-minus>", lambda e: dec_font_size())

# click color panel to open color chooser
color_preveiw.bind("<Button-1>", lambda e: open_color_chooser())

picker_lbl.bind("<ButtonPress-1>", start_get_desktop_color)

# Ctrl+q : exit
root.bind("<Control-Key-q>", lambda e: root.destroy())

root.mainloop()
