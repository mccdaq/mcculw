from __future__ import absolute_import, division, print_function
from builtins import *  # @UnusedWildImport

from tkinter import messagebox

from mcculw import ul
from examples.ui.uiexample import UIExample
from examples.props.ai import AnalogInputProps
from mcculw.ul import ULError
import tkinter as tk


class ULAI02(UIExample):
    def __init__(self, master=None):
        super(ULAI02, self).__init__(master)

        self.board_num = 0
        self.ai_props = AnalogInputProps(self.board_num)

        self.create_widgets()

    def start_scan(self):
        low_chan = self.get_low_channel_num()
        high_chan = self.get_high_channel_num()

        if low_chan > high_chan:
            messagebox.showerror(
                "Error",
                "Low Channel Number must be greater than or equal to High "
                "Channel Number")
            self.start_button["state"] = tk.NORMAL
            return

        rate = 100
        points_per_channel = 10
        num_channels = high_chan - low_chan + 1
        total_count = points_per_channel * num_channels

        range_ = self.ai_props.available_ranges[0]

        # Allocate a buffer for the scan
        if self.ai_props.resolution <= 16:
            # Use the win_buf_alloc method for devices with a resolution
            # <= 16
            memhandle = ul.win_buf_alloc(total_count)
        else:
            # Use the win_buf_alloc_32 method for devices with a resolution
            # > 16
            memhandle = ul.win_buf_alloc_32(total_count)

        # Check if the buffer was successfully allocated
        if not memhandle:
            messagebox.showerror("Error", "Failed to allocate memory")
            self.start_button["state"] = tk.NORMAL
            return

        try:
            # Run the scan
            ul.a_in_scan(
                self.board_num, low_chan, high_chan, total_count,
                rate, range_, memhandle, 0)

            # Cast the memhandle to a ctypes pointer
            # Note: the ctypes array will only be valid until win_buf_free
            # is called.
            # A copy of the buffer can be created using win_buf_to_array
            # or win_buf_to_array_32 before the memory is freed. The copy
            # can be used at any time.
            if self.ai_props.resolution <= 16:
                # Use the memhandle_as_ctypes_array method for devices with
                # a resolution <= 16
                array = self.memhandle_as_ctypes_array(memhandle)
            else:
                # Use the memhandle_as_ctypes_array_32 method for devices
                # with a resolution > 16
                array = self.memhandle_as_ctypes_array_32(memhandle)

            # Display the values
            self.display_values(array, range_, total_count,
                                low_chan, high_chan)
        except ULError as e:
            self.show_ul_error(e)
        finally:
            # Free the allocated memory
            ul.win_buf_free(memhandle)
            self.start_button["state"] = tk.NORMAL

    def display_values(self, array, range_, total_count, low_chan,
                       high_chan):
        new_data_frame = tk.Frame(self.results_group)

        channel_text = []

        # Add the headers
        for chan_num in range(low_chan, high_chan + 1):
            channel_text.append("Channel " + str(chan_num) + "\n")

        chan_count = high_chan - low_chan + 1

        # Add (up to) the first 10 values for each channel to the text
        chan_num = low_chan
        for data_index in range(0, min(chan_count * 10, total_count)):
            if self.ai_props.resolution <= 16:
                eng_value = ul.to_eng_units(
                    self.board_num, range_, array[data_index])
            else:
                eng_value = ul.to_eng_units_32(
                    self.board_num, range_, array[data_index])
            channel_text[chan_num -
                         low_chan] += '{:.3f}'.format(eng_value) + "\n"
            if chan_num == high_chan:
                chan_num = low_chan
            else:
                chan_num += 1

        # Add the labels for each channel
        for chan_num in range(low_chan, high_chan + 1):
            chan_label = tk.Label(new_data_frame, justify=tk.LEFT, padx=3)
            chan_label["text"] = channel_text[chan_num - low_chan]
            chan_label.grid(row=0, column=chan_num - low_chan)

        self.data_frame.destroy()
        self.data_frame = new_data_frame
        self.data_frame.grid()

    def start(self):
        self.start_button["state"] = tk.DISABLED
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
        else:
            self.create_unsupported_widgets(self.board_num)


if __name__ == "__main__":
    # Start the example
    ULAI02(master=tk.Tk()).mainloop()
