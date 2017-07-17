from __future__ import absolute_import, division, print_function

import math
import time

from builtins import *  # @UnusedWildImport

from mcculw import ul
from mcculw.enums import ScanOptions, FunctionType, Status
from examples.console import util
from examples.props.ao import AnalogOutputProps
from mcculw.ul import ULError

use_device_detection = True


def run_example():
    board_num = 0

    if use_device_detection:
        ul.ignore_instacal()
        if not util.config_first_detected_device(board_num):
            print("Could not find device.")
            return

    ao_props = AnalogOutputProps(board_num)
    if ao_props.num_chans < 1:
        util.print_unsupported_example(board_num)
        return

    low_chan = 0
    high_chan = min(3, ao_props.num_chans - 1)
    num_chans = high_chan - low_chan + 1

    rate = 100
    points_per_channel = 1000
    total_count = points_per_channel * num_chans

    ao_range = ao_props.available_ranges[0]

    # Allocate a buffer for the scan
    memhandle = ul.win_buf_alloc(total_count)
    # Convert the memhandle to a ctypes array
    # Note: the ctypes array will no longer be valid after win_buf_free
    # is called.
    # A copy of the buffer can be created using win_buf_to_array
    # before the memory is freed. The copy can be used at any time.
    ctypes_array = util.memhandle_as_ctypes_array(memhandle)

    # Check if the buffer was successfully allocated
    if not memhandle:
        print("Failed to allocate memory.")
        return

    frequencies = add_example_data(
        board_num, ctypes_array, ao_range, num_chans, rate,
        points_per_channel)

    for ch_num in range(low_chan, high_chan + 1):
        print(
            "Channel " + str(ch_num) + " Output Signal Frequency: "
            + str(frequencies[ch_num - low_chan]))

    try:
        # Start the scan
        ul.a_out_scan(
            board_num, low_chan, high_chan, total_count, rate, ao_range,
            memhandle, ScanOptions.BACKGROUND)

        # Wait for the scan to complete
        print("Waiting for output scan to complete...", end="")
        status = Status.RUNNING
        while status != Status.IDLE:
            print(".", end="")

            # Slow down the status check so as not to flood the CPU
            time.sleep(0.5)

            status, _, _ = ul.get_status(
                board_num, FunctionType.AOFUNCTION)
        print("")

        print("Scan completed successfully.")
    except ULError as e:
        util.print_ul_error(e)
    finally:
        # Free the buffer in a finally block to prevent errors from causing
        # a memory leak.
        ul.win_buf_free(memhandle)
        if use_device_detection:
            ul.release_daq_device(board_num)


def add_example_data(board_num, data_array, ao_range, num_chans, rate,
                     points_per_channel):
    # Calculate frequencies that will work well with the size of the array
    frequencies = []
    for channel_num in range(num_chans):
        frequencies.append(
            (channel_num + 1) / (points_per_channel / rate) * 10)

    # Calculate an amplitude and y-offset for the signal
    # to fill the analog output range
    amplitude = (ao_range.range_max - ao_range.range_min) / 2
    y_offset = (amplitude + ao_range.range_min) / 2

    # Fill the array with sine wave data at the calculated frequencies.
    # Note that since we are using the SCALEDATA option, the values
    # added to data_array are the actual voltage values that the device
    # will output
    data_index = 0
    for point_num in range(points_per_channel):
        for channel_num in range(num_chans):
            freq = frequencies[channel_num]
            value = amplitude * math.sin(
                2 * math.pi * freq * point_num / rate) + y_offset
            raw_value = ul.from_eng_units(
                board_num, ao_range, value)
            data_array[data_index] = raw_value
            data_index += 1

    return frequencies


if __name__ == '__main__':
    run_example()
