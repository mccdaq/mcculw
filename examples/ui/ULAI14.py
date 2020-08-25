"""
File:                       ULAI14.py

Library Call Demonstrated:  mcculw.ul.set_trigger()

Purpose:                    Selects the Trigger source. This trigger is
                            used to initiate A/D conversion using
                            mcculw.ul.a_in_scan(), with
                            mcculw.enums.ScanOptions.EXTTRIGGER Option.

Demonstration:              Selects the trigger source and
                            displays the analog input on up to eight channels.

Other Library Calls:        mcculw.ul.win_buf_alloc()
                                or mcculw.ul.win_buf_alloc_32()
                            mcculw.win_buf_free()
                            mcculw.ul.a_in_scan()
                            mcculw.ul.from_eng_units()
                            mcculw.ul.to_eng_units()
                                or mcculw.ul.to_eng_units_32()

Special Requirements:       Device must have software selectable
                            triggering source and type.
                            Device must have an A/D converter.
                            Analog signals on up to eight input channels.
"""
from __future__ import absolute_import, division, print_function
from builtins import *  # @UnusedWildImport

import tkinter as tk
from tkinter import messagebox
from ctypes import cast, POINTER, c_ushort, c_ulong

from mcculw import ul
from mcculw.enums import TrigType, ULRange, ScanOptions
from mcculw.ul import ULError
from mcculw.device_info import DaqDeviceInfo

try:
    from ui_examples_util import UIExample, show_ul_error
except ImportError:
    from .ui_examples_util import UIExample, show_ul_error


class ULAI14(UIExample):
    def __init__(self, master=None):
        super(ULAI14, self).__init__(master)
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
            self.ai_info = self.device_info.get_ai_info()
            if self.ai_info.is_supported and self.ai_info.supports_analog_trig:
                self.create_widgets()
            else:
                self.create_unsupported_widgets()
        except ULError:
            self.create_unsupported_widgets(True)

    def start_scan(self):
        low_chan = self.get_low_channel_num()
        high_chan = self.get_high_channel_num()

        if low_chan > high_chan:
            messagebox.showerror(
                "Error",
                "Low Channel Number must be greater than or equal to "
                "High Channel Number")
            self.start_button["state"] = tk.NORMAL
            return

        rate = 1000
        points_per_channel = 10
        num_channels = high_chan - low_chan + 1
        total_count = points_per_channel * num_channels
        ai_range = self.ai_info.supported_ranges[0]

        trig_type = TrigType.TRIG_ABOVE
        low_threshold_volts = 0.1
        high_threshold_volts = 1.53

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
            self.start_button["state"] = tk.NORMAL
            return

        try:
            low_threshold, high_threshold = self.get_threshold_counts(
                ai_range, low_threshold_volts, high_threshold_volts)

            ul.set_trigger(self.board_num, trig_type, low_threshold,
                           high_threshold)

            # Run the scan
            ul.a_in_scan(self.board_num, low_chan, high_chan, total_count,
                         rate, ai_range, memhandle, ScanOptions.EXTTRIGGER)

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
            self.display_values(array, ai_range, total_count,
                                low_chan, high_chan)
        except ULError as e:
            show_ul_error(e)
        finally:
            # Free the allocated memory
            ul.win_buf_free(memhandle)
            self.start_button["state"] = tk.NORMAL

    def get_threshold_counts(self, ai_range, low_threshold_volts,
                             high_threshold_volts):
        if self.ai_info.analog_trig_resolution == 0:
            # If the trigger resolution from AnalogInputProps is 0,
            # the resolution of the trigger is the same as the
            # analog input resolution, and we can use from_eng_units
            # to convert from engineering units to count
            low_threshold = ul.from_eng_units(self.board_num, ai_range,
                                              low_threshold_volts)
            high_threshold = ul.from_eng_units(self.board_num, ai_range,
                                               high_threshold_volts)
        else:
            # Otherwise, the resolution of the triggers are different
            # from the analog input, and we must convert from engineering
            # units to count manually

            trig_range = self.ai_info.analog_trig_range
            if trig_range == ULRange.UNKNOWN:
                # If the analog_trig_range is UNKNOWN, the trigger voltage
                # range is the same as the analog input.
                trig_range = ai_range

            low_threshold = self.volts_to_count(
                low_threshold_volts, self.ai_info.analog_trig_resolution,
                trig_range)
            high_threshold = self.volts_to_count(
                high_threshold_volts, self.ai_info.analog_trig_resolution,
                trig_range)

        return low_threshold, high_threshold

    def volts_to_count(self, volts, resolution, voltage_range):
        full_scale_count = 2 ** resolution
        range_min = voltage_range.range_min
        range_max = voltage_range.range_max
        return (full_scale_count / (range_max - range_min)
                * (volts - range_min))

    def display_values(self, array, range_, total_count, low_chan, high_chan):
        new_data_frame = tk.Frame(self.results_group)

        channel_text = []

        # Add the headers
        for chan_num in range(low_chan, high_chan + 1):
            channel_text.append("Channel " + str(chan_num) + "\n")

        chan_count = high_chan - low_chan + 1

        # Add (up to) the first 10 values for each channel to the text
        chan_num = low_chan
        for data_index in range(0, min(chan_count * 10, total_count)):
            if self.ai_info.resolution <= 16:
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
        if self.ai_info.num_chans == 1:
            return 0
        try:
            return int(self.low_channel_entry.get())
        except ValueError:
            return 0

    def get_high_channel_num(self):
        if self.ai_info.num_chans == 1:
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
            if value < 0 or value > self.ai_info.num_chans - 1:
                return False
        except ValueError:
            return False

        return True

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
        if self.ai_info.num_chans > 1:
            channel_vcmd = self.register(self.validate_channel_entry)

            low_channel_entry_label = tk.Label(main_frame)
            low_channel_entry_label["text"] = "Low Channel Number:"
            low_channel_entry_label.grid(
                row=curr_row, column=0, sticky=tk.W)

            self.low_channel_entry = tk.Spinbox(
                main_frame, from_=0,
                to=max(self.ai_info.num_chans - 1, 0),
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
                to=max(self.ai_info.num_chans - 1, 0),
                validatecommand=(channel_vcmd, '%P'))
            self.high_channel_entry.grid(
                row=curr_row, column=1, sticky=tk.W)
            initial_value = min(self.ai_info.num_chans - 1, 3)
            self.high_channel_entry.delete(0, tk.END)
            self.high_channel_entry.insert(0, str(initial_value))

            curr_row += 1

        self.results_group = tk.LabelFrame(
            self, text="Results", padx=3, pady=3)
        self.results_group.pack(fill=tk.X, anchor=tk.NW, padx=3, pady=3)

        self.data_frame = tk.Frame(self.results_group)
        self.data_frame.grid()

        curr_row += 1
        warning_label = tk.Label(
            self, justify=tk.LEFT, wraplength=400, fg="red")
        warning_label["text"] = (
            "Warning: Clicking Start will freeze the UI until the "
            "trigger condition is met. Real-world applications should "
            "run the a_in_scan method on a separate thread or use the "
            "BACKGROUND option.")
        warning_label.pack(fill=tk.X, anchor=tk.NW, padx=3, pady=3)

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
    ULAI14(master=tk.Tk()).mainloop()
