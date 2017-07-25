from __future__ import absolute_import, division, print_function

from builtins import *  # @UnusedWildImport
from mcculw import ul
from mcculw.enums import BoardInfo, InfoType, ULRange, FunctionType,\
    TrigType, ScanOptions, ErrorCode
from mcculw.ul import ULError

from examples.props.propsbase import Props


class AnalogInputProps(Props):
    """Provides analog input information on the hardware configured at the
    board number given.

    This class is used to provide hardware information for the library
    examples, and may change hardware values. It is recommended that the
    values provided by this class be hard-coded in production code. 
    """

    def __init__(self, board_num):
        self._board_num = board_num

        # Get the board type from UL
        board_type = ul.get_config(
            InfoType.BOARDINFO, self._board_num, 0, BoardInfo.BOARDTYPE)

        self.resolution = self._get_resolution()
        self.num_ai_chans = self._get_num_ai_chans()
        self.num_ti_chans = self._get_num_ti_chans()
        self.available_ranges = self._get_available_ranges(self.resolution)
        self.supports_v_in = self._get_supports_v_in(self.available_ranges)
        self.supports_scan = self._get_supports_scan()
        if self.supports_scan:
            self.supported_scan_options = self._get_supported_scan_options()
        else:
            self.supported_scan_options = None

        self.packet_size = \
            self._get_packet_size(board_type)
        self.continuous_requires_packet_size_multiple = \
            self.packet_size != 1

        self.supports_gain_queue = self._get_supports_gain_queue()
        self.supports_analog_trig = self._get_supports_analog_trig()
        self.analog_trig_resolution = 0
        self.analog_trig_range = -1
        if self.supports_analog_trig:
            self.analog_trig_resolution, self.analog_trig_range = \
                self._get_analog_trig_info(board_type)

    def _get_packet_size(self, board_type):
        """
        The hardware in the following table will return a packet size.
        This hardware must use an integer multiple of the packet size as
        the total_count for a_in_scan when using the
        :const:`~mcculw.enums.CONTINUOUS` option in
        :const:`~mcculw.enums.BLOCKIO` mode.

        For all other hardware, this method will return 1.

        ==========  ==========  ===========
        Hardware    Product Id  Packet Size
        ==========  ==========  ===========
        USB-1208LS  122         64
        USB-1208FS  130         31
        USB-1408FS  161         31
        USB-7204    240         31
        ==========  ==========  ===========
        """
        if board_type == 122:
            return 64
        elif board_type in [130, 161, 240]:
            return 31

        return 1

    def _get_analog_trig_info(self, board_type):
        try:
            trig_source = ul.get_config(
                InfoType.BOARDINFO, self._board_num, 0, BoardInfo.ADTRIGSRC)
        except ULError:
            trig_source = 0

        # PCI-DAS6030, 6031, 6032, 6033, 6052
        # USB-1602HS, 1602HS-2AO, 1604HS, 1604HS-2AO
        # PCI-2511, 2513, 2515, 2517, USB-2523, 2527, 2533, 2537
        # USB-1616HS, 1616HS-2, 1616HS-4, 1616HS-BNC
        type_a = [95, 96, 97, 98, 102, 165, 166, 167, 168, 177, 178, 179,
                  180, 203, 204, 205, 213, 214, 215, 216, 217]
        if board_type in type_a:
            if trig_source > 0:
                return 12, ULRange.UNKNOWN
            return 12, ULRange.BIP10VOLTS

        # PCI-DAS6040, 6070, 6071
        type_b = [101, 103, 104]
        if board_type in type_b:
            if trig_source > 0:
                return 8, ULRange.UNKNOWN
            return 8, ULRange.BIP10VOLTS

        return 0, ULRange.UNKNOWN

    def _get_supports_analog_trig(self):
        try:
            ul.set_trigger(
                self._board_num, TrigType.TRIG_ABOVE, 0, 0)
            return True
        except ULError:
            return False

    def _get_resolution(self):
        return ul.get_config(
            InfoType.BOARDINFO, self._board_num, 0, BoardInfo.ADRES)

    def _get_num_ai_chans(self):
        return ul.get_config(
            InfoType.BOARDINFO, self._board_num, 0, BoardInfo.NUMADCHANS)

    def _get_num_ti_chans(self):
        return ul.get_config(
            InfoType.BOARDINFO, self._board_num, 0, BoardInfo.NUMTEMPCHANS)

    def _get_supports_v_in(self, available_ranges):
        if len(available_ranges) == 0:
            return False
        try:
            ul.v_in(self._board_num, 0, available_ranges[0])
        except ULError:
            return False
        return True

    def _get_supports_scan(self):
        try:
            ul.get_status(self._board_num, FunctionType.AIFUNCTION)
        except ULError:
            return False
        return True

    def _get_supported_scan_options(self):
        return ScanOptions(ul.get_config(
            InfoType.BOARDINFO, self._board_num, 0,
            BoardInfo.ADSCANOPTIONS))

    def _get_supports_gain_queue(self):
        try:
            ul.a_load_queue(self._board_num, [], [], 0)
        except ULError:
            return False
        return True

    def _get_available_ranges(self, ad_resolution):
        result = []

        # Check if the board has a switch-selectable, or only one, range
        hard_range = ul.get_config(
            InfoType.BOARDINFO, self._board_num, 0, BoardInfo.RANGE)

        if hard_range >= 0:
            result.append(ULRange(hard_range))
        else:
            for ai_range in ULRange:
                try:
                    if ad_resolution <= 16:
                        ul.a_in(self._board_num, 0, ai_range)
                    else:
                        ul.a_in_32(self._board_num, 0, ai_range)
                    result.append(ai_range)
                except ULError as e:
                    if (e.errorcode == ErrorCode.NETDEVINUSE or
                            e.errorcode == ErrorCode.NETDEVINUSEBYANOTHERPROC):
                        raise

        return result
