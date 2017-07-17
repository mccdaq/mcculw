from __future__ import absolute_import, division, print_function
from builtins import *  # @UnusedWildImport

from mcculw import ul
from examples.ui.uiexample import UIExample
from mcculw.ul import ULError
import tkinter as tk


class ULFL01(UIExample):
    def __init__(self, master):
        super(ULFL01, self).__init__(master)

        self.board_num = 0
        self.create_widgets()

    def flash_led(self):
        try:
            ul.flash_led(self.board_num)
        except ULError as e:
            self.show_ul_error(e)

    def create_widgets(self):
        '''Create the tkinter UI'''
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.flash_led_button = tk.Button(self)
        self.flash_led_button["text"] = "Flash LED"
        self.flash_led_button["command"] = self.flash_led
        self.flash_led_button.grid(
            row=0, column=0, padx=3, pady=3, sticky=tk.NSEW)

        quit_button = tk.Button(self)
        quit_button["text"] = "Quit"
        quit_button["command"] = self.master.destroy
        quit_button.grid(
            row=0, column=1, padx=3, pady=3, sticky=tk.NSEW)


# Start the example if this module is being run
if __name__ == "__main__":
    # Start the example
    ULFL01(master=tk.Tk()).mainloop()
