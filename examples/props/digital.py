from __future__ import absolute_import, division, print_function

from builtins import *  # @UnusedWildImport

from mcculw import ul
from mcculw.enums import InfoType, BoardInfo, DigitalInfo, DigitalPortType, \
    DigitalIODirection, FunctionType
from examples.props.propsbase import Props
from mcculw.ul import ULError


class DigitalProps(Props):
    """Provides digital IO information on the hardware configured at the
    board number given.

    This class is used to provide hardware information for the library
    examples, and may change hardware values. It is recommended that the
    values provided by this class be hard-coded in production code. 
    """

    def __init__(self, board_num):
        self._board_num = board_num
        self.num_ports = self._get_num_digital_chans()

        self.port_info = []
        for port_index in range(self.num_ports):
            self.port_info.append(PortInfo(board_num, port_index))

    def _get_num_digital_chans(self):
        try:
            return ul.get_config(
                InfoType.BOARDINFO, self._board_num, 0,
                BoardInfo.DINUMDEVS)
        except ULError:
            return 0


class PortInfo(object):
    def __init__(self, board_num, port_index):
        self._board_num = board_num
        self._port_index = port_index

        self.type = self._get_digital_dev_type()
        self.first_bit = self._get_first_bit(port_index, self.type)
        self.num_bits = self._get_num_bits()
        self.in_mask = self._get_in_mask()
        self.out_mask = self._get_out_mask()
        self.is_bit_configurable = self._get_is_bit_configurable(
            self.type, self.first_bit, self.in_mask, self.out_mask)
        self.is_port_configurable = self._get_is_port_configurable(
            self.type, self.in_mask, self.out_mask)
        self.supports_input = self._get_supports_input(
            self.in_mask, self.is_port_configurable)
        self.supports_input_scan = self._get_supports_input_scan()
        self.supports_output = self._get_supports_output(
            self.out_mask, self.is_port_configurable)
        self.supports_output_scan = self._get_supports_output_scan()

    def _get_num_bits(self):
        return ul.get_config(
            InfoType.DIGITALINFO, self._board_num, self._port_index,
            DigitalInfo.NUMBITS)

    def _get_supports_input(self, in_mask, is_port_programmable):
        return in_mask > 0 or is_port_programmable

    def _get_supports_input_scan(self):
        try:
            ul.get_status(self._board_num, FunctionType.DIFUNCTION)
        except ULError:
            return False
        return True

    def _get_supports_output_scan(self):
        try:
            ul.get_status(self._board_num, FunctionType.DOFUNCTION)
        except ULError:
            return False
        return True

    def _get_supports_output(self, out_mask, is_port_programmable):
        return out_mask > 0 or is_port_programmable

    def _get_first_bit(self, port_index, port_type):
        # A few devices (USB-SSR08 for example) start at FIRSTPORTCL and
        # number the bits as if FIRSTPORTA and FIRSTPORTB exist for
        # compatibility with older digital peripherals
        if port_index == 0 and port_type == DigitalPortType.FIRSTPORTCL:
            return 16
        return 0

    def _get_is_bit_configurable(self, port_type, first_bit, in_mask,
                                 out_mask):
        if in_mask & out_mask > 0:
            return False
        # AUXPORT type ports might be configurable, check if d_config_bit
        # completes without error
        if port_type == DigitalPortType.AUXPORT:
            try:
                ul.d_config_bit(
                    self._board_num, port_type, first_bit,
                    DigitalIODirection.OUT)
                ul.d_config_bit(
                    self._board_num, port_type, first_bit,
                    DigitalIODirection.IN)
            except ULError:
                return False
            return True
        return False

    def _get_is_port_configurable(self, port_type, in_mask, out_mask):
        if in_mask & out_mask > 0:
            return False
        # Check if d_config_port completes without error
        try:
            ul.d_config_port(self._board_num, port_type,
                             DigitalIODirection.OUT)
            ul.d_config_port(self._board_num, port_type,
                             DigitalIODirection.IN)
        except ULError:
            return False
        return True

    def _get_digital_dev_type(self):
        return DigitalPortType(ul.get_config(
            InfoType.DIGITALINFO, self._board_num, self._port_index,
            DigitalInfo.DEVTYPE))

    def _get_in_mask(self):
        return ul.get_config(
            InfoType.DIGITALINFO, self._board_num, self._port_index,
            DigitalInfo.INMASK)

    def _get_out_mask(self):
        return ul.get_config(
            InfoType.DIGITALINFO, self._board_num, self._port_index,
            DigitalInfo.OUTMASK)
