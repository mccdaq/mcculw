"""
File:                       ULAI01.py

Library Call Demonstrated:  mcculw.ul.a_in() or mcculw.ul.a_in_32()

Purpose:                    Reads an A/D Input Channel.

Demonstration:              Displays the analog input on a user-specified
                            channel.

Other Library Calls:        mcculw.ul.to_eng_units()
                                or mcculw.ul.to_eng_units_32()

Special Requirements:       Device must have an A/D converter.
                            Analog signal on an input channel.
"""
from __future__ import absolute_import, division, print_function
from builtins import *  # @UnusedWildImport

import tkinter as tk

from mcculw import ul
from mcculw.ul import ULError
from mcculw.device_info import DaqDeviceInfo

try:
    from ui_examples_util import UIExample, show_ul_error
except ImportError:
    from .ui_examples_util import UIExample, show_ul_error


class ULAI01(UIExample):
    def __init__(self, master):
        super(ULAI01, self).__init__(master)
        # By default, the example detects all available devices and selects the
        # first device listed.
        # If use_device_detection is set to False, the board_num property needs
        # to match the desired board number configured with Instacal.
        use_device_detection = True
        self.board_num = 0

        self.running = False

        try:
            if use_device_detection:
                self.configure_first_detected_device()

            self.device_info = DaqDeviceInfo(self.board_num)
            if self.device_info.supports_analog_input:
                self.ai_info = self.device_info.get_ai_info()
                self.create_widgets()
            else:
                self.create_unsupported_widgets()
        except ULError:
            self.create_unsupported_widgets(True)

    def update_value(self):
        channel = self.get_channel_num()
        ai_range = self.ai_info.supported_ranges[0]

        try:
            # Get a value from the device
            if self.ai_info.resolution <= 16:
                # Use the a_in method for devices with a resolution <= 16
                value = ul.a_in(self.board_num, channel, ai_range)
                # Convert the raw value to engineering units
                eng_units_value = ul.to_eng_units(self.board_num, ai_range,
                                                  value)
            else:
                # Use the a_in_32 method for devices with a resolution > 16
                # (optional parameter omitted)
                value = ul.a_in_32(self.board_num, channel, ai_range)
                # Convert the raw value to engineering units
                eng_units_value = ul.to_eng_units_32(self.board_num, ai_range,
                                                     value)

            # Display the raw value
            self.value_label["text"] = str(value)
            # Display the engineering value
            self.eng_value_label["text"] = '{:.3f}'.format(eng_units_value)

            # Call this method again until the stop button is pressed (or an
            # error occurs)
            if self.running:
                self.after(100, self.update_value)
        except ULError as e:
            self.stop()
            show_ul_error(e)

    def stop(self):
        self.running = False
        self.start_button["command"] = self.start
        self.start_button["text"] = "Start"

    def start(self):
        self.running = True
        self.start_button["command"] = self.stop
        self.start_button["text"] = "Stop"
        self.update_value()

    def get_channel_num(self):
        if self.ai_info.num_chans == 1:
            return 0
        try:
            return int(self.channel_entry.get())
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

            channel_entry_label = tk.Label(main_frame)
            channel_entry_label["text"] = "Channel Number:"
            channel_entry_label.grid(
                row=curr_row, column=0, sticky=tk.W)

            self.channel_entry = tk.Spinbox(
                main_frame, from_=0,
                to=max(self.ai_info.num_chans - 1, 0),
                validate='key', validatecommand=(channel_vcmd, '%P'))
            self.channel_entry.grid(
                row=curr_row, column=1, sticky=tk.W)

            curr_row += 1

        raw_value_left_label = tk.Label(main_frame)
        raw_value_left_label["text"] = "Value read from selected channel:"
        raw_value_left_label.grid(row=curr_row, column=0, sticky=tk.W)

        self.value_label = tk.Label(main_frame)
        self.value_label.grid(row=curr_row, column=1, sticky=tk.W)

        curr_row += 1
        eng_value_left_label = tk.Label(main_frame)
        eng_value_left_label["text"] = "Value converted to voltage:"
        eng_value_left_label.grid(row=curr_row, column=0, sticky=tk.W)

        self.eng_value_label = tk.Label(main_frame)
        self.eng_value_label.grid(row=curr_row, column=1, sticky=tk.W)

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


# Start the example if this module is being run
if __name__ == "__main__":
    # Start the example
    ULAI01(master=tk.Tk()).mainloop()
