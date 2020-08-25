"""
File:                       DaqInScan01.py

Library Call Demonstrated:  mcculw.ul.daq_in_scan()

Purpose:                    Synchronously scans Analog channels,
                            digital ports and counters in the foreground.

Demonstration:              Collects data on first and last analog channels, a
                            digital channel, and a counter channel if available.

Other Library Calls:        mcculw.ul.d_config_port()
                            mcculw.ul.win_buf_alloc()
                            mcculw.ul.win_buf_alloc_32()
                            mcculw.ul.win_buf_free()

Special Requirements:       Device must support mcculw.ul.daq_in_scan().
"""
from __future__ import absolute_import, division, print_function
from builtins import *  # @UnusedWildImport

import tkinter as tk
from tkinter import messagebox
from enum import Enum
from ctypes import cast, POINTER, c_ushort, c_ulong

from mcculw import ul
from mcculw.enums import ChannelType, ULRange, DigitalIODirection
from mcculw.ul import ULError
from mcculw.device_info import DaqDeviceInfo

try:
    from ui_examples_util import UIExample, show_ul_error
except ImportError:
    from .ui_examples_util import UIExample, show_ul_error


class DaqInScan01(UIExample):
    def __init__(self, master=None):
        super(DaqInScan01, self).__init__(master)
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

            ai_info = self.device_info.get_ai_info()
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
        points_per_channel = 10
        total_count = points_per_channel * self.num_chans

        # Allocate a buffer for the scan
        if self.resolution <= 16:
            memhandle = ul.win_buf_alloc(total_count)
        else:
            memhandle = ul.win_buf_alloc_32(total_count)

        # Check if the buffer was successfully allocated
        if not memhandle:
            messagebox.showerror("Error", "Failed to allocate memory")
            self.start_button["state"] = tk.NORMAL
            return

        try:
            # Run the scan
            ul.daq_in_scan(self.board_num, self.chan_list, self.chan_type_list,
                           self.gain_list, self.num_chans, rate, 0, total_count,
                           memhandle, 0)

            # Cast the memhandle to a ctypes pointer
            # Note: the ctypes array will only be valid until win_buf_free
            # is called.
            # A copy of the buffer can be created using win_buf_to_array
            # or win_buf_to_array_32 before the memory is freed. The copy can
            # be used at any time.
            if self.resolution <= 16:
                # Use the memhandle_as_ctypes_array method for devices with a
                # resolution <= 16
                array = cast(memhandle, POINTER(c_ushort))
            else:
                # Use the memhandle_as_ctypes_array_32 method for devices with
                # a resolution > 16
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
        channel_text = []

        # Add a string to the array for each channel
        for _ in range(0, self.num_chans):
            channel_text.append("")

        # Add (up to) the first 10 values for each channel to the text
        chan_num = 0
        for data_index in range(0, min(self.num_chans * 10, total_count)):
            channel_text[chan_num] += str(array[data_index]) + "\n"
            if chan_num == self.num_chans - 1:
                chan_num = 0
            else:
                chan_num += 1

        # Update the labels for each channel
        for chan_num in range(0, self.num_chans):
            self.data_labels[chan_num]["text"] = channel_text[chan_num]

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

        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.X, anchor=tk.NW)

        self.results_group = tk.LabelFrame(
            self, text="Results", padx=3, pady=3)
        self.results_group.pack(fill=tk.X, anchor=tk.NW, padx=3, pady=3)

        self.data_frame = tk.Frame(self.results_group)
        self.data_frame.grid()

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
    DaqInScan01(master=tk.Tk()).mainloop()
