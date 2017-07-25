from __future__ import absolute_import, division, print_function

from builtins import *  # @UnusedWildImport
from mcculw import ul
from mcculw.enums import InterfaceType
from mcculw.ul import ULError
from tkinter import StringVar
from tkinter.ttk import Combobox  # @UnresolvedImport

from examples.ui.uiexample import UIExample
import tkinter as tk


class DaqDevDiscovery01(UIExample):
    def __init__(self, master):
        super(DaqDevDiscovery01, self).__init__(master)

        self.board_num = 0

        self.device_created = False

        # Tell the UL to ignore any boards configured in InstaCal
        ul.ignore_instacal()

        self.create_widgets()

    def discover_devices(self):
        self.inventory = ul.get_daq_device_inventory(InterfaceType.ANY)

        if len(self.inventory) > 0:
            combobox_values = []
            for device in self.inventory:
                combobox_values.append(str(device))

            self.devices_combobox["values"] = combobox_values
            self.devices_combobox.current(0)
            self.status_label["text"] = (str(len(self.inventory))
                                         + " DAQ Device(s) Discovered")
            self.devices_combobox["state"] = "readonly"
            self.flash_led_button["state"] = "normal"
        else:
            self.devices_combobox["values"] = [""]
            self.devices_combobox.current(0)
            self.status_label["text"] = "No Devices Discovered"
            self.devices_combobox["state"] = "disabled"
            self.flash_led_button["state"] = "disabled"

        self.update_selected_device_id()

    def flash_led(self):
        try:
            # Flash the device LED
            ul.flash_led(self.board_num)
        except ULError as e:
            self.show_ul_error(e)

    def selected_device_changed(self, *args):  # @UnusedVariable
        selected_index = self.devices_combobox.current()
        inventory_count = len(self.inventory)

        if self.device_created:
            # Release any previously configured DAQ device from the UL.
            ul.release_daq_device(self.board_num)
            self.device_created = False

        if inventory_count > 0 and selected_index < inventory_count:
            descriptor = self.inventory[selected_index]
            # Update the device ID label
            self.device_id_label["text"] = descriptor.unique_id

            # Create the DAQ device from the descriptor
            # For performance reasons, it is not recommended to create
            # and release the device every time hardware communication is
            # required. Instead, create the device once and do not release
            # it until no additional library calls will be made for this
            # device
            ul.create_daq_device(self.board_num, descriptor)
            self.device_created = True

    def create_widgets(self):
        '''Create the tkinter UI'''
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.X, anchor=tk.NW)

        discover_button = tk.Button(main_frame)
        discover_button["text"] = "Discover DAQ Devices"
        discover_button["command"] = self.discover_devices
        discover_button.pack(padx=3, pady=3)

        self.status_label = tk.Label(main_frame)
        self.status_label["text"] = "Status"
        self.status_label.pack(anchor=tk.NW, padx=3, pady=3)

        results_group = tk.LabelFrame(self, text="Discovered Devices")
        results_group.pack(fill=tk.X, anchor=tk.NW, padx=3, pady=3)

        self.selected_device_textvar = StringVar()
        self.selected_device_textvar.trace('w', self.selected_device_changed)
        self.devices_combobox = Combobox(
            results_group, textvariable=self.selected_device_textvar)
        self.devices_combobox["state"] = "disabled"
        self.devices_combobox.pack(fill=tk.X, padx=3, pady=3)

        device_id_frame = tk.Frame(results_group)
        device_id_frame.pack(anchor=tk.NW)

        device_id_left_label = tk.Label(device_id_frame)
        device_id_left_label["text"] = "Device Identifier:"
        device_id_left_label.grid(row=0, column=0, sticky=tk.W, padx=3, pady=3)

        self.device_id_label = tk.Label(device_id_frame)
        self.device_id_label.grid(row=0, column=1, sticky=tk.W, padx=3, pady=3)

        self.flash_led_button = tk.Button(results_group)
        self.flash_led_button["text"] = "Flash LED"
        self.flash_led_button["command"] = self.flash_led
        self.flash_led_button["state"] = "disabled"
        self.flash_led_button.pack(padx=3, pady=3)

        button_frame = tk.Frame(self)
        button_frame.pack(fill=tk.X, side=tk.RIGHT, anchor=tk.SE)

        quit_button = tk.Button(button_frame)
        quit_button["text"] = "Quit"
        quit_button["command"] = self.master.destroy
        quit_button.grid(row=0, column=1, padx=3, pady=3)


# Start the example if this module is being run
if __name__ == "__main__":
    # Start the example
    DaqDevDiscovery01(master=tk.Tk()).mainloop()
