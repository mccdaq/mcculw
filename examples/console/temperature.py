"""
File:                       temperature.py

Library Call Demonstrated:  mcculw.ul.t_in()

Purpose:                    Reads a temperature input channel.

Demonstration:              Displays the temperature input.

Other Library Calls:        mcculw.ul.release_daq_device()

Special Requirements:       Unless the board at BoardNum(=0) does not use
                            EXP boards for temperature measurements(the
                            CIO-DAS-TC or USB-2001-TC for example), it must
                            have an A/D converter with an attached EXP
                            board.  Thermocouples must be wired to EXP
                            channels selected.
"""
from __future__ import absolute_import, division, print_function
from builtins import *  # @UnusedWildImport

from mcculw import ul
from mcculw.enums import TempScale
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
        if ai_info.num_temp_chans <= 0:
            raise Exception('Error: The DAQ device does not support '
                            'temperature input')
        channel = 0

        # Get the value from the device (optional parameters omitted)
        value = ul.t_in(board_num, channel, TempScale.CELSIUS)

        # Display the value
        print('Channel', channel, 'Value (deg C):', value)
    except Exception as e:
        print('\n', e)
    finally:
        if use_device_detection:
            ul.release_daq_device(board_num)


if __name__ == '__main__':
    run_example()
