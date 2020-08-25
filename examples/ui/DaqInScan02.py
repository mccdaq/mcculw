"""
File:                       DaqInScan02.py

Library Call Demonstrated:  mcculw.ul.daq_in_scan()

Purpose:                    Synchronously scans Analog channels, digital
                            ports, and counters in the background.

Demonstration:              Collects data on first analog, digital,
                            and counter channel if available.

Other Library Calls:        mcculw.ul.d_config_port()
                            mcculw.ul.win_buf_alloc()
                            mcculw.ul.win_buf_alloc_32()
                            mcculw.ul.win_buf_free()
                            mcculw.ul.get_status()
                            mcculw.ul.stop_background()

Special Requirements:       Device must support mcculw.ul.daq_in_scan().
"""
from __future__ import absolute_import, division, print_function
from builtins import *  # @UnusedWildImport

import tkinter as tk
from tkinter import messagebox
from enum import Enum
from ctypes import cast, POINTER, c_ushort, c_ulong

from mcculw import ul
from mcculw.enums import (ScanOptions, Status, FunctionType, ChannelType,
                          ULRange, DigitalIODirection)
from mcculw.ul import ULError
from mcculw.device_info import DaqDeviceInfo

try:
    from ui_examples_util import UIExample, show_ul_error
except ImportError:
    from .ui_examples_util import UIExample, show_ul_error


