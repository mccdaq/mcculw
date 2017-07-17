from __future__ import absolute_import, division, print_function
from builtins import *  # @UnusedWildImport

from mcculw import ul
from mcculw.enums import DigitalIODirection
from examples.ui.uiexample import UIExample
from examples.props.digital import DigitalProps
from mcculw.ul import ULError
import tkinter as tk


class ULDI06(UIExample):
    def __init__(self, master=None):
        super(ULDI06, self).__init__(master)

        self.board_num = 0
        self.digital_props = DigitalProps(self.board_num)

        # Find the first port that supports input, defaulting to None
        # if one is not found.
        self.port = next(
            (port for port in self.digital_props.port_info
             if (port.supports_input and port.is_bit_configurable)), None)
        self.running = False

        self.create_widgets()

    def update_value(self):
        try:
            # Get a value from the device
            value = ul.d_bit_in(
                self.board_num, self.port.type, self.port.first_bit)

            # Display the value
            self.value_label["text"] = str(value)

            # Call this method again until the stop button is pressed (or an
            # error occurs)
            if self.running:
                self.after(100, self.update_value)
        except ULError as e:
            self.stop()
            self.show_ul_error(e)

    def stop(self):
        self.running = False
        self.start_button["command"] = self.start
        self.start_button["text"] = "Start"

    def start(self):
        self.running = True
        self.start_button["command"] = self.stop
        self.start_button["text"] = "Stop"

        try:
            ul.d_config_bit(
                self.board_num, self.port.type, self.port.first_bit,
                DigitalIODirection.IN)
        except ULError as e:
            self.stop()
            self.show_ul_error(e)
            return

        self.update_value()

    def create_widgets(self):
        '''Create the tkinter UI'''
        if self.port != None:
            main_frame = tk.Frame(self)
            main_frame.pack(fill=tk.X, anchor=tk.NW)

            curr_row = 0
            raw_value_left_label = tk.Label(main_frame)
            raw_value_left_label["text"] = (
                self.port.type.name + " bit " + str(self.port.first_bit)
                + " value read:")
            raw_value_left_label.grid(row=curr_row, column=0, sticky=tk.W)

            self.value_label = tk.Label(main_frame)
            self.value_label.grid(row=curr_row, column=1, sticky=tk.W)

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
    ULDI06(master=tk.Tk()).mainloop()
