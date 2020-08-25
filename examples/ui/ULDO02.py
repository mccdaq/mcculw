"""
File:                       ULDO02.py

Library Call Demonstrated:  mcculw.ul.d_out()

Purpose:                    Sets the state of a single digital output bit.

Demonstration:              Configures the first digital bit for output
                            (if necessary) and writes a value to the bit.

Other Library Calls:        mcculw.ul.d_config_port()

Special Requirements:       Device must have a digital output port
                            or have digital ports programmable as output.
"""
from __future__ import absolute_import, division, print_function
from builtins import *  # @UnusedWildImport

import tkinter as tk
from tkinter import IntVar

from mcculw import ul
from mcculw.enums import DigitalIODirection
from mcculw.ul import ULError
from mcculw.device_info import DaqDeviceInfo

try:
    from ui_examples_util import UIExample, show_ul_error
except ImportError:
    from .ui_examples_util import UIExample, show_ul_error


class ULDO02(UIExample):
    def __init__(self, master=None):
        super(ULDO02, self).__init__(master)
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

    def exit(self):
        # Set the port to 0 at exit
        try:
            ul.d_out(self.board_num, self.port.type, 0)
        except ULError as e:
            show_ul_error(e)
        self.master.destroy()

    def bit_checkbutton_changed(self, bit_num):
        try:
            # Get the value from the checkbutton
            bit_value = self.bit_checkbutton_vars[bit_num].get()
            # Output the value to the board
            ul.d_bit_out(self.board_num, self.port.type, bit_num, bit_value)
        except ULError as e:
            show_ul_error(e)

    def create_widgets(self):
        '''Create the tkinter UI'''
        self.device_label = tk.Label(self)
        self.device_label.pack(fill=tk.NONE, anchor=tk.NW)
        self.device_label["text"] = ('Board Number ' + str(self.board_num)
                                     + ": " + self.device_info.product_name
                                     + " (" + self.device_info.unique_id + ")")

        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.X, anchor=tk.NW)

        curr_row = 0
        bit_values_frame = tk.Frame(main_frame)
        bit_values_frame.grid(row=curr_row, column=0, padx=3, pady=3)

        label = tk.Label(bit_values_frame, text="Bit Number:")
        label.grid(row=0, column=0, sticky=tk.W)

        label = tk.Label(bit_values_frame, text="State:")
        label.grid(row=1, column=0, sticky=tk.W)

        # Create Checkbutton controls for each bit
        self.bit_checkbutton_vars = []
        max_bit = min(self.port.num_bits, 8)
        for bit_num in range(0, max_bit):
            bit_label = tk.Label(bit_values_frame, text=str(bit_num))
            bit_label.grid(row=0, column=bit_num + 1)

            var = IntVar(value=-1)
            bit_checkbutton = tk.Checkbutton(
                bit_values_frame, tristatevalue=-1, variable=var,
                borderwidth=0,
                command=lambda n=bit_num:
                self.bit_checkbutton_changed(n))
            bit_checkbutton.grid(row=1, column=bit_num + 1, padx=(5, 0))
            self.bit_checkbutton_vars.append(var)

        button_frame = tk.Frame(self)
        button_frame.pack(fill=tk.X, side=tk.RIGHT, anchor=tk.SE)

        quit_button = tk.Button(button_frame)
        quit_button["text"] = "Quit"
        quit_button["command"] = self.exit
        quit_button.grid(row=0, column=0, padx=3, pady=3)


if __name__ == "__main__":
    # Start the example
    ULDO02(master=tk.Tk()).mainloop()
