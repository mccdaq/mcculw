from __future__ import absolute_import, division, print_function

import time

from builtins import *  # @UnusedWildImport

from mcculw import ul
from mcculw.enums import ScanOptions, FunctionType, Status
from examples.console import util
from examples.props.ai import AnalogInputProps
from mcculw.ul import ULError


use_device_detection = True


def run_example():
    board_num = 0
    rate = 100
    points_per_channel = 1000

    if use_device_detection:
        ul.ignore_instacal()
        if not util.config_first_detected_device(board_num):
            print("Could not find device.")
            return

    ai_props = AnalogInputProps(board_num)
    if ai_props.num_ai_chans < 1:
        util.print_unsupported_example(board_num)
        return

    low_chan = 0
    high_chan = min(3, ai_props.num_ai_chans - 1)
    num_chans = high_chan - low_chan + 1

    total_count = points_per_channel * num_chans

    ai_range = ai_props.available_ranges[0]

    scan_options = ScanOptions.BACKGROUND

    if ScanOptions.SCALEDATA in ai_props.supported_scan_options:
        # If the hardware supports the SCALEDATA option, it is easiest to
        # use it.
        scan_options |= ScanOptions.SCALEDATA

        memhandle = ul.scaled_win_buf_alloc(total_count)
        # Convert the memhandle to a ctypes array.
        # Use the memhandle_as_ctypes_array_scaled method for scaled
        # buffers.
        ctypes_array = util.memhandle_as_ctypes_array_scaled(memhandle)
    elif ai_props.resolution <= 16:
        # Use the win_buf_alloc method for devices with a resolution <= 16
        memhandle = ul.win_buf_alloc(total_count)
        # Convert the memhandle to a ctypes array.
        # Use the memhandle_as_ctypes_array method for devices with a
        # resolution <= 16.
        ctypes_array = util.memhandle_as_ctypes_array(memhandle)
    else:
        # Use the win_buf_alloc_32 method for devices with a resolution > 16
        memhandle = ul.win_buf_alloc_32(total_count)
        # Convert the memhandle to a ctypes array.
        # Use the memhandle_as_ctypes_array_32 method for devices with a
        # resolution > 16
        ctypes_array = util.memhandle_as_ctypes_array_32(memhandle)

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
        ul.a_in_scan(
            board_num, low_chan, high_chan, total_count,
            rate, ai_range, memhandle, scan_options)

        # Create a format string that aligns the data in columns
        row_format = "{:>12}" * num_chans

        # Print the channel name headers
        labels = []
        for ch_num in range(low_chan, high_chan + 1):
            labels.append("CH" + str(ch_num))
        print(row_format.format(*labels))

        # Start updating the displayed values
        status, curr_count, curr_index = ul.get_status(
            board_num, FunctionType.AIFUNCTION)
        while status != Status.IDLE:
            # Make sure a data point is available for display.
            if curr_count > 0:
                # curr_index points to the start of the last completed
                # channel scan that was transferred between the board and
                # the data buffer. Display the latest value for each
                # channel.
                display_data = []
                for data_index in range(curr_index, curr_index + num_chans):
                    if ScanOptions.SCALEDATA in scan_options:
                        # If the SCALEDATA ScanOption was used, the values
                        # in the array are already in engineering units.
                        eng_value = ctypes_array[data_index]
                    else:
                        # If the SCALEDATA ScanOption was NOT used, the
                        # values in the array must be converted to
                        # engineering units using ul.to_eng_units().
                        eng_value = ul.to_eng_units(
                            board_num, ai_range, ctypes_array[data_index])
                    display_data.append('{:.3f}'.format(eng_value))
                print(row_format.format(*display_data))

            # Wait a while before adding more values to the display.
            time.sleep(0.5)

            status, curr_count, curr_index = ul.get_status(
                board_num, FunctionType.AIFUNCTION)

        # Stop the background operation (this is required even if the
        # scan completes successfully)
        ul.stop_background(board_num, FunctionType.AIFUNCTION)

        print("Scan completed successfully.")
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
