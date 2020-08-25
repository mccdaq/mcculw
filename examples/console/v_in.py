"""
File:                       v_in.py

Library Call Demonstrated:  mcculw.ul.v_in() or mcculw.ul.v_in_32

Purpose:                    Reads an A/D Input Channel.

Demonstration:              Displays the voltage input on a user-specified
                            channel.

Other Library Calls:        mcculw.ul.release_daq_device()

Special Requirements:       Device must have an A/D converter.
                            Analog signal on an input channel.
"""
from __future__ import absolute_import, division, print_function
from builtins import *  # @UnusedWildImport

from mcculw import ul
from mcculw.device_info import DaqDeviceInfo

try:
    from console_examples_util import config_first_detected_device
except ImportError:
    from .console_examples_util import config_first_detected_device


def run_example():
    # By default, the example detects and displays all available devices and
    # selects the first device listed. Use the dev_id_list variable to filter
    # detected devices by device ID (see UL documentation for device IDs).
    # If use_device_detection is set to False, the board_num variable needs to
    # match the desired board number configured with Instacal.
    use_device_detection = True
    dev_id_list = []
    board_num = 0

    try:
        if use_device_detection:
            config_first_detected_device(board_num, dev_id_list)

        daq_dev_info = DaqDeviceInfo(board_num)
        if not daq_dev_info.supports_analog_input:
            raise Exception('Error: The DAQ device does not support '
                            'analog input')

        print('\nActive DAQ device: ', daq_dev_info.product_name, ' (',
              daq_dev_info.unique_id, ')\n', sep='')

        ai_info = daq_dev_info.get_ai_info()
        ai_range = ai_info.supported_ranges[0]
        channel = 0

        # Get a value from the device
        if ai_info.resolution <= 16:
            # Use the v_in method for devices with a resolution <= 16
            # (optional parameter omitted)
            value = ul.v_in(board_num, channel, ai_range)
        else:
            # Use the v_in_32 method for devices with a resolution > 16
            # (optional parameter omitted)
            value = ul.v_in_32(board_num, channel, ai_range)

        # Display the value
        print('Value:', value)
    except Exception as e:
        print('\n', e)
    finally:
        if use_device_detection:
            ul.release_daq_device(board_num)


if __name__ == '__main__':
    run_example()
