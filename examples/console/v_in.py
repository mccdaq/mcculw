from __future__ import absolute_import, division, print_function

from builtins import *  # @UnusedWildImport
from mcculw import ul
from mcculw.ul import ULError

from examples.console import util
from examples.props.ai import AnalogInputProps


use_device_detection = True


def run_example():
    board_num = 0

    if use_device_detection:
        ul.ignore_instacal()
        if not util.config_first_detected_device(board_num):
            print("Could not find device.")
            return

    channel = 0

    ai_props = AnalogInputProps(board_num)
    if ai_props.num_ai_chans < 1:
        util.print_unsupported_example(board_num)
        return

    ai_range = ai_props.available_ranges[0]

    try:
        # Get a value from the device
        if ai_props.resolution <= 16:
            # Use the v_in method for devices with a resolution <= 16
            # (optional parameter omitted)
            value = ul.v_in(board_num, channel, ai_range)
        else:
            # Use the v_in_32 method for devices with a resolution > 16
            # (optional parameter omitted)
            value = ul.v_in_32(board_num, channel, ai_range)

        # Display the value
        print("Value: " + str(value))
    except ULError as e:
        util.print_ul_error(e)
    finally:
        if use_device_detection:
            ul.release_daq_device(board_num)


if __name__ == '__main__':
    run_example()
