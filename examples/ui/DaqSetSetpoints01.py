"""
File:                       DaqSetSetpoints01.py

Library Call Demonstrated:  mcculw.ul.daq_set_setpoints()

Purpose:                    Demonstrate the configuration and usage of
                            setpoints, including adding the setpoint status to
                            the scanlist and asynchronous reads of the setpoint
                            status.

Demonstration:              Continuously displays the input channel data while
                            monitoring the scan status until the Stop button is
                            pressed.

Other Library Calls:        mcculw.ul.win_buf_alloc()
                            mcculw.ul.win_buf_free()
                            mcculw.ul.daq_in_scan()
                            mcculw.ul.get_status()
                            mcculw.ul.to_eng_units()
                            mcculw.ul.stop_background()

Special Requirements:       Device must support mcculw.ul.daq_set_setpoints().
"""
from __future__ import absolute_import, division, print_function
from builtins import *  # @UnusedWildImport

import tkinter as tk
from tkinter import messagebox
from ctypes import cast, POINTER, c_ushort

from mcculw import ul
from mcculw.enums import (ScanOptions, Status, FunctionType, ChannelType,
                          ULRange, DigitalPortType, SetpointFlag, SetpointOutput)
from mcculw.ul import ULError
from mcculw.device_info import DaqDeviceInfo

try:
    from ui_examples_util import UIExample, show_ul_error
except ImportError:
    from .ui_examples_util import UIExample, show_ul_error


