"""
File:                       ULDI06.py

Library Call Demonstrated:  mcculw.ul.d_config_bit()

Purpose:                    Reads the status of a single bit within a
                            digital port after configuring for input.

Demonstration:              Configures a single bit (within a digital port) for
                            input (if programmable) and reads the bit status.

Other Library Calls:        mcculw.ul.d_bit_in()

Special Requirements:       Device must have a digital port that supports
                            input or bits that can be configured for input.
"""
from __future__ import absolute_import, division, print_function
from builtins import *  # @UnusedWildImport

import tkinter as tk

from mcculw import ul
from mcculw.enums import DigitalIODirection
from mcculw.ul import ULError
from mcculw.device_info import DaqDeviceInfo

try:
    from ui_examples_util import UIExample, show_ul_error
except ImportError:
    from .ui_examples_util import UIExample, show_ul_error


class ULDI06(UIExample):
    def __init__(self, master=None):
        super(ULDI06, self).__init__(master)
        # By default, the example detects all available devices and selects the
        # first device listed.
        # If use_device_detection is set to False, the board_num property needs
        # to match the desired board number configured with Instacal.
        use_device_detection = True
        self.board_num = 0

        self.running = False

        try:
            if use_device_detection:
                self.configure_first_detected_device()

            self.device_info = DaqDeviceInfo(self.board_num)
            dio_info = self.device_info.get_dio_info()

            # Find the first port that supports input, defaulting to None
            # if one is not found.
            self.port = next((port for port in dio_info.port_info
                              if (port.supports_input
                                  and port.is_bit_configurable)), None)

            if self.port is not None:
                self.create_widgets()
            else:
                self.create_unsupported_widgets()

        except ULError:
            self.create_unsupported_widgets(True)

    def update_value(self):
        try:
            # Get a value from the device
            value = ul.d_bit_in(self.board_num, self.port.type,
                                self.port.first_bit)

            # Display the value
            self.value_label["text"] = str(value)

            # Call this method again until the stop button is pressed (or an
            # error occurs)
            if self.running:
                self.after(100, self.update_value)
        except ULError as e:
            self.stop()
            show_ul_error(e)

    def stop(self):
        self.running = False
        self.start_button["command"] = self.start
        self.start_button["text"] = "Start"

    def start(self):
        self.running = True
        self.start_button["command"] = self.stop
        self.start_button["text"] = "Stop"

        try:
            ul.d_config_bit(
                self.board_num, self.port.type, self.port.first_bit,
                DigitalIODirection.IN)
        except ULError as e:
            self.stop()
            show_ul_error(e)
            return

        self.update_value()

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
        raw_value_left_label = tk.Label(main_frame)
        raw_value_left_label["text"] = (
            self.port.type.name + " bit " + str(self.port.first_bit)
            + " value read:")
        raw_value_left_label.grid(row=curr_row, column=0, sticky=tk.W)

        self.value_label = tk.Label(main_frame)
        self.value_label.grid(row=curr_row, column=1, sticky=tk.W)

        button_frame = tk.Frame(self)
        button_frame.pack(fill=tk.X, side=tk.RIGHT, anchor=tk.SE)

        self.start_button = tk.Button(button_frame)
        self.start_button["text"] = "Start"
        self.start_button["command"] = self.start
        self.start_button.grid(row=0, column=0, padx=3, pady=3)

        quit_button = tk.Button(button_frame)
        quit_button["text"] = "Quit"
        quit_button["command"] = self.master.destroy
        quit_button.grid(row=0, column=1, padx=3, pady=3)


if __name__ == "__main__":
    # Start the example
    ULDI06(master=tk.Tk()).mainloop()
