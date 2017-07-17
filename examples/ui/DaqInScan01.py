from __future__ import absolute_import, division, print_function
from builtins import *  # @UnusedWildImport

from enum import Enum
from tkinter import messagebox

from mcculw import ul
from mcculw.enums import ChannelType, ULRange, DigitalIODirection
from examples.ui.uiexample import UIExample
from examples.props.ai import AnalogInputProps
from examples.props.counter import CounterProps
from examples.props.daqi import DaqInputProps
from examples.props.digital import DigitalProps
from mcculw.ul import ULError
import tkinter as tk


class DaqInScan01(UIExample):
    def __init__(self, master=None):
        super(DaqInScan01, self).__init__(master)

        self.board_num = 0
        self.daqi_props = DaqInputProps(self.board_num)
        self.ai_props = AnalogInputProps(self.board_num)
        self.digital_props = DigitalProps(self.board_num)
        self.counter_props = CounterProps(self.board_num)
        self.init_scan_channel_info()

        self.create_widgets()

    def init_scan_channel_info(self):
        num_channels = 0

        self.chan_list = []
        self.chan_type_list = []
        self.gain_list = []

        if self.daqi_props.is_supported:
            supported_channel_types = self.daqi_props.supported_channel_types
            self.resolution = 16

            # Add analog input channels if available
            if (ChannelType.ANALOG in supported_channel_types):
                self.resolution = self.ai_props.resolution
                self.chan_list.append(0)
                self.chan_type_list.append(ChannelType.ANALOG)
                self.gain_list.append(self.ai_props.available_ranges[0])
                num_channels += 1

                if(self.ai_props.num_ai_chans > 1):
                    self.chan_list.append(self.ai_props.num_ai_chans - 1)
                    self.chan_type_list.append(ChannelType.ANALOG)
                    self.gain_list.append(self.ai_props.available_ranges[0])
                    num_channels += 1

            # Add a digital input channel if available
            if self.digital_props.num_ports > 0:
                chan_type = None
                if ChannelType.DIGITAL16 in supported_channel_types:
                    chan_type = ChannelType.DIGITAL16
                elif ChannelType.DIGITAL8 in supported_channel_types:
                    chan_type = ChannelType.DIGITAL8
                elif ChannelType.DIGITAL in supported_channel_types:
                    chan_type = ChannelType.DIGITAL

                if chan_type != None:
                    port_info = self.digital_props.port_info[0]
                    self.chan_list.append(port_info.type)
                    self.chan_type_list.append(chan_type)
                    self.gain_list.append(ULRange.NOTUSED)
                    num_channels += 1

                    # Configure all digital ports for input
                    for port in self.digital_props.port_info:
                        if port.is_port_configurable:
                            ul.d_config_port(
                                self.board_num, port.type,
                                DigitalIODirection.IN)

            if self.counter_props.num_chans > 0:
                chan_type = None
                if ChannelType.CTR16 in supported_channel_types:
                    chan_type = ChannelType.CTR16
                elif ChannelType.CTRBANK0 in supported_channel_types:
                    chan_type = ChannelType.CTRBANK0
                elif ChannelType.CTR in supported_channel_types:
                    chan_type = ChannelType.CTR

                if chan_type != None:
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
            ul.daq_in_scan(
                self.board_num, self.chan_list, self.chan_type_list,
                self.gain_list, self.num_chans, rate, 0, total_count, memhandle, 0)

            # Cast the memhandle to a ctypes pointer
            # Note: the ctypes array will only be valid until win_buf_free
            # is called.
            # A copy of the buffer can be created using win_buf_to_array
            # or win_buf_to_array_32 before the memory is freed. The copy can
            # be used at any time.
            if self.resolution <= 16:
                # Use the memhandle_as_ctypes_array method for devices with a
                # resolution <= 16
                array = self.memhandle_as_ctypes_array(memhandle)
            else:
                # Use the memhandle_as_ctypes_array_32 method for devices with
                # a resolution > 16
                array = self.memhandle_as_ctypes_array_32(memhandle)

            # Display the values
            self.display_values(
                array, total_count)
        except ULError as e:
            self.show_ul_error(e)
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
        if self.daqi_props.is_supported:
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
        else:
            self.create_unsupported_widgets(self.board_num)


if __name__ == "__main__":
    # Start the example
    DaqInScan01(master=tk.Tk()).mainloop()
