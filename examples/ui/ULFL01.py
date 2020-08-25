"""
File:                       ULFL01.py

Library Call Demonstrated:  mcculw.ul.flash_led()

Purpose:                    Operate the LED.

Demonstration:              Flashes onboard LED for visual identification.

Special Requirements:       Device must have an external LED.
"""
from __future__ import absolute_import, division, print_function
from builtins import *  # @UnusedWildImport

import tkinter as tk

from mcculw import ul
from mcculw.ul import ULError
from mcculw.device_info import DaqDeviceInfo

try:
    from ui_examples_util import UIExample, show_ul_error
except ImportError:
    from .ui_examples_util import UIExample, show_ul_error


class ULFL01(UIExample):
    def __init__(self, master):
        super(ULFL01, self).__init__(master)
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
            self.create_widgets()
        except ULError:
            self.create_unsupported_widgets()

    def flash_led(self):
        try:
            ul.flash_led(self.board_num)
        except ULError as e:
            show_ul_error(e)

    def create_widgets(self):
        '''Create the tkinter UI'''
        self.device_label = tk.Label(self)
        self.device_label.grid(row=0, column=0, columnspan=2, sticky=tk.W)
        self.device_label["text"] = ('Board Number ' + str(self.board_num)
                                     + ": " + self.device_info.product_name
                                     + " (" + self.device_info.unique_id + ")")

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.flash_led_button = tk.Button(self)
        self.flash_led_button["text"] = "Flash LED"
        self.flash_led_button["command"] = self.flash_led
        self.flash_led_button.grid(
            row=1, column=0, padx=3, pady=3, sticky=tk.NSEW)

        quit_button = tk.Button(self)
        quit_button["text"] = "Quit"
        quit_button["command"] = self.master.destroy
        quit_button.grid(
            row=1, column=1, padx=3, pady=3, sticky=tk.NSEW)


# Start the example if this module is being run
if __name__ == "__main__":
    # Start the example
    ULFL01(master=tk.Tk()).mainloop()
