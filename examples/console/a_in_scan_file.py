"""
File:                       a_in_scan_file.py

Library Call Demonstrated:  mcculw.ul.a_in_scan() in Background mode with scan
                            option mcculw.enums.ScanOptions.BACKGROUND,
                            mcculw.enums.ScanOptions.CONTINUOUS and
                            mcculw.enums.ScanOptions.SCALEDATA

Purpose:                    Scans a range of A/D Input Channels and stores
                            the sample data in a file.

Demonstration:              Stores analog input values on up to four channels
                            in a file.

Other Library Calls:        mcculw.ul.scaled_win_buf_alloc()
                            mcculw.ul.scaled_win_buf_to_array()
                            mcculw.ul.win_buf_free()
                            mcculw.ul.get_status()
                            mcculw.ul.stop_background()
                            mcculw.ul.release_daq_device()

Special Requirements:       Device must have an A/D converter.
                            Analog signals on up to four input channels.
"""
from __future__ import absolute_import, division, print_function
from builtins import *  # @UnusedWildImport

from ctypes import c_double, cast, POINTER, addressof, sizeof
from time import sleep

from mcculw import ul
from mcculw.enums import ScanOptions, FunctionType, Status
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
    rate = 100
    file_name = 'scan_data.csv'
    memhandle = None

    # The size of the UL buffer to create, in seconds
    buffer_size_seconds = 2
    # The number of buffers to write. After this number of UL buffers are
    # written to file, the example will be stopped.
    num_buffers_to_write = 5

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

        low_chan = 0
        high_chan = min(3, ai_info.num_chans - 1)
        num_chans = high_chan - low_chan + 1

        # Create a circular buffer that can hold buffer_size_seconds worth of
        # data, or at least 10 points (this may need to be adjusted to prevent
        # a buffer overrun)
        points_per_channel = max(rate * buffer_size_seconds, 10)

        # Some hardware requires that the total_count is an integer multiple
        # of the packet size. For this case, calculate a points_per_channel
        # that is equal to or just above the points_per_channel selected
        # which matches that requirement.
        if ai_info.packet_size != 1:
            packet_size = ai_info.packet_size
            remainder = points_per_channel % packet_size
            if remainder != 0:
                points_per_channel += packet_size - remainder

        ul_buffer_count = points_per_channel * num_chans

        # Write the UL buffer to the file num_buffers_to_write times.
        points_to_write = ul_buffer_count * num_buffers_to_write

        # When handling the buffer, we will read 1/10 of the buffer at a time
        write_chunk_size = int(ul_buffer_count / 10)

        ai_range = ai_info.supported_ranges[0]

        scan_options = (ScanOptions.BACKGROUND | ScanOptions.CONTINUOUS |
                        ScanOptions.SCALEDATA)

        memhandle = ul.scaled_win_buf_alloc(ul_buffer_count)

        # Allocate an array of doubles temporary storage of the data
        write_chunk_array = (c_double * write_chunk_size)()

        # Check if the buffer was successfully allocated
        if not memhandle:
            raise Exception('Failed to allocate memory')

        # Start the scan
        ul.a_in_scan(
            board_num, low_chan, high_chan, ul_buffer_count,
            rate, ai_range, memhandle, scan_options)

        status = Status.IDLE
        # Wait for the scan to start fully
        while status == Status.IDLE:
            status, _, _ = ul.get_status(board_num, FunctionType.AIFUNCTION)

        # Create a file for storing the data
        with open(file_name, 'w') as f:
            print('Writing data to ' + file_name, end='')

            # Write a header to the file
            for chan_num in range(low_chan, high_chan + 1):
                f.write('Channel ' + str(chan_num) + ',')
            f.write(u'\n')

            # Start the write loop
            prev_count = 0
            prev_index = 0
            write_ch_num = low_chan
            while status != Status.IDLE:
                # Get the latest counts
                status, curr_count, _ = ul.get_status(board_num,
                                                      FunctionType.AIFUNCTION)

                new_data_count = curr_count - prev_count

                # Check for a buffer overrun before copying the data, so
                # that no attempts are made to copy more than a full buffer
                # of data
                if new_data_count > ul_buffer_count:
                    # Print an error and stop writing
                    ul.stop_background(board_num, FunctionType.AIFUNCTION)
                    print('A buffer overrun occurred')
                    break

                # Check if a chunk is available
                if new_data_count > write_chunk_size:
                    wrote_chunk = True
                    # Copy the current data to a new array

                    # Check if the data wraps around the end of the UL
                    # buffer. Multiple copy operations will be required.
                    if prev_index + write_chunk_size > ul_buffer_count - 1:
                        first_chunk_size = ul_buffer_count - prev_index
                        second_chunk_size = (
                            write_chunk_size - first_chunk_size)

                        # Copy the first chunk of data to the
                        # write_chunk_array
                        ul.scaled_win_buf_to_array(
                            memhandle, write_chunk_array, prev_index,
                            first_chunk_size)

                        # Create a pointer to the location in
                        # write_chunk_array where we want to copy the
                        # remaining data
                        second_chunk_pointer = cast(addressof(write_chunk_array)
                                                    + first_chunk_size
                                                    * sizeof(c_double),
                                                    POINTER(c_double))

                        # Copy the second chunk of data to the
                        # write_chunk_array
                        ul.scaled_win_buf_to_array(
                            memhandle, second_chunk_pointer,
                            0, second_chunk_size)
                    else:
                        # Copy the data to the write_chunk_array
                        ul.scaled_win_buf_to_array(
                            memhandle, write_chunk_array, prev_index,
                            write_chunk_size)

                    # Check for a buffer overrun just after copying the data
                    # from the UL buffer. This will ensure that the data was
                    # not overwritten in the UL buffer before the copy was
                    # completed. This should be done before writing to the
                    # file, so that corrupt data does not end up in it.
                    status, curr_count, _ = ul.get_status(
                        board_num, FunctionType.AIFUNCTION)
                    if curr_count - prev_count > ul_buffer_count:
                        # Print an error and stop writing
                        ul.stop_background(board_num, FunctionType.AIFUNCTION)
                        print('A buffer overrun occurred')
                        break

                    for i in range(write_chunk_size):
                        f.write(str(write_chunk_array[i]) + ',')
                        write_ch_num += 1
                        if write_ch_num == high_chan + 1:
                            write_ch_num = low_chan
                            f.write(u'\n')
                else:
                    wrote_chunk = False

                if wrote_chunk:
                    # Increment prev_count by the chunk size
                    prev_count += write_chunk_size
                    # Increment prev_index by the chunk size
                    prev_index += write_chunk_size
                    # Wrap prev_index to the size of the UL buffer
                    prev_index %= ul_buffer_count

                    if prev_count >= points_to_write:
                        break
                    print('.', end='')
                else:
                    # Wait a short amount of time for more data to be
                    # acquired.
                    sleep(0.1)

        ul.stop_background(board_num, FunctionType.AIFUNCTION)
    except Exception as e:
        print('\n', e)
    finally:
        print('Done')
        if memhandle:
            # Free the buffer in a finally block to prevent  a memory leak.
            ul.win_buf_free(memhandle)
        if use_device_detection:
            ul.release_daq_device(board_num)


if __name__ == '__main__':
    run_example()
