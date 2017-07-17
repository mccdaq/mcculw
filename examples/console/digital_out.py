from __future__ import absolute_import, division, print_function

from builtins import *  # @UnusedWildImport

from mcculw import ul
from mcculw.enums import DigitalIODirection
from examples.console import util
from examples.props.digital import DigitalProps
from mcculw.ul import ULError


use_device_detection = True


def run_example():
    board_num = 0

    if use_device_detection:
        ul.ignore_instacal()
        if not util.config_first_detected_device(board_num):
            print("Could not find device.")
            return

    digital_props = DigitalProps(board_num)

    # Find the first port that supports input, defaulting to None
    # if one is not found.
    port = next(
        (port for port in digital_props.port_info
         if port.supports_output), None)
    if port == None:
        util.print_unsupported_example(board_num)
        return

    try:
        # If the port is configurable, configure it for output.
        if port.is_port_configurable:
            ul.d_config_port(board_num, port.type, DigitalIODirection.OUT)

        port_value = 0xFF

        print(
            "Setting " + port.type.name + " to " + str(port_value) + ".")

        # Output the value to the port
        ul.d_out(board_num, port.type, port_value)

        bit_num = 0
        bit_value = 0
        print(
            "Setting " + port.type.name + " bit " + str(bit_num) + " to "
            + str(bit_value) + ".")

        # Output the value to the bit
        ul.d_bit_out(board_num, port.type, bit_num, bit_value)

    except ULError as e:
        util.print_ul_error(e)
    finally:
        if use_device_detection:
            ul.release_daq_device(board_num)


if __name__ == '__main__':
    run_example()
