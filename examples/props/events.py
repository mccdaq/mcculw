from __future__ import absolute_import, division, print_function

from builtins import *  # @UnusedWildImport
from mcculw import ul
from mcculw.enums import EventType
from mcculw.ul import ULError

from examples.props.propsbase import Props


class EventProps(Props):
    """Provides events information on the hardware configured at the board
    number given.

    This class is used to provide hardware information for the library
    examples, and may change hardware values. It is recommended that the
    values provided by this class be hard-coded in production code. 
    """

    def __init__(self, board_num):
        self._board_num = board_num
        self.supported_event_types = self._get_supported_event_types()

    def _get_supported_event_types(self):
        result = []

        for event_type in EventType:
            try:
                ul.disable_event(self._board_num, event_type)
                result.append(event_type)
            except ULError:
                pass

        return result
