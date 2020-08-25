"""
File:                       c_in.py

Library Call Demonstrated:  mcculw.ul.c_in_32()
                            mcculw.ul.c_clear()

Purpose:                    Operate the counter.

Demonstration:              Resets and reads the counter.

Other Library Calls:        mcculw.ul.release_daq_device()

Special Requirements:       Device must have an Event Counter (or Scan Counter
                            that doesn't require configuration) such as the
                            miniLAB 1008, USB-CTR04 or USB-1208LS.
"""
from __future__ import absolute_import, division, print_function
from builtins import *  # @UnusedWildImport
from time import sleep
from sys import stdout

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
        if not daq_dev_info.supports_counters:
            raise Exception('Error: The DAQ device does not support counters')

        print('\nActive DAQ device: ', daq_dev_info.product_name, ' (',
              daq_dev_info.unique_id, ')\n', sep='')

        ctr_info = daq_dev_info.get_ctr_info()

        # Use the first counter channel on the board (some boards start channel
        # numbering at 1 instead of 0, the CtrInfo class is used here to find
        # the first one).
        counter_num = ctr_info.chan_info[0].channel_num

        ul.c_clear(board_num, counter_num)
        print('Please enter CTRL + C to terminate the process\n')
        try:
            while True:
                try:
                    # Read and display the data.
                    counter_value = ul.c_in_32(board_num, counter_num)
                    print('\r    Counter ', counter_num, ':',
                          str(counter_value).rjust(12), sep='', end='')
                    stdout.flush()
                    sleep(0.1)
                except (ValueError, NameError, SyntaxError):
                    break
        except KeyboardInterrupt:
            pass

    except Exception as e:
        print('\n', e)
    finally:
        if use_device_detection:
            ul.release_daq_device(board_num)


if __name__ == '__main__':
    run_example()
