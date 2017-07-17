from __future__ import absolute_import, division, print_function

from builtins import *  # @UnusedWildImport

from mcculw import ul
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
    if ctr_props.num_chans < 1:
        util.print_unsupported_example(board_num)
        return

    # Use the first counter channel on the board (some boards start channel
    # numbering at 1 instead of 0, CounterProps are used here to find the
    # first one).
    counter_num = ctr_props.counter_info[0].channel_num

    try:
        # Get a value from the device
        value = ul.c_in_32(board_num, counter_num)
        # Display the value
        print("Counter Value: " + str(value))
    except ULError as e:
        util.print_ul_error(e)
    finally:
        if use_device_detection:
            ul.release_daq_device(board_num)


if __name__ == '__main__':
    run_example()
