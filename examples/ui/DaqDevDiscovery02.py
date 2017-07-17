from __future__ import absolute_import, division, print_function
from builtins import *  # @UnusedWildImport

from mcculw import ul
from examples.ui.uiexample import UIExample
from mcculw.ul import ULError
import tkinter as tk


class DaqDevDiscovery02(UIExample):
    def __init__(self, master):
        super(DaqDevDiscovery02, self).__init__(master)

        ul.ignore_instacal()
        self.board_num = 0
        self.device_created = False

        self.create_widgets()

    def discover_device(self):
        host = self.host_entry.get()
        port = self.get_port()
        timeout_ms = 5000

        try:
            # Release any previously created device
            if self.device_created:
                ul.release_daq_device(self.board_num)
                self.device_created = False

            descriptor = ul.get_net_device_descriptor(host, port, timeout_ms)
            if descriptor != None:
                # Create the DAQ device from the descriptor
                ul.create_daq_device(self.board_num, descriptor)
                self.device_created = True

                self.status_label["text"] = "DAQ Device Discovered"
                self.flash_led_button["state"] = "normal"
                self.device_name_label["text"] = descriptor.product_name
                self.device_id_label["text"] = descriptor.unique_id
            else:
                self.status_label["text"] = "No Device Discovered"
                self.flash_led_button["state"] = "disabled"
                self.device_name_label["text"] = ""
                self.device_id_label["text"] = ""

        except ULError as e:
            self.status_label["text"] = "No Device Discovered"
            self.flash_led_button["state"] = "disabled"
            self.device_name_label["text"] = ""
            self.device_id_label["text"] = ""
            self.show_ul_error(e)

    def flash_led(self):
        try:
            # Flash the device LED
            ul.flash_led(self.board_num)
        except ULError as e:
            self.show_ul_error(e)

    def get_port(self):
        try:
            return int(self.port_entry.get())
        except ValueError:
            return 0

    def update_selected_device_id(self, *args):
        selected_index = self.devices_combobox.current()
        inventory_count = len(self.inventory)
        if inventory_count > 0 and selected_index < inventory_count:
            descriptor = self.inventory[selected_index]
            self.device_id_label["text"] = descriptor.UniqueID

    def create_widgets(self):
        '''Create the tkinter UI'''
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.X, anchor=tk.NW)

        positive_int_vcmd = self.register(self.validate_positive_int_entry)

        settings_grid_frame = tk.Frame(main_frame)
        settings_grid_frame.pack(anchor=tk.NW)

        curr_row = 0
        host_label = tk.Label(settings_grid_frame)
        host_label["text"] = "Hostname or IP Address:"
        host_label.grid(row=curr_row, column=0, sticky=tk.W, padx=3, pady=3)

        self.host_entry = tk.Entry(settings_grid_frame)
        self.host_entry.grid(
            row=curr_row, column=1, sticky=tk.W, padx=3, pady=3)

        curr_row += 1
        port_label = tk.Label(settings_grid_frame)
        port_label["text"] = "Port:"
        port_label.grid(row=curr_row, column=0, sticky=tk.W, padx=3, pady=3)

        self.port_entry = tk.Entry(
            settings_grid_frame, validate="key",
            validatecommand=(positive_int_vcmd, "%P"))
        self.port_entry.grid(
            row=curr_row, column=1, sticky=tk.W, padx=3, pady=3)
        self.port_entry.insert(0, "54211")

        discover_button = tk.Button(main_frame)
        discover_button["text"] = "Discover DAQ Device"
        discover_button["command"] = self.discover_device
        discover_button.pack(padx=3, pady=3)

        self.status_label = tk.Label(main_frame)
        self.status_label["text"] = "Status"
        self.status_label.pack(anchor=tk.NW, padx=3, pady=3)

        results_group = tk.LabelFrame(self, text="Discovered Device")
        results_group.pack(fill=tk.X, anchor=tk.NW, padx=3, pady=3)

        device_info_frame = tk.Frame(results_group)
        device_info_frame.pack(anchor=tk.NW)

        curr_row = 0
        device_name_left_label = tk.Label(device_info_frame)
        device_name_left_label["text"] = "Device Identifier:"
        device_name_left_label.grid(
            row=curr_row, column=0, sticky=tk.W, padx=3, pady=3)

        self.device_name_label = tk.Label(device_info_frame)
        self.device_name_label.grid(
            row=curr_row, column=1, sticky=tk.W, padx=3, pady=3)

        curr_row += 1
        device_id_left_label = tk.Label(device_info_frame)
        device_id_left_label["text"] = "Device Identifier:"
        device_id_left_label.grid(row=curr_row, sticky=tk.W, padx=3, pady=3)

        self.device_id_label = tk.Label(device_info_frame)
        self.device_id_label.grid(
            row=curr_row, column=1, sticky=tk.W, padx=3, pady=3)

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
    DaqDevDiscovery02(master=tk.Tk()).mainloop()
