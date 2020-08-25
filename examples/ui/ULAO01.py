"""
File:                       ULAO01.py

Library Call Demonstrated:  mcculw.ul.a_out()

Purpose:                    Writes to a D/A Output Channel.

Demonstration:              Sends a digital output to D/A 0.

Other Library Calls:        mcculw.ul.from_eng_units()

Special Requirements:       Device must have a D/A converter.
"""
from __future__ import absolute_import, division, print_function
from builtins import *  # @UnusedWildImport

import tkinter as tk

from mcculw import ul
from mcculw.enums import ULRange
from mcculw.ul import ULError
from mcculw.device_info import DaqDeviceInfo

try:
    from ui_examples_util import UIExample, show_ul_error, validate_float_entry
except ImportError:
    from .ui_examples_util import UIExample, show_ul_error, validate_float_entry


class ULAO01(UIExample):
    def __init__(self, master=None):
        super(ULAO01, self).__init__(master)
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
            self.ao_info = self.device_info.get_ao_info()
            if self.ao_info.is_supported:
                self.create_widgets()
            else:
                self.create_unsupported_widgets()
        except ULError:
            self.create_unsupported_widgets(True)

    def update_value(self):
        channel = self.get_channel_num()
        ao_range = self.ao_info.supported_ranges[0]
        data_value = self.get_data_value()

        raw_value = ul.from_eng_units(self.board_num, ao_range, data_value)

        try:
            ul.a_out(self.board_num, channel, ao_range, raw_value)
        except ULError as e:
            show_ul_error(e)

    def get_data_value(self):
        try:
            return float(self.data_value_entry.get())
        except ValueError:
            return 0

    def get_channel_num(self):
        if self.ao_info.num_chans == 1:
            return 0
        try:
            return int(self.channel_entry.get())
        except ValueError:
            return 0

    def validate_channel_entry(self, p):
        if p == '':
            return True
        try:
            value = int(p)
            if value < 0 or value > self.ao_info.num_chans - 1:
                return False
        except ValueError:
            return False

        return True

    def create_widgets(self):
        '''Create the tkinter UI'''
        self.device_label = tk.Label(self)
        self.device_label.pack(fill=tk.NONE, anchor=tk.NW)
        self.device_label["text"] = ('Board Number ' + str(self.board_num)
                                     + ": " + self.device_info.product_name
                                     + " (" + self.device_info.unique_id + ")")

        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.X, anchor=tk.NW)

        float_vcmd = self.register(validate_float_entry)

        curr_row = 0
        if self.ao_info.num_chans > 1:
            channel_vcmd = self.register(self.validate_channel_entry)

            channel_entry_label = tk.Label(main_frame)
            channel_entry_label["text"] = "Channel Number:"
            channel_entry_label.grid(
                row=curr_row, column=0, sticky=tk.W)

            self.channel_entry = tk.Spinbox(
                main_frame, from_=0,
                to=max(self.ao_info.num_chans - 1, 0),
                validate='key', validatecommand=(channel_vcmd, '%P'))
            self.channel_entry.grid(
                row=curr_row, column=1, sticky=tk.W)

            curr_row += 1

        mv_ranges = [ULRange.MA4TO20, ULRange.MA2TO10, ULRange.MA1TO5,
                     ULRange.MAPT5TO2PT5]
        if self.ao_info.supported_ranges[0] in mv_ranges:
            units_text = "mA"
        else:
            units_text = "V"

        value_label_text = "Value (" + units_text + "):"
        data_value_label = tk.Label(main_frame)
        data_value_label["text"] = value_label_text
        data_value_label.grid(row=curr_row, column=0, sticky=tk.W)

        self.data_value_entry = tk.Entry(
            main_frame, validate='key', validatecommand=(float_vcmd, '%P'))
        self.data_value_entry.grid(row=curr_row, column=1, sticky=tk.W)
        self.data_value_entry.insert(0, "0")

        update_button = tk.Button(main_frame)
        update_button["text"] = "Update"
        update_button["command"] = self.update_value
        update_button.grid(row=curr_row, column=2, padx=3, pady=3)

        button_frame = tk.Frame(self)
        button_frame.pack(fill=tk.X, side=tk.RIGHT, anchor=tk.SE)

        quit_button = tk.Button(button_frame)
        quit_button["text"] = "Quit"
        quit_button["command"] = self.master.destroy
        quit_button.grid(row=0, column=0, padx=3, pady=3)


if __name__ == "__main__":
    # Start the example
    ULAO01(master=tk.Tk()).mainloop()
