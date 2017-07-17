from __future__ import absolute_import, division, print_function

from builtins import *  # @UnusedWildImport
from tkinter import messagebox

from mcculw import ul
from mcculw.enums import CounterChannelType, CounterMode, \
    CounterDebounceTime, CounterEdgeDetection, CounterTickSize
from examples.props.counter import CounterProps
from examples.ui.uiexample import UIExample
from mcculw.ul import ULError
import tkinter as tk


class CInScan03(UIExample):
    def __init__(self, master=None):
        super(CInScan03, self).__init__(master)

        self.board_num = 0
        self.ctr_props = CounterProps(self.board_num)

        chan = next(
            (channel for channel in self.ctr_props.counter_info
             if channel.type == CounterChannelType.CTRQUAD), None)
        if chan == None:
            # Check for scan counters, which may (or may not) support
            # encoder modes
            chan = next(
                (channel for channel in self.ctr_props.counter_info
                 if channel.type == CounterChannelType.CTRSCAN), None)
        if chan != None:
            self.chan_num = chan.channel_num
        else:
            self.chan_num = -1

        self.create_widgets()

    def start_scan(self):
        rate = 100
        total_count = 10

        # Allocate a buffer for the scan
        memhandle = ul.win_buf_alloc_32(total_count)

        # Check if the buffer was successfully allocated
        if not memhandle:
            messagebox.showerror("Error", "Failed to allocate memory")
            self.start_button["state"] = tk.NORMAL
            return

        try:
            mode = CounterMode.ENCODER + CounterMode.ENCODER_MODE_X1 \
                + CounterMode.ENCODER_MODE_CLEAR_ON_Z_ON
            debounce_time = CounterDebounceTime.DEBOUNCE_NONE
            debounce_mode = 0
            edge_detection = CounterEdgeDetection.RISING_EDGE
            tick_size = CounterTickSize.TICK20PT83ns
            mapped_channel = 2

            # Configure the first counter channel for Encoder mode
            ul.c_config_scan(
                self.board_num, self.chan_num, mode, debounce_time,
                debounce_mode, edge_detection, tick_size, mapped_channel)

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
        data_text = ""

        # Add (up to) the first 10 values for each channel to the text
        for data_index in range(0, min(10, total_count)):
            data_text += str(array[data_index]) + "\n"

        self.data_label["text"] = data_text

    def start(self):
        self.start_button["state"] = tk.DISABLED
        self.start_scan()

    def create_widgets(self):
        '''Create the tkinter UI'''
        if self.chan_num != -1:
            info_text = tk.Label(self)
            info_text["text"] = (
                "Encoder scan on device " + str(self.board_num)
                + " counter channel " + str(self.chan_num))
            info_text.pack(fill=tk.X, anchor=tk.NW, padx=3, pady=3)

            results_group = tk.LabelFrame(self, text="Results")
            results_group.pack(fill=tk.X, anchor=tk.NW, padx=3, pady=3)

            self.data_label = tk.Label(results_group, justify=tk.LEFT)
            self.data_label.grid(padx=3, pady=3)

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
    CInScan03(master=tk.Tk()).mainloop()
