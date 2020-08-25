from __future__ import absolute_import, division, print_function
from builtins import *  # @UnusedWildImport

from mcculw import ul
from mcculw.ul import ULError
from mcculw.enums import (InfoType, BoardInfo, ULRange, FunctionType,
                          ErrorCode, TrigType, ScanOptions)


class AiInfo:
    """Provides analog input information for the device with the specified
    board number.

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
        # Get the board type from UL
        self._board_type = ul.get_config(InfoType.BOARDINFO, self._board_num,
                                         0, BoardInfo.BOARDTYPE)

    @property
    def board_num(self):
        return self._board_num

    @property
    def num_chans(self):
        return ul.get_config(InfoType.BOARDINFO, self._board_num, 0,
                             BoardInfo.NUMADCHANS)

    @property
    def is_supported(self):
        return self.num_chans > 0

    @property
    def num_temp_chans(self):
        return ul.get_config(InfoType.BOARDINFO, self._board_num, 0,
                             BoardInfo.NUMTEMPCHANS)

    @property
    def temp_supported(self):
        return self.num_temp_chans > 0

    @property
    def resolution(self):
        return ul.get_config(InfoType.BOARDINFO, self._board_num, 0,
                             BoardInfo.ADRES)

    @property
    def supports_scan(self):
        scan_supported = True
        try:
            ul.get_status(self._board_num, FunctionType.AIFUNCTION)
        except ULError:
            scan_supported = False
        return scan_supported

    @property
    def supported_ranges(self):
        result = []

        # Check if the board has a switch-selectable, or only one, range
        hard_range = ul.get_config(InfoType.BOARDINFO, self._board_num, 0,
                                   BoardInfo.RANGE)

        if hard_range >= 0:
            result.append(ULRange(hard_range))
        else:
            for ai_range in ULRange:
                try:
                    if self.resolution <= 16:
                        ul.a_in(self._board_num, 0, ai_range)
                    else:
                        ul.a_in_32(self._board_num, 0, ai_range)
                    result.append(ai_range)
                except ULError as e:
                    if (e.errorcode == ErrorCode.NETDEVINUSE or
                            e.errorcode == ErrorCode.NETDEVINUSEBYANOTHERPROC):
                        raise

        return result

    @property
    def packet_size(self):
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
        packet_size = 1
        if self._board_type == 122:
            packet_size = 64
        elif self._board_type in [130, 161, 240]:
            packet_size = 31

        return packet_size

    @property
    def supports_v_in(self):
        v_in_supported = True
        ai_ranges = self.supported_ranges
        if not ai_ranges:
            v_in_supported = False
        else:
            try:
                ul.v_in(self._board_num, 0, ai_ranges[0])
            except ULError:
                v_in_supported = False
        return v_in_supported

    @property
    def analog_trig_resolution(self):
        # PCI-DAS6030, 6031, 6032, 6033, 6052
        # USB-1602HS, 1602HS-2AO, 1604HS, 1604HS-2AO
        # PCI-2511, 2513, 2515, 2517, USB-2523, 2527, 2533, 2537
        # USB-1616HS, 1616HS-2, 1616HS-4, 1616HS-BNC
        trig_res_12_bit_types = [95, 96, 97, 98, 102, 165, 166, 167, 168, 177,
                                 178, 179, 180, 203, 204, 205, 213, 214, 215,
                                 216, 217]

        # PCI-DAS6040, 6070, 6071
        trig_res_8_bit_types = [101, 103, 104]

        trigger_resolution = 0
        if self._board_type in trig_res_12_bit_types:
            trigger_resolution = 12
        elif self._board_type in trig_res_8_bit_types:
            trigger_resolution = 8

        return trigger_resolution

    @property
    def analog_trig_range(self):
        # Get the analog trigger source
        try:
            trig_source = ul.get_config(InfoType.BOARDINFO, self._board_num, 0,
                                        BoardInfo.ADTRIGSRC)
        except ULError:
            trig_source = 0

        if self.analog_trig_resolution > 0 and trig_source <= 0:
            trigger_range = ULRange.BIP10VOLTS
        else:
            trigger_range = ULRange.UNKNOWN

        return trigger_range

    @property
    def supports_analog_trig(self):
        analog_trig_supported = True
        try:
            ul.set_trigger(self._board_num, TrigType.TRIG_ABOVE, 0, 0)
        except ULError:
            analog_trig_supported = False
        return analog_trig_supported

    @property
    def supported_scan_options(self):
        if self.supports_scan:
            scan_options_supported = ScanOptions(ul.get_config(
                InfoType.BOARDINFO, self._board_num, 0,
                BoardInfo.ADSCANOPTIONS))
        else:
            scan_options_supported = None
        return scan_options_supported

    @property
    def supports_gain_queue(self):
        gain_queue_supported = True
        try:
            ul.a_load_queue(self._board_num, [], [], 0)
        except ULError:
            gain_queue_supported = False
        return gain_queue_supported
