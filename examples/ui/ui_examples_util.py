from __future__ import absolute_import, division, print_function
from builtins import *  # @UnusedWildImport

import os
import tkinter as tk
from tkinter import messagebox

from mcculw import ul
from mcculw.enums import InterfaceType, ErrorCode
from mcculw.ul import ULError


class UIExample(tk.Frame, object):
    """Provides a base class for all UI-based examples in this package."""

    def __init__(self, master=None):
        super(UIExample, self).__init__(master)

        self.board_num = 0

        example_dir = os.path.dirname(os.path.realpath(__file__))
        icon_path = os.path.join(example_dir, 'MCC.ico')

        # Initialize tkinter properties
        master.iconbitmap(icon_path)
        master.wm_title(type(self).__name__)
        master.minsize(width=400, height=75)
        master.grid_columnconfigure(0, weight=1)
        master.grid_rowconfigure(0, weight=1)

        self.grid(sticky=tk.NSEW)

    def create_unsupported_widgets(self, error=False):
        incompatible_label = tk.Label(self, fg="red")
        incompatible_label["text"] = "Board " + str(self.board_num) + " "
        if error:
            incompatible_label["text"] += "was not found."
        else:
            incompatible_label["text"] += "is not compatible with this example."
        incompatible_label.pack(fill=tk.X, side=tk.LEFT, anchor=tk.NW)

        button_frame = tk.Frame(self)
        button_frame.pack(fill=tk.X, side=tk.RIGHT, anchor=tk.SE)

    def configure_first_detected_device(self):
        ul.ignore_instacal()
        devices = ul.get_daq_device_inventory(InterfaceType.ANY)
        if not devices:
            raise ULError(ErrorCode.BADBOARD)

        # Add the first DAQ device to the UL with the specified board number
        ul.create_daq_device(self.board_num, devices[0])


def show_ul_error(ul_error):
    message = 'A UL Error occurred.\n\n' + str(ul_error)
    messagebox.showerror("Error", message)


def validate_positive_int_entry(p):
    valid = False if p is None else True
    if p:
        try:
            value = int(p)
            if value < 0:
                valid = False
        except ValueError:
            valid = False
    return valid


def validate_float_entry(p):
    valid = False if p is None else True
    if p:
        try:
            float(p)
        except ValueError:
            valid = False
    return valid
