from __future__ import absolute_import, division, print_function
from builtins import *  # @UnusedWildImport

from mcculw import ul
from mcculw.ul import ULError
from mcculw.enums import (InfoType, BoardInfo, DigitalInfo, DigitalPortType,
                          DigitalIODirection, FunctionType)


class DioInfo:
    """Provides digital input/output information for the device with the
    specified board number.

    NOTE: This class is primarily used to provide hardware information for the
    library examples and may change some hardware configuration values. It is
    recommended that values provided by this class be hard-coded in production
    code.

    Parameters
    ----------
    board_num : int
        The board number associated with the device when created with
        :func:`.create_daq_device` or configured with Instacal.
    """
    def __init__(self, board_num):
        self._board_num = board_num

    @property
    def num_ports(self):
        try:
            port_count = ul.get_config(InfoType.BOARDINFO, self._board_num, 0,
                                       BoardInfo.DINUMDEVS)
        except ULError:
            port_count = 0

        return port_count

    @property
    def is_supported(self):
        return self.num_ports > 0

    @property
    def port_info(self):
        port_info_list = []
        for port_index in range(self.num_ports):
            port_info_list.append(PortInfo(self._board_num, port_index))
        return port_info_list


class PortInfo:
    def __init__(self, board_num, port_index):
        self._board_num = board_num
        self._port_index = port_index

    @property
    def num_bits(self):
        return ul.get_config(InfoType.DIGITALINFO, self._board_num,
                             self._port_index, DigitalInfo.NUMBITS)

    @property
    def in_mask(self):
        return ul.get_config(InfoType.DIGITALINFO, self._board_num,
                             self._port_index, DigitalInfo.INMASK)

    @property
    def out_mask(self):
        return ul.get_config(InfoType.DIGITALINFO, self._board_num,
                             self._port_index, DigitalInfo.OUTMASK)

    @property
    def type(self):
        dev_type = ul.get_config(InfoType.DIGITALINFO, self._board_num,
                                 self._port_index, DigitalInfo.DEVTYPE)
        return DigitalPortType(dev_type)

    @property
    def first_bit(self):
        # A few devices (USB-SSR08 for example) start at FIRSTPORTCL and
        # number the bits as if FIRSTPORTA and FIRSTPORTB exist for
        # compatibility with older digital peripherals
        first_bit_value = 0
        if self._port_index == 0 and self.type == DigitalPortType.FIRSTPORTCL:
            first_bit_value = 16
        return first_bit_value

    @property
    def supports_input(self):
        return self.in_mask > 0 or self.is_port_configurable

    @property
    def supports_input_scan(self):
        input_scan_supported = True
        try:
            ul.get_status(self._board_num, FunctionType.DIFUNCTION)
        except ULError:
            input_scan_supported = False
        return input_scan_supported

    @property
    def supports_output_scan(self):
        output_scan_supported = True
        try:
            ul.get_status(self._board_num, FunctionType.DOFUNCTION)
        except ULError:
            output_scan_supported = False
        return output_scan_supported

    @property
    def supports_output(self):
        return self.out_mask > 0 or self.is_port_configurable

    @property
    def is_bit_configurable(self):
        bit_configurable = False
        if self.in_mask & self.out_mask == 0:
            # AUXPORT type ports might be configurable, check if d_config_bit
            # completes without error
            if self.type == DigitalPortType.AUXPORT:
                try:
                    ul.d_config_bit(self._board_num, self.type, self.first_bit,
                                    DigitalIODirection.OUT)
                    ul.d_config_bit(self._board_num, self.type, self.first_bit,
                                    DigitalIODirection.IN)
                    bit_configurable = True
                except ULError:
                    bit_configurable = False
        return bit_configurable

    @property
    def is_port_configurable(self):
        port_configurable = False
        if self.in_mask & self.out_mask == 0:
            # Check if d_config_port completes without error
            try:
                ul.d_config_port(self._board_num, self.type,
                                 DigitalIODirection.OUT)
                ul.d_config_port(self._board_num, self.type,
                                 DigitalIODirection.IN)
                port_configurable = True
            except ULError:
                port_configurable = False
        return port_configurable
