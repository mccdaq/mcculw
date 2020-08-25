"""
File:                       CInScan02.py

Library Call Demonstrated:  mcculw.ul.c_config_scan() and mcculw.ul.c_in_scan()

Purpose:                    Scans a Counter Input in decrement mode and stores
                            the sample data in an array.

Demonstration:              Displays counts for the first compatible counter.

Other Library Calls:        mcculw.ul.win_buf_alloc_32()
                            mcculw.ul.win_buf_free()

Special Requirements:       Device must support counter scan function and
                            decrement mode.
                            TTL signals on selected counter inputs.
"""
from __future__ import absolute_import, division, print_function
from builtins import *  # @UnusedWildImport

import tkinter as tk
from tkinter import messagebox
from ctypes import cast, POINTER, c_ulong

from mcculw import ul
from mcculw.enums import (CounterChannelType, CounterDebounceTime, CounterMode,
                          CounterEdgeDetection, CounterTickSize)
from mcculw.ul import ULError
from mcculw.device_info import DaqDeviceInfo

try:
    from ui_examples_util import UIExample, show_ul_error
except ImportError:
    from .ui_examples_util import UIExample, show_ul_error


class CInScan02(UIExample):
    def __init__(self, master=None):
        super(CInScan02, self).__init__(master)
        # By default, the example detects all available devices and selects the
        # first device listed.
        # If use_device_detection is set to False, the board_num property needs
        # to match the desired board number configured with Instacal.
        use_device_detection = True
        self.board_num = 0

        self.chan_num = -1

        try:
            if use_device_detection:
                self.configure_first_detected_device()

            self.device_info = DaqDeviceInfo(self.board_num)
            counter_info = self.device_info.get_ctr_info()

            chan = next(
                (channel for channel in counter_info.chan_info
                 if channel.type == CounterChannelType.CTRSCAN), None)
            if chan:
                self.chan_num = chan.channel_num

            if self.chan_num != -1:
                self.create_widgets()
            else:
                self.create_unsupported_widgets()
        except ULError:
            self.create_unsupported_widgets(True)

    def start_scan(self):
        rate = 390
        total_count = 100

        # Allocate a buffer for the scan
        memhandle = ul.win_buf_alloc_32(total_count)

        # Check if the buffer was successfully allocated
        if not memhandle:
            messagebox.showerror("Error", "Failed to allocate memory")
            self.start_button["state"] = tk.NORMAL
            return

        try:
            # Configure the counter
            ul.c_config_scan(
                self.board_num, self.chan_num, CounterMode.DECREMENT_ON,
                CounterDebounceTime.DEBOUNCE_NONE, 0,
                CounterEdgeDetection.FALLING_EDGE,
                CounterTickSize.TICK20PT83ns, 1)

            # Run the scan
            ul.c_in_scan(
                self.board_num, self.chan_num, self.chan_num, total_count,
                rate, memhandle, 0)

            # Convert the memhandle to a ctypes array
            # Note: the ctypes array will only be valid until win_buf_free
            # is called.
            # A copy of the buffer can be created using win_buf_to_array_32
            # before the memory is freed. The copy can be used at any time.
            array = cast(memhandle, POINTER(c_ulong))

            # Display the values
            self.display_values(array, total_count)
        except ULError as e:
            show_ul_error(e)
        finally:
            # Free the allocated memory
            ul.win_buf_free(memhandle)
            self.start_button["state"] = tk.NORMAL

    def display_values(self, array, total_count):
        new_data_frame = tk.Frame(self.results_group)

        # Add the header
        channel_text = "Channel " + str(self.chan_num) + "\n"

        # Add (up to) the first 10 values to the display
        for data_index in range(0, min(10, total_count)):
            channel_text += str(array[data_index]) + "\n"

        # Add the labels
        chan_label = tk.Label(new_data_frame, justify=tk.LEFT, padx=3)
        chan_label["text"] = channel_text
        chan_label.grid(row=0, column=0)

        self.data_frame.destroy()
        self.data_frame = new_data_frame
        self.data_frame.grid()

    def start(self):
        self.start_button["state"] = tk.DISABLED
        self.start_scan()

    def create_widgets(self):
        '''Create the tkinter UI'''
        self.device_label = tk.Label(self)
        self.device_label.pack(fill=tk.NONE, anchor=tk.NW)
        self.device_label["text"] = ('Board Number ' + str(self.board_num)
                                     + ": " + self.device_info.product_name
                                     + " (" + self.device_info.unique_id + ")")

        # Initialize tkinter
        self.grid(sticky=tk.NSEW)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.results_group = tk.LabelFrame(
            self, text="Results", padx=3, pady=3)
        self.results_group.pack(
            fill=tk.X, anchor=tk.NW, padx=3, pady=3)

        self.data_frame = tk.Frame(self.results_group)
        self.data_frame.grid()

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
    CInScan02(master=tk.Tk()).mainloop()
