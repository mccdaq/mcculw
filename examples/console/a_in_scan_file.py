from __future__ import absolute_import, division, print_function

from _ctypes import POINTER, addressof, sizeof
from ctypes import c_double, cast
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
    file_name = 'scan_data.csv'

    # The size of the UL buffer to create, in seconds
    buffer_size_seconds = 2
    # The number of buffers to write. After this number of UL buffers are
    # written to file, the example will be stopped.
    num_buffers_to_write = 5

    if use_device_detection:
        ul.ignore_instacal()
        if not util.config_first_detected_device(board_num):
            print("Could not find device.")
            return

    ai_props = AnalogInputProps(board_num)
    if (ai_props.num_ai_chans < 1 or
            not ScanOptions.SCALEDATA in ai_props.supported_scan_options):
        util.print_unsupported_example(board_num)
        return

    low_chan = 0
    high_chan = min(3, ai_props.num_ai_chans - 1)
    num_chans = high_chan - low_chan + 1

    # Create a circular buffer that can hold buffer_size_seconds worth of
    # data, or at least 10 points (this may need to be adjusted to prevent
    # a buffer overrun)
    points_per_channel = max(rate * buffer_size_seconds, 10)

    # Some hardware requires that the total_count is an integer multiple
    # of the packet size. For this case, calculate a points_per_channel
    # that is equal to or just above the points_per_channel selected
    # which matches that requirement.
    if ai_props.continuous_requires_packet_size_multiple:
        packet_size = ai_props.packet_size
        remainder = points_per_channel % packet_size
        if remainder != 0:
            points_per_channel += packet_size - remainder

    ul_buffer_count = points_per_channel * num_chans

    # Write the UL buffer to the file num_buffers_to_write times.
    points_to_write = ul_buffer_count * num_buffers_to_write

    # When handling the buffer, we will read 1/10 of the buffer at a time
    write_chunk_size = int(ul_buffer_count / 10)

    ai_range = ai_props.available_ranges[0]

    scan_options = (ScanOptions.BACKGROUND | ScanOptions.CONTINUOUS |
                    ScanOptions.SCALEDATA)

    memhandle = ul.scaled_win_buf_alloc(ul_buffer_count)

    # Allocate an array of doubles temporary storage of the data
    write_chunk_array = (c_double * write_chunk_size)()

    # Check if the buffer was successfully allocated
    if not memhandle:
        print("Failed to allocate memory.")
        return

    try:
        # Start the scan
        ul.a_in_scan(
            board_num, low_chan, high_chan, ul_buffer_count,
            rate, ai_range, memhandle, scan_options)

        status = Status.IDLE
        # Wait for the scan to start fully
        while(status == Status.IDLE):
            status, _, _ = ul.get_status(
                board_num, FunctionType.AIFUNCTION)

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
                status, curr_count, _ = ul.get_status(
                    board_num, FunctionType.AIFUNCTION)

                new_data_count = curr_count - prev_count

                # Check for a buffer overrun before copying the data, so
                # that no attempts are made to copy more than a full buffer
                # of data
                if new_data_count > ul_buffer_count:
                    # Print an error and stop writing
                    ul.stop_background(board_num, FunctionType.AIFUNCTION)
                    print("A buffer overrun occurred")
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
                        second_chunk_pointer = cast(
                            addressof(write_chunk_array) + first_chunk_size
                            * sizeof(c_double), POINTER(c_double))

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
                        print("A buffer overrun occurred")
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
                    time.sleep(0.1)

        ul.stop_background(board_num, FunctionType.AIFUNCTION)
    except ULError as e:
        util.print_ul_error(e)
    finally:
        print('Done')

        # Free the buffer in a finally block to prevent errors from causing
        # a memory leak.
        ul.win_buf_free(memhandle)

        if use_device_detection:
            ul.release_daq_device(board_num)


if __name__ == '__main__':
    run_example()
