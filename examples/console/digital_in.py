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
         if port.supports_input), None)
    if port == None:
        util.print_unsupported_example(board_num)
        return

    try:
        # If the port is configurable, configure it for input.
        if port.is_port_configurable:
            ul.d_config_port(board_num, port.type, DigitalIODirection.IN)

        # Get a value from the digital port
        port_value = ul.d_in(board_num, port.type)

        # Get a value from the first digital bit
        bit_num = 0
        bit_value = ul.d_bit_in(board_num, port.type, bit_num)

        # Display the port value
        print(port.type.name + " Value: " + str(port_value))
        # Display the bit value
        print("Bit " + str(bit_num) + " Value: " + str(bit_value))
    except ULError as e:
        util.print_ul_error(e)
    finally:
        if use_device_detection:
            ul.release_daq_device(board_num)


if __name__ == '__main__':
    run_example()
