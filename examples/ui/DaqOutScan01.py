"""
File:                       DaqOutScan01.py

Library Call Demonstrated:  mcculw.ul.daq_out_scan()

Purpose:                    Synchronously writes to an analog channel and a
                            digital port in the background (if each is
                            available).

Demonstration:              Sends output to the analog and digital channels if
                            available.

Other Library Calls:        mcculw.ul.win_buf_alloc()
                            mcculw.ul.win_buf_free()
                            mcculw.ul.d_config_port()
                            mcculw.ul.from_eng_units()
                            mcculw.ul.get_status()
                            mcculw.ul.stop_background()

Special Requirements:       Device must support mcculw.ul.daq_out_scan().
"""
from __future__ import absolute_import, division, print_function
from builtins import *  # @UnusedWildImport

import math
import tkinter as tk
from tkinter import messagebox
from ctypes import cast, POINTER, c_ushort

from mcculw import ul
from mcculw.enums import (Status, FunctionType, ScanOptions, ChannelType,
                          ULRange, DigitalIODirection)
from mcculw.ul import ULError
from mcculw.device_info import DaqDeviceInfo

try:
    from ui_examples_util import UIExample, show_ul_error
except ImportError:
    from .ui_examples_util import UIExample, show_ul_error


class DaqOutScan01(UIExample):
    def __init__(self, master=None):
        super(DaqOutScan01, self).__init__(master)
        # By default, the example detects all available devices and selects the
        # first device listed.
        # If use_device_detection is set to False, the board_num property needs
        # to match the desired board number configured with Instacal.
        use_device_detection = True
        self.board_num = 0

        self.num_chans = 2
        self.chan_list = []
        self.chan_type_list = []
        self.gain_list = []

        try:
            if use_device_detection:
                self.configure_first_detected_device()

            self.device_info = DaqDeviceInfo(self.board_num)
            if self.device_info.supports_daq_output:
                self.ao_info = self.device_info.get_ao_info()
                self.init_scan_channel_info()
                self.create_widgets()
            else:
                self.create_unsupported_widgets()
        except ULError:
            self.create_unsupported_widgets(True)

    def init_scan_channel_info(self):
        daqo_info = self.device_info.get_daqo_info()
        supported_channel_types = daqo_info.supported_channel_types

        # Add an analog output channel
        self.chan_list.append(0)
        self.chan_type_list.append(ChannelType.ANALOG)
        self.gain_list.append(self.ao_info.supported_ranges[0])

        # Add a digital output channel
        if ChannelType.DIGITAL16 in supported_channel_types:
            chan_type = ChannelType.DIGITAL16
        elif ChannelType.DIGITAL8 in supported_channel_types:
            chan_type = ChannelType.DIGITAL8
        else:
            chan_type = ChannelType.DIGITAL

        dio_info = self.device_info.get_dio_info()
        port_info = dio_info.port_info[0]
        self.chan_list.append(port_info.type)
        self.chan_type_list.append(chan_type)
        self.gain_list.append(ULRange.NOTUSED)

        # Configure all digital ports for output
        for port in dio_info.port_info:
            if port.is_port_configurable:
                ul.d_config_port(self.board_num, port.type,
                                 DigitalIODirection.OUT)

    def start_scan(self):
        # Build the data array
        points_per_channel = 1000
        rate = 1000
        num_points = self.num_chans * points_per_channel
        scan_options = ScanOptions.BACKGROUND | ScanOptions.CONTINUOUS
        ao_range = self.ao_info.supported_ranges[0]

        self.memhandle = ul.win_buf_alloc(num_points)
        # Check if the buffer was successfully allocated
        if not self.memhandle:
            messagebox.showerror("Error", "Failed to allocate memory")
            self.start_button["state"] = tk.NORMAL
            return

        try:
            data_array = cast(self.memhandle, POINTER(c_ushort))
            freq = self.add_example_data(data_array, ao_range, rate,
                                         points_per_channel)
            self.freq_label["text"] = str(freq) + "Hz"

            ul.daq_out_scan(self.board_num, self.chan_list, self.chan_type_list,
                            self.gain_list, self.num_chans, rate, num_points,
                            self.memhandle, scan_options)

            # Start updating the displayed values
            self.update_displayed_values()
        except ULError as e:
            show_ul_error(e)
            self.set_ui_idle_state()
            return

    def add_example_data(self, data_array, ao_range, rate, points_per_channel):
        # Calculate a frequency that will work well with the size of the array
        freq = rate / points_per_channel

        # Calculate an amplitude and y-offset for the signal
        # to fill the analog output range
        amplitude = (ao_range.range_max - ao_range.range_min) / 2
        y_offset = (amplitude + ao_range.range_min) / 2

        # Fill the array with sine wave data for the analog channel, and square
        # wave data for all bits on the digital port.
        data_index = 0
        for point_num in range(0, points_per_channel):
            # Generate a value in volts for output from the analog channel
            value_volts = amplitude * math.sin(
                2 * math.pi * freq * point_num / rate) + y_offset
            # Convert the volts to counts
            value_count = ul.from_eng_units(
                self.board_num, ao_range, value_volts)
            data_array[data_index] = value_count
            data_index += 1

            # Generate a value for output from the digital port
            if point_num < points_per_channel / 2:
                data_array[data_index] = 0
            else:
                data_array[data_index] = 0xFFFF
            data_index += 1

        return freq

    def update_displayed_values(self):
        # Get the status from the device
        status, curr_count, curr_index = ul.get_status(
            self.board_num, FunctionType.DAQOFUNCTION)

        # Display the status info
        self.update_status_labels(status, curr_count, curr_index)

        # Call this method again until the stop button is pressed
        if status == Status.RUNNING:
            self.after(100, self.update_displayed_values)
        else:
            # Free the allocated memory
            ul.win_buf_free(self.memhandle)
            self.set_ui_idle_state()

    def update_status_labels(self, status, curr_count, curr_index):
        if status == Status.IDLE:
            self.status_label["text"] = "Idle"
        else:
            self.status_label["text"] = "Running"

        self.index_label["text"] = str(curr_index)
        self.count_label["text"] = str(curr_count)

    def stop(self):
        ul.stop_background(self.board_num, FunctionType.DAQOFUNCTION)

    def exit(self):
        self.stop()
        self.master.destroy()

    def set_ui_idle_state(self):
        self.start_button["command"] = self.start
        self.start_button["text"] = "Start"

    def start(self):
        self.start_button["command"] = self.stop
        self.start_button["text"] = "Stop"
        self.start_scan()

    def create_widgets(self):
        '''Create the tkinter UI'''
        self.device_label = tk.Label(self)
        self.device_label.pack(fill=tk.NONE, anchor=tk.NW)
        self.device_label["text"] = ('Board Number ' + str(self.board_num)
                                     + ": " + self.device_info.product_name
                                     + " (" + self.device_info.unique_id + ")")

        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.X, anchor=tk.NW)

        results_frame = tk.Frame(main_frame)
        results_frame.pack(fill=tk.X, anchor=tk.NW)

        curr_row = 0
        status_left_label = tk.Label(results_frame)
        status_left_label["text"] = "Status:"
        status_left_label.grid(row=curr_row, column=0, sticky=tk.W)

        self.status_label = tk.Label(results_frame)
        self.status_label["text"] = "Idle"
        self.status_label.grid(row=curr_row, column=1, sticky=tk.W)

        curr_row += 1
        index_left_label = tk.Label(results_frame)
        index_left_label["text"] = "Index:"
        index_left_label.grid(row=curr_row, column=0, sticky=tk.W)

        self.index_label = tk.Label(results_frame)
        self.index_label["text"] = "-1"
        self.index_label.grid(row=curr_row, column=1, sticky=tk.W)

        curr_row += 1
        count_left_label = tk.Label(results_frame)
        count_left_label["text"] = "Count:"
        count_left_label.grid(row=curr_row, column=0, sticky=tk.W)

        self.count_label = tk.Label(results_frame)
        self.count_label["text"] = "0"
        self.count_label.grid(row=curr_row, column=1, sticky=tk.W)

        curr_row += 1
        freq_left_label = tk.Label(results_frame)
        freq_left_label["text"] = "Frequency:"
        freq_left_label.grid(row=curr_row, column=0, sticky=tk.W)

        self.freq_label = tk.Label(results_frame)
        self.freq_label.grid(row=curr_row, column=1, sticky=tk.W)

        button_frame = tk.Frame(self)
        button_frame.pack(fill=tk.X, side=tk.RIGHT, anchor=tk.SE)

        self.start_button = tk.Button(button_frame)
        self.start_button["text"] = "Start"
        self.start_button["command"] = self.start
        self.start_button.grid(row=0, column=0, padx=3, pady=3)

        quit_button = tk.Button(button_frame)
        quit_button["text"] = "Quit"
        quit_button["command"] = self.exit
        quit_button.grid(row=0, column=1, padx=3, pady=3)


if __name__ == "__main__":
    # Start the example
    DaqOutScan01(master=tk.Tk()).mainloop()