class DaqSetSetpoints01(UIExample):
    def __init__(self, master=None):
        super(DaqSetSetpoints01, self).__init__(master)
        # By default, the example detects all available devices and selects the
        # first device listed.
        # If use_device_detection is set to False, the board_num property needs
        # to match the desired board number configured with Instacal.
        use_device_detection = True
        self.board_num = 0

        self.chan_list = []
        self.chan_type_list = []
        self.gain_list = []
        self.num_chans = 4

        self.setpoint_flags_list = []
        self.setpoint_output_list = []
        self.limit_a_list = []
        self.limit_b_list = []
        self.output_1_list = []
        self.output_2_list = []
        self.output_mask_1_list = []
        self.output_mask_2_list = []
        self.setpoint_count = 3

        try:
            if use_device_detection:
                self.configure_first_detected_device()

            self.device_info = DaqDeviceInfo(self.board_num)

            daqi_info = self.device_info.get_daqi_info()
            if (self.device_info.supports_daq_input
                    and daqi_info.supports_setpoints):
                self.init_scan_channel_info()
                self.init_setpoints()
                self.create_widgets()
            else:
                self.create_unsupported_widgets()
        except ULError:
            self.create_unsupported_widgets(True)

    def init_scan_channel_info(self):
        # Add analog input channels
        self.chan_list.append(0)
        self.chan_type_list.append(
            ChannelType.ANALOG + ChannelType.SETPOINT_ENABLE)
        self.gain_list.append(ULRange.BIP10VOLTS)

        self.chan_list.append(1)
        self.chan_type_list.append(
            ChannelType.ANALOG + ChannelType.SETPOINT_ENABLE)
        self.gain_list.append(ULRange.BIP10VOLTS)

        # Add a digital input channel
        self.chan_list.append(DigitalPortType.FIRSTPORTA)
        self.chan_type_list.append(
            ChannelType.DIGITAL8 + ChannelType.SETPOINT_ENABLE)
        self.gain_list.append(ULRange.NOTUSED)

        # Add a setpoint status channel
        self.chan_list.append(0)
        self.chan_type_list.append(ChannelType.SETPOINTSTATUS)
        self.gain_list.append(ULRange.NOTUSED)

    def init_setpoints(self):
        # Setpoint configurations for ChanArray[0] (CH0)
        self.setpoint_flags_list.append(
            SetpointFlag.LESSTHAN_LIMITA + SetpointFlag.UPDATEON_TRUEANDFALSE)
        # Setpoint result outputs a value to Analog Out 0
        self.setpoint_output_list.append(SetpointOutput.DAC0)
        # If CH0 less than 3.0 volts apply output1, else apply output2
        self.limit_a_list.append(3)
        self.limit_b_list.append(0)  # Ignored when LessThanLimitA flag is used
        self.output_1_list.append(5)  # Output 5.0 volts on Analog Out 0
        self.output_2_list.append(-5)  # Output -5.0 volts on Analog Out 0
        self.output_mask_1_list.append(0)  # Ignored for DAC0 output type
        self.output_mask_2_list.append(0)  # Ignored for DAC0 output type

        # Setpoint configurations for ChanArray[1] (CH1)
        self.setpoint_flags_list.append(SetpointFlag.GREATERTHAN_LIMITB
                                        + SetpointFlag.UPDATEON_TRUEANDFALSE)
        # Setpoint result outputs a value to digital port C
        self.setpoint_output_list.append(SetpointOutput.FIRSTPORTC)
        # Ignored when GreaterThanLimitB flag is used
        self.limit_a_list.append(0)
        # If CH1 greater than 2.0 volts apply output1
        self.limit_b_list.append(2)
        # Output a bit pattern of 01010101 to digital port C
        self.output_1_list.append(0x55)
        # Output a bit pattern of 10101010 to digital port C
        self.output_2_list.append(0xAA)
        # Output the value of 'out1' on low nibble only
        self.output_mask_1_list.append(0x0F)
        # Output the value of 'out2' on low nibble only
        self.output_mask_2_list.append(0x0F)

        # Setpoint configurations for ChanArray[2] (FIRSTPORTA)
        self.setpoint_flags_list.append(
            SetpointFlag.EQUAL_LIMITA | SetpointFlag.UPDATEON_TRUEONLY)
        # Setpoint result outputs a value to Timer 0
        self.setpoint_output_list.append(SetpointOutput.TMR0)
        # If FirstPortA equal 00001111 bit pattern apply output1
        self.limit_a_list.append(0x0F)
        self.limit_b_list.append(2)  # Ignored when EqualLimitA flag is used
        self.output_1_list.append(100)  # Output a 100Hz square wave on Timer 0
        # Ignored when SF_UPDATEON_TRUEONLY flag is used
        self.output_2_list.append(0)
        self.output_mask_1_list.append(0)  # Ignored for 'TMR0' output type
        self.output_mask_2_list.append(0)  # Ignored for 'TMR0' output type

    def start_scan(self):
        rate = 100
        points_per_channel = 100
        total_count = points_per_channel * self.num_chans
        scan_options = ScanOptions.BACKGROUND | ScanOptions.CONTINUOUS

        # Allocate a buffer for the scan
        self.memhandle = ul.win_buf_alloc(total_count)

        # Check if the buffer was successfully allocated
        if not self.memhandle:
            messagebox.showerror("Error", "Failed to allocate memory")
            self.start_button["state"] = tk.NORMAL
            return

        try:
            # Configure the setpoints
            ul.daq_set_setpoints(self.board_num, self.limit_a_list,
                                 self.limit_b_list, self.setpoint_flags_list,
                                 self.setpoint_output_list, self.output_1_list,
                                 self.output_2_list, self.output_mask_1_list,
                                 self.output_mask_2_list, self.setpoint_count)

            # Run the scan
            ul.daq_in_scan(self.board_num, self.chan_list, self.chan_type_list,
                           self.gain_list, self.num_chans, rate, 0, total_count,
                           self.memhandle, scan_options)

            # Cast the memhandle to a ctypes pointer
            # Note: the ctypes array will only be valid until win_buf_free
            # is called.
            # A copy of the buffer can be created using win_buf_to_array
            # before the memory is freed. The copy can be used at any time.
            self.array = cast(self.memhandle, POINTER(c_ushort))
        except ULError as e:
            # Free the allocated memory
            ul.win_buf_free(self.memhandle)
            show_ul_error(e)
            return

        # Start updating the displayed values
        self.update_displayed_values()

    def update_displayed_values(self):
        # Get the status from the device
        status, curr_count, curr_index = ul.get_status(
            self.board_num, FunctionType.DAQIFUNCTION)

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
            self.set_ui_idle_state()

    def update_status_labels(self, status, curr_count, curr_index):
        if status == Status.IDLE:
            self.setpoint_status_label["text"] = "Idle"
        else:
            self.setpoint_status_label["text"] = "Running"

        self.index_label["text"] = str(curr_index)
        self.count_label["text"] = str(curr_count)

    def display_values(self, curr_index, curr_count):
        array = self.array

        # If no data has been gathered, don't add data to the labels
        if curr_count > 1:
            # Convert the CH0 value to volts and display it
            chan_0_eng_value = ul.to_eng_units(
                self.board_num, self.gain_list[0], array[curr_index])
            self.chan_0_label["text"] = '{:.3f}'.format(
                chan_0_eng_value) + " Volts"

            # Convert the CH1 value to volts and display it
            chan_1_eng_value = ul.to_eng_units(
                self.board_num, self.gain_list[0], array[curr_index + 1])
            self.chan_1_label["text"] = '{:.3f}'.format(
                chan_1_eng_value) + " Volts"

            # Display the digital port value as hex
            self.digital_label["text"] = '0x' + \
                '{:0<2X}'.format(array[curr_index + 2])

            # Display the setpoint status as hex
            self.setpoint_status_label["text"] = '0x' + \
                '{:0<4X}'.format(array[curr_index + 3])

    def stop(self):
        ul.stop_background(self.board_num, FunctionType.DAQIFUNCTION)

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

        curr_row = 0
        chan_0_left_label = tk.Label(main_frame, justify=tk.LEFT, padx=3)
        chan_0_left_label["text"] = "Channel 0:"
        chan_0_left_label.grid(row=curr_row, column=0, sticky=tk.W)

        self.chan_0_label = tk.Label(main_frame, justify=tk.LEFT, padx=3)
        self.chan_0_label.grid(row=curr_row, column=1, sticky=tk.W)

        curr_row += 1
        chan_1_left_label = tk.Label(main_frame, justify=tk.LEFT, padx=3)
        chan_1_left_label["text"] = "Channel 1:"
        chan_1_left_label.grid(row=curr_row, column=0, sticky=tk.W)

        self.chan_1_label = tk.Label(main_frame, justify=tk.LEFT, padx=3)
        self.chan_1_label.grid(row=curr_row, column=1, sticky=tk.W)

        curr_row += 1
        digital_left_label = tk.Label(main_frame, justify=tk.LEFT, padx=3)
        digital_left_label["text"] = "FIRSTPORTA:"
        digital_left_label.grid(row=curr_row, column=0, sticky=tk.W)

        self.digital_label = tk.Label(main_frame, justify=tk.LEFT, padx=3)
        self.digital_label.grid(row=curr_row, column=1, sticky=tk.W)

        curr_row += 1
        setpoint_status_left_label = tk.Label(
            main_frame, justify=tk.LEFT, padx=3)
        setpoint_status_left_label["text"] = "Status:"
        setpoint_status_left_label.grid(
            row=curr_row, column=0, sticky=tk.W)

        self.setpoint_status_label = tk.Label(
            main_frame, justify=tk.LEFT, padx=3)
        self.setpoint_status_label["text"] = "Idle"
        self.setpoint_status_label.grid(
            row=curr_row, column=1, sticky=tk.W)

        curr_row += 1
        index_left_label = tk.Label(main_frame, justify=tk.LEFT, padx=3)
        index_left_label["text"] = "Index:"
        index_left_label.grid(row=curr_row, column=0, sticky=tk.W)

        self.index_label = tk.Label(main_frame, justify=tk.LEFT, padx=3)
        self.index_label["text"] = "-1"
        self.index_label.grid(row=curr_row, column=1, sticky=tk.W)

        curr_row += 1
        count_left_label = tk.Label(main_frame, justify=tk.LEFT, padx=3)
        count_left_label["text"] = "Count:"
        count_left_label.grid(row=curr_row, column=0, sticky=tk.W)

        self.count_label = tk.Label(main_frame, justify=tk.LEFT, padx=3)
        self.count_label["text"] = "0"
        self.count_label.grid(row=curr_row, column=1, sticky=tk.W)

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


if __name__ == "__main__":
    # Start the example
    DaqSetSetpoints01(master=tk.Tk()).mainloop()
