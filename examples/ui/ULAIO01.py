from __future__ import absolute_import, division, print_function

import math

from builtins import *  # @UnusedWildImport
from mcculw import ul
from mcculw.enums import ScanOptions, Status, FunctionType
from mcculw.ul import ULError
from tkinter import messagebox

from examples.props.ai import AnalogInputProps
from examples.props.ao import AnalogOutputProps
from examples.ui.uiexample import UIExample
import tkinter as tk


class ULAIO01(UIExample):
    def __init__(self, master=None):
        super(ULAIO01, self).__init__(master)

        self.board_num = 0
        self.ai_props = AnalogInputProps(self.board_num)
        self.ao_props = AnalogOutputProps(self.board_num)

        # Initialize tkinter
        self.create_widgets()

    def start_input_scan(self):
        self.input_low_chan = self.get_input_low_channel_num()
        self.input_high_chan = self.get_input_high_channel_num()
        self.num_input_chans = (
            self.input_high_chan - self.input_low_chan + 1)

        if self.input_low_chan > self.input_high_chan:
            messagebox.showerror(
                "Error",
                "Low Channel Number must be greater than or equal to High "
                "Channel Number")
            self.set_input_ui_idle_state()
            return

        rate = 100
        points_per_channel = 1000
        total_count = points_per_channel * self.num_input_chans
        range_ = self.ai_props.available_ranges[0]
        scan_options = ScanOptions.BACKGROUND | ScanOptions.CONTINUOUS

        # Allocate a buffer for the scan
        if self.ai_props.resolution <= 16:
            # Use the win_buf_alloc method for devices with a resolution <=
            # 16
            self.input_memhandle = ul.win_buf_alloc(total_count)
        else:
            # Use the win_buf_alloc_32 method for devices with a resolution
            # > 16
            self.input_memhandle = ul.win_buf_alloc_32(total_count)

        if not self.input_memhandle:
            messagebox.showerror("Error", "Failed to allocate memory")
            self.set_input_ui_idle_state()
            return

        # Create the frames that will hold the data
        self.recreate_input_data_frame()

        try:
            # Run the scan
            ul.a_in_scan(
                self.board_num, self.input_low_chan, self.input_high_chan,
                total_count, rate, range_, self.input_memhandle,
                scan_options)
        except ULError as e:
            self.show_ul_error(e)
            self.set_input_ui_idle_state()
            return

        # Convert the input_memhandle to a ctypes array
        # Note: the ctypes array will no longer be valid after win_buf_free is called.
        # A copy of the buffer can be created using win_buf_to_array
        # or win_buf_to_array_32 before the memory is freed. The copy can
        # be used at any time.
        if self.ai_props.resolution <= 16:
            # Use the memhandle_as_ctypes_array method for devices with a
            # resolution <= 16
            self.ctypes_array = self.memhandle_as_ctypes_array(
                self.input_memhandle)
        else:
            # Use the memhandle_as_ctypes_array_32 method for devices with a
            # resolution > 16
            self.ctypes_array = self.memhandle_as_ctypes_array_32(
                self.input_memhandle)

        # Start updating the displayed values
        self.update_input_displayed_values(range_)

    def update_input_displayed_values(self, range_):
        # Get the status from the device
        status, curr_count, curr_index = ul.get_status(
            self.board_num, FunctionType.AIFUNCTION)

        # Display the status info
        self.update_input_status_labels(status, curr_count, curr_index)

        # Display the values
        self.display_input_values(range_, curr_index, curr_count)

        # Call this method again until the stop_input button is pressed
        if status == Status.RUNNING:
            self.after(100, self.update_input_displayed_values, range_)
        else:
            # Free the allocated memory
            ul.win_buf_free(self.input_memhandle)
            self.set_input_ui_idle_state()

    def update_input_status_labels(self, status, curr_count, curr_index):
        if status == Status.IDLE:
            self.input_status_label["text"] = "Idle"
        else:
            self.input_status_label["text"] = "Running"

        self.input_index_label["text"] = str(curr_index)
        self.input_count_label["text"] = str(curr_count)

    def display_input_values(self, range_, curr_index, curr_count):
        per_channel_display_count = 10
        array = self.ctypes_array
        low_chan = self.input_low_chan
        high_chan = self.input_high_chan
        channel_text = []

        # Add the headers
        for chan_num in range(low_chan, high_chan + 1):
            channel_text.append("Channel " + str(chan_num) + "\n")

        # If no data has been gathered, don't add data to the labels
        if curr_count > 1:
            chan_count = high_chan - low_chan + 1

            chan_num = low_chan
            # curr_index points to the start_input of the last completed channel scan that
            # was transferred between the board and the data buffer. Based on this,
            # calculate the first index we want to display using subtraction.
            first_index = max(
                curr_index - ((per_channel_display_count - 1) * chan_count),
                0)
            # Add (up to) the latest 10 values for each channel to the text
            for data_index in range(
                    first_index,
                    first_index + min(
                        chan_count * per_channel_display_count,
                        curr_count)):

                raw_value = array[data_index]
                if self.ai_props.resolution <= 16:
                    eng_value = ul.to_eng_units(
                        self.board_num, range_, raw_value)
                else:
                    eng_value = ul.to_eng_units_32(
                        self.board_num, range_, raw_value)
                channel_text[chan_num - low_chan] += (
                    '{:.3f}'.format(eng_value) + "\n")
                if chan_num == high_chan:
                    chan_num = low_chan
                else:
                    chan_num += 1

        # Update the labels for each channel
        for chan_num in range(low_chan, high_chan + 1):
            chan_index = chan_num - low_chan
            self.chan_labels[chan_index]["text"] = channel_text[chan_index]

    def recreate_input_data_frame(self):
        low_chan = self.input_low_chan
        high_chan = self.input_high_chan

        new_data_frame = tk.Frame(self.input_inner_data_frame)

        self.chan_labels = []
        # Add the labels for each channel
        for chan_num in range(low_chan, high_chan + 1):
            chan_label = tk.Label(new_data_frame, justify=tk.LEFT, padx=3)
            chan_label.grid(row=0, column=chan_num - low_chan)
            self.chan_labels.append(chan_label)

        self.data_frame.destroy()
        self.data_frame = new_data_frame
        self.data_frame.grid()

    def exit(self):
        self.stop_input()
        self.stop_output()
        self.master.destroy()

    def start_output_scan(self):
        # Build the data array
        self.output_low_chan = self.get_output_low_channel_num()
        self.output_high_chan = self.get_output_high_channel_num()
        self.num_output_chans = (
            self.output_high_chan - self.output_low_chan + 1)

        if self.output_low_chan > self.output_high_chan:
            messagebox.showerror(
                "Error",
                "Low Channel Number must be greater than or equal to High "
                "Channel Number")
            self.set_ui_idle_state()
            return

        points_per_channel = 1000
        rate = 1000
        num_points = self.num_output_chans * points_per_channel
        scan_options = (ScanOptions.BACKGROUND |
                        ScanOptions.CONTINUOUS | ScanOptions.SCALEDATA)
        ao_range = self.ao_props.available_ranges[0]

        self.output_memhandle = ul.scaled_win_buf_alloc(num_points)

        # Check if the buffer was successfully allocated
        if not self.output_memhandle:
            messagebox.showerror("Error", "Failed to allocate memory")
            self.start_button["state"] = tk.NORMAL
            return

        try:
            data_array = self.memhandle_as_ctypes_array_scaled(
                self.output_memhandle)
            frequencies = self.add_output_example_data(
                data_array, ao_range, self.num_output_chans, rate,
                points_per_channel)

            self.recreate_freq_frame()
            self.display_output_signal_info(frequencies)

            ul.a_out_scan(
                self.board_num, self.output_low_chan, self.output_high_chan,
                num_points, rate, ao_range, self.output_memhandle,
                scan_options)

            # Start updating the displayed values
            self.update_output_displayed_values()
        except ULError as e:
            self.show_ul_error(e)
            self.set_ui_idle_state()
            return

    def display_output_signal_info(self, frequencies):
        for channel_num in range(
                self.output_low_chan, self.output_high_chan + 1):
            curr_row = channel_num - self.output_low_chan
            self.freq_labels[curr_row]["text"] = str(
                frequencies[curr_row]) + " Hz"

    def add_output_example_data(self, data_array, ao_range, num_chans,
                                rate, points_per_channel):
        # Calculate frequencies that will work well with the size of the array
        frequencies = []
        for channel_num in range(0, num_chans):
            frequencies.append(
                (channel_num + 1) / (points_per_channel / rate))

        # Calculate an amplitude and y-offset for the signal
        # to fill the analog output range
        amplitude = (ao_range.range_max - ao_range.range_min) / 2
        y_offset = (amplitude + ao_range.range_min) / 2

        # Fill the array with sine wave data at the calculated frequencies.
        # Note that since we are using the SCALEDATA option, the values
        # added to data_array are the actual voltage values that the device
        # will output
        data_index = 0
        for point_num in range(0, points_per_channel):
            for channel_num in range(0, num_chans):
                freq = frequencies[channel_num]
                value = amplitude * math.sin(
                    2 * math.pi * freq * point_num / rate) + y_offset
                data_array[data_index] = value
                data_index += 1

        return frequencies

    def update_output_displayed_values(self):
        # Get the status from the device
        status, curr_count, curr_index = ul.get_status(
            self.board_num, FunctionType.AOFUNCTION)

        # Display the status info
        self.update_output_status_labels(status, curr_count, curr_index)

        # Call this method again until the stop button is pressed
        if status == Status.RUNNING:
            self.after(100, self.update_output_displayed_values)
        else:
            # Free the allocated memory
            ul.win_buf_free(self.output_memhandle)
            self.set_output_ui_idle_state()

    def update_output_status_labels(self, status, curr_count, curr_index):
        if status == Status.IDLE:
            self.output_status_label["text"] = "Idle"
        else:
            self.output_status_label["text"] = "Running"

        self.output_index_label["text"] = str(curr_index)
        self.output_count_label["text"] = str(curr_count)

    def recreate_freq_frame(self):
        low_chan = self.output_low_chan
        high_chan = self.output_high_chan

        new_freq_frame = tk.Frame(self.freq_inner_frame)

        curr_row = 0
        self.freq_labels = []
        for chan_num in range(low_chan, high_chan + 1):
            curr_row += 1
            channel_label = tk.Label(new_freq_frame)
            channel_label["text"] = (
                "Channel " + str(chan_num) + " Frequency:")
            channel_label.grid(row=curr_row, column=0, sticky=tk.W)

            freq_label = tk.Label(new_freq_frame)
            freq_label.grid(row=curr_row, column=1, sticky=tk.W)
            self.freq_labels.append(freq_label)

        self.freq_frame.destroy()
        self.freq_frame = new_freq_frame
        self.freq_frame.grid()

    def stop_output(self):
        ul.stop_background(self.board_num, FunctionType.AOFUNCTION)

    def set_output_ui_idle_state(self):
        self.output_high_channel_entry["state"] = tk.NORMAL
        self.output_low_channel_entry["state"] = tk.NORMAL
        self.output_start_button["command"] = self.start_output
        self.output_start_button["text"] = "Start Analog Output"

    def start_output(self):
        self.output_high_channel_entry["state"] = tk.DISABLED
        self.output_low_channel_entry["state"] = tk.DISABLED
        self.output_start_button["command"] = self.stop_output
        self.output_start_button["text"] = "Stop Analog Output"
        self.start_output_scan()

    def stop_input(self):
        ul.stop_background(self.board_num, FunctionType.AIFUNCTION)

    def set_input_ui_idle_state(self):
        self.input_high_channel_entry["state"] = tk.NORMAL
        self.input_low_channel_entry["state"] = tk.NORMAL
        self.input_start_button["command"] = self.start_input
        self.input_start_button["text"] = "Start Analog Input"

    def start_input(self):
        self.input_high_channel_entry["state"] = tk.DISABLED
        self.input_low_channel_entry["state"] = tk.DISABLED
        self.input_start_button["command"] = self.stop_input
        self.input_start_button["text"] = "Stop Analog Input"
        self.start_input_scan()

    def get_input_low_channel_num(self):
        if self.ai_props.num_ai_chans == 1:
            return 0
        try:
            return int(self.input_low_channel_entry.get())
        except ValueError:
            return 0

    def get_input_high_channel_num(self):
        if self.ai_props.num_ai_chans == 1:
            return 0
        try:
            return int(self.input_high_channel_entry.get())
        except ValueError:
            return 0

    def get_output_low_channel_num(self):
        if self.ao_props.num_chans == 1:
            return 0
        try:
            return int(self.output_low_channel_entry.get())
        except ValueError:
            return 0

    def get_output_high_channel_num(self):
        if self.ao_props.num_chans == 1:
            return 0
        try:
            return int(self.output_high_channel_entry.get())
        except ValueError:
            return 0

    def validate_channel_entry(self, p):
        if p == '':
            return True
        try:
            value = int(p)
            if(value < 0 or value > self.ai_props.num_ai_chans - 1):
                return False
        except ValueError:
            return False

        return True

    def create_widgets(self):
        '''Create the tkinter UI'''
        example_supported = (
            self.ao_props.num_chans > 0
            and self.ao_props.supports_scan
            and self.ai_props.num_ai_chans > 0
            and self.ai_props.supports_scan)

        if example_supported:
            channel_vcmd = self.register(self.validate_channel_entry)

            main_frame = tk.Frame(self)
            main_frame.pack(fill=tk.X, anchor=tk.NW)

            input_groupbox = tk.LabelFrame(main_frame, text="Analog Input")
            input_groupbox.pack(side=tk.LEFT, anchor=tk.NW)

            if self.ai_props.num_ai_chans > 1:
                curr_row = 0

                input_channels_frame = tk.Frame(input_groupbox)
                input_channels_frame.pack(fill=tk.X, anchor=tk.NW)

                input_low_channel_entry_label = tk.Label(
                    input_channels_frame)
                input_low_channel_entry_label["text"] = (
                    "Low Channel Number:")
                input_low_channel_entry_label.grid(
                    row=curr_row, column=0, sticky=tk.W)

                self.input_low_channel_entry = tk.Spinbox(
                    input_channels_frame, from_=0,
                    to=max(self.ai_props.num_ai_chans - 1, 0),
                    validate='key', validatecommand=(channel_vcmd, '%P'))
                self.input_low_channel_entry.grid(
                    row=curr_row, column=1, sticky=tk.W)

                curr_row += 1
                input_high_channel_entry_label = tk.Label(
                    input_channels_frame)
                input_high_channel_entry_label["text"] = (
                    "High Channel Number:")
                input_high_channel_entry_label.grid(
                    row=curr_row, column=0, sticky=tk.W)

                self.input_high_channel_entry = tk.Spinbox(
                    input_channels_frame, from_=0,
                    to=max(self.ai_props.num_ai_chans - 1, 0),
                    validate='key', validatecommand=(channel_vcmd, '%P'))
                self.input_high_channel_entry.grid(
                    row=curr_row, column=1, sticky=tk.W)
                initial_value = min(self.ai_props.num_ai_chans - 1, 3)
                self.input_high_channel_entry.delete(0, tk.END)
                self.input_high_channel_entry.insert(0, str(initial_value))

                curr_row += 1

            self.input_start_button = tk.Button(input_groupbox)
            self.input_start_button["text"] = "Start Analog Input"
            self.input_start_button["command"] = self.start_input
            self.input_start_button.pack(
                fill=tk.X, anchor=tk.NW, padx=3, pady=3)

            self.input_results_group = tk.LabelFrame(
                input_groupbox, text="Results", padx=3, pady=3)
            self.input_results_group.pack(
                fill=tk.X, anchor=tk.NW, padx=3, pady=3)

            self.input_results_group.grid_columnconfigure(1, weight=1)

            curr_row = 0
            input_status_left_label = tk.Label(self.input_results_group)
            input_status_left_label["text"] = "Status:"
            input_status_left_label.grid(
                row=curr_row, column=0, sticky=tk.W)

            self.input_status_label = tk.Label(self.input_results_group)
            self.input_status_label["text"] = "Idle"
            self.input_status_label.grid(
                row=curr_row, column=1, sticky=tk.W)

            curr_row += 1
            input_index_left_label = tk.Label(self.input_results_group)
            input_index_left_label["text"] = "Index:"
            input_index_left_label.grid(row=curr_row, column=0, sticky=tk.W)

            self.input_index_label = tk.Label(self.input_results_group)
            self.input_index_label["text"] = "-1"
            self.input_index_label.grid(row=curr_row, column=1, sticky=tk.W)

            curr_row += 1
            input_count_left_label = tk.Label(self.input_results_group)
            input_count_left_label["text"] = "Count:"
            input_count_left_label.grid(row=curr_row, column=0, sticky=tk.W)

            self.input_count_label = tk.Label(self.input_results_group)
            self.input_count_label["text"] = "0"
            self.input_count_label.grid(row=curr_row, column=1, sticky=tk.W)

            curr_row += 1
            self.input_inner_data_frame = tk.Frame(self.input_results_group)
            self.input_inner_data_frame.grid(
                row=curr_row, column=0, columnspan=2, sticky=tk.W)

            self.data_frame = tk.Frame(self.input_inner_data_frame)
            self.data_frame.grid()

            output_groupbox = tk.LabelFrame(
                main_frame, text="Analog Output")
            output_groupbox.pack(side=tk.RIGHT, anchor=tk.NW)

            if self.ao_props.num_chans > 1:
                curr_row = 0
                output_channels_frame = tk.Frame(output_groupbox)
                output_channels_frame.pack(fill=tk.X, anchor=tk.NW)

                output_low_channel_entry_label = tk.Label(
                    output_channels_frame)
                output_low_channel_entry_label["text"] = (
                    "Low Channel Number:")
                output_low_channel_entry_label.grid(
                    row=curr_row, column=0, sticky=tk.W)

                self.output_low_channel_entry = tk.Spinbox(
                    output_channels_frame, from_=0,
                    to=max(self.ao_props.num_chans - 1, 0),
                    validate='key', validatecommand=(channel_vcmd, '%P'))
                self.output_low_channel_entry.grid(
                    row=curr_row, column=1, sticky=tk.W)

                curr_row += 1
                output_high_channel_entry_label = tk.Label(
                    output_channels_frame)
                output_high_channel_entry_label["text"] = (
                    "High Channel Number:")
                output_high_channel_entry_label.grid(
                    row=curr_row, column=0, sticky=tk.W)

                self.output_high_channel_entry = tk.Spinbox(
                    output_channels_frame, from_=0,
                    to=max(self.ao_props.num_chans - 1, 0),
                    validate='key', validatecommand=(channel_vcmd, '%P'))
                self.output_high_channel_entry.grid(
                    row=curr_row, column=1, sticky=tk.W)
                initial_value = min(self.ao_props.num_chans - 1, 3)
                self.output_high_channel_entry.delete(0, tk.END)
                self.output_high_channel_entry.insert(0, str(initial_value))

            self.output_start_button = tk.Button(output_groupbox)
            self.output_start_button["text"] = "Start Analog Output"
            self.output_start_button["command"] = self.start_output
            self.output_start_button.pack(
                fill=tk.X, anchor=tk.NW, padx=3, pady=3)

            output_scan_info_group = tk.LabelFrame(
                output_groupbox, text="Scan Information", padx=3, pady=3)
            output_scan_info_group.pack(
                fill=tk.X, anchor=tk.NW, padx=3, pady=3)

            output_scan_info_group.grid_columnconfigure(1, weight=1)

            curr_row = 0
            output_status_left_label = tk.Label(output_scan_info_group)
            output_status_left_label["text"] = "Status:"
            output_status_left_label.grid(
                row=curr_row, column=0, sticky=tk.W)

            self.output_status_label = tk.Label(output_scan_info_group)
            self.output_status_label["text"] = "Idle"
            self.output_status_label.grid(
                row=curr_row, column=1, sticky=tk.W)

            curr_row += 1
            output_index_left_label = tk.Label(output_scan_info_group)
            output_index_left_label["text"] = "Index:"
            output_index_left_label.grid(
                row=curr_row, column=0, sticky=tk.W)

            self.output_index_label = tk.Label(output_scan_info_group)
            self.output_index_label["text"] = "-1"
            self.output_index_label.grid(
                row=curr_row, column=1, sticky=tk.W)

            curr_row += 1
            output_count_left_label = tk.Label(output_scan_info_group)
            output_count_left_label["text"] = "Count:"
            output_count_left_label.grid(
                row=curr_row, column=0, sticky=tk.W)

            self.output_count_label = tk.Label(output_scan_info_group)
            self.output_count_label["text"] = "0"
            self.output_count_label.grid(
                row=curr_row, column=1, sticky=tk.W)

            curr_row += 1
            self.freq_inner_frame = tk.Frame(output_scan_info_group)
            self.freq_inner_frame.grid(
                row=curr_row, column=0, columnspan=2, sticky=tk.W)

            self.freq_frame = tk.Frame(self.freq_inner_frame)
            self.freq_frame.grid()

            button_frame = tk.Frame(self)
            button_frame.pack(fill=tk.X, side=tk.RIGHT, anchor=tk.SE)

            self.quit_button = tk.Button(button_frame)
            self.quit_button["text"] = "Quit"
            self.quit_button["command"] = self.exit
            self.quit_button.grid(row=0, column=1, padx=3, pady=3)
        else:
            self.create_unsupported_widgets(self.board_num)


if __name__ == "__main__":
    # Start the example
    ULAIO01(master=tk.Tk()).mainloop()
