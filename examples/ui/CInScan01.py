from __future__ import absolute_import, division, print_function

from builtins import *  # @UnusedWildImport
from tkinter import messagebox

from mcculw import ul
from mcculw.enums import CounterChannelType
from examples.props.counter import CounterProps
from examples.ui.uiexample import UIExample
from mcculw.ul import ULError
import tkinter as tk


class CInScan01(UIExample):
    def __init__(self, master=None):
        super(CInScan01, self).__init__(master)

        self.board_num = 0
        self.ctr_props = CounterProps(self.board_num)

        min_chan = next(
            (channel for channel in self.ctr_props.counter_info
             if channel.type == CounterChannelType.CTRSCAN
             or channel.type == CounterChannelType.CTRQUAD), None)
        if min_chan is not None:
            self.min_chan_num = min_chan.channel_num
        else:
            self.min_chan_num = -1

        max_chan = next(
            (channel for channel
             in reversed(self.ctr_props.counter_info)
             if channel.type == CounterChannelType.CTRSCAN
             or channel.type == CounterChannelType.CTRQUAD), None)
        if max_chan is not None:
            self.max_chan_num = max_chan.channel_num
        else:
            self.max_chan_num = -1

        self.create_widgets()

    def start_scan(self):
        low_chan = self.get_low_channel_num()
        high_chan = self.get_high_channel_num()

        if low_chan > high_chan:
            messagebox.showerror(
                "Error", "Low Channel Number must be greater than or equal "
                "to High Channel Number")
            self.start_button["state"] = tk.NORMAL
            return

        rate = 100
        points_per_channel = 10
        num_channels = high_chan - low_chan + 1
        total_count = points_per_channel * num_channels

        # Allocate a buffer for the scan
        memhandle = ul.win_buf_alloc_32(total_count)

        # Check if the buffer was successfully allocated
        if not memhandle:
            messagebox.showerror("Error", "Failed to allocate memory")
            self.start_button["state"] = tk.NORMAL
            return

        try:
            # Run the scan
            ul.c_in_scan(
                self.board_num, low_chan, high_chan, total_count,
                rate, memhandle, 0)

            # Convert the memhandle to a ctypes array
            # Note: the ctypes array will only be valid until win_buf_free
            # is called.
            # A copy of the buffer can be created using win_buf_to_array_32
            # before the memory is freed. The copy can be used at any time.
            array = self.memhandle_as_ctypes_array_32(memhandle)

            # Display the values
            self.display_values(array, total_count, low_chan, high_chan)
        except ULError as e:
            self.show_ul_error(e)
        finally:
            # Free the allocated memory
            ul.win_buf_free(memhandle)
            self.start_button["state"] = tk.NORMAL

    def display_values(self, array, total_count, low_chan, high_chan):
        new_data_frame = tk.Frame(self.results_group)

        channel_text = []

        # Add the headers
        for chan_num in range(low_chan, high_chan + 1):
            channel_text.append("Channel " + str(chan_num) + "\n")

        chan_count = high_chan - low_chan + 1

        # Add (up to) the first 10 values for each channel to the text
        chan_num = low_chan
        for data_index in range(0, min(chan_count * 10, total_count)):
            channel_text[chan_num - low_chan] += (
                str(array[data_index]) + "\n")
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
            if(value < self.min_chan_num or value > self.max_chan_num):
                return False
        except ValueError:
            return False

        return True

    def create_widgets(self):
        '''Create the tkinter UI'''
        if self.min_chan_num != -1 and self.max_chan_num != -1:
            main_frame = tk.Frame(self)
            main_frame.pack(fill=tk.X, anchor=tk.NW)

            channel_vcmd = self.register(self.validate_channel_entry)

            curr_row = 0
            low_channel_entry_label = tk.Label(main_frame)
            low_channel_entry_label["text"] = "Low Channel Number:"
            low_channel_entry_label.grid(
                row=curr_row, column=0, sticky=tk.W)

            self.low_channel_entry = tk.Spinbox(
                main_frame, from_=self.min_chan_num, to=self.max_chan_num,
                validate='key', validatecommand=(channel_vcmd, '%P'))
            self.low_channel_entry.grid(row=curr_row, column=1, sticky=tk.W)

            curr_row += 1
            high_channel_entry_label = tk.Label(main_frame)
            high_channel_entry_label["text"] = "High Channel Number:"
            high_channel_entry_label.grid(
                row=curr_row, column=0, sticky=tk.W)

            self.high_channel_entry = tk.Spinbox(
                main_frame, from_=self.min_chan_num, to=self.max_chan_num,
                validate='key', validatecommand=(channel_vcmd, '%P'))
            self.high_channel_entry.grid(
                row=curr_row, column=1, sticky=tk.W)
            initial_value = self.max_chan_num
            self.high_channel_entry.delete(0, tk.END)
            self.high_channel_entry.insert(0, str(initial_value))

            self.results_group = tk.LabelFrame(
                self, text="Results", padx=3, pady=3)
            self.results_group.pack(fill=tk.X, anchor=tk.NW, padx=3, pady=3)

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


# Start the example if this module is being run
if __name__ == "__main__":
    # Start the example
    CInScan01(master=tk.Tk()).mainloop()
