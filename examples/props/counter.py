from __future__ import absolute_import, division, print_function

from builtins import *  # @UnusedWildImport

from mcculw import ul
from mcculw.enums import InfoType, BoardInfo, CounterInfo, \
    CounterChannelType, ScanOptions
from examples.props.propsbase import Props


class CounterProps(Props):
    """Provides counter input information on the hardware configured at the
    board number given.

    This class is used to provide hardware information for the library
    examples, and may change hardware values. It is recommended that the
    values provided by this class be hard-coded in production code. 
    """

    def __init__(self, board_num):
        self._board_num = board_num

        self.num_chans = self._get_num_ci_chans()

        self.counter_info = []
        # _get_ctr_type uses a 0-based index, not first_channel_num
        for dev_num in range(self.num_chans):
            channel_info = CounterProps.CounterChannelInfo(
                self._board_num, dev_num)
            self.counter_info.append(channel_info)

    def _get_num_ci_chans(self):
        return ul.get_config(
            InfoType.BOARDINFO, self._board_num, 0, BoardInfo.CINUMDEVS)

    class CounterChannelInfo(object):
        def __init__(self, board_num, dev_num):
            self._board_num = board_num
            self._dev_num = dev_num
            self.channel_num = self._get_channel_num()
            self.type = self._get_ctr_type()
            self.supported_scan_options = self._get_supported_scan_options()

        def _get_channel_num(self):
            return ul.get_config(
                InfoType.COUNTERINFO, self._board_num, self._dev_num,
                CounterInfo.CTRNUM)

        def _get_ctr_type(self):
            return CounterChannelType(ul.get_config(
                InfoType.COUNTERINFO, self._board_num, self._dev_num,
                CounterInfo.CTRTYPE))

        def _get_supported_scan_options(self):
            return ScanOptions(ul.get_config(
                InfoType.BOARDINFO, self._board_num, self._dev_num,
                BoardInfo.CTRSCANOPTIONS))
