from __future__ import absolute_import, division, print_function

from builtins import *  # @UnusedWildImport
from mcculw import ul
from mcculw.ul import ULError

from examples.props.ao import AnalogOutputProps
from examples.ui.uiexample import UIExample
import tkinter as tk


class ULAO01(UIExample):
    def __init__(self, master=None):
        super(ULAO01, self).__init__(master)

        self.board_num = 0
        self.ao_props = AnalogOutputProps(self.board_num)

        self.create_widgets()

    def update_value(self):
        channel = self.get_channel_num()
        ao_range = self.ao_props.available_ranges[0]
        data_value = self.get_data_value()

        raw_value = ul.from_eng_units(self.board_num, ao_range, data_value)

        try:
            ul.a_out(self.board_num, channel, ao_range, raw_value)
        except ULError as e:
            self.show_ul_error(e)

    def get_data_value(self):
        try:
            return float(self.data_value_entry.get())
        except ValueError:
            return 0

    def get_channel_num(self):
        if self.ao_props.num_chans == 1:
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
            if(value < 0 or value > self.ao_props.num_chans - 1):
                return False
        except ValueError:
            return False

        return True

    def create_widgets(self):
        '''Create the tkinter UI'''
        if self.ao_props.num_chans > 0:
            main_frame = tk.Frame(self)
            main_frame.pack(fill=tk.X, anchor=tk.NW)

            channel_vcmd = self.register(self.validate_channel_entry)
            float_vcmd = self.register(self.validate_float_entry)

            curr_row = 0
            if self.ao_props.num_chans > 1:
                channel_vcmd = self.register(self.validate_channel_entry)

                channel_entry_label = tk.Label(main_frame)
                channel_entry_label["text"] = "Channel Number:"
                channel_entry_label.grid(
                    row=curr_row, column=0, sticky=tk.W)

                self.channel_entry = tk.Spinbox(
                    main_frame, from_=0,
                    to=max(self.ao_props.num_chans - 1, 0),
                    validate='key', validatecommand=(channel_vcmd, '%P'))
                self.channel_entry.grid(
                    row=curr_row, column=1, sticky=tk.W)

                curr_row += 1

            units_text = self.ao_props.get_units_string(
                self.ao_props.available_ranges[0])
            value_label_text = "Value (" + units_text + "):"
            data_value_label = tk.Label(main_frame)
            data_value_label["text"] = value_label_text
            data_value_label.grid(row=curr_row, column=0, sticky=tk.W)

            self.data_value_entry = tk.Entry(
                main_frame, validate='key', validatecommand=(float_vcmd, '%P'))
            self.data_value_entry.grid(row=curr_row, column=1, sticky=tk.W)
            self.data_value_entry.insert(0, "0")

            update_button = tk.Button(main_frame)
            update_button["text"] = "Update"
            update_button["command"] = self.update_value
            update_button.grid(row=curr_row, column=2, padx=3, pady=3)

            button_frame = tk.Frame(self)
            button_frame.pack(fill=tk.X, side=tk.RIGHT, anchor=tk.SE)

            quit_button = tk.Button(button_frame)
            quit_button["text"] = "Quit"
            quit_button["command"] = self.master.destroy
            quit_button.grid(row=0, column=0, padx=3, pady=3)
        else:
            self.create_unsupported_widgets(self.board_num)


if __name__ == "__main__":
    # Start the example
    ULAO01(master=tk.Tk()).mainloop()
