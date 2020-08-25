"""
File:                       ULAO02.py

Library Call Demonstrated:  mcculw.ul.a_out_scan()

Purpose:                    Writes to a range of D/A Output Channels.

Demonstration:              Sends a digital output to the D/A channels

Other Library Calls:        mcculw.ul.win_buf_alloc()
                            mcculw.ul.win_buf_free()

Special Requirements:       Device must have 2 or more D/A converters.
                            This function is designed for boards that
                            support timed analog output.  It can be used
                            for polled output boards but only for values
                            of NumPoints up to the number of channels
                            that the board supports (i.e., NumPoints =
                            6 maximum for the six channel CIO-DDA06).
"""
from __future__ import absolute_import, division, print_function
from builtins import *  # @UnusedWildImport

import tkinter as tk
from tkinter import messagebox
from ctypes import cast, POINTER, c_ushort

from mcculw import ul
from mcculw.ul import ULError
from mcculw.device_info import DaqDeviceInfo

try:
    from ui_examples_util import UIExample, show_ul_error
except ImportError:
    from .ui_examples_util import UIExample, show_ul_error


class ULAO02(UIExample):
    def __init__(self, master=None):
        super(ULAO02, self).__init__(master)
        # By default, the example detects all available devices and selects the
        # first device listed.
        # If use_device_detection is set to False, the board_num property needs
        # to match the desired board number configured with Instacal.
        use_device_detection = True
        self.board_num = 0

        try:
            if use_device_detection:
                self.configure_first_detected_device()

            self.device_info = DaqDeviceInfo(self.board_num)
            self.ao_info = self.device_info.get_ao_info()
            if self.ao_info.is_supported and self.ao_info.supports_scan:
                self.create_widgets()
            else:
                self.create_unsupported_widgets()
        except ULError:
            self.create_unsupported_widgets(True)

    def send_data(self):
        # Build the data array
        num_chans = min(self.ao_info.num_chans, 4)
        num_points = num_chans
        ao_range = self.ao_info.supported_ranges[0]

        memhandle = ul.win_buf_alloc(num_points)

        # Check if the buffer was successfully allocated
        if not memhandle:
            messagebox.showerror("Error", "Failed to allocate memory")
            self.send_data["state"] = tk.NORMAL
            return

        try:
            data_array = cast(memhandle, POINTER(c_ushort))

            full_scale_count = (2 ** self.ao_info.resolution) - 1
            value_step = full_scale_count / (num_chans + 1)
            for point_num in range(0, num_points):
                raw_value = int(value_step * (point_num + 1))
                data_array[point_num] = raw_value

                self.raw_data_labels[point_num]["text"] = str(raw_value)
                # ul.to_eng_units cannot be used here, as it uses the analog
                # input resolution. Instead, do the conversion on our own.
                volts = self.ao_to_eng_units(
                    raw_value, ao_range, self.ao_info.resolution)
                self.volts_labels[point_num]["text"] = (
                    '{:.3f}'.format(volts))

            ul.a_out_scan(self.board_num, 0, num_chans - 1, num_points, 100,
                          ao_range, memhandle, 0)
        except ULError as e:
            show_ul_error(e)
        finally:
            ul.win_buf_free(memhandle)

    def ao_to_eng_units(self, raw_value, ao_range, resolution):
        full_scale_volts = ao_range.range_max - ao_range.range_min
        full_scale_count = (2 ** resolution) - 1
        return ((full_scale_volts / full_scale_count) * raw_value
                + ao_range.range_min)

    def create_widgets(self):
        '''Create the tkinter UI'''
        self.device_label = tk.Label(self)
        self.device_label.pack(fill=tk.NONE, anchor=tk.NW)
        self.device_label["text"] = ('Board Number ' + str(self.board_num)
                                     + ": " + self.device_info.product_name
                                     + " (" + self.device_info.unique_id + ")")

        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.X, anchor=tk.NW)

        data_frame = tk.Frame(main_frame)
        data_frame.pack(fill=tk.X, anchor=tk.NW)

        raw_data_label = tk.Label(data_frame)
        raw_data_label["text"] = "Raw Data"
        raw_data_label.grid(row=1, sticky=tk.W)

        volts_label = tk.Label(data_frame)
        volts_label["text"] = "Volts"
        volts_label.grid(row=2, sticky=tk.W)

        self.raw_data_labels = []
        self.volts_labels = []

        for chan_num in range(0, min(self.ao_info.num_chans, 4)):
            name_label = tk.Label(data_frame)
            name_label["text"] = "Channel " + str(chan_num)
            name_label.grid(row=0, column=chan_num + 1, sticky=tk.W)

            raw_data_label = tk.Label(data_frame)
            raw_data_label.grid(row=1, column=chan_num + 1, sticky=tk.W)
            self.raw_data_labels.append(raw_data_label)

            volts_label = tk.Label(data_frame)
            volts_label.grid(row=2, column=chan_num + 1, sticky=tk.W)
            self.volts_labels.append(volts_label)

        button_frame = tk.Frame(self)
        button_frame.pack(fill=tk.X, side=tk.RIGHT, anchor=tk.SE)

        send_data_button = tk.Button(button_frame)
        send_data_button["text"] = "Start"
        send_data_button["command"] = self.send_data
        send_data_button.grid(row=0, column=0, padx=3, pady=3)

        quit_button = tk.Button(button_frame)
        quit_button["text"] = "Quit"
        quit_button["command"] = self.master.destroy
        quit_button.grid(row=0, column=1, padx=3, pady=3)


if __name__ == "__main__":
    # Start the example
    ULAO02(master=tk.Tk()).mainloop()
