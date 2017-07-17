from __future__ import absolute_import, division, print_function

import ctypes
import os

from builtins import *  # @UnusedWildImport
from tkinter import messagebox

import tkinter as tk


class UIExample(tk.Frame, object):
    """Provides a base class for all UI-based examples in this package.
    """

    def __init__(self, master=None):
        super(UIExample, self).__init__(master)

        example_dir = os.path.dirname(os.path.realpath(__file__))
        icon_path = os.path.join(example_dir, 'MCC.ico')

        # Initialize tkinter properties
        master.iconbitmap(icon_path)
        master.wm_title(type(self).__name__)
        master.minsize(width=400, height=75)
        master.grid_columnconfigure(0, weight=1)
        master.grid_rowconfigure(0, weight=1)

        self.grid(sticky=tk.NSEW)

    def create_unsupported_widgets(self, board_num):
        incompatible_label = tk.Label(self, fg="red")
        incompatible_label["text"] = (
            "Board " + str(board_num)
            + " was not found or is not compatible with this example.")
        incompatible_label.pack(fill=tk.X, side=tk.LEFT, anchor=tk.NW)

        button_frame = tk.Frame(self)
        button_frame.pack(fill=tk.X, side=tk.RIGHT, anchor=tk.SE)

        quit_button = tk.Button(button_frame)
        quit_button["text"] = "Quit"
        quit_button["command"] = self.master.destroy
        quit_button.grid(row=0, column=0, padx=3, pady=3)

    def show_ul_error(self, ul_error):
        message = (
            "A UL Error occurred.\n\n Error Code: " + str(ul_error.errorcode)
            + "\nMessage: " + ul_error.message)
        messagebox.showerror("Error", message)

    def memhandle_as_ctypes_array(self, memhandle):
        return ctypes.cast(memhandle, ctypes.POINTER(ctypes.c_ushort))

    def memhandle_as_ctypes_array_32(self, memhandle):
        return ctypes.cast(memhandle, ctypes.POINTER(ctypes.c_ulong))

    def memhandle_as_ctypes_array_scaled(self, memhandle):
        return ctypes.cast(memhandle, ctypes.POINTER(ctypes.c_double))

    def validate_positive_int_entry(self, p):
        if p == '':
            return True
        try:
            value = int(p)
            if(value < 0):
                return False
        except ValueError:
            return False
        return True

    def validate_float_entry(self, p):
        if p == '':
            return True
        try:
            float(p)
        except ValueError:
            return False
        return True
