from __future__ import absolute_import, division, print_function
from builtins import *  # @UnusedWildImport

from tkinter import StringVar

from mcculw import ul
from mcculw.enums import InfoType, GlobalInfo, BoardInfo, DigitalInfo, \
    ExpansionInfo
from examples.ui.uiexample import UIExample
from mcculw.ul import ULError
import tkinter as tk


class ULGT03(UIExample):
    def __init__(self, master):
        super(ULGT03, self).__init__(master)

        self.max_board_num = self.get_max_board_num()
        self.board_num = 0
        self.create_widgets()
        self.update_board_info()

    def update_board_info(self):
        info_text = ""

        board_type = self.get_board_type()

        if board_type != 0:
            info_text += self.get_ad_info()
            info_text += self.get_temperature_info()
            info_text += self.get_da_info()
            info_text += self.get_digital_info()
            info_text += self.get_counter_info()
            info_text += self.get_expansion_info()
            # Remove the last "newline" character
            info_text = info_text[:-1]
        else:
            info_text = (
                "No board found at board number " + str(self.board_num)
                + ". Run InstaCal to add or remove boards before running this program.")

        self.info_label["text"] = info_text

    def get_board_type(self):
        try:
            return ul.get_config(
                InfoType.BOARDINFO, self.board_num, 0, BoardInfo.BOARDTYPE)
        except ULError:
            return 0

    def get_ad_info(self):
        try:
            num_ad_chans = ul.get_config(
                InfoType.BOARDINFO, self.board_num, 0, BoardInfo.NUMADCHANS)
            if num_ad_chans > 0:
                return "Number of A/D channels: " + str(num_ad_chans) + "\n"
        except ULError:
            return ""

        return ""

    def get_temperature_info(self):
        try:
            num_ti_chans = ul.get_config(
                InfoType.BOARDINFO, self.board_num, 0, BoardInfo.NUMTEMPCHANS)
            if num_ti_chans > 0:
                return ("Number of temperature channels: "
                        + str(num_ti_chans) + "\n")
        except ULError:
            return ""

        return ""

    def get_da_info(self):
        try:
            num_da_chans = ul.get_config(
                InfoType.BOARDINFO, self.board_num, 0, BoardInfo.NUMDACHANS)
            if num_da_chans > 0:
                return ("Number of D/A channels: "
                        + str(num_da_chans) + "\n")
        except ULError:
            return ""

        return ""

    def get_digital_info(self):
        try:
            num_di_ports = ul.get_config(
                InfoType.BOARDINFO, self.board_num, 0, BoardInfo.DINUMDEVS)
        except ULError:
            return ""
        if num_di_ports < 1:
            return ""

        result = ""
        for port_num in range(0, num_di_ports):
            try:
                num_bits = ul.get_config(
                    InfoType.DIGITALINFO, self.board_num,
                    port_num, DigitalInfo.NUMBITS)

                result += ("Digital Port #" + str(port_num) + ": "
                           + str(num_bits) + " bits\n")
            except ULError:
                pass
        return result

    def get_counter_info(self):
        try:
            num_ctr_chans = ul.get_config(
                InfoType.BOARDINFO, self.board_num, 0, BoardInfo.CINUMDEVS)
            if num_ctr_chans > 0:
                return ("Number of counter devices: "
                        + str(num_ctr_chans) + "\n")
        except ULError:
            return ""

        return ""

    def get_expansion_info(self):
        try:
            num_exps = ul.get_config(
                InfoType.BOARDINFO, self.board_num, 0, BoardInfo.NUMEXPS)
        except ULError:
            return ""

        result = ""
        for exp_num in range(0, num_exps):
            try:
                exp_board_type = ul.get_config(
                    InfoType.EXPANSIONINFO, self.board_num, exp_num,
                    ExpansionInfo.BOARDTYPE)
                exp_mux_first_chan = ul.get_config(
                    InfoType.EXPANSIONINFO, self.board_num, exp_num,
                    ExpansionInfo.MUX_AD_CHAN1)

                result += (
                    "A/D channel " + str(exp_mux_first_chan) +
                    " connected to EXP (device ID=" + str(exp_board_type) + ").\n")
            except ULError:
                pass

        return result

    def get_max_board_num(self):
        return ul.get_config(
            InfoType.GLOBALINFO, 0, 0, GlobalInfo.NUMBOARDS)

    def board_num_changed(self, *args):
        try:
            self.board_num = int(self.board_num_variable.get())
            self.update_board_info()
        except ValueError:
            self.board_num = 0

    def create_widgets(self):
        '''Create the tkinter UI'''
        main_frame = tk.Frame(self)
        main_frame.pack(fill=tk.X, anchor=tk.NW)

        positive_int_vcmd = self.register(self.validate_positive_int_entry)

        board_num_label = tk.Label(main_frame)
        board_num_label["text"] = "Board Number:"
        board_num_label.grid(row=0, column=0, sticky=tk.W)

        self.board_num_variable = StringVar()
        board_num_entry = tk.Spinbox(
            main_frame, from_=0, to=self.max_board_num,
            textvariable=self.board_num_variable,
            validate="key", validatecommand=(positive_int_vcmd, "%P"))
        board_num_entry.grid(row=0, column=1, sticky=tk.W)
        self.board_num_variable.trace("w", self.board_num_changed)

        info_groupbox = tk.LabelFrame(self, text="Board Information")
        info_groupbox.pack(fill=tk.X, anchor=tk.NW, padx=3, pady=3)

        self.info_label = tk.Label(
            info_groupbox, justify=tk.LEFT, wraplength=400)
        self.info_label.grid()

        button_frame = tk.Frame(self)
        button_frame.pack(fill=tk.X, side=tk.RIGHT, anchor=tk.SE)

        quit_button = tk.Button(button_frame)
        quit_button["text"] = "Quit"
        quit_button["command"] = self.master.destroy
        quit_button.grid(row=0, column=0, padx=3, pady=3)


# Start the example if this module is being run
if __name__ == "__main__":
    # Start the example
    ULGT03(master=tk.Tk()).mainloop()
