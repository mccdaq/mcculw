# -*- coding: UTF-8 -*-

from __future__ import absolute_import, division, print_function

from ctypes import Structure, c_char, c_uint, c_ulonglong

from builtins import *  # @UnusedWildImport
from mcculw.enums import InterfaceType


class DaqDeviceDescriptor(Structure):
    """The DaqDeviceDescriptor class includes the properties that you use to
    examine the descriptor information of a detected device.

    Attributes
    ----------
    product_name : string
        The product name of the detected device
    product_id : int
        A number associated with the detected device
    interface_type : InterfaceType
        The bus type associated with the detected DAQ device
    dev_string : string
        A string associated with the detected device. For Ethernet devices,
        this value represents a NetBIOS name. This value may be the same as
        the product_name on some devices, but may contain more specific
        information on other devices.
    unique_id : string
        A string identifier that indicates the serial number of a detected
        USB device, or the MAC address of a detected Bluetooth or Ethernet
        device
    nuid : int
        Byte array indicating the numeric representation of the unique
        identifier of the detected device
    """

    _fields_ = [
        ("_product_name", c_char * 64),
        ("product_id", c_uint),
        ("_interface_type", c_uint),
        ("_dev_string", c_char * 64),
        ("_unique_id", c_char * 64),
        ("nuid", c_ulonglong),
        ("_reserved", c_char * 512)
    ]

    # Create getters and setters for the string fields. This prevents the
    # user from having to convert to/from utf8

    @property
    def product_name(self):
        return self._product_name.decode('utf8')

    @product_name.setter
    def product_name(self, value):
        self._product_name = value.encode('utf8')

    @property
    def interface_type(self):
        return InterfaceType(self._interface_type)

    @interface_type.setter
    def interface_type(self, value):
        self._interface_type = value

    @property
    def dev_string(self):
        return self._dev_string.decode('utf8')

    @dev_string.setter
    def dev_string(self, value):
        self._dev_string = value.encode('utf8')

    @property
    def unique_id(self):
        return self._unique_id.decode('utf8')

    @unique_id.setter
    def unique_id(self, value):
        self._unique_id = value.encode('utf8')

    def __str__(self):
        if self.dev_string != None and self.dev_string != "":
            return self.dev_string
        else:
            return self.product_name
