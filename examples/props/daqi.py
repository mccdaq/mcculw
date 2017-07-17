from __future__ import absolute_import, division, print_function

from builtins import *  # @UnusedWildImport
from mcculw import ul
from mcculw.enums import FunctionType, InfoType, BoardInfo, ChannelType
from mcculw.ul import ULError

from examples.props.propsbase import Props


class DaqInputProps(Props):
    """Provides DAQ input information on the hardware configured at the
    board number given.

    This class is used to provide hardware information for the library
    examples, and may change hardware values. It is recommended that the
    values provided by this class be hard-coded in production code. 
    """

    def __init__(self, board_num):
        self._board_num = board_num
        self.is_supported = self._get_is_supported()

        if self.is_supported:
            self.supported_channel_types = self._get_chan_types()
            self.supports_setpoints = self._get_supports_setpoints()
        else:
            self.supported_channel_types = []
            self.supports_setpoints = False

    def _get_is_supported(self):
        try:
            ul.get_status(self._board_num, FunctionType.DAQIFUNCTION)
        except ULError:
            return False
        return True

    def _get_chan_types(self):
        return self.get_config_array(
            InfoType.BOARDINFO, self._board_num, BoardInfo.DAQINUMCHANTYPES,
            BoardInfo.DAQICHANTYPE, ChannelType)

    def _get_supports_setpoints(self):
        try:
            ul.daq_set_setpoints(
                self._board_num, [], [], [], [], [], [], [], [], 0)
            return True
        except ULError:
            return False
