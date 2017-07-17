from __future__ import absolute_import, division, print_function
from builtins import *  # @UnusedWildImport

from mcculw import ul


class Props(object):
    """The base class for classes that provide hardware information for the
    library examples. Subclasses of this class may change hardware values.
    It is recommended that the values provided by these classes be
    hard-coded in production code.
    """

    def __init__(self, params): pass

    def get_config_array(self, info_type, board_num, count_item, value_item,
                         wrapper_type=None):
        result = []

        count = ul.get_config(info_type, board_num, 0, count_item)
        for item_num in range(count):
            config_value = ul.get_config(
                info_type, board_num, item_num, value_item)
            if wrapper_type == None:
                result.append(config_value)
            else:
                result.append(wrapper_type(config_value))

        return result
