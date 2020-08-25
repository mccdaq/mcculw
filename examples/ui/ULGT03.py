"""
File:                       ULGT03.py

Library Call Demonstrated:  mcculw.device_info package

Purpose:                    Prints a list of all boards installed in
                            the system and their base addresses.  Also
                            prints the number of channels for each of the
                            supported device subsystems.

Other Library Calls:        mcculw.ul.get_config()
"""
from __future__ import absolute_import, division, print_function
from builtins import *  # @UnusedWildImport

import tkinter as tk
from tkinter import StringVar

from mcculw import ul
from mcculw.enums import InfoType, GlobalInfo
from mcculw.ul import ULError
from mcculw.device_info import DaqDeviceInfo

try:
    from ui_examples_util import UIExample, validate_positive_int_entry
except ImportError:
    from .ui_examples_util import UIExample, validate_positive_int_entry


class ULGT03(UIExample):
    def __init__(self, master):
        super(ULGT03, self).__init__(master)
        self.board_num = 0

        self.max_board_num = ul.get_config(InfoType.GLOBALINFO, 0, 0,
                                           GlobalInfo.NUMBOARDS)
        self.create_widgets()
        self.update_board_info()

    def update_board_info(self):
        info_text = ""

        try:
            # Raises exception is board_num is not valid
            self.device_info = DaqDeviceInfo(self.board_num)

            info_text += self.get_ad_info()
            info_text += self.get_temperature_info()
            info_text += self.get_da_info()
            info_text += self.get_digital_info()
            info_text += self.get_counter_info()
            info_text += self.get_expansion_info()
            # Remove the last "newline" character
            info_text = info_text[:-1]
        except ULError:
            info_text = (
                "No board found at board number " + str(self.board_num)
                + ".\nRun InstaCal to add or remove boards before running this "
                + "program.")
        finally:
            self.info_label["text"] = info_text

    def get_ad_info(self):
        result = ''
        if self.device_info.supports_analog_input:
            ai_info = self.device_info.get_ai_info()
            result = ("Number of A/D channels: " + str(ai_info.num_chans)
                      + "\n")
        return result

    def get_temperature_info(self):
        result = ''
        if self.device_info.supports_temp_input:
            ai_info = self.device_info.get_ai_info()
            result = ("Number of Temperature channels: "
                      + str(ai_info.num_temp_chans) + "\n")
        return result

    def get_da_info(self):
        result = ''
        if self.device_info.supports_analog_output:
            ao_info = self.device_info.get_ao_info()
            result = ("Number of D/A channels: " + str(ao_info.num_chans)
                      + "\n")
        return result

    def get_digital_info(self):
        result = ''
        if self.device_info.supports_digital_io:
            dio_info = self.device_info.get_dio_info()
            for port_num in range(len(dio_info.port_info)):
                result += ("Digital Port #" + str(port_num) + ": "
                           + str(dio_info.port_info[port_num].num_bits)
                           + " bits\n")
        return result

    def get_counter_info(self):
        result = ''
        if self.device_info.supports_counters:
            ctr_info = self.device_info.get_ctr_info()
            result = ("Number of counter devices: " + str(ctr_info.num_chans)
                      + "\n")
        return result

    def get_expansion_info(self):
        result = ''
        if self.device_info.num_expansions > 0:
            for exp_info in self.device_info.exp_info:
                result += ("A/D channel " + str(exp_info.mux_ad_chan)
                           + " connected to EXP (device ID="
                           + str(exp_info.board_type) + ").\n")
        return result

    def board_num_changed(self, *args):
        try:
            self.board_num = int(self.board_num_variable.get())
            self.update_board_info()
        except ValueError:
            self.board_num = 0

    def create_widgets(self):
        '''Create the tkinter UI'''
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.X, anchor=tk.NW)

        positive_int_vcmd = self.register(validate_positive_int_entry)

        board_num_label = tk.Label(main_frame)
        board_num_label["text"] = "Board Number:"
        board_num_label.grid(row=0, column=0, sticky=tk.W)

        self.board_num_variable = StringVar()
        board_num_entry = tk.Spinbox(
            main_frame, from_=0, to=self.max_board_num,
            textvariable=self.board_num_variable,
            validate="key", validatecommand=(positive_int_vcmd, "%P"))
        board_num_entry.grid(row=0, column=1, sticky=tk.W)
        self.board_num_variable.trace("w", self.board_num_changed)

        info_groupbox = tk.LabelFrame(self, text="Board Information")
        info_groupbox.pack(fill=tk.X, anchor=tk.NW, padx=3, pady=3)

        self.info_label = tk.Label(
            info_groupbox, justify=tk.LEFT, wraplength=400)
        self.info_label.grid()

        button_frame = tk.Frame(self)
        button_frame.pack(fill=tk.X, side=tk.RIGHT, anchor=tk.SE)

        quit_button = tk.Button(button_frame)
        quit_button["text"] = "Quit"
        quit_button["command"] = self.master.destroy
        quit_button.grid(row=0, column=0, padx=3, pady=3)


# Start the example if this module is being run
if __name__ == "__main__":
    # Start the example
    ULGT03(master=tk.Tk()).mainloop()
