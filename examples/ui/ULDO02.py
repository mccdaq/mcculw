from __future__ import absolute_import, division, print_function
from builtins import *  # @UnusedWildImport

from tkinter import IntVar

from mcculw import ul
from mcculw.enums import DigitalIODirection
from examples.ui.uiexample import UIExample
from examples.props.digital import DigitalProps
from mcculw.ul import ULError
import tkinter as tk


class ULDO02(UIExample):
    def __init__(self, master=None):
        super(ULDO02, self).__init__(master)
        master.protocol("WM_DELETE_WINDOW", self.exit)

        self.board_num = 0
        self.digital_props = DigitalProps(self.board_num)

        # Find the first port that supports output, defaulting to None
        # if one is not found.
        self.port = next(
            (port for port in self.digital_props.port_info
             if port.supports_output), None)

        # If the port is configurable, configure it for output
        if self.port != None and self.port.is_port_configurable:
            try:
                ul.d_config_port(
                    self.board_num, self.port.type, DigitalIODirection.OUT)
            except ULError as e:
                self.show_ul_error(e)

        self.create_widgets()

    def exit(self):
        # Set the port to 0 at exit
        try:
            ul.d_out(self.board_num, self.port.type, 0)
        except ULError as e:
            self.show_ul_error(e)
        self.master.destroy()

    def bit_checkbutton_changed(self, bit_num):
        try:
            # Get the value from the checkbutton
            bit_value = self.bit_checkbutton_vars[bit_num].get()
            # Output the value to the board
            ul.d_bit_out(self.board_num, self.port.type, bit_num, bit_value)
        except ULError as e:
            self.show_ul_error(e)

    def create_widgets(self):
        '''Create the tkinter UI'''
        if self.port != None:
            main_frame = tk.Frame(self)
            main_frame.pack(fill=tk.X, anchor=tk.NW)

            curr_row = 0
            bit_values_frame = tk.Frame(main_frame)
            bit_values_frame.grid(row=curr_row, column=0, padx=3, pady=3)

            label = tk.Label(bit_values_frame, text="Bit Number:")
            label.grid(row=0, column=0, sticky=tk.W)

            label = tk.Label(bit_values_frame, text="State:")
            label.grid(row=1, column=0, sticky=tk.W)

            # Create Checkbutton controls for each bit
            self.bit_checkbutton_vars = []
            max_bit = min(self.port.num_bits, 8)
            for bit_num in range(0, max_bit):
                bit_label = tk.Label(bit_values_frame, text=str(bit_num))
                bit_label.grid(row=0, column=bit_num + 1)

                var = IntVar(value=-1)
                bit_checkbutton = tk.Checkbutton(
                    bit_values_frame, tristatevalue=-1, variable=var,
                    borderwidth=0,
                    command=lambda n=bit_num:
                    self.bit_checkbutton_changed(n))
                bit_checkbutton.grid(row=1, column=bit_num + 1, padx=(5, 0))
                self.bit_checkbutton_vars.append(var)

            button_frame = tk.Frame(self)
            button_frame.pack(fill=tk.X, side=tk.RIGHT, anchor=tk.SE)

            quit_button = tk.Button(button_frame)
            quit_button["text"] = "Quit"
            quit_button["command"] = self.exit
            quit_button.grid(row=0, column=0, padx=3, pady=3)
        else:
            self.create_unsupported_widgets(self.board_num)


if __name__ == "__main__":
    # Start the example
    ULDO02(master=tk.Tk()).mainloop()