class DaqInScan02(UIExample):
    def __init__(self, master=None):
        super(DaqInScan02, self).__init__(master)
        # By default, the example detects all available devices and selects the
        # first device listed.
        # If use_device_detection is set to False, the board_num property needs
        # to match the desired board number configured with Instacal.
        use_device_detection = True
        self.board_num = 0

        self.chan_list = []
        self.chan_type_list = []
        self.gain_list = []
        self.num_chans = 0
        self.resolution = 16

        try:
            if use_device_detection:
                self.configure_first_detected_device()

            self.device_info = DaqDeviceInfo(self.board_num)
            if self.device_info.supports_daq_input:
                self.init_scan_channel_info()
                self.create_widgets()
            else:
                self.create_unsupported_widgets()
        except ULError:
            self.create_unsupported_widgets(True)

    def init_scan_channel_info(self):
        num_channels = 0

        daqi_info = self.device_info.get_daqi_info()
        supported_channel_types = daqi_info.supported_channel_types

        # Add analog input channels if available
        if ChannelType.ANALOG in supported_channel_types:
            ai_info = self.device_info.get_ai_info()
            self.resolution = ai_info.resolution
            self.chan_list.append(0)
            self.chan_type_list.append(ChannelType.ANALOG)
            self.gain_list.append(ai_info.supported_ranges[0])
            num_channels += 1

            if ai_info.num_chans > 1:
                self.chan_list.append(ai_info.num_chans - 1)
                self.chan_type_list.append(ChannelType.ANALOG)
                self.gain_list.append(ai_info.supported_ranges[0])
                num_channels += 1

        # Add a digital input channel if available
        if self.device_info.supports_digital_io:
            chan_type = None
            if ChannelType.DIGITAL16 in supported_channel_types:
                chan_type = ChannelType.DIGITAL16
            elif ChannelType.DIGITAL8 in supported_channel_types:
                chan_type = ChannelType.DIGITAL8
            elif ChannelType.DIGITAL in supported_channel_types:
                chan_type = ChannelType.DIGITAL

            if chan_type is not None:
                dio_info = self.device_info.get_dio_info()
                port_info = dio_info.port_info[0]
                self.chan_list.append(port_info.type)
                self.chan_type_list.append(chan_type)
                self.gain_list.append(ULRange.NOTUSED)
                num_channels += 1

                # Configure all digital ports for input
                for port in dio_info.port_info:
                    if port.is_port_configurable:
                        ul.d_config_port(self.board_num, port.type,
                                         DigitalIODirection.IN)

        if self.device_info.supports_counters:
            chan_type = None
            if ChannelType.CTR16 in supported_channel_types:
                chan_type = ChannelType.CTR16
            elif ChannelType.CTRBANK0 in supported_channel_types:
                chan_type = ChannelType.CTRBANK0
            elif ChannelType.CTR in supported_channel_types:
                chan_type = ChannelType.CTR

            if chan_type is not None:
                self.chan_list.append(0)
                self.chan_type_list.append(chan_type)
                self.gain_list.append(ULRange.NOTUSED)
                num_channels += 1

        self.num_chans = num_channels

    def start_scan(self):
        rate = 100
        points_per_channel = 100
        total_count = points_per_channel * self.num_chans
        scan_options = ScanOptions.BACKGROUND | ScanOptions.CONTINUOUS

        # Allocate a buffer for the scan
        if self.resolution <= 16:
            self.memhandle = ul.win_buf_alloc(total_count)
        else:
            self.memhandle = ul.win_buf_alloc_32(total_count)

        # Check if the buffer was successfully allocated
        if not self.memhandle:
            messagebox.showerror("Error", "Failed to allocate memory")
            self.start_button["state"] = tk.NORMAL
            return

        try:
            # Run the scan
            ul.daq_in_scan(self.board_num, self.chan_list, self.chan_type_list,
                           self.gain_list, self.num_chans, rate, 0, total_count,
                           self.memhandle, scan_options)

            # Cast the memhandle to a ctypes pointer
            # Note: the ctypes array will only be valid until win_buf_free
            # is called.
            # A copy of the buffer can be created using win_buf_to_array
            # or win_buf_to_array_32 before the memory is freed. The copy can
            # be used at any time.
            if self.resolution <= 16:
                # Use the memhandle_as_ctypes_array method for devices with a
                # resolution <= 16
                self.array = cast(self.memhandle, POINTER(c_ushort))
            else:
                # Use the memhandle_as_ctypes_array_32 method for devices with a
                # resolution > 16
                self.array = cast(self.memhandle, POINTER(c_ulong))
        except ULError as e:
            # Free the allocated memory
            ul.win_buf_free(self.memhandle)
            show_ul_error(e)
            return

        # Start updating the displayed values
        self.update_displayed_values()

    def update_displayed_values(self):
        # Get the status from the device
        status, curr_count, curr_index = ul.get_status(
            self.board_num, FunctionType.DAQIFUNCTION)

        # Display the status info
        self.update_status_labels(status, curr_count, curr_index)

        # Display the values
        self.display_values(curr_index, curr_count)

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

    def display_values(self, curr_index, curr_count):
        per_channel_display_count = 10
        array = self.array
        chan_count = self.num_chans
        channel_text = []

        # Add a string to the array for each channel
        for _ in range(0, self.num_chans):
            channel_text.append("")

        # If no data has been gathered, don't add data to the labels
        if curr_count > 1:
            # curr_index points to the start of the last completed channel scan
            # that was transferred between the board and the data buffer. Based
            # on this, calculate the first index we want to display using
            # subtraction.
            first_index = max(
                curr_index - ((per_channel_display_count - 1) * chan_count), 0)
            chan_num = 0
            # Add (up to) the latest 10 values for each channel to the text
            for data_index in range(
                    first_index,
                    first_index + min(chan_count * per_channel_display_count,
                                      curr_count)):
                channel_text[chan_num] += str(array[data_index]) + "\n"
                if chan_num == self.num_chans - 1:
                    chan_num = 0
                else:
                    chan_num += 1

            # Update the labels for each channel
            for chan_num in range(0, self.num_chans):
                self.data_labels[chan_num]["text"] = channel_text[chan_num]

    def stop(self):
        ul.stop_background(self.board_num, FunctionType.DAQIFUNCTION)

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

        self.results_group = tk.LabelFrame(
            self, text="Results", padx=3, pady=3)
        self.results_group.pack(fill=tk.X, anchor=tk.NW, padx=3, pady=3)

        curr_row = 0
        status_left_label = tk.Label(self.results_group)
        status_left_label["text"] = "Status:"
        status_left_label.grid(row=curr_row, column=0, sticky=tk.W)

        self.status_label = tk.Label(self.results_group)
        self.status_label["text"] = "Idle"
        self.status_label.grid(row=curr_row, column=1, sticky=tk.W)

        curr_row += 1
        index_left_label = tk.Label(self.results_group)
        index_left_label["text"] = "Index:"
        index_left_label.grid(row=curr_row, column=0, sticky=tk.W)

        self.index_label = tk.Label(self.results_group)
        self.index_label["text"] = "-1"
        self.index_label.grid(row=curr_row, column=1, sticky=tk.W)

        curr_row += 1
        count_left_label = tk.Label(self.results_group)
        count_left_label["text"] = "Count:"
        count_left_label.grid(row=curr_row, column=0, sticky=tk.W)

        self.count_label = tk.Label(self.results_group)
        self.count_label["text"] = "0"
        self.count_label.grid(row=curr_row, column=1, sticky=tk.W)

        curr_row += 1
        self.data_frame = tk.Frame(self.results_group)
        self.data_frame.grid(row=curr_row, column=0,
                             columnspan=2, sticky=tk.W)

        chan_header_label = tk.Label(
            self.data_frame, justify=tk.LEFT, padx=3)
        chan_header_label["text"] = "Channel:"
        chan_header_label.grid(row=0, column=0)

        type_header_label = tk.Label(
            self.data_frame, justify=tk.LEFT, padx=3)
        type_header_label["text"] = "Type:"
        type_header_label.grid(row=1, column=0)

        range_header_label = tk.Label(
            self.data_frame, justify=tk.LEFT, padx=3)
        range_header_label["text"] = "Range:"
        range_header_label.grid(row=2, column=0)

        self.data_labels = []
        for chan_num in range(0, self.num_chans):
            column = chan_num + 1
            chan_label = tk.Label(self.data_frame, justify=tk.LEFT, padx=3)
            chan_num_item = self.chan_list[chan_num]
            if isinstance(chan_num_item, Enum):
                chan_label["text"] = self.chan_list[chan_num].name
            else:
                chan_label["text"] = str(self.chan_list[chan_num])
            chan_label.grid(row=0, column=column)

            type_label = tk.Label(self.data_frame, justify=tk.LEFT, padx=3)
            type_label["text"] = self.chan_type_list[chan_num].name
            type_label.grid(row=1, column=column)

            range_label = tk.Label(
                self.data_frame, justify=tk.LEFT, padx=3)
            range_label["text"] = self.gain_list[chan_num].name
            range_label.grid(row=2, column=column)

            data_label = tk.Label(self.data_frame, justify=tk.LEFT, padx=3)
            data_label.grid(row=3, column=column)
            self.data_labels.append(data_label)

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
    DaqInScan02(master=tk.Tk()).mainloop()
