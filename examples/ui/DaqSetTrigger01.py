from __future__ import absolute_import, division, print_function
from builtins import *  # @UnusedWildImport

from tkinter import messagebox

from mcculw import ul
from mcculw.enums import ScanOptions, Status, FunctionType, ChannelType, \
    ULRange, DigitalPortType, TriggerSensitivity, \
    TriggerEvent, TriggerSource
from examples.ui.uiexample import UIExample
from examples.props.ai import AnalogInputProps
from examples.props.counter import CounterProps
from examples.props.daqi import DaqInputProps
from examples.props.digital import DigitalProps
from mcculw.ul import ULError
import tkinter as tk


class DaqSetTrigger01(UIExample):
    def __init__(self, master=None):
        super(DaqSetTrigger01, self).__init__(master)

        self.board_num = 0
        self.daqi_props = DaqInputProps(self.board_num)
        if self.daqi_props.is_supported:
            self.ai_props = AnalogInputProps(self.board_num)
            self.digital_props = DigitalProps(self.board_num)
            self.counter_props = CounterProps(self.board_num)
            self.init_scan_channel_info()

        self.create_widgets()

    def init_scan_channel_info(self):
        self.num_chans = 4

        self.chan_list = []
        self.chan_type_list = []
        self.gain_list = []

        # Add analog input channels
        self.chan_list.append(0)
        self.chan_type_list.append(ChannelType.ANALOG)
        self.gain_list.append(ULRange.BIP10VOLTS)

        # Add a digital input channel
        self.chan_list.append(DigitalPortType.FIRSTPORTA)
        self.chan_type_list.append(ChannelType.DIGITAL8)
        self.gain_list.append(ULRange.NOTUSED)

        # Add a counter input channel
        self.chan_list.append(0)
        self.chan_type_list.append(ChannelType.CTR16)
        self.gain_list.append(ULRange.NOTUSED)

    def start_scan(self):
        rate = 100
        points_per_channel = 100
        total_count = points_per_channel * self.num_chans
        scan_options = (ScanOptions.BACKGROUND |
                        ScanOptions.CONTINUOUS | ScanOptions.EXTTRIGGER)

        # Allocate a buffer for the scan
        self.memhandle = ul.win_buf_alloc(total_count)

        # Check if the buffer was successfully allocated
        if not self.memhandle:
            messagebox.showerror("Error", "Failed to allocate memory")
            self.start_button["state"] = tk.NORMAL
            return

        try:
            # Set the start trigger settings
            ul.daq_set_trigger(
                self.board_num, TriggerSource.ANALOG_SW, TriggerSensitivity.RISING_EDGE,
                self.chan_list[0], self.chan_type_list[0], self.gain_list[0],
                2, 0, TriggerEvent.START)

            # Set the stop trigger settings
            ul.daq_set_trigger(
                self.board_num, TriggerSource.COUNTER, TriggerSensitivity.ABOVE_LEVEL,
                self.chan_list[2], self.chan_type_list[2], self.gain_list[2],
                2, 0, TriggerEvent.START)

            # Run the scan
            ul.daq_in_scan(
                self.board_num, self.chan_list, self.chan_type_list,
                self.gain_list, self.num_chans, rate, 0, total_count, self.memhandle,
                scan_options)

            # Cast the memhandle to a ctypes pointer
            # Note: the ctypes array will only be valid until win_buf_free
            # is called.
            # A copy of the buffer can be created using win_buf_to_array
            # before the memory is freed. The copy can be used at any time.
            self.array = self.memhandle_as_ctypes_array(self.memhandle)
        except ULError as e:
            # Free the allocated memory
            ul.win_buf_free(self.memhandle)
            self.show_ul_error(e)
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
            # Convert the analog value to volts and display it
            chan_0_eng_value = ul.to_eng_units(
                self.board_num, self.gain_list[0], array[curr_index])
            self.chan_0_label["text"] = '{:.3f}'.format(
                chan_0_eng_value) + " Volts"

            # Display the digital port value as hex
            self.digital_label["text"] = '0x' + \
                '{:0<2X}'.format(array[curr_index + 1])

            # Display the counter value
            self.counter_0_label["text"] = str(array[curr_index + 2])

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
        ul.stop_background(self.board_num, FunctionType.DAQIFUNCTION)

    def set_ui_idle_state(self):
        self.start_button["command"] = self.start
        self.start_button["text"] = "Start"

    def start(self):
        self.start_button["command"] = self.stop
        self.start_button["text"] = "Stop"
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
            if(value < 0 or value > self.ai_props.num_ai_chans - 1):
                return False
        except ValueError:
            return False

        return True

    def create_widgets(self):
        '''Create the tkinter UI'''
        if self.daqi_props.is_supported:
            main_frame = tk.Frame(self)
            main_frame.pack(fill=tk.X, anchor=tk.NW)

            curr_row = 0
            chan_0_left_label = tk.Label(main_frame, justify=tk.LEFT, padx=3)
            chan_0_left_label["text"] = "Channel 0:"
            chan_0_left_label.grid(row=curr_row, column=0, sticky=tk.W)

            self.chan_0_label = tk.Label(main_frame, justify=tk.LEFT, padx=3)
            self.chan_0_label.grid(row=curr_row, column=1, sticky=tk.W)

            curr_row += 1
            digital_left_label = tk.Label(main_frame, justify=tk.LEFT, padx=3)
            digital_left_label["text"] = "FIRSTPORTA:"
            digital_left_label.grid(row=curr_row, column=0, sticky=tk.W)

            self.digital_label = tk.Label(main_frame, justify=tk.LEFT, padx=3)
            self.digital_label.grid(row=curr_row, column=1, sticky=tk.W)

            curr_row += 1
            counter_0_left_label = tk.Label(
                main_frame, justify=tk.LEFT, padx=3)
            counter_0_left_label["text"] = "Counter 0:"
            counter_0_left_label.grid(row=curr_row, column=0, sticky=tk.W)

            self.counter_0_label = tk.Label(
                main_frame, justify=tk.LEFT, padx=3)
            self.counter_0_label.grid(row=curr_row, column=1, sticky=tk.W)

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
        else:
            self.create_unsupported_widgets(self.board_num)


if __name__ == "__main__":
    # Start the example
    DaqSetTrigger01(master=tk.Tk()).mainloop()
