from __future__ import absolute_import, division, print_function

import math

from builtins import *  # @UnusedWildImport
from tkinter import messagebox

from mcculw import ul
from mcculw.enums import Status, FunctionType, ScanOptions, ChannelType, \
    ULRange, DigitalIODirection
from examples.ui.uiexample import UIExample
from examples.props.ao import AnalogOutputProps
from examples.props.daqo import DaqOutputProps
from examples.props.digital import DigitalProps
from mcculw.ul import ULError
import tkinter as tk


class DaqOutScan01(UIExample):
    def __init__(self, master=None):
        super(DaqOutScan01, self).__init__(master)

        self.board_num = 0
        self.daqo_props = DaqOutputProps(self.board_num)
        if self.daqo_props.is_supported:
            self.ao_props = AnalogOutputProps(self.board_num)
            self.digital_props = DigitalProps(self.board_num)
            self.init_scan_channel_info()

        self.create_widgets()

    def init_scan_channel_info(self):
        self.num_chans = 2

        self.chan_list = []
        self.chan_type_list = []
        self.gain_list = []

        supported_channel_types = self.daqo_props.supported_channel_types

        # Add an analog output channel
        self.chan_list.append(0)
        self.chan_type_list.append(ChannelType.ANALOG)
        self.gain_list.append(self.ao_props.available_ranges[0])

        # Add a digital output channel
        if ChannelType.DIGITAL16 in supported_channel_types:
            chan_type = ChannelType.DIGITAL16
        elif ChannelType.DIGITAL8 in supported_channel_types:
            chan_type = ChannelType.DIGITAL8
        else:
            chan_type = ChannelType.DIGITAL

        port_info = self.digital_props.port_info[0]
        self.chan_list.append(port_info.type)
        self.chan_type_list.append(chan_type)
        self.gain_list.append(ULRange.NOTUSED)

        # Configure all digital ports for output
        for port in self.digital_props.port_info:
            if port.is_port_configurable:
                ul.d_config_port(
                    self.board_num, port.type,
                    DigitalIODirection.OUT)

    def start_scan(self):
        # Build the data array
        points_per_channel = 1000
        rate = 1000
        num_points = self.num_chans * points_per_channel
        scan_options = ScanOptions.BACKGROUND | ScanOptions.CONTINUOUS
        ao_range = self.ao_props.available_ranges[0]

        self.memhandle = ul.win_buf_alloc(num_points)
        # Check if the buffer was successfully allocated
        if not self.memhandle:
            messagebox.showerror("Error", "Failed to allocate memory")
            self.start_button["state"] = tk.NORMAL
            return

        try:
            data_array = self.memhandle_as_ctypes_array(self.memhandle)
            freq = self.add_example_data(
                data_array, ao_range, rate, points_per_channel)
            self.freq_label["text"] = str(freq) + "Hz"

            ul.daq_out_scan(
                self.board_num, self.chan_list, self.chan_type_list, self.gain_list,
                self.num_chans, rate, num_points, self.memhandle, scan_options)

            # Start updating the displayed values
            self.update_displayed_values()
        except ULError as e:
            self.show_ul_error(e)
            self.set_ui_idle_state()
            return

    def display_signal_info(self, frequencies):
        for channel_num in range(0, min(self.ao_props.num_chans, 4)):
            self.freq_labels[channel_num]["text"] = str(
                frequencies[channel_num]) + " Hz"

    def add_example_data(self, data_array, ao_range, rate, points_per_channel):
        # Calculate a frequency that will work well with the size of the array
        freq = rate / points_per_channel

        # Calculate an amplitude and y-offset for the signal
        # to fill the analog output range
        amplitude = (ao_range.range_max - ao_range.range_min) / 2
        y_offset = (amplitude + ao_range.range_min) / 2

        # Fill the array with sine wave data for the analog channel, and square wave data for all bits
        # on the digital port.
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

    def recreate_data_frame(self):
        low_chan = self.low_chan
        high_chan = self.high_chan

        new_data_frame = tk.Frame(self.inner_data_frame)

        self.chan_labels = []
        # Add the labels for each channel
        for chan_num in range(low_chan, high_chan + 1):
            chan_label = tk.Label(new_data_frame, justify=tk.LEFT, padx=3)
            chan_label.grid(row=0, column=chan_num - low_chan)
            self.chan_labels.append(chan_label)

        self.data_frame.destroy()
        self.data_frame = new_data_frame
        self.data_frame.grid()

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

    def get_low_channel_num(self):
        try:
            return int(self.low_channel_entry.get())
        except ValueError:
            return 0

    def get_high_channel_num(self):
        try:
            return int(self.high_channel_entry.get())
        except ValueError:
            return 0

    def validate_channel_entry(self, p):
        if p == '':
            return True
        try:
            value = int(p)
            if(value < 0 or value > self.ai_props.num_chans - 1):
                return False
        except ValueError:
            return False

        return True

    def create_widgets(self):
        '''Create the tkinter UI'''
        example_supported = self.daqo_props.is_supported

        if example_supported:
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
        else:
            self.create_unsupported_widgets(self.board_num)


if __name__ == "__main__":
    # Start the example
    DaqOutScan01(master=tk.Tk()).mainloop()
