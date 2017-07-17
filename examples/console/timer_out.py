from __future__ import absolute_import, division, print_function

import time

from builtins import *  # @UnusedWildImport

from mcculw import ul
from mcculw.enums import CounterChannelType
from examples.console import util
from examples.props.counter import CounterProps
from mcculw.ul import ULError


use_device_detection = True


def run_example():
    board_num = 0

    if use_device_detection:
        ul.ignore_instacal()
        if not util.config_first_detected_device(board_num):
            print("Could not find device.")
            return

    ctr_props = CounterProps(board_num)

    # Find a timer channel on the board
    first_chan = next(
        (channel for channel in ctr_props.counter_info
         if channel.type == CounterChannelType.CTRTMR), None)

    if first_chan == None:
        util.print_unsupported_example(board_num)
        return

    timer_num = first_chan.channel_num
    frequency = 100

    try:
        # Start the timer output
        actual_frequency = ul.timer_out_start(
            board_num, timer_num, frequency)

        # Print information about the output
        print(
            "Outputting " + str(actual_frequency) + " Hz to timer channel "
            + str(timer_num) + ".")

        # Wait for 5 seconds
        time.sleep(5)

        # Stop the timer output
        ul.timer_out_stop(board_num, timer_num)

        print("Timer output stopped.")
    except ULError as e:
        util.print_ul_error(e)
    finally:
        if use_device_detection:
            ul.release_daq_device(board_num)


if __name__ == '__main__':
    run_example()
