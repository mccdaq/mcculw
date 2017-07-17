from __future__ import absolute_import, division, print_function
from builtins import *  # @UnusedWildImport

from tkinter import StringVar

from mcculw import ul
from mcculw.enums import DigitalIODirection
from examples.ui.uiexample import UIExample
from examples.props.digital import DigitalProps
from mcculw.ul import ULError
import tkinter as tk


class ULDO01(UIExample):
    def __init__(self, master=None):
        super(ULDO01, self).__init__(master)
        master.protocol("WM_DELETE_WINDOW", self.exit)

        self.board_num = 0
        self.digital_props = DigitalProps(self.board_num)

        # Find the first port that supports output, defaulting to None
        # if one is not found.
        self.port = next(
            (port for port in self.digital_props.port_info
             if port.supports_output), None)

        # If the port is configurable, configure it for output
        if self.port != None and self.port.is_port_configurable:
            try:
                ul.d_config_port(
                    self.board_num, self.port.type, DigitalIODirection.OUT)
            except ULError as e:
                self.show_ul_error(e)

        self.running = False

        self.create_widgets()

    def get_data_value(self):
        try:
            return int(self.data_value_entry.get())
        except ValueError:
            return 0

    def data_value_changed(self, *args):
        try:
            # Get the data value
            data_value = self.get_data_value()
            # Send the value to the device
            ul.d_out(self.board_num, self.port.type, data_value)
        except ULError as e:
            self.stop()
            self.show_ul_error(e)

    def exit(self):
        # Set the port to 0 at exit
        try:
            ul.d_out(self.board_num, self.port.type, 0)
        except ULError as e:
            self.show_ul_error(e)
        self.master.destroy()

    def create_widgets(self):
        '''Create the tkinter UI'''
        if self.port != None:
            main_frame = tk.Frame(self)
            main_frame.pack(fill=tk.X, anchor=tk.NW)

            positive_int_vcmd = self.register(self.validate_positive_int_entry)

            curr_row = 0
            value_label = tk.Label(main_frame)
            value_label["text"] = "Value:"
            value_label.grid(row=curr_row, column=0, sticky=tk.W)

            self.data_value_variable = StringVar()
            self.data_value_entry = tk.Spinbox(
                main_frame, from_=0, to=255, textvariable=self.data_value_variable,
                validate="key", validatecommand=(positive_int_vcmd, "%P"))
            self.data_value_entry.grid(row=curr_row, column=1, sticky=tk.W)
            self.data_value_variable.trace("w", self.data_value_changed)

            button_frame = tk.Frame(self)
            button_frame.pack(fill=tk.X, side=tk.RIGHT, anchor=tk.SE)

            quit_button = tk.Button(button_frame)
            quit_button["text"] = "Quit"
            quit_button["command"] = self.exit
            quit_button.grid(row=0, column=1, padx=3, pady=3)
        else:
            self.create_unsupported_widgets(self.board_num)


if __name__ == "__main__":
    # Start the example
    ULDO01(master=tk.Tk()).mainloop()
