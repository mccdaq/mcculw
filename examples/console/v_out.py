from __future__ import absolute_import, division, print_function

from builtins import *  # @UnusedWildImport
from mcculw import ul
from mcculw.ul import ULError

from examples.console import util
from examples.props.ao import AnalogOutputProps


use_device_detection = True


def run_example():
    board_num = 0

    if use_device_detection:
        ul.ignore_instacal()
        if not util.config_first_detected_device(board_num):
            print("Could not find device.")
            return

    channel = 0

    ao_props = AnalogOutputProps(board_num)
    if ao_props.num_chans < 1:
        util.print_unsupported_example(board_num)
        return

    ao_range = ao_props.available_ranges[0]

    data_value = ao_range.range_max / 2

    try:
        print(
            "Outputting " + str(data_value) + " Volts to channel "
            + str(channel) + ".")
        # Send the value to the device (optional parameter omitted)
        ul.v_out(board_num, channel, ao_range, data_value)
    except ULError as e:
        util.print_ul_error(e)
    finally:
        if use_device_detection:
            ul.release_daq_device(board_num)


if __name__ == '__main__':
    run_example()
