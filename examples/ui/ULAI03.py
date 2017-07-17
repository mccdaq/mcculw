from __future__ import absolute_import, division, print_function

from builtins import *  # @UnusedWildImport
from tkinter import messagebox

from mcculw import ul
from mcculw.enums import ScanOptions, Status, FunctionType
from examples.props.ai import AnalogInputProps
from examples.ui.uiexample import UIExample
from mcculw.ul import ULError
import tkinter as tk


class ULAI03(UIExample):
    def __init__(self, master=None):
        super(ULAI03, self).__init__(master)

        self.board_num = 0
        self.ai_props = AnalogInputProps(self.board_num)

        self.create_widgets()

    def start_scan(self):
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

        rate = 100
        points_per_channel = 1000
        total_count = points_per_channel * self.num_chans
        ai_range = self.ai_props.available_ranges[0]

        # Allocate a buffer for the scan
        if self.ai_props.resolution <= 16:
            # Use the win_buf_alloc method for devices with a resolution <=
            # 16
            self.memhandle = ul.win_buf_alloc(total_count)
            # Convert the memhandle to a ctypes array
            # Use the memhandle_as_ctypes_array method for devices with a
            # resolution <= 16
            self.ctypes_array = self.memhandle_as_ctypes_array(
                self.memhandle)
        else:
            # Use the win_buf_alloc_32 method for devices with a resolution
            # > 16
            self.memhandle = ul.win_buf_alloc_32(total_count)
            # Use the memhandle_as_ctypes_array_32 method for devices with a
            # resolution > 16
            self.ctypes_array = self.memhandle_as_ctypes_array_32(
                self.memhandle)

        # Note: the ctypes array will no longer be valid after
        # win_buf_free is called.
        # A copy of the buffer can be created using win_buf_to_array
        # or win_buf_to_array_32 before the memory is freed. The copy
        # can be used at any time.

        # Check if the buffer was successfully allocated
        if not self.memhandle:
            messagebox.showerror("Error", "Failed to allocate memory")
            self.set_ui_idle_state()
            return

        # Create the frames that will hold the data
        self.recreate_data_frame()

        try:
            # Start the scan
            ul.a_in_scan(
                self.board_num, self.low_chan, self.high_chan, total_count,
                rate, ai_range, self.memhandle, ScanOptions.BACKGROUND)
        except ULError as e:
            self.show_ul_error(e)
            self.set_ui_idle_state()
            return

        # Start updating the displayed values
        self.update_displayed_values()

    def update_displayed_values(self):
        # Get the status from the device
        status, curr_count, curr_index = ul.get_status(
            self.board_num, FunctionType.AIFUNCTION)

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
            # Stop the background operation (this is required even if the
            # scan completes successfully)
            ul.stop_background(self.board_num, FunctionType.AIFUNCTION)
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
        array = self.ctypes_array
        low_chan = self.low_chan
        high_chan = self.high_chan
        channel_text = []

        # Add the headers
        for chan_num in range(low_chan, high_chan + 1):
            channel_text.append("Channel " + str(chan_num) + "\n")

        # If no data has been gathered, don't add data to the labels
        if curr_count > 1:
            chan_count = high_chan - low_chan + 1

            chan_num = low_chan
            # curr_index points to the start of the last completed channel
            # scan that was transferred between the board and the data
            # buffer. Based on this, calculate the first index we want to
            # display using subtraction.
            first_index = max(
                curr_index - ((per_channel_display_count - 1) * chan_count),
                0)
            # Add (up to) the latest 10 values for each channel to the text
            for data_index in range(
                    first_index,
                    first_index + min(
                        chan_count * per_channel_display_count,
                        curr_count)):
                channel_text[chan_num -
                             low_chan] += str(array[data_index]) + "\n"
                if chan_num == high_chan:
                    chan_num = low_chan
                else:
                    chan_num += 1

        # Update the labels for each channel
        for chan_num in range(low_chan, high_chan + 1):
            chan_index = chan_num - low_chan
            self.chan_labels[chan_index]["text"] = channel_text[chan_index]

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
        ul.stop_background(self.board_num, FunctionType.AIFUNCTION)

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
        if self.ai_props.num_ai_chans == 1:
            return 0
        try:
            return int(self.low_channel_entry.get())
        except ValueError:
            return 0

    def get_high_channel_num(self):
        if self.ai_props.num_ai_chans == 1:
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
            if(value < 0 or value > self.ai_props.num_ai_chans - 1):
                return False
        except ValueError:
            return False

        return True

    def create_widgets(self):
        '''Create the tkinter UI'''
        example_supported = (
            self.ai_props.num_ai_chans > 0 and self.ai_props.supports_scan)

        if example_supported:
            main_frame = tk.Frame(self)
            main_frame.pack(fill=tk.X, anchor=tk.NW)

            channel_vcmd = self.register(self.validate_channel_entry)

            curr_row = 0
            if self.ai_props.num_ai_chans > 1:
                channel_vcmd = self.register(self.validate_channel_entry)

                low_channel_entry_label = tk.Label(main_frame)
                low_channel_entry_label["text"] = "Low Channel Number:"
                low_channel_entry_label.grid(
                    row=curr_row, column=0, sticky=tk.W)

                self.low_channel_entry = tk.Spinbox(
                    main_frame, from_=0,
                    to=max(self.ai_props.num_ai_chans - 1, 0),
                    validate='key', validatecommand=(channel_vcmd, '%P'))
                self.low_channel_entry.grid(
                    row=curr_row, column=1, sticky=tk.W)

                curr_row += 1
                high_channel_entry_label = tk.Label(main_frame)
                high_channel_entry_label["text"] = "High Channel Number:"
                high_channel_entry_label.grid(
                    row=curr_row, column=0, sticky=tk.W)

                self.high_channel_entry = tk.Spinbox(
                    main_frame, from_=0, validate='key',
                    to=max(self.ai_props.num_ai_chans - 1, 0),
                    validatecommand=(channel_vcmd, '%P'))
                self.high_channel_entry.grid(
                    row=curr_row, column=1, sticky=tk.W)
                initial_value = min(self.ai_props.num_ai_chans - 1, 3)
                self.high_channel_entry.delete(0, tk.END)
                self.high_channel_entry.insert(0, str(initial_value))

                curr_row += 1

            self.results_group = tk.LabelFrame(
                self, text="Results", padx=3, pady=3)
            self.results_group.pack(fill=tk.X, anchor=tk.NW, padx=3, pady=3)

            self.results_group.grid_columnconfigure(1, weight=1)

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
            self.inner_data_frame = tk.Frame(self.results_group)
            self.inner_data_frame.grid(
                row=curr_row, column=0, columnspan=2, sticky=tk.W)

            self.data_frame = tk.Frame(self.inner_data_frame)
            self.data_frame.grid()

            button_frame = tk.Frame(self)
            button_frame.pack(fill=tk.X, side=tk.RIGHT, anchor=tk.SE)

            self.start_button = tk.Button(button_frame)
            self.start_button["text"] = "Start"
            self.start_button["command"] = self.start
            self.start_button.grid(row=0, column=0, padx=3, pady=3)

            self.quit_button = tk.Button(button_frame)
            self.quit_button["text"] = "Quit"
            self.quit_button["command"] = self.master.destroy
            self.quit_button.grid(row=0, column=1, padx=3, pady=3)
        else:
            self.create_unsupported_widgets(self.board_num)


if __name__ == "__main__":
    # Start the example
    ULAI03(master=tk.Tk()).mainloop()
