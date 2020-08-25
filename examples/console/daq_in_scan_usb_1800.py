"""
File:                       daq_in_scan_usb_1800.py

Library Call Demonstrated:  mcculw.ul.daq_in_scan()

Purpose:                    Synchronously scans Analog channels,
                            digital ports and counters in the foreground.

Demonstration:              Collects data on two analog channels, a
                            digital channel, and a counter channel.

Other Library Calls:        mcculw.ul.scaled_win_buf_alloc()
                            mcculw.ul.win_buf_free()
                            mcculw.ul.release_daq_device()

Special Requirements:       This examples filters on the USB-1808 Series.
"""
from __future__ import absolute_import, division, print_function
from builtins import *  # @UnusedWildImport

from ctypes import cast, POINTER, c_double

from mcculw import ul
from mcculw.enums import ScanOptions, ChannelType, ULRange, DigitalPortType
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
    dev_id_list = [317, 318]  # USB-1808 = 317, USB-1808X = 318
    board_num = 0
    # Supported PIDs for the USB-1808 Series
    rate = 100
    points_per_channel = 100
    memhandle = None

    try:
        if use_device_detection:
            config_first_detected_device(board_num, dev_id_list)

        daq_dev_info = DaqDeviceInfo(board_num)
        print('\nActive DAQ device: ', daq_dev_info.product_name, ' (',
              daq_dev_info.unique_id, ')\n', sep='')

        scan_options = ScanOptions.FOREGROUND | ScanOptions.SCALEDATA

        # Create the daq_in_scan channel configuration lists
        chan_list = []
        chan_type_list = []
        gain_list = []

        # Analog channels must be first in the list
        chan_list.append(1)
        chan_type_list.append(ChannelType.ANALOG_SE)
        gain_list.append(ULRange.BIP10VOLTS)

        chan_list.append(2)
        chan_type_list.append(ChannelType.ANALOG_DIFF)
        gain_list.append(ULRange.BIP10VOLTS)

        chan_list.append(DigitalPortType.AUXPORT)
        chan_type_list.append(ChannelType.DIGITAL)
        gain_list.append(ULRange.NOTUSED)

        chan_list.append(0)
        chan_type_list.append(ChannelType.CTR)
        gain_list.append(ULRange.NOTUSED)

        num_chans = len(chan_list)

        total_count = num_chans * points_per_channel

        # Allocate memory for the scan and cast it to a ctypes array pointer
        memhandle = ul.scaled_win_buf_alloc(total_count)
        ctypes_array = cast(memhandle, POINTER(c_double))

        # Note: the ctypes array will no longer be valid after win_buf_free is
        # called.
        # A copy of the buffer can be created using win_buf_to_array or
        # win_buf_to_array_32 before the memory is freed. The copy can be used
        # at any time.

        # Check if the buffer was successfully allocated
        if not memhandle:
            raise Exception('Error: Failed to allocate memory')

        # Start the scan
        ul.daq_in_scan(
            board_num, chan_list, chan_type_list, gain_list, num_chans,
            rate, 0, total_count, memhandle, scan_options)

        print('Scan completed successfully. Data:')

        # Create a format string that aligns the data in columns
        row_format = '{:>5}' + '{:>10}' * num_chans

        # Print the channel name headers
        labels = ['Index']
        for ch_index in range(num_chans):
            channel_label = {
                ChannelType.ANALOG: lambda:
                    'AI' + str(chan_list[ch_index]),
                ChannelType.ANALOG_DIFF: lambda:
                    'AI' + str(chan_list[ch_index]),
                ChannelType.ANALOG_SE: lambda:
                    'AI' + str(chan_list[ch_index]),
                ChannelType.DIGITAL: lambda:
                    chan_list[ch_index].name,
                ChannelType.CTR: lambda:
                    'CI' + str(chan_list[ch_index]),
            }[chan_type_list[ch_index]]()
            labels.append(channel_label)
        print(row_format.format(*labels))

        # Print the data
        data_index = 0
        for index in range(points_per_channel):
            display_data = [index]
            for ch_index in range(num_chans):
                data_label = {
                    ChannelType.ANALOG: lambda:
                        '{:.3f}'.format(ctypes_array[data_index]),
                    ChannelType.ANALOG_DIFF: lambda:
                        '{:.3f}'.format(ctypes_array[data_index]),
                    ChannelType.ANALOG_SE: lambda:
                        '{:.3f}'.format(ctypes_array[data_index]),
                    ChannelType.DIGITAL: lambda:
                        '{:d}'.format(int(ctypes_array[data_index])),
                    ChannelType.CTR: lambda:
                        '{:d}'.format(int(ctypes_array[data_index])),
                }[chan_type_list[ch_index]]()

                display_data.append(data_label)
                data_index += 1
            # Print this row
            print(row_format.format(*display_data))
    except Exception as e:
        print('\n', e)
    finally:
        if memhandle:
            # Free the buffer in a finally block to prevent a memory leak.
            ul.win_buf_free(memhandle)
        if use_device_detection:
            ul.release_daq_device(board_num)


if __name__ == '__main__':
    run_example()
