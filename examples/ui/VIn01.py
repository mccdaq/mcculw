"""
File:                       VIn01.py

Library Call Demonstrated:  mcculw.ul.v_in() or mcculw.ul.v_in_32

Purpose:                    Reads an A/D Input Channel.

Demonstration:              Displays the voltage input on a user-specified
                            channel.

Special Requirements:       Device must have an A/D converter.
                            Analog signal on an input channel.
"""
from __future__ import absolute_import, division, print_function
from builtins import *  # @UnusedWildImport

import tkinter as tk
from tkinter.ttk import Combobox  # @UnresolvedImport

from mcculw import ul
from mcculw.ul import ULError
from mcculw.device_info import DaqDeviceInfo

try:
    from ui_examples_util import UIExample, show_ul_error
except ImportError:
    from .ui_examples_util import UIExample, show_ul_error


class VIn01(UIExample):
    def __init__(self, master):
        super(VIn01, self).__init__(master)
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
            self.ai_info = self.device_info.get_ai_info()
            if self.ai_info.is_supported and self.ai_info.supports_v_in:
                self.create_widgets()
            else:
                self.create_unsupported_widgets()
        except ULError:
            self.create_unsupported_widgets(True)

    def update_value(self):
        channel = self.get_channel_num()
        ai_range = self.get_range()

        try:
            # Get a value from the device
            if self.ai_info.resolution <= 16:
                # Use the v_in method for devices with a resolution <= 16
                # (optional parameter omitted)
                value = ul.v_in(self.board_num, channel, ai_range)
            else:
                # Use the v_in_32 method for devices with a resolution > 16
                # (optional parameter omitted)
                value = ul.v_in_32(self.board_num, channel, ai_range)

            # Display the raw value
            self.value_label["text"] = '{:.3f}'.format(value)

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
        self.update_value()

    def get_range(self):
        selected_index = self.range_combobox.current()
        return self.ai_info.supported_ranges[selected_index]

    def get_channel_num(self):
        try:
            return int(self.channel_entry.get())
        except ValueError:
            return 0

    def validate_channel_entry(self, p):
        if p == '':
            return True
        try:
            value = int(p)
            if value < 0 or value > self.ai_info.num_chans - 1:
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

        channel_vcmd = self.register(self.validate_channel_entry)

        curr_row = 0
        channel_entry_label = tk.Label(main_frame)
        channel_entry_label["text"] = "Channel Number:"
        channel_entry_label.grid(row=curr_row, column=0, sticky=tk.W)

        self.channel_entry = tk.Spinbox(
            main_frame, from_=0,
            to=max(self.ai_info.num_chans - 1, 0),
            validate='key', validatecommand=(channel_vcmd, '%P'))
        self.channel_entry.grid(row=curr_row, column=1, sticky=tk.W)

        curr_row += 1
        range_label = tk.Label(main_frame)
        range_label["text"] = "Range:"
        range_label.grid(row=curr_row, column=0, sticky=tk.W)

        self.range_combobox = Combobox(main_frame)
        self.range_combobox["state"] = "readonly"
        self.range_combobox["values"] = [
            x.name for x in self.ai_info.supported_ranges]
        self.range_combobox.current(0)
        self.range_combobox.grid(row=curr_row, column=1, padx=3, pady=3)

        curr_row += 1
        value_left_label = tk.Label(main_frame)
        value_left_label["text"] = (
            "Value read from selected channel (V):")
        value_left_label.grid(row=curr_row, column=0, sticky=tk.W)

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


# Start the example if this module is being run
if __name__ == "__main__":
    # Start the example
    VIn01(master=tk.Tk()).mainloop()
