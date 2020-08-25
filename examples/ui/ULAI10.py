"""
File:                       ULAI10.py

Library Call Demonstrated:  mcculw.ul.a_load_queue()

Purpose:                    Loads an A/D board's channel/gain queue.

Demonstration:              Prepares a channel/gain queue and loads it to the
                            board. An analog input function is then called to
                            show how the queue values work.

Other Library Calls:        mcculw.ul.win_buf_alloc()
                                or mcculw.ul.win_buf_alloc_32()
                            mcculw.ul.a_in_scan()
                            mcculw.ul.win_buf_free()

Special Requirements:       Device must have an A/D converter and
                            channel gain queue hardware.
"""
from __future__ import absolute_import, division, print_function
from builtins import *  # @UnusedWildImport

import random
import tkinter as tk
from tkinter import messagebox, IntVar
from ctypes import cast, POINTER, c_ushort, c_ulong

from mcculw import ul
from mcculw.enums import ErrorCode
from mcculw.ul import ULError
from mcculw.device_info import DaqDeviceInfo

try:
    from ui_examples_util import UIExample, show_ul_error
except ImportError:
    from .ui_examples_util import UIExample, show_ul_error


class ULAI10(UIExample):
    def __init__(self, master=None):
        super(ULAI10, self).__init__(master)
        # By default, the example detects all available devices and selects the
        # first device listed.
        # If use_device_detection is set to False, the board_num property needs
        # to match the desired board number configured with Instacal.
        use_device_detection = True
        self.board_num = 0

        self.num_elements = 4
        self.queue_loaded = False

        try:
            if use_device_detection:
                self.configure_first_detected_device()

            self.device_info = DaqDeviceInfo(self.board_num)
            self.ai_info = self.device_info.get_ai_info()
            if self.ai_info.is_supported:
                self.create_widgets()
                self.scan_loop()
            else:
                self.create_unsupported_widgets()
        except ULError:
            self.create_unsupported_widgets(True)

    def scan_loop(self):
        rate = 100
        points_per_channel = 10
        low_chan = 0  # Ignored by a_in_scan when queue is enabled
        high_chan = 3  # Ignored by a_in_scan when queue is enabled
        num_channels = high_chan - low_chan + 1
        total_count = points_per_channel * num_channels

        # Ignored by a_in_scan when queue is enabled
        range_ = self.ai_info.supported_ranges[0]

        # Allocate a buffer for the scan
        if self.ai_info.resolution <= 16:
            # Use the win_buf_alloc method for devices with a resolution <= 16
            memhandle = ul.win_buf_alloc(total_count)
        else:
            # Use the win_buf_alloc_32 method for devices with a resolution >
            # 16
            memhandle = ul.win_buf_alloc_32(total_count)

        # Check if the buffer was successfully allocated
        if not memhandle:
            messagebox.showerror("Error", "Failed to allocate memory")
            return

        try:
            # Run the scan
            ul.a_in_scan(self.board_num, low_chan, high_chan, total_count,
                         rate, range_, memhandle, 0)

            # Convert the memhandle to a ctypes array
            # Note: the ctypes array will only be valid until win_buf_free
            # is called.
            # A copy of the buffer can be created using win_buf_to_array
            # or win_buf_to_array_32 before the memory is freed. The copy can
            # be used at any time.
            if self.ai_info.resolution <= 16:
                # Use the memhandle_as_ctypes_array method for devices with a
                # resolution <= 16
                array = cast(memhandle, POINTER(c_ushort))
            else:
                # Use the memhandle_as_ctypes_array_32 method for devices with
                # a resolution > 16
                array = cast(memhandle, POINTER(c_ulong))

            # Display the values
            self.display_values(array, total_count)

            self.after(1000, self.scan_loop)
        except ULError as e:
            show_ul_error(e)
        finally:
            # Free the allocated memory
            ul.win_buf_free(memhandle)

    def display_values(self, array, total_count):
        data_text = []

        for _ in range(0, self.num_elements):
            data_text.append("")

        # Add (up to) the first 10 values for each channel to the text
        chan_num = 0
        for data_index in range(0, min(self.num_elements * 10, total_count)):
            data_text[chan_num] += str(array[data_index]) + "\n"
            if chan_num == self.num_elements - 1:
                chan_num = 0
            else:
                chan_num += 1

        # Add the labels for each channel
        for chan_num in range(0, self.num_elements):
            self.data_labels[chan_num]["text"] = data_text[chan_num]

    def toggle_load_queue(self):
        if not self.queue_loaded:
            chan_array = []
            if self.random_channels_checkbutton_var.get():
                for chan_num in range(0, self.num_elements):
                    chan_array.append(random.randint(
                        0, self.ai_info.num_chans - 1))
            else:
                for chan_num in range(0, self.num_elements):
                    chan_array.append(chan_num)

            gain_array = []
            if self.random_ranges_checkbutton_var.get():
                for chan_num in range(0, self.num_elements):
                    gain_array.append(random.choice(
                        self.ai_info.supported_ranges))
            else:
                range_ = self.ai_info.supported_ranges[0]
                for chan_num in range(0, self.num_elements):
                    gain_array.append(range_)

            try:
                ul.a_load_queue(self.board_num, chan_array,
                                gain_array, self.num_elements)

                self.queue_loaded = True
                self.toggle_load_queue_button["text"] = "Unload Queue"
                self.instructions_label["text"] = (
                    "Queue loaded on board " + str(self.board_num))

                # Update the headers
                for chan_num in range(0, self.num_elements):
                    self.channel_labels[chan_num]["text"] = (
                        "Channel " + str(chan_array[chan_num]))
                for chan_num in range(0, self.num_elements):
                    self.range_labels[chan_num]["text"] = \
                        gain_array[chan_num].name
            except ULError as e:
                if e.errorcode == ErrorCode.BADADCHAN:
                    self.instructions_label["text"] = (
                        "Board " + str(self.board_num) +
                        " doesn't support random channels. Queue was not "
                        "changed.")
                else:
                    raise
        else:
            # Set Count to 0 to disable the queue
            ul.a_load_queue(self.board_num, [], [], 0)

            self.queue_loaded = False
            self.toggle_load_queue_button["text"] = "Load Queue"
            self.instructions_label["text"] = (
                "Board " + str(self.board_num)
                + " scanning contiguous channels with with Range set to "
                + str(self.ai_info.supported_ranges[0]))

            # Update the headers
            for chan_num in range(0, self.num_elements):
                self.channel_labels[chan_num]["text"] = (
                    "Channel " + str(chan_num))
            for chan_num in range(0, self.num_elements):
                self.range_labels[chan_num]["text"] = (
                    self.ai_info.supported_ranges[0].name)

    def create_widgets(self):
        '''Create the tkinter UI'''
        self.device_label = tk.Label(self)
        self.device_label.pack(fill=tk.NONE, anchor=tk.NW)
        self.device_label["text"] = ('Board Number ' + str(self.board_num)
                                     + ": " + self.device_info.product_name
                                     + " (" + self.device_info.unique_id + ")")

        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.X, anchor=tk.NW)

        self.instructions_label = tk.Label(
            main_frame, justify=tk.LEFT, wraplength=400)
        self.instructions_label["text"] = (
            "Board " + str(self.board_num)
            + " collecting analog data on up to "
            + str(self.num_elements)
            + " channels between channel 0 and channel "
            + str(self.ai_info.num_chans)
            + " using AInScan and ALoadQueue.")
        self.instructions_label.pack(
            fill=tk.X, anchor=tk.NW, padx=3, pady=3)

        self.results_group = tk.LabelFrame(
            main_frame, text="Results", padx=3, pady=3)
        self.results_group.pack(fill=tk.X, anchor=tk.NW, padx=3, pady=3)

        self.data_frame = tk.Frame(self.results_group)
        self.data_frame.grid()

        self.channel_labels = []
        self.range_labels = []
        self.data_labels = []
        # Add the labels for each channel
        for chan_num in range(0, self.num_elements):
            chan_label = tk.Label(
                self.data_frame, justify=tk.LEFT, padx=3)
            chan_label.grid(row=0, column=chan_num)
            chan_label["text"] = "Channel " + str(chan_num)
            self.channel_labels.append(chan_label)

            range_label = tk.Label(
                self.data_frame, justify=tk.LEFT, padx=3)
            range_label.grid(row=1, column=chan_num)
            range_label["text"] = self.ai_info.supported_ranges[0].name
            self.range_labels.append(range_label)

            data_label = tk.Label(
                self.data_frame, justify=tk.LEFT, padx=3)
            data_label.grid(row=2, column=chan_num)
            self.data_labels.append(data_label)

        self.random_ranges_checkbutton_var = IntVar(value=1)
        random_ranges_checkbutton = tk.Checkbutton(
            main_frame, text="Random Ranges",
            variable=self.random_ranges_checkbutton_var,
            borderwidth=0)
        random_ranges_checkbutton.pack(
            fill=tk.X, anchor=tk.NW, padx=3, pady=3)

        self.random_channels_checkbutton_var = IntVar(value=0)
        random_channels_checkbutton = tk.Checkbutton(
            main_frame, text="Random Channels",
            variable=self.random_channels_checkbutton_var,
            borderwidth=0)
        random_channels_checkbutton.pack(
            fill=tk.X, anchor=tk.NW, padx=3, pady=3)

        button_frame = tk.Frame(self)
        button_frame.pack(fill=tk.X, side=tk.RIGHT, anchor=tk.SE)

        self.toggle_load_queue_button = tk.Button(button_frame)
        self.toggle_load_queue_button["text"] = "Load Queue"
        self.toggle_load_queue_button["command"] = \
            self.toggle_load_queue
        self.toggle_load_queue_button.grid(
            row=0, column=1, rowspan=2, padx=3, pady=3)

        quit_button = tk.Button(button_frame)
        quit_button["text"] = "Quit"
        quit_button["command"] = self.master.destroy
        quit_button.grid(row=0, column=2, rowspan=2, padx=3, pady=3)


if __name__ == "__main__":
    # Start the example
    ULAI10(master=tk.Tk()).mainloop()
