from __future__ import absolute_import, division, print_function

import math

from builtins import *  # @UnusedWildImport
from tkinter import messagebox

from mcculw import ul
from mcculw.enums import Status, FunctionType, ScanOptions
from examples.ui.uiexample import UIExample
from examples.props.ao import AnalogOutputProps
from mcculw.ul import ULError
import tkinter as tk


class ULAO04(UIExample):
    def __init__(self, master=None):
        super(ULAO04, self).__init__(master)

        self.board_num = 0
        self.ao_props = AnalogOutputProps(self.board_num)

        self.create_widgets()

    def start_scan(self):
        # Build the data array
        self.low_chan = self.get_low_channel_num()
        self.high_chan = self.get_high_channel_num()
        self.num_chans = self.high_chan - self.low_chan + 1

        if self.low_chan > self.high_chan:
            messagebox.showerror(
                "Error",
                "Low Channel Number must be greater than or equal to High "
                "Channel Number")
            self.set_ui_idle_state()
            return

        points_per_channel = 1000
        rate = 1000
        num_points = self.num_chans * points_per_channel
        scan_options = (ScanOptions.BACKGROUND |
                        ScanOptions.CONTINUOUS | ScanOptions.SCALEDATA)
        ao_range = self.ao_props.available_ranges[0]

        self.memhandle = ul.scaled_win_buf_alloc(num_points)

        # Check if the buffer was successfully allocated
        if not self.memhandle:
            messagebox.showerror("Error", "Failed to allocate memory")
            self.start_button["state"] = tk.NORMAL
            return

        try:
            data_array = self.memhandle_as_ctypes_array_scaled(
                self.memhandle)
            frequencies = self.add_example_data(
                data_array, ao_range, self.num_chans, rate,
                points_per_channel)

            self.recreate_freq_frame()
            self.display_signal_info(frequencies)

            ul.a_out_scan(
                self.board_num, self.low_chan, self.high_chan, num_points,
                rate, ao_range, self.memhandle, scan_options)

            # Start updating the displayed values
            self.update_displayed_values()
        except ULError as e:
            self.show_ul_error(e)
            self.set_ui_idle_state()
            return

    def display_signal_info(self, frequencies):
        for channel_num in range(self.low_chan, self.high_chan + 1):
            curr_row = channel_num - self.low_chan
            self.freq_labels[curr_row]["text"] = str(
                frequencies[curr_row]) + " Hz"

    def add_example_data(self, data_array, ao_range, num_chans,
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

    def update_displayed_values(self):
        # Get the status from the device
        status, curr_count, curr_index = ul.get_status(
            self.board_num, FunctionType.AOFUNCTION)

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

    def recreate_freq_frame(self):
        low_chan = self.low_chan
        high_chan = self.high_chan

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

    def stop(self):
        ul.stop_background(self.board_num, FunctionType.AOFUNCTION)

    def exit(self):
        self.stop()
        self.master.destroy()

    def set_ui_idle_state(self):
        self.high_channel_entry["state"] = tk.NORMAL
        self.low_channel_entry["state"] = tk.NORMAL
        self.start_button["command"] = self.start
        self.start_button["text"] = "Start"

    def start(self):
        self.high_channel_entry["state"] = tk.DISABLED
        self.low_channel_entry["state"] = tk.DISABLED
        self.start_button["command"] = self.stop
        self.start_button["text"] = "Stop"
        self.start_scan()

    def get_low_channel_num(self):
        if self.ao_props.num_chans == 1:
            return 0
        try:
            return int(self.low_channel_entry.get())
        except ValueError:
            return 0

    def get_high_channel_num(self):
        if self.ao_props.num_chans == 1:
            return 0
        try:
            return int(self.high_channel_entry.get())
        except ValueError:
            return 0

    def validate_channel_entry(self, p):
        if p == '':
            return True
        try:
            value = int(p)
            if(value < 0 or value > self.ao_props.num_chans - 1):
                return False
        except ValueError:
            return False

        return True

    def create_widgets(self):
        '''Create the tkinter UI'''
        example_supported = (
            self.ao_props.num_chans > 0
            and self.ao_props.supports_scan)

        if example_supported:
            main_frame = tk.Frame(self)
            main_frame.pack(fill=tk.X, anchor=tk.NW)

            if self.ao_props.num_chans > 1:
                channel_vcmd = self.register(self.validate_channel_entry)

                curr_row = 0
                low_channel_entry_label = tk.Label(main_frame)
                low_channel_entry_label["text"] = "Low Channel Number:"
                low_channel_entry_label.grid(
                    row=curr_row, column=0, sticky=tk.W)

                self.low_channel_entry = tk.Spinbox(
                    main_frame, from_=0,
                    to=max(self.ao_props.num_chans - 1, 0),
                    validate='key', validatecommand=(channel_vcmd, '%P'))
                self.low_channel_entry.grid(
                    row=curr_row, column=1, sticky=tk.W)

                curr_row += 1
                high_channel_entry_label = tk.Label(main_frame)
                high_channel_entry_label["text"] = "High Channel Number:"
                high_channel_entry_label.grid(
                    row=curr_row, column=0, sticky=tk.W)

                self.high_channel_entry = tk.Spinbox(
                    main_frame, from_=0,
                    to=max(self.ao_props.num_chans - 1, 0),
                    validate='key', validatecommand=(channel_vcmd, '%P'))
                self.high_channel_entry.grid(
                    row=curr_row, column=1, sticky=tk.W)
                initial_value = min(self.ao_props.num_chans - 1, 3)
                self.high_channel_entry.delete(0, tk.END)
                self.high_channel_entry.insert(0, str(initial_value))

            scan_info_group = tk.LabelFrame(
                self, text="Scan Information", padx=3, pady=3)
            scan_info_group.pack(fill=tk.X, anchor=tk.NW, padx=3, pady=3)

            scan_info_group.grid_columnconfigure(1, weight=1)

            curr_row += 1
            status_left_label = tk.Label(scan_info_group)
            status_left_label["text"] = "Status:"
            status_left_label.grid(row=curr_row, column=0, sticky=tk.W)

            self.status_label = tk.Label(scan_info_group)
            self.status_label["text"] = "Idle"
            self.status_label.grid(row=curr_row, column=1, sticky=tk.W)

            curr_row += 1
            index_left_label = tk.Label(scan_info_group)
            index_left_label["text"] = "Index:"
            index_left_label.grid(row=curr_row, column=0, sticky=tk.W)

            self.index_label = tk.Label(scan_info_group)
            self.index_label["text"] = "-1"
            self.index_label.grid(row=curr_row, column=1, sticky=tk.W)

            curr_row += 1
            count_left_label = tk.Label(scan_info_group)
            count_left_label["text"] = "Count:"
            count_left_label.grid(row=curr_row, column=0, sticky=tk.W)

            self.count_label = tk.Label(scan_info_group)
            self.count_label["text"] = "0"
            self.count_label.grid(row=curr_row, column=1, sticky=tk.W)

            curr_row += 1
            self.freq_inner_frame = tk.Frame(scan_info_group)
            self.freq_inner_frame.grid(
                row=curr_row, column=0, columnspan=2, sticky=tk.W)

            self.freq_frame = tk.Frame(self.freq_inner_frame)
            self.freq_frame.grid()

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
    ULAO04(master=tk.Tk()).mainloop()
