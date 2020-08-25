from __future__ import absolute_import, division, print_function
from builtins import *  # @UnusedWildImport

from mcculw import ul
from mcculw.ul import ULError
from mcculw.enums import FunctionType, InfoType, BoardInfo, ChannelType


class DaqiInfo:
    """Provides DAQ input information for the device with the specified
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
    def is_supported(self):
        daqi_supported = True
        try:
            ul.get_status(self._board_num, FunctionType.DAQIFUNCTION)
        except ul.ULError:
            daqi_supported = False
        return daqi_supported

    @property
    def supported_channel_types(self):
        chan_types = []

        if self.is_supported:
            count = ul.get_config(InfoType.BOARDINFO, self._board_num, 0,
                                  BoardInfo.DAQINUMCHANTYPES)

            for type_index in range(count):
                chan_type = ul.get_config(InfoType.BOARDINFO, self._board_num,
                                          type_index, BoardInfo.DAQICHANTYPE)
                chan_types.append(ChannelType(chan_type))

        return chan_types

    @property
    def supports_setpoints(self):
        setpoints_supported = False
        if self.is_supported:
            try:
                ul.daq_set_setpoints(self._board_num, [], [], [], [], [], [],
                                     [], [], 0)
                setpoints_supported = True
            except ULError:
                setpoints_supported = False

        return setpoints_supported
