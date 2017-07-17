from __future__ import absolute_import, division, print_function

from builtins import *  # @UnusedWildImport
from tkinter import messagebox

from mcculw import ul
from examples.props.ao import AnalogOutputProps
from examples.ui.uiexample import UIExample
from mcculw.ul import ULError
import tkinter as tk


class ULAO02(UIExample):
    def __init__(self, master=None):
        super(ULAO02, self).__init__(master)

        self.board_num = 0
        self.ao_props = AnalogOutputProps(self.board_num)

        self.create_widgets()

    def send_data(self):
        # Build the data array
        num_chans = min(self.ao_props.num_chans, 4)
        num_points = num_chans
        ao_range = self.ao_props.available_ranges[0]

        memhandle = ul.win_buf_alloc(num_points)

        # Check if the buffer was successfully allocated
        if not memhandle:
            messagebox.showerror("Error", "Failed to allocate memory")
            self.start_button["state"] = tk.NORMAL
            return

        try:
            data_array = self.memhandle_as_ctypes_array(memhandle)

            full_scale_count = (2 ** self.ao_props.resolution) - 1
            value_step = full_scale_count / (num_chans + 1)
            for point_num in range(0, num_points):
                raw_value = int(value_step * (point_num + 1))
                data_array[point_num] = raw_value

                self.raw_data_labels[point_num]["text"] = str(raw_value)
                # ul.to_eng_units cannot be used here, as it uses the analog
                # input resolution. Instead, do the conversion on our own.
                volts = self.ao_to_eng_units(
                    raw_value, ao_range, self.ao_props.resolution)
                self.volts_labels[point_num]["text"] = (
                    '{:.3f}'.format(volts))

            ul.a_out_scan(
                self.board_num, 0, num_chans - 1, num_points, 100, ao_range,
                memhandle, 0)
        except ULError as e:
            self.show_ul_error(e)
        finally:
            ul.win_buf_free(memhandle)

    def ao_to_eng_units(self, raw_value, ao_range, resolution):
        full_scale_volts = ao_range.range_max - ao_range.range_min
        full_scale_count = (2 ** resolution) - 1
        return ((full_scale_volts / full_scale_count) * raw_value
                + ao_range.range_min)

    def create_widgets(self):
        '''Create the tkinter UI'''
        example_supported = (
            self.ao_props.num_chans > 0
            and self.ao_props.supports_scan)

        if example_supported:
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

            for chan_num in range(0, min(self.ao_props.num_chans, 4)):
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
        else:
            self.create_unsupported_widgets(self.board_num)


if __name__ == "__main__":
    # Start the example
    ULAO02(master=tk.Tk()).mainloop()
