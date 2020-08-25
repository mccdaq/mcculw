"""
File:                       ULGT04.py

Library Call Demonstrated:  mcculw.get_board_name()

Purpose:                    Lists board names of boards installed or supported
                            by Universal Library.

Demonstration:              Displays the board names of all boards configured
                            with Instacal when the List Installed button is
                            clicked. Lists all boards supported by the base
                            Universal Library when the List Supported button is
                            clicked. Note that this does not necessarily reflect
                            the boards supported by the mcculw Python layer.

Other Library Calls:        mcculw.ul.get_config()
"""
from __future__ import absolute_import, division, print_function
from builtins import *  # @UnusedWildImport

import tkinter as tk

from mcculw import ul
from mcculw.enums import InfoType, GlobalInfo, Iterator
from mcculw.ul import ULError
from mcculw.device_info import DaqDeviceInfo

try:
    from ui_examples_util import UIExample, show_ul_error
except ImportError:
    from .ui_examples_util import UIExample, show_ul_error


class ULGT04(UIExample):
    def __init__(self, master):
        super(ULGT04, self).__init__(master)

        self.max_board_num = ul.get_config(InfoType.GLOBALINFO, 0, 0,
                                           GlobalInfo.NUMBOARDS)
        self.create_widgets()
        self.list_installed()

    def list_installed(self):
        installed_text = ""
        for board_num in range(0, self.max_board_num):
            try:
                device_info = DaqDeviceInfo(board_num)
                installed_text += ("Board #" + str(board_num) + " = "
                                   + device_info.product_name + "\n")
            except ULError:
                pass

        self.info_groupbox["text"] = "Installed Devices"
        self.info_text.delete(0.0, tk.END)
        self.info_text.insert(0.0, installed_text[:-1])

    def list_supported(self):
        supported_text = ("Note: this lists all boards supported by the base "
                          "Universal Library, and does not necessarily reflect "
                          "those supported by the Python layer.\n\n")

        try:
            board_name = ul.get_board_name(Iterator.GET_FIRST)
            supported_text += board_name + "\n"
        except ULError as e:
            show_ul_error(e)
            return

        while len(board_name) > 3:
            try:
                board_name = ul.get_board_name(Iterator.GET_NEXT)
                supported_text += board_name + "\n"
            except ULError as e:
                show_ul_error(e)
                return

        self.info_groupbox["text"] = "Supported Devices"
        self.info_text.delete(0.0, tk.END)
        self.info_text.insert(0.0, supported_text[:-1])

    def create_widgets(self):
        '''Create the tkinter UI'''
        self.info_groupbox = tk.LabelFrame(self, text="Installed Devices")
        self.info_groupbox.pack(
            fill=tk.BOTH, anchor=tk.NW, padx=3, pady=3, expand=True)

        scrollbar = tk.Scrollbar(self.info_groupbox)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=3, pady=3)

        self.info_text = tk.Text(
            self.info_groupbox, width=50, height=15, wrap=tk.WORD,
            yscrollcommand=scrollbar.set)
        self.info_text.pack(
            side=tk.LEFT, fill=tk.BOTH, padx=3, pady=3, expand=True)

        scrollbar.config(command=self.info_text.yview)

        upper_button_frame = tk.Frame(self)
        upper_button_frame.pack(fill=tk.BOTH, anchor=tk.S)
        upper_button_frame.grid_columnconfigure(0, weight=1)
        upper_button_frame.grid_columnconfigure(1, weight=1)

        list_installed_button = tk.Button(upper_button_frame)
        list_installed_button["text"] = "List Installed"
        list_installed_button["command"] = self.list_installed
        list_installed_button.grid(
            row=0, column=0, padx=3, pady=3, sticky=tk.NSEW)

        list_installed_button = tk.Button(upper_button_frame)
        list_installed_button["text"] = "List Supported"
        list_installed_button["command"] = self.list_supported
        list_installed_button.grid(
            row=0, column=1, padx=3, pady=3, sticky=tk.NSEW)

        button_frame = tk.Frame(self)
        button_frame.pack(fill=tk.X, side=tk.RIGHT, anchor=tk.SE)

        quit_button = tk.Button(button_frame)
        quit_button["text"] = "Quit"
        quit_button["command"] = self.master.destroy
        quit_button.grid(row=0, column=0, padx=3, pady=3)


# Start the example if this module is being run
if __name__ == "__main__":
    # Start the example
    ULGT04(master=tk.Tk()).mainloop()
