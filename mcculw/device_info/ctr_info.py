from __future__ import absolute_import, division, print_function
from builtins import *  # @UnusedWildImport

from mcculw import ul
from mcculw.enums import (InfoType, BoardInfo, CounterInfo, CounterChannelType,
                          ScanOptions)


class CtrInfo:
    """Provides counter information for the device with the specified
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
    def num_chans(self):
        return ul.get_config(InfoType.BOARDINFO, self._board_num, 0,
                             BoardInfo.CINUMDEVS)

    @property
    def is_supported(self):
        return self.num_chans > 0

    @property
    def chan_info(self):
        chan_info_list = []
        for chan_index in range(self.num_chans):
            channel_info = CtrChanInfo(self._board_num, chan_index)
            chan_info_list.append(channel_info)
        return chan_info_list


class CtrChanInfo:
    def __init__(self, board_num, chan_index):
        self._board_num = board_num
        self._chan_index = chan_index

    @property
    def channel_num(self):
        return ul.get_config(InfoType.COUNTERINFO, self._board_num,
                             self._chan_index, CounterInfo.CTRNUM)

    @property
    def type(self):
        return CounterChannelType(ul.get_config(InfoType.COUNTERINFO,
                                                self._board_num,
                                                self._chan_index,
                                                CounterInfo.CTRTYPE))

    @property
    def supported_scan_options(self):
        return ScanOptions(ul.get_config(InfoType.BOARDINFO, self._board_num,
                                         self._chan_index,
                                         BoardInfo.CTRSCANOPTIONS))
