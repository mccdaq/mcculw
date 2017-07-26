from __future__ import absolute_import, division, print_function

from builtins import *  # @UnusedWildImport
from mcculw import ul
from mcculw.enums import TempScale, ErrorCode
from mcculw.ul import ULError

from examples.props.ai import AnalogInputProps
from examples.ui.uiexample import UIExample
import tkinter as tk


class ULTI02(UIExample):
    def __init__(self, master):
        super(ULTI02, self).__init__(master)

        self.board_num = 0
        self.ai_props = AnalogInputProps(self.board_num)

        self.running = False

        self.create_widgets()

    def update_values(self):
        try:
            # Get the values from the device (optional parameters omitted)
            err_code, data_array = ul.t_in_scan(
                self.board_num, self.low_chan, self.high_chan,
                TempScale.CELSIUS)

            # Check err_code for OUTOFRANGE or OPENCONNECTION. All other
            # error codes will raise a ULError and are checked by the except
            # clause.
            if err_code == ErrorCode.OUTOFRANGE:
                self.warning_label["text"] = (
                    "A thermocouple input is out of range.")
            elif err_code == ErrorCode.OPENCONNECTION:
                self.warning_label["text"] = (
                    "A thermocouple input has an open connection.")

            self.display_values(data_array)

            # Call this method again until the stop button is pressed (or an
            # error occurs)
            if self.running:
                self.after(100, self.update_values)
        except ULError as e:
            self.stop()
            self.show_ul_error(e)

    def display_values(self, array):
        low_chan = self.low_chan
        high_chan = self.high_chan

        for chan_num in range(low_chan, high_chan + 1):
            index = chan_num - low_chan
            self.data_labels[index]["text"] = '{:.3f}'.format(
                array[index]) + "\n"

    def stop(self):
        self.running = False
        self.start_button["command"] = self.start
        self.start_button["text"] = "Start"
        self.low_channel_entry["state"] = tk.NORMAL
        self.high_channel_entry["state"] = tk.NORMAL

    def start(self):
        self.running = True
        self.start_button["command"] = self.stop
        self.start_button["text"] = "Stop"
        self.low_channel_entry["state"] = tk.DISABLED
        self.high_channel_entry["state"] = tk.DISABLED
        self.low_chan = self.get_low_channel_num()
        self.high_chan = self.get_high_channel_num()
        self.recreate_data_frame()
        self.update_values()

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
            if(value < 0 or value > self.ai_props.num_ti_chans - 1):
                return False
        except ValueError:
            return False

        return True

    def recreate_data_frame(self):
        low_chan = self.low_chan
        high_chan = self.high_chan
        channels_per_row = 4

        new_data_frame = tk.Frame(self.results_group)

        self.data_labels = []
        row = 0
        column = 0
        # Add the labels for each channel
        for chan_num in range(low_chan, high_chan + 1):
            chan_label = tk.Label(new_data_frame, justify=tk.LEFT, padx=3)
            chan_label["text"] = "Channel " + str(chan_num)
            chan_label.grid(row=row, column=column)

            data_label = tk.Label(new_data_frame, justify=tk.LEFT, padx=3)
            data_label.grid(row=row + 1, column=column)
            self.data_labels.append(data_label)

            column += 1
            if column >= channels_per_row:
                row += 2
                column = 0

        self.data_frame.destroy()
        self.data_frame = new_data_frame
        self.data_frame.pack(side=tk.TOP)

    def create_widgets(self):
        '''Create the tkinter UI'''
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.X, anchor=tk.NW)

        example_supported = self.ai_props.num_ti_chans > 1

        if example_supported:
            channel_vcmd = self.register(self.validate_channel_entry)

            curr_row = 0

            if self.ai_props.num_ti_chans > 1:
                low_channel_entry_label = tk.Label(main_frame)
                low_channel_entry_label["text"] = "Low Channel Number:"
                low_channel_entry_label.grid(
                    row=curr_row, column=0, sticky=tk.W)

                self.low_channel_entry = tk.Spinbox(
                    main_frame, from_=0,
                    to=max(self.ai_props.num_ti_chans - 1, 0),
                    validate='key', validatecommand=(channel_vcmd, '%P'))
                self.low_channel_entry.grid(
                    row=curr_row, column=1, sticky=tk.W)

                curr_row += 1
                high_channel_entry_label = tk.Label(main_frame)
                high_channel_entry_label["text"] = "High Channel Number:"
                high_channel_entry_label.grid(
                    row=curr_row, column=0, sticky=tk.W)

                self.high_channel_entry = tk.Spinbox(
                    main_frame, from_=0,
                    to=max(self.ai_props.num_ti_chans - 1, 0),
                    validate='key', validatecommand=(channel_vcmd, '%P'))
                self.high_channel_entry.grid(
                    row=curr_row, column=1, sticky=tk.W)
                initial_value = min(self.ai_props.num_ti_chans - 1, 3)
                self.high_channel_entry.delete(0, tk.END)
                self.high_channel_entry.insert(0, str(initial_value))

            self.results_group = tk.LabelFrame(self, text="Results")
            self.results_group.pack(fill=tk.X, anchor=tk.NW, padx=3, pady=3)

            self.data_frame = tk.Frame(self.results_group)
            self.data_frame.pack(side=tk.TOP)

            self.warning_label = tk.Label(self.results_group, fg="red")
            self.warning_label.pack(side=tk.BOTTOM)

            button_frame = tk.Frame(self)
            button_frame.pack(fill=tk.X, side=tk.RIGHT, anchor=tk.SE)

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


# Start the example if this module is being run
if __name__ == "__main__":
    # Start the example
    ULTI02(master=tk.Tk()).mainloop()
