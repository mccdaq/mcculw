"""
File:                       ULDI03.py

Library Call Demonstrated:  mcculw.ul.d_in_scan()

Purpose:                    Reads digital input port(s) at specified rate and
                            number of samples.

Demonstration:              Configures the first one or two digital
                            scan ports for input (if programmable)
                            and reads the value on the port.

Other Library Calls:        mcculw.ul.win_buf_alloc()
                            mcculw.ul.win_buf_free()
                            mcculw.ul.d_config_port()
                            mcculw.ul.stop_background()

Special Requirements:       Device must support paced digital input

"""
from __future__ import absolute_import, division, print_function
from builtins import *  # @UnusedWildImport

import tkinter as tk
from tkinter import messagebox
from ctypes import cast, POINTER, c_ushort

from mcculw import ul
from mcculw.enums import ScanOptions, Status, FunctionType, DigitalIODirection
from mcculw.ul import ULError
from mcculw.device_info import DaqDeviceInfo

try:
    from ui_examples_util import UIExample, show_ul_error
except ImportError:
    from .ui_examples_util import UIExample, show_ul_error


class ULDI03(UIExample):
    def __init__(self, master=None):
        super(ULDI03, self).__init__(master)
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
            dio_info = self.device_info.get_dio_info()
            # Find the first port that supports input, defaulting to None
            # if one is not found.
            self.port = next((port for port in dio_info.port_info
                              if port.supports_input_scan), None)

            if self.port is not None:
                self.create_widgets()
            else:
                self.create_unsupported_widgets()

        except ULError:
            self.create_unsupported_widgets(True)

    def start_scan(self):
        rate = 100
        count = 1000

        # Allocate a buffer for the scan
        self.memhandle = ul.win_buf_alloc(count)

        # Check if the buffer was successfully allocated
        if not self.memhandle:
            messagebox.showerror("Error", "Failed to allocate memory")
            self.set_ui_idle_state()
            return

        try:
            # Configure the port (if necessary)
            if self.port.is_port_configurable:
                ul.d_config_port(self.board_num, self.port.type,
                                 DigitalIODirection.IN)

            # Run the scan
            ul.d_in_scan(self.board_num, self.port.type, count, rate,
                         self.memhandle, ScanOptions.BACKGROUND)
        except ULError as e:
            show_ul_error(e)
            self.set_ui_idle_state()
            return

        # Convert the memhandle to a ctypes array
        # Note: the ctypes array will no longer be valid after win_buf_free is
        # called. A copy of the buffer can be created using win_buf_to_array
        # before the memory is freed. The copy can be used at any time.
        self.ctypes_array = cast(self.memhandle, POINTER(c_ushort))

        # Start updating the displayed values
        self.update_displayed_values()

    def update_displayed_values(self):
        # Get the status from the device
        status, curr_count, curr_index = ul.get_status(self.board_num,
                                                       FunctionType.DIFUNCTION)

        # Display the status info
        self.update_status_labels(status, curr_count, curr_index)

        # Display the values
        self.display_values(curr_index, curr_count)

        # Call this method again until the stop button is pressed (or an error
        # occurs)
        if status == Status.RUNNING:
            self.after(100, self.update_displayed_values)
        else:
            # Free the allocated memory
            ul.win_buf_free(self.memhandle)
            # Stop the background operation (this is required even if the
            # scan completes successfully)
            ul.stop_background(self.board_num, FunctionType.DIFUNCTION)
            self.set_ui_idle_state()

    def update_status_labels(self, status, curr_count, curr_index):
        if status == Status.IDLE:
            self.status_label["text"] = "Idle"
        else:
            self.status_label["text"] = "Running"

        self.index_label["text"] = str(curr_index)
        self.count_label["text"] = str(curr_count)

    def display_values(self, curr_index, curr_count):
        display_count = 10
        array = self.ctypes_array
        data_text = ""

        # If no data has been gathered, don't add data to the labels
        if curr_count > 1:
            # curr_index points to the start of the last completed data point
            # that was transferred between the board and the data buffer. Based
            # on this, calculate the first index we want to display using
            # subtraction.
            first_index = max(curr_index - display_count - 1, 0)
            # Add (up to) the latest 10 values for each channel to the text
            for data_index in range(
                    first_index,
                    first_index + min(display_count, curr_count)):
                data_text += hex(array[data_index]) + "\n"

        self.data_label["text"] = data_text

    def stop(self):
        ul.stop_background(self.board_num, FunctionType.DIFUNCTION)

    def set_ui_idle_state(self):
        self.start_button["command"] = self.start
        self.start_button["text"] = "Start"

    def start(self):
        self.start_button["command"] = self.stop
        self.start_button["text"] = "Stop"
        self.start_scan()

    def create_widgets(self):
        '''Create the tkinter UI'''
        self.device_label = tk.Label(self)
        self.device_label.pack(fill=tk.NONE, anchor=tk.NW)
        self.device_label["text"] = ('Board Number ' + str(self.board_num)
                                     + ": " + self.device_info.product_name
                                     + " (" + self.device_info.unique_id + ")")

        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.X, anchor=tk.NW)

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

        self.data_label = tk.Label(self.inner_data_frame)
        self.data_label.grid()

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


if __name__ == "__main__":
    # Start the example
    ULDI03(master=tk.Tk()).mainloop()
