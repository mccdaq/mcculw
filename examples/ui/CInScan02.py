from __future__ import absolute_import, division, print_function

from builtins import *  # @UnusedWildImport
from tkinter import messagebox

from mcculw import ul
from mcculw.enums import CounterChannelType, CounterDebounceTime, \
    CounterMode, CounterEdgeDetection, CounterTickSize
from examples.props.counter import CounterProps
from examples.ui.uiexample import UIExample
from mcculw.ul import ULError
import tkinter as tk


class CInScan02(UIExample):
    def __init__(self, master=None):
        super(CInScan02, self).__init__(master)

        self.board_num = 0
        self.ctr_props = CounterProps(self.board_num)

        chan = next(
            (channel for channel in self.ctr_props.counter_info
             if channel.type == CounterChannelType.CTRSCAN), None)
        if chan != None:
            self.chan_num = chan.channel_num
        else:
            self.chan_num = -1

        # Initialize tkinter
        self.grid(sticky=tk.NSEW)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.create_widgets()

    def start_scan(self):
        rate = 390
        total_count = 100

        # Allocate a buffer for the scan
        memhandle = ul.win_buf_alloc_32(total_count)

        # Check if the buffer was successfully allocated
        if not memhandle:
            messagebox.showerror("Error", "Failed to allocate memory")
            self.start_button["state"] = tk.NORMAL
            return

        try:
            # Configure the counter
            ul.c_config_scan(
                self.board_num, self.chan_num, CounterMode.DECREMENT_ON,
                CounterDebounceTime.DEBOUNCE_NONE, 0,
                CounterEdgeDetection.FALLING_EDGE,
                CounterTickSize.TICK20PT83ns, 1)

            # Run the scan
            ul.c_in_scan(
                self.board_num, self.chan_num, self.chan_num, total_count,
                rate, memhandle, 0)

            # Convert the memhandle to a ctypes array
            # Note: the ctypes array will only be valid until win_buf_free
            # is called.
            # A copy of the buffer can be created using win_buf_to_array_32
            # before the memory is freed. The copy can be used at any time.
            array = self.memhandle_as_ctypes_array_32(memhandle)

            # Display the values
            self.display_values(array, total_count)
        except ULError as e:
            self.show_ul_error(e)
        finally:
            # Free the allocated memory
            ul.win_buf_free(memhandle)
            self.start_button["state"] = tk.NORMAL

    def display_values(self, array, total_count):
        new_data_frame = tk.Frame(self.results_group)

        # Add the header
        channel_text = "Channel " + str(self.chan_num) + "\n"

        # Add (up to) the first 10 values to the display
        for data_index in range(0, min(10, total_count)):
            channel_text += str(array[data_index]) + "\n"

        # Add the labels
        chan_label = tk.Label(new_data_frame, justify=tk.LEFT, padx=3)
        chan_label["text"] = channel_text
        chan_label.grid(row=0, column=0)

        self.data_frame.destroy()
        self.data_frame = new_data_frame
        self.data_frame.grid()

    def start(self):
        self.start_button["state"] = tk.DISABLED
        self.start_scan()

    def create_widgets(self):
        '''Create the tkinter UI'''
        if self.chan_num != -1:
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
    CInScan02(master=tk.Tk()).mainloop()
