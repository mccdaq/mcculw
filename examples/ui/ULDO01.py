"""
File:                       ULDO01.py

Library Call Demonstrated:  mcculw.ul.d_out()

Purpose:                    Writes a byte to digital output ports.

Demonstration:              Configures the first digital port for output
                            (if necessary) and writes a value to the port.

Other Library Calls:        mcculw.ul.d_config_port()

Special Requirements:       Device must have a digital output port
                            or have digital ports programmable as output.
"""
from __future__ import absolute_import, division, print_function
from builtins import *  # @UnusedWildImport

import tkinter as tk
from tkinter import StringVar

from mcculw import ul
from mcculw.enums import DigitalIODirection
from mcculw.ul import ULError
from mcculw.device_info import DaqDeviceInfo

try:
    from ui_examples_util import (UIExample, show_ul_error,
                                  validate_positive_int_entry)
except ImportError:
    from .ui_examples_util import (UIExample, show_ul_error,
                                   validate_positive_int_entry)


class ULDO01(UIExample):
    def __init__(self, master=None):
        super(ULDO01, self).__init__(master)
        master.protocol("WM_DELETE_WINDOW", self.exit)
        # By default, the example detects all available devices and selects the
        # first device listed.
        # If use_device_detection is set to False, the board_num property needs
        # to match the desired board number configured with Instacal.
        use_device_detection = True
        self.board_num = 0

        try:
            if use_device_detection:
                self.configure_first_detected_device()

            self.device_info = DaqDeviceInfo(self.board_num)
            dio_info = self.device_info.get_dio_info()

            # Find the first port that supports output, defaulting to None
            # if one is not found.
            self.port = next((port for port in dio_info.port_info
                              if port.supports_output), None)

            if self.port is not None:
                # If the port is configurable, configure it for output
                if self.port.is_port_configurable:
                    try:
                        ul.d_config_port(self.board_num, self.port.type,
                                         DigitalIODirection.OUT)
                    except ULError as e:
                        show_ul_error(e)
                self.create_widgets()
            else:
                self.create_unsupported_widgets()
        except ULError:
            self.create_unsupported_widgets(True)

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
            show_ul_error(e)

    def exit(self):
        # Set the port to 0 at exit
        try:
            ul.d_out(self.board_num, self.port.type, 0)
        except ULError as e:
            show_ul_error(e)
        self.master.destroy()

    def create_widgets(self):
        '''Create the tkinter UI'''
        self.device_label = tk.Label(self)
        self.device_label.pack(fill=tk.NONE, anchor=tk.NW)
        self.device_label["text"] = ('Board Number ' + str(self.board_num)
                                     + ": " + self.device_info.product_name
                                     + " (" + self.device_info.unique_id + ")")

        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.X, anchor=tk.NW)

        positive_int_vcmd = self.register(validate_positive_int_entry)

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


if __name__ == "__main__":
    # Start the example
    ULDO01(master=tk.Tk()).mainloop()
