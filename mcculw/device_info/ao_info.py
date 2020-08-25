from __future__ import absolute_import, division, print_function
from builtins import *  # @UnusedWildImport

from mcculw import ul
from mcculw.ul import ULError
from mcculw.enums import BoardInfo, InfoType, ULRange, ErrorCode, ScanOptions


class AoInfo:
    """Provides analog output information for the device with the specified
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

    @property
    def board_num(self):
        return self._board_num

    @property
    def num_chans(self):
        return ul.get_config(InfoType.BOARDINFO, self._board_num, 0,
                             BoardInfo.NUMDACHANS)

    @property
    def is_supported(self):
        return self.num_chans > 0

    @property
    def resolution(self):
        return ul.get_config(InfoType.BOARDINFO, self._board_num, 0,
                             BoardInfo.DACRES)

    @property
    def supports_scan(self):
        return ScanOptions.CONTINUOUS in self.supported_scan_options

    @property
    def supported_scan_options(self):
        try:
            scan_options_supported = ScanOptions(ul.get_config(
                InfoType.BOARDINFO, self._board_num, 0,
                BoardInfo.DACSCANOPTIONS))
        except ULError:
            scan_options_supported = ScanOptions(0)

        return scan_options_supported

    @property
    def supported_ranges(self):
        result = []
        # Check if the range is ignored by passing a bogus range in
        try:
            ul.a_out(self._board_num, 0, -5, 0)
            range_ignored = True
        except ULError as e:
            if (e.errorcode == ErrorCode.NETDEVINUSE or
                    e.errorcode == ErrorCode.NETDEVINUSEBYANOTHERPROC):
                raise
            range_ignored = False

        if range_ignored:
            # Try and get the range configured in InstaCal
            try:
                curr_range = ULRange(ul.get_config(InfoType.BOARDINFO,
                                                   self._board_num, 0,
                                                   BoardInfo.DACRANGE))
                result.append(curr_range)
            except ULError as e:
                if (e.errorcode == ErrorCode.NETDEVINUSE or
                        e.errorcode == ErrorCode.NETDEVINUSEBYANOTHERPROC):
                    raise
        else:
            for dac_range in ULRange:
                try:
                    ul.a_out(self._board_num, 0, dac_range, 0)
                    result.append(dac_range)
                except ULError as e:
                    if (e.errorcode == ErrorCode.NETDEVINUSE or
                            e.errorcode == ErrorCode.NETDEVINUSEBYANOTHERPROC):
                        raise

        return result

    @property
    def supports_v_out(self):
        ranges_supported = self.supported_ranges
        v_out_supported = False
        if ranges_supported:
            try:
                ul.v_out(self._board_num, 0, ranges_supported[0], 0)
                v_out_supported = True
            except ULError:
                v_out_supported = False
        return v_out_supported
