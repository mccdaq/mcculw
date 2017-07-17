from __future__ import absolute_import, division, print_function

from builtins import *  # @UnusedWildImport

from mcculw import ul
from mcculw.enums import TempScale
from mcculw.examples.console import util
from mcculw.examples.props.ai import AnalogInputProps
from mcculw.ul import ULError


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
    if ai_props.num_ti_chans < 1:
        util.print_unsupported_example(board_num)
        return

    try:
        value = ul.t_in(board_num, channel, TempScale.CELSIUS)

        # Display the value
        print("Channel " + str(channel) + " Value (deg C): " + str(value))
    except ULError as e:
        util.print_ul_error(e)
    finally:
        if use_device_detection:
            ul.release_daq_device(board_num)


if __name__ == '__main__':
    run_example()
