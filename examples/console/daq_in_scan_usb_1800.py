from __future__ import absolute_import, division, print_function

from builtins import *  # @UnusedWildImport

from mcculw import ul
from mcculw.enums import ScanOptions, ChannelType, ULRange, DigitalPortType
from examples.console import util
from mcculw.ul import ULError


use_device_detection = True
# Supported PIDs for the USB-1808 Series
# USB-1808 = 317
# USB-1808X = 318
supported_pids = [317, 318]


def run_example():
    board_num = 0
    rate = 100
    points_per_channel = 100

    if use_device_detection:
        ul.ignore_instacal()
        if not util.config_first_detected_device_of_type(
                board_num, supported_pids):
            print("Could not find a supported device.")
            return

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
    ctypes_array = util.memhandle_as_ctypes_array_scaled(memhandle)

    # Note: the ctypes array will no longer be valid after win_buf_free is
    # called.
    # A copy of the buffer can be created using win_buf_to_array or
    # win_buf_to_array_32 before the memory is freed. The copy can be used
    # at any time.

    # Check if the buffer was successfully allocated
    if not memhandle:
        print("Failed to allocate memory.")
        return

    try:
        # Start the scan
        ul.daq_in_scan(
            board_num, chan_list, chan_type_list, gain_list, num_chans,
            rate, 0, total_count, memhandle, scan_options)

        print("Scan completed successfully. Data:")

        # Create a format string that aligns the data in columns
        row_format = "{:>5}" + "{:>10}" * num_chans

        # Print the channel name headers
        labels = []
        labels.append("Index")
        for ch_index in range(num_chans):
            channel_label = {
                ChannelType.ANALOG: lambda:
                    "AI" + str(chan_list[ch_index]),
                ChannelType.ANALOG_DIFF: lambda:
                    "AI" + str(chan_list[ch_index]),
                ChannelType.ANALOG_SE: lambda:
                    "AI" + str(chan_list[ch_index]),
                ChannelType.DIGITAL: lambda:
                    chan_list[ch_index].name,
                ChannelType.CTR: lambda:
                    "CI" + str(chan_list[ch_index]),
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
    except ULError as e:
        util.print_ul_error(e)
    finally:
        # Free the buffer in a finally block to prevent errors from causing
        # a memory leak.
        ul.win_buf_free(memhandle)

        if use_device_detection:
            ul.release_daq_device(board_num)


if __name__ == '__main__':
    run_example()
