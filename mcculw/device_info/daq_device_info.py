from __future__ import absolute_import, division, print_function
from builtins import *  # @UnusedWildImport

from mcculw import ul
from mcculw.ul import ULError
from mcculw.enums import (BoardInfo, InfoType, ErrorCode, EventType,
                          ExpansionInfo)
from .ai_info import AiInfo
from .ao_info import AoInfo
from .ctr_info import CtrInfo
from .daqi_info import DaqiInfo
from .daqo_info import DaqoInfo
from .dio_info import DioInfo


class DaqDeviceInfo:
    """Provides hardware information for the DAQ device configured with the
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
        self._board_type = ul.get_config(InfoType.BOARDINFO, board_num, 0,
                                         BoardInfo.BOARDTYPE)
        if self._board_type == 0:
            raise ULError(ErrorCode.BADBOARD)

        self._ai_info = AiInfo(self._board_num)
        self._ao_info = AoInfo(self._board_num)
        self._ctr_info = CtrInfo(self._board_num)
        self._daqi_info = DaqiInfo(self._board_num)
        self._daqo_info = DaqoInfo(self._board_num)
        self._dio_info = DioInfo(self._board_num)

    @property
    def board_num(self):  # -> int
        return self._board_num

    @property
    def product_name(self):  # -> str
        return ul.get_board_name(self._board_num)

    @property
    def unique_id(self):  # -> str
        return ul.get_config_string(InfoType.BOARDINFO, self._board_num, 0,
                                    BoardInfo.DEVUNIQUEID, 32)

    @property
    def supports_analog_input(self):  # -> boolean
        return self._ai_info.is_supported

    @property
    def supports_temp_input(self):  # -> boolean
        return self._ai_info.temp_supported

    def get_ai_info(self):  # -> AiInfo
        return self._ai_info

    @property
    def supports_analog_output(self):  # -> boolean
        return self._ao_info.is_supported

    def get_ao_info(self):  # -> AoInfo
        return self._ao_info

    @property
    def supports_counters(self):  # -> boolean
        return self._ctr_info.is_supported

    def get_ctr_info(self):  # -> CtrInfo
        return self._ctr_info

    @property
    def supports_daq_input(self):  # -> boolean
        return self._daqi_info.is_supported

    def get_daqi_info(self):  # -> DaqiInfo
        return self._daqi_info

    @property
    def supports_daq_output(self):  # -> boolean
        return self._daqo_info.is_supported

    def get_daqo_info(self):  # -> DaqoInfo
        return self._daqo_info

    @property
    def supports_digital_io(self):  # -> boolean
        return self._dio_info.is_supported

    def get_dio_info(self):  # -> DioInfo
        return self._dio_info

    @property
    def supported_event_types(self):  # -> list[EventType]
        event_types = []

        for event_type in EventType:
            try:
                ul.disable_event(self._board_num, event_type)
                event_types.append(event_type)
            except ULError:
                pass

        return event_types

    @property
    def num_expansions(self):  # -> int
        return ul.get_config(InfoType.BOARDINFO, self.board_num, 0,
                             BoardInfo.NUMEXPS)

    @property
    def exp_info(self):  # -> list[ExpInfo]
        exp_info = []
        for expansion_num in range(self.num_expansions):
            exp_info.append(ExpInfo(self._board_num, expansion_num))
        return exp_info


class ExpInfo:
    def __init__(self, board_num, expansion_num):
        self._board_num = board_num
        self._expansion_num = expansion_num

    @property
    def board_type(self):
        return ul.get_config(InfoType.EXPANSIONINFO, self._board_num,
                             self._expansion_num, ExpansionInfo.BOARDTYPE)

    @property
    def mux_ad_chan(self):
        return ul.get_config(InfoType.EXPANSIONINFO, self._board_num,
                             self._expansion_num, ExpansionInfo.MUX_AD_CHAN1)
