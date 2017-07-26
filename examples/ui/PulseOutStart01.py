from __future__ import absolute_import, division, print_function

from builtins import *  # @UnusedWildImport
from mcculw import ul
from mcculw.enums import CounterChannelType
from mcculw.ul import ULError

from examples.props.counter import CounterProps
from examples.ui.uiexample import UIExample
import tkinter as tk


class PulseOutStart01(UIExample):
    def __init__(self, master=None):
        super(PulseOutStart01, self).__init__(master)
        master.protocol("WM_DELETE_WINDOW", self.exit)

        self.board_num = 0
        self.ctr_props = CounterProps(self.board_num)

        # Find the first pulse counter
        first_chan = next(
            (channel for channel in self.ctr_props.counter_info
             if channel.type == CounterChannelType.CTRPULSE), None)
        if first_chan != None:
            last_chan = next(
                (channel for channel in reversed(self.ctr_props.counter_info)
                 if channel.type == CounterChannelType.CTRPULSE), None)
            self.first_chan_num = first_chan.channel_num
            self.last_chan_num = last_chan.channel_num
        else:
            self.first_chan_num = -1
            self.last_chan_num = -1

        self.create_widgets()

    def update_output(self):
        try:
            timer_num = self.get_channel_num()
            frequency = self.get_frequency()
            duty_cycle = self.get_duty_cycle()

            # Start the pulse output (optional parameters omitted)
            actual_freq, actual_duty_cycle, _ = ul.pulse_out_start(
                self.board_num, timer_num, frequency, duty_cycle)

            self.update_actual_values(actual_freq, actual_duty_cycle)
        except ULError as e:
            self.show_ul_error(e)

    def exit(self):
        # Stop all the timers at exit
        if self.first_chan_num != -1:
            for chan_num in range(self.first_chan_num, self.last_chan_num + 1):
                try:
                    ul.pulse_out_stop(self.board_num, chan_num)
                except ULError as e:
                    self.show_ul_error(e)
        self.master.destroy()

    def update_actual_values(self, actual_freq, actual_duty_cycle):
        self.actual_freq_label["text"] = str(actual_freq)
        self.actual_duty_cycle_label["text"] = str(actual_duty_cycle)

    def get_frequency(self):
        try:
            return float(self.freq_entry.get())
        except ValueError:
            return 100000

    def get_duty_cycle(self):
        try:
            return float(self.duty_cycle_entry.get())
        except ValueError:
            return 0.5

    def get_channel_num(self):
        if self.last_chan_num == self.first_chan_num:
            return self.last_chan_num
        try:
            return int(self.channel_entry.get())
        except ValueError:
            return 0

    def validate_channel_entry(self, p):
        if p == '':
            return True
        try:
            value = int(p)
            if(value < self.first_chan_num or value > self.last_chan_num):
                return False
        except ValueError:
            return False

        return True

    def create_widgets(self):
        '''Create the tkinter UI'''
        example_supported = self.first_chan_num != -1

        if example_supported:
            main_frame = tk.Frame(self)
            main_frame.pack(fill=tk.X, anchor=tk.NW)

            channel_vcmd = self.register(self.validate_channel_entry)
            float_vcmd = self.register(self.validate_float_entry)

            curr_row = 0
            if self.last_chan_num != self.first_chan_num:
                channel_entry_label = tk.Label(main_frame)
                channel_entry_label["text"] = "Channel Number:"
                channel_entry_label.grid(row=curr_row, column=0, sticky=tk.W)

                self.channel_entry = tk.Spinbox(
                    main_frame, from_=self.first_chan_num, to=self.last_chan_num,
                    validate='key', validatecommand=(channel_vcmd, '%P'))
                self.channel_entry.grid(row=curr_row, column=1, sticky=tk.W)

            curr_row += 1
            freq_label = tk.Label(main_frame)
            freq_label["text"] = "Frequency:"
            freq_label.grid(row=curr_row, column=0, sticky=tk.W)

            self.freq_entry = tk.Entry(
                main_frame, validate='key', validatecommand=(float_vcmd, '%P'))
            self.freq_entry.grid(row=curr_row, column=1, sticky=tk.W)
            self.freq_entry.insert(0, "100000")

            curr_row += 1
            duty_cycle_label = tk.Label(main_frame)
            duty_cycle_label["text"] = "Duty Cycle (0-1):"
            duty_cycle_label.grid(row=curr_row, column=0, sticky=tk.W)

            self.duty_cycle_entry = tk.Entry(
                main_frame, validate='key', validatecommand=(float_vcmd, '%P'))
            self.duty_cycle_entry.grid(row=curr_row, column=1, sticky=tk.W)
            self.duty_cycle_entry.insert(0, "0.5")

            curr_row += 1
            update_button = tk.Button(main_frame)
            update_button["text"] = "Update"
            update_button["command"] = self.update_output
            update_button.grid(row=curr_row, column=0,
                               columnspan=2, padx=3, pady=3)

            curr_row += 1
            actual_freq_left_label = tk.Label(main_frame)
            actual_freq_left_label["text"] = "Actual Frequency:"
            actual_freq_left_label.grid(row=curr_row, column=0, sticky=tk.W)

            self.actual_freq_label = tk.Label(main_frame)
            self.actual_freq_label.grid(row=curr_row, column=1, sticky=tk.W)

            curr_row += 1
            actual_duty_cycle_left_label = tk.Label(main_frame)
            actual_duty_cycle_left_label["text"] = "Actual Duty Cycle:"
            actual_duty_cycle_left_label.grid(
                row=curr_row, column=0, sticky=tk.W)

            self.actual_duty_cycle_label = tk.Label(main_frame)
            self.actual_duty_cycle_label.grid(
                row=curr_row, column=1, sticky=tk.W)

            button_frame = tk.Frame(self)
            button_frame.pack(fill=tk.X, side=tk.RIGHT, anchor=tk.SE)

            quit_button = tk.Button(button_frame)
            quit_button["text"] = "Quit"
            quit_button["command"] = self.exit
            quit_button.grid(row=0, column=1, padx=3, pady=3)
        else:
            self.create_unsupported_widgets(self.board_num)


if __name__ == "__main__":
    # Start the example
    PulseOutStart01(master=tk.Tk()).mainloop()
