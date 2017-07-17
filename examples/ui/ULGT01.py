from __future__ import absolute_import, division, print_function
from builtins import *  # @UnusedWildImport

from tkinter import StringVar

from mcculw import ul
from examples.ui.uiexample import UIExample
from mcculw.ul import ULError
import tkinter as tk


class ULGT01(UIExample):
    def __init__(self, master):
        super(ULGT01, self).__init__(master)
        self.create_widgets()

    def err_code_changed(self, *args):
        try:
            err_code = int(self.err_code_variable.get())
        except ValueError:
            err_code = 0

        try:
            message = ul.get_err_msg(err_code)

            self.err_msg_label["text"] = message
        except ULError as e:
            self.show_ul_error(e)

    def create_widgets(self):
        '''Create the tkinter UI'''
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.X, anchor=tk.NW)

        positive_int_vcmd = self.register(self.validate_positive_int_entry)

        err_code_label = tk.Label(main_frame)
        err_code_label["text"] = "Error Code:"
        err_code_label.grid(row=0, column=0, sticky=tk.W)

        self.err_code_variable = StringVar(0)
        self.err_code_entry = tk.Spinbox(
            main_frame, from_=0, to=2000,
            textvariable=self.err_code_variable,
            validate="key", validatecommand=(positive_int_vcmd, "%P"))
        self.err_code_entry.grid(row=0, column=1, sticky=tk.W)
        self.err_code_variable.trace("w", self.err_code_changed)

        err_msg_left_label = tk.Label(main_frame)
        err_msg_left_label["text"] = "Message:"
        err_msg_left_label.grid(row=1, column=0, sticky=tk.NW)

        self.err_msg_label = tk.Label(
            main_frame, justify=tk.LEFT, wraplength=300)
        self.err_msg_label["text"] = "No error has occurred."
        self.err_msg_label.grid(row=1, column=1, sticky=tk.W)

        button_frame = tk.Frame(self)
        button_frame.pack(fill=tk.X, side=tk.RIGHT, anchor=tk.SE)

        quit_button = tk.Button(button_frame)
        quit_button["text"] = "Quit"
        quit_button["command"] = self.master.destroy
        quit_button.grid(row=0, column=0, padx=3, pady=3)


# Start the example if this module is being run
if __name__ == "__main__":
    # Start the example
    ULGT01(master=tk.Tk()).mainloop()
