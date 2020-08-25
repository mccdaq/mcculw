"""
File:                       ULAI07.py

Library Call Demonstrated:  mcculw.ul.a_trig()

Purpose:                    Waits for a specified analog input channel to
                            go above or below a specified value.

Demonstration:              Displays the digital value of a user-specified
                            analog input channel when the user-specifed
                            value is detected.

Other Library Calls:        mcculw.ul.from_eng_units()
                            mcculw.ul.to_eng_units()

Special Requirements:       Device must have an A/D converter.
                            Analog signal on an input channel.
"""
from __future__ import absolute_import, division, print_function
from builtins import *  # @UnusedWildImport

import tkinter as tk
from tkinter.ttk import Combobox  # @UnresolvedImport

from mcculw import ul
from mcculw.enums import TrigType
from mcculw.ul import ULError
from mcculw.device_info import DaqDeviceInfo

try:
    from ui_examples_util import UIExample, show_ul_error, validate_float_entry
except ImportError:
    from .ui_examples_util import UIExample, show_ul_error, validate_float_entry


class ULAI07(UIExample):
    def __init__(self, master=None):
        super(ULAI07, self).__init__(master)
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
            if self.ai_info.is_supported and self.ai_info.resolution <= 16:
                self.create_widgets()
            else:
                self.create_unsupported_widgets()
        except ULError:
            self.create_unsupported_widgets(True)

    def update_value(self):
        channel = self.get_channel_num()
        ai_range = self.ai_info.supported_ranges[0]

        try:
            gain = self.ai_info.supported_ranges[0]
            trig_type = self.get_trigger_type()
            trig_value_eng = self.get_trigger_level()
            trig_value = ul.from_eng_units(self.board_num, gain, trig_value_eng)

            # Get a value from the device
            value = ul.a_trig(self.board_num, channel,
                              trig_type, trig_value, gain)
            # Convert the raw value to engineering units
            eng_units_value = ul.to_eng_units(self.board_num, ai_range, value)

            # Display the raw value
            self.value_label["text"] = str(value)
            # Display the engineering value
            self.eng_value_label["text"] = '{:.3f}'.format(eng_units_value)
        except ULError as e:
            self.stop()
            show_ul_error(e)

    def start(self):
        self.update_value()

    def get_channel_num(self):
        try:
            return int(self.channel_entry.get())
        except ValueError:
            return 0

    def get_trigger_type(self):
        if self.trigger_type_combobox.get() == "Above":
            return TrigType.TRIG_ABOVE
        else:
            return TrigType.TRIG_BELOW

    def get_trigger_level(self):
        try:
            return float(self.trigger_level_entry.get())
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

        channel_vcmd = self.register(self.validate_channel_entry)
        float_vcmd = self.register(validate_float_entry)

        curr_row = 0
        channel_entry_label = tk.Label(main_frame)
        channel_entry_label["text"] = "Channel Number:"
        channel_entry_label.grid(row=curr_row, column=0, sticky=tk.W)

        self.channel_entry = tk.Spinbox(
            main_frame, from_=0,
            to=max(self.ai_info.num_chans - 1, 0),
            validate='key', validatecommand=(channel_vcmd, '%P'))
        self.channel_entry.grid(row=curr_row, column=1, sticky=tk.W)

        curr_row += 1
        trigger_type_label = tk.Label(main_frame)
        trigger_type_label["text"] = "Trigger Type:"
        trigger_type_label.grid(row=curr_row, column=0, sticky=tk.W)

        self.trigger_type_combobox = Combobox(main_frame)
        self.trigger_type_combobox["values"] = ["Above", "Below"]
        self.trigger_type_combobox["state"] = "readonly"
        self.trigger_type_combobox.current(0)
        self.trigger_type_combobox.grid(
            row=curr_row, column=1, sticky=tk.W)

        curr_row += 1
        trigger_level_label = tk.Label(main_frame)
        trigger_level_label["text"] = "Trigger Level (V):"
        trigger_level_label.grid(row=curr_row, column=0, sticky=tk.W)

        self.trigger_level_entry = tk.Entry(
            main_frame, validate='key',
            validatecommand=(float_vcmd, '%P'))
        self.trigger_level_entry.grid(
            row=curr_row, column=1, sticky=tk.W)
        self.trigger_level_entry.insert(0, "2")

        curr_row += 1
        raw_value_left_label = tk.Label(main_frame)
        raw_value_left_label["text"] = (
            "Value read from selected channel:")
        raw_value_left_label.grid(row=curr_row, column=0, sticky=tk.W)

        self.value_label = tk.Label(main_frame)
        self.value_label.grid(row=curr_row, column=1, sticky=tk.W)

        curr_row += 1
        eng_value_left_label = tk.Label(main_frame)
        eng_value_left_label["text"] = "Value converted to voltage:"
        eng_value_left_label.grid(row=curr_row, column=0, sticky=tk.W)

        self.eng_value_label = tk.Label(main_frame)
        self.eng_value_label.grid(row=curr_row, column=1, sticky=tk.W)

        curr_row += 1
        warning_label = tk.Label(
            main_frame, justify=tk.LEFT, wraplength=400, fg="red")
        warning_label["text"] = (
            "Warning: Clicking Start will freeze the UI until the "
            "trigger condition is met. Real-world applications should "
            "run the a_trig method on a separate thread.")
        warning_label.grid(row=curr_row, columnspan=2, sticky=tk.W)

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
    ULAI07(master=tk.Tk()).mainloop()
