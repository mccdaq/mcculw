from __future__ import absolute_import, division, print_function

import time

from builtins import *  # @UnusedWildImport
from mcculw import ul
from mcculw.enums import CounterChannelType
from mcculw.ul import ULError

from examples.console import util
from examples.props.counter import CounterProps


use_device_detection = True


def run_example():
    board_num = 0

    if use_device_detection:
        ul.ignore_instacal()
        if not util.config_first_detected_device(board_num):
            print("Could not find device.")
            return

    ctr_props = CounterProps(board_num)

    # Find a pulse timer channel on the board
    first_chan = next(
        (channel for channel in ctr_props.counter_info
         if channel.type == CounterChannelType.CTRPULSE), None)

    if first_chan == None:
        util.print_unsupported_example(board_num)
        return

    timer_num = first_chan.channel_num
    frequency = 100
    duty_cycle = 0.5

    try:
        # Start the pulse timer output (optional parameters omitted)
        actual_frequency, actual_duty_cycle, _ = ul.pulse_out_start(
            board_num, timer_num, frequency, duty_cycle)

        # Print information about the output
        print(
            "Outputting " + str(actual_frequency)
            + " Hz with a duty cycle of " + str(actual_duty_cycle)
            + " to pulse timer channel " + str(timer_num) + ".")

        # Wait for 5 seconds
        time.sleep(5)

        # Stop the pulse timer output
        ul.pulse_out_stop(board_num, timer_num)

        print("Timer output stopped.")
    except ULError as e:
        util.print_ul_error(e)
    finally:
        if use_device_detection:
            ul.release_daq_device(board_num)


if __name__ == '__main__':
    run_example()
