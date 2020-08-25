"""
File:                       ULCT07.py

Library Call Demonstrated:  mcculw.ul.c_in_32()
                            mcculw.ul.c_clear()

Purpose:                    Operate the counter.

Demonstration:              Resets and reads the counter.

Special Requirements:       Device must have an Event Counter (or Scan Counter
                            that doesn't require configuration) such as the
                            miniLAB 1008, USB-CTR04 or USB-1208LS.
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


class ULCT07(UIExample):
    def __init__(self, master=None):
        super(ULCT07, self).__init__(master)
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
            self.ctr_info = self.device_info.get_ctr_info()
            if self.ctr_info.is_supported:
                self.create_widgets()
            else:
                self.create_unsupported_widgets()
        except ULError:
            self.create_unsupported_widgets(True)

    def update_value(self):
        channel = self.get_channel_num()

        try:
            # Get a value from the device
            value = ul.c_in_32(self.board_num, channel)

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
            # Clear the counter
            ul.c_clear(self.board_num, self.get_channel_num())
            # Start updating the counter values
            self.update_value()
        except ULError as e:
            self.stop()
            show_ul_error(e)

    def get_channel_num(self):
        if self.ctr_info.num_chans == 1:
            return self.ctr_info.chan_info[0].channel_num
        try:
            return int(self.channel_entry.get())
        except ValueError:
            return 0

    def validate_channel_entry(self, p):
        if p == '':
            return True
        try:
            value = int(p)
            if value < 0 or value > self.ctr_info.num_chans - 1:
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
        if self.ctr_info.num_chans > 1:
            channel_entry_label = tk.Label(main_frame)
            channel_entry_label["text"] = "Channel Number:"
            channel_entry_label.grid(
                row=curr_row, column=0, sticky=tk.W)

            chan_info_list = self.ctr_info.chan_info
            first_chan = chan_info_list[0].channel_num
            # last_chan = chan_info_list[len(chan_info_list) - 1].channel_num
            last_chan = first_chan
            for chan_info in chan_info_list:
                if chan_info.channel_num >= last_chan:
                    last_chan = chan_info.channel_num
                else:
                    break
            self.channel_entry = tk.Spinbox(
                main_frame, from_=first_chan, to=last_chan,
                validate='key', validatecommand=(channel_vcmd, '%P'))
            self.channel_entry.grid(row=curr_row, column=1, sticky=tk.W)

            curr_row += 1

        value_left_label = tk.Label(main_frame)
        value_left_label["text"] = "Value read from selected channel:"
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


if __name__ == "__main__":
    # Start the example
    ULCT07(master=tk.Tk()).mainloop()
