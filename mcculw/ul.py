# -*- coding: UTF-8 -*-

"""
Wraps all of the methods from UL for use in Python.
"""
from __future__ import absolute_import, division, print_function

import collections
from ctypes import *  # @UnusedWildImport
from ctypes.wintypes import HGLOBAL
import struct

from builtins import *  # @UnusedWildImport

from mcculw.enums import ErrorCode, Status, ChannelType, TimerIdleState, \
    PulseOutOptions, TInOptions
from mcculw.structs import DaqDeviceDescriptor


class ULError(Exception):
    def __init__(self, errorcode):
        super(ULError, self).__init__()
        self.errorcode = errorcode
        self.message = get_err_msg(errorcode)

    def __str__(self):
        return "Error " + str(self.errorcode) + ": " + self.message


_ERRSTRLEN = 256
_BOARDNAMELEN = 64

# Load the correct library based on the Python architecture in use
if struct.calcsize("P") == 4:
    _cbw = WinDLL('cbw32.dll')
else:
    _cbw = WinDLL('cbw64.dll')

_cbw.cbAChanInputMode.argtypes = [c_int, c_int, c_int]


def a_chan_input_mode(board_num, channel, input_mode):
    """Sets the analog input mode for a specified A/D channel.

    Parameters
    ----------
    board_num : int
        The number associated with the board when it was installed with InstaCal or created with
        :func:`.create_daq_device`.
    channel : int
        The A/D input channel number.
    input_mode : AnalogInputMode
        The channel input mode.
    """
    _check_err(_cbw.cbAChanInputMode(board_num, channel, input_mode))


_cbw.cbAIn.argtypes = [c_int, c_int, c_int, POINTER(c_ushort)]


def a_in(board_num, channel, ul_range):
    """Reads an A/D input channel from the specified board, and returns a 16-bit unsigned integer
    value. If the specified A/D board has programmable gain then it sets the gain to the specified
    range. The raw A/D value is converted to an A/D value and returned.

    Parameters
    ----------
    board_num : int
        The number associated with the board when it was installed with InstaCal or created with
        :func:`.create_daq_device`.
    channel : int
        The A/D input channel number.
    ul_range : ULRange
        A/D Range code. If the selected A/D board does not have a programmable gain feature, this
        parameter is ignored. If the A/D board does have programmable gain, set the ul_range
        parameter to the desired A/D range.

    Returns
    -------
    int
        The A/D value
    """
    data_value = c_ushort()
    _check_err(_cbw.cbAIn(
        board_num, channel, ul_range, byref(data_value)))
    return data_value.value


_cbw.cbAIn32.argtypes = [c_int, c_int, c_int, POINTER(c_ulong), c_int]


def a_in_32(board_num, channel, ul_range, options=0):
    """Reads an A/D input channel from the specified board, and returns a 32-bit unsigned integer
    value. If the specified A/D board has programmable gain then it sets the gain to the specified
    range. The raw A/D value is converted to an A/D value and returned. In general, this function
    should be used with devices with a resolution higher than 16-bits.

    Parameters
    ----------
    board_num : int
        The number associated with the board when it was installed with InstaCal or created
        with :func:`.create_daq_device`.
    channel : int
        The A/D input channel number.
    ul_range : ULRange
        A/D Range code. If the selected A/D board does not have a programmable gain feature, this
        parameter is ignored. If the A/D board does have programmable gain, set the ul_range
        parameter to the desired A/D range.
    options, optional
        Reserved for future use

    Returns
    -------
    int
        The A/D value
    """
    data_value = c_ulong()
    _check_err(_cbw.cbAIn32(
        board_num, channel, ul_range, byref(data_value), options))
    return data_value.value


_cbw.cbAInScan.argtypes = [c_int, c_int, c_int, c_long, POINTER(c_long),
                           c_int, HGLOBAL, c_int]


def a_in_scan(
        board_num, low_chan, high_chan, num_points, rate, ul_range, memhandle,
        options):
    """Scans a range of A/D channels and stores the samples in an array. :func:`.a_in_scan` reads
    the specified number of A/D samples at the specified sampling rate from the specified range of
    A/D channels from the specified board. If the A/D board has programmable gain, then it sets
    the gain to the specified range. The collected data is returned to the data array.

    Parameters
    ----------
    board_num : int
        The number associated with the board when it was installed with InstaCal or created
        with :func:`.create_daq_device`.
    low_chan : int
        First A/D channel of the scan. When :func:`.a_load_queue` is used, the channel count is
        determined by the total number of entries in the channel gain queue and low_chan is
        ignored.
    high_chan : int
        Last A/D channel of the scan. When :func:`.a_load_queue` is used, the channel count is
        determined by the total number of entries in the channel gain queue and high_chan is
        ignored.
    num_points : int
        The number of A/D samples to collect. Specifies the total number of A/D samples to collect.
        If more than one channel is being sampled, then the number of samples collected per channel
        is equal to count / (high_chan - low_chan + 1).
    rate : int
        The rate at which samples are acquired, in samples per second per channel.

        For example, sampling four channels, 0-3, at a rate of 10,000 scans per second
        (10 kilohertz (kHz)) results in an A/D converter rate of 40 kHz: four channels at 10,000
        samples per channel per second. With other software, you specify the total A/D chip rate.
        In those systems, the per channel rate is equal to the A/D rate divided by the number
        of channels in a scan.

        The actual sampling rate in some cases will vary a small amount from the requested rate.
        The actual rate is returned.

        The channel count is determined by the low_chan and high_chan parameters.
        Channel Count = (high_chan - low_chan + 1).

        When :func:`.a_load_queue` is used, the channel count is determined by the total number of
        entries in the channel gain queue. low_chan and high_chan are ignored.
    ul_range : ULRange
        A/D range code. If the selected A/D board does not have a programmable range feature, this
        parameter is ignored. Otherwise, set the range parameter to any range that is supported by
        the selected A/D board. Refer to board-specific information for a list of the supported A/D
        ranges of each board.
    memhandle : int
        Handle for the Windows buffer to store data. This buffer must have been previously
        allocated. For 16-bit data, create the buffer with :func:`.win_buf_alloc`. For data that is
        > 16-bit and <= 32-bit, use :func:`.win_buf_alloc_32`. For data that is > 32-bit and <=
        64-bit, use :func:`.win_buf_alloc_64`. When using scaled data, use
        :func:`.scaled_win_buf_alloc`.
    options : ScanOptions
        Flags that control various options. May contain any combination of non-contradictory
        choices in the "options parameter values" table below.

    Returns
    -------
    int
        The actual rate set, which may be different from the requested rate because of pacer
        limitations.


    .. table:: **options parameter values**

        =======================  ==================================================================
        Transfer method options  The following four options determine how data is transferred from
                                 the board to PC memory. If none of these options are specified
                                 (recommended), the optimum sampling mode is automatically chosen
                                 based on board type and sampling speed. Use the default method
                                 unless you have a reason to select a specific transfer method.


                                 - SINGLEIO
                                   A/D data is transferred to memory one sample at a time. Rates
                                   attainable using SINGLEIO are PC-dependent and generally less
                                   than 4 kHz.

                                 - DMAIO
                                   A/D transfers are initiated by a DMA request.

                                 - BLOCKIO
                                   A/D transfers are handled in blocks (by REP-INSW for example).

                                   **BLOCKIO is not recommended for slow acquisition rates.** If
                                   the rate of acquisition is very slow (for example less than
                                   200 Hz) BLOCKIO is probably not the best choice for transfer
                                   mode. The reason for this is that status for the operation is
                                   not available until one packet of data has been collected
                                   (typically 512 samples). The implication is that if acquiring
                                   100 samples at 100 Hz using BLOCKIO, the operation will not
                                   complete until 5.12 seconds has elapsed.

                                 - BURSTIO
                                   Allows higher sampling rates for sample counts up to full FIFO.
                                   Data is collected into the local FIFO. Data transfers to the PC
                                   are held off until after the scan is complete. For BACKGROUND
                                   scans, the count and index returned by :func:`.get_status`
                                   remain 0 and the status equals RUNNING until the scan finishes.
                                   When the scan is complete and the data is retrieved, the count
                                   and index are updated and the status equals IDLE.

                                   BURSTIO is the default mode for non-Continuous fast scans
                                   (aggregate sample rates above 1000 Hz) with sample counts up to
                                   full FIFO. To avoid the BURSTIO default, specify BLOCKIO.

                                   BURSTIO is not a valid option for most boards. It is used mainly
                                   for USB products.
        -----------------------  ------------------------------------------------------------------
        BACKGROUND               If the BACKGROUND option is not used then the :func:`.a_in_scan`
                                 function will not return to your program until all of the
                                 requested data has been collected and returned to the buffer. When
                                 the BACKGROUND option is used, control will return immediately to
                                 the next line in your program and the data collection from the A/D
                                 into the buffer will continue in the background. Use
                                 :func:`.get_status` with AIFUNCTION to check on the status of the
                                 background operation. Alternatively, some boards support
                                 :func:`.enable_event` for event notification of changes in status
                                 of BACKGROUND scans. Use :func:`.stop_background` with AIFUNCTION
                                 to terminate the background process before it has completed.
                                 :func:`.stop_background` should be executed after normal
                                 termination of all background functions in order to clear
                                 variables and flags.
        -----------------------  ------------------------------------------------------------------
        BURSTMODE                Enables burst mode sampling. Scans from low_chan to high_chan are
                                 clocked at the maximum A/D rate in order to minimize channel to
                                 channel skew. Scans are initiated at the rate specified by the
                                 rate parameter.

                                 BURSTMODE is not recommended for use with the SINGLEIO option. If
                                 this combination is used, the count value should be set as low as
                                 possible, preferably to the number of channels in the scan.
                                 Otherwise, overruns may occur.
        -----------------------  ------------------------------------------------------------------
        CONTINUOUS               This option puts the function in an endless loop. Once it collects
                                 the required number of samples, it resets to the start of the
                                 buffer and begins again. The only way to stop this operation is
                                 with :func:`.stop_background`. Normally this option should be used
                                 in combination with BACKGROUND so that your program will regain
                                 control.

                                 **count parameter settings in CONTINUOUS mode**: For some DAQ
                                 hardware, count must be an integer multiple of the packet size.
                                 Packet size is the amount of data that a DAQ device transmits back
                                 to the PC's memory buffer during each data transfer. Packet size
                                 can differ among DAQ hardware, and can even differ on the same DAQ
                                 product depending on the transfer method.

                                 In some cases, the minimum value for the count parameter may
                                 change when the CONTINUOUS option is used. This can occur for
                                 several reasons; the most common is that in order to trigger an
                                 interrupt on boards with FIFOs, the circular buffer must occupy at
                                 least half the FIFO. Typical half-FIFO sizes are 256, 512 and
                                 1,024.

                                 Another reason for a minimum count value is that the buffer in
                                 memory must be periodically transferred to the user buffer. If the
                                 buffer is too small, data will be overwritten during the transfer
                                 resulting in garbled data.

                                 Refer to board-specific information in the Universal Library
                                 User's Guide for packet size information for your particular DAQ
                                 hardware.
        -----------------------  ------------------------------------------------------------------
        EXTCLOCK                 If this option is used, conversions will be controlled by the
                                 signal on the external clock input rather than by the internal
                                 pacer clock. Each conversion will be triggered on the appropriate
                                 edge of the clock input signal (refer to the board-specific
                                 information in the Universal Library User's Guide). In most cases,
                                 when this option is used the rate parameter is ignored. The
                                 sampling rate is dependent on the clock signal. Options for the
                                 board will default to a transfer mode that will allow the maximum
                                 conversion rate to be attained unless otherwise specified.

                                 In some cases, such as with the PCI-DAS4020/12, an approximation
                                 of the rate is used to determine the size of the packets to
                                 transfer from the board. Set the rate parameter to an approximate
                                 maximum value.

                                 **SINGLEIO is recommended for slow external clock rates**: If the
                                 rate of the external clock is very slow (for example less than
                                 200 Hz) and the board you are using supports BLOCKIO, you may want
                                 to include the SINGLEIO option. The reason for this is that the
                                 status for the operation is not available until one packet of data
                                 has been collected (typically 512 samples). The implication is
                                 that, if acquiring 100 samples at 100 Hz using BLOCKIO (the
                                 default for boards that support it if EXTCLOCK is used), the
                                 operation will not complete until 5.12 seconds has elapsed.
        -----------------------  ------------------------------------------------------------------
        EXTTRIGGER               If this option is specified, the sampling will not begin until the
                                 trigger condition is met. On many boards, this trigger condition
                                 is programmable (refer to the :func:`.set_trigger` function and
                                 board-specific information for details) and can be programmed for
                                 rising or falling edge or an analog level.

                                 On other boards, only 'polled gate' triggering is supported. In
                                 this case, assuming active high operation, data acquisition will
                                 commence immediately if the trigger input is high. If the trigger
                                 input is low, acquisition will be held off unit it goes high.
                                 Acquisition will then continue until num_points samples have been
                                 taken regardless of the state of the trigger input. For "polled
                                 gate" triggering, this option is most useful if the signal is a
                                 pulse with a very low duty cycle (trigger signal in TTL low state 
                                 most of the time) so that triggering will be held off until the
                                 occurrence of the pulse.
        -----------------------  ------------------------------------------------------------------
        HIGHRESRATE              Acquires data at a high resolution rate. When specified, the rate
                                 at which samples are acquired is in "samples per 1000 seconds per
                                 channel". When this option is not specified, the rate at which
                                 samples are acquired is in "samples per second per channel" (refer
                                 to the rate parameter above).
        -----------------------  ------------------------------------------------------------------
        NOCALIBRATEDATA          Turns off real-time software calibration for boards which are
                                 software calibrated. This is done by applying calibration factors
                                 to the data on a sample by sample basis as it is acquired.
                                 Examples are the PCM-DAS16/330 and PCM-DAS16x/12. Turning off
                                 software calibration saves CPU time during a high speed
                                 acquisition run. This may be required if your processor is less
                                 than a 150 MHz Pentium and you desire an acquisition speed in
                                 excess of 200 kHz. These numbers may not apply to your system.
                                 Only trial will tell for sure. DO NOT use this option if you do
                                 not have to. If this option is used, the data must be calibrated
                                 after the acquisition run with the :func:`.a_calibrate_data`
                                 function.
        -----------------------  ------------------------------------------------------------------
        RETRIGMODE               Re-arms the trigger after a trigger event is performed. With this
                                 mode, the scan begins when a trigger event occurs. When the scan
                                 completes, the trigger is re-armed to acquire the next the batch
                                 of data. You can specify the number of samples in the scan for
                                 each trigger event (described below). The RETRIGMODE option can be
                                 used with the CONTINUOUS option to continue arming the trigger
                                 until :func:`.stop_background` is called.

                                 You can specify the number of samples to acquire with each trigger
                                 event. This is the trigger count. Use the :func:`.set_config`
                                 config_item option BIADTRIGCOUNT to set the trigger count. If you
                                 specify a trigger count that is either zero or greater than the
                                 value of the :func:`.a_in_scan` count parameter, the trigger count
                                 will be set to the value of the count parameter.

                                 Specify the CONTINUOUS option with the trigger count set to zero
                                 to fill the buffer with count samples, re-arm the trigger, and
                                 refill the buffer upon the next trigger.
        -----------------------  ------------------------------------------------------------------
        SCALEDATA                Converts raw scan data - to voltage, temperature, and so on,
                                 depending upon the selected channel sensor category - during the
                                 analog input scan, and puts the scaled data directly into the user
                                 buffer. The user buffer should have been allocated with
                                 :func:`.scaled_win_buf_alloc`.
        =======================  ==================================================================

    **Caution!**

    You will generate an error if you specify a total A/D rate beyond the capability
    of the board. The maximum update rate depends on the A/D board that is being used and on the
    sampling mode options.

    **Important**

    In order to understand the functions, you must read the board-specific
    information found in the Universal Library User's Guide. The example programs should be
    examined and run prior to attempting any programming of your own. Following this advice will
    save you hours of frustration, and possibly time wasted holding for technical support.

    This note, which appears elsewhere, is especially applicable to this function. Now is the time
    to read the board specific information for your board that is contained in the Universal
    Library User's Guide. We suggest that you make a copy of this information for reference as you
    read this manual and examine the example programs.
    """
    rate_internal = c_long(rate)
    _check_err(_cbw.cbAInScan(
        board_num, low_chan, high_chan, num_points, byref(rate_internal),
        ul_range, memhandle, options))
    return rate_internal.value


_cbw.cbAInputMode.argtypes = [c_int, c_int]


def a_input_mode(board_num, input_mode):
    """Sets the A/D channel input mode.

    Parameters
    ----------
    board_num : int
        The number associated with the board when it was installed with InstaCal or created
        with :func:`.create_daq_device`.
    input_mode : AnalogInputMode
        The channel input mode
    """
    _check_err(_cbw.cbAInputMode(board_num, input_mode))


_cbw.cbALoadQueue.argtypes = [c_int, POINTER(c_short), POINTER(c_short), c_int]


def a_load_queue(board_num, chan_list, gain_list, count):
    """Loads the A/D board's channel/gain queue. This function only works with A/D boards that have
    channel/gain queue hardware. Some products do not support channel/gain queue, and some that do
    support it are limited on the order of elements, number of elements, and gain values that can
    be included, etc. Refer to the device-specific information in the Universal Library User's
    Guide to find details for your particular product.

    Parameters
    ----------
    board_num : int
        The number associated with the board when it was installed with InstaCal or created
        with :func:`.create_daq_device`.
    chan_list : list of int
        list containing channel values. This array should contain all of the channels that
        will be loaded into the channel gain queue.
    gain_list : list of ULRange
        list containing A/D range values. This array should contain each of the A/D ranges that
        will be loaded into the channel gain queue.
    count : int
        Number of elements in chan_list and gain_list or 0 to disable channel/gain queue.
        Specifies the total number of channel/gain pairs that will be loaded into the queue.
        chan_list and gain_list should contain at least count elements. Set count = 0 to disable
        the board's channel/gain queue. The maximum value is specific to the queue size of the
        A/D board's channel gain queue.
    """
    _check_err(_cbw.cbALoadQueue(
        board_num, _to_ctypes_array(chan_list, c_short),
        _to_ctypes_array(gain_list, c_short), count))


_cbw.cbAOut.argtypes = [c_int, c_int, c_int, c_ushort]


def a_out(board_num, channel, ul_range, data_value):
    """Sets the value of a D/A channel.

    Parameters
    ----------
    board_num : int
        The number associated with the board when it was installed with InstaCal or created
        with :func:`.create_daq_device`.
    channel : int
        D/A channel number. The maximum allowable channel depends on which type of D/A board is
        being used.
    ul_range : ULRange
        The D/A range. The output range of the D/A channel can be set to any of those supported by
        the board. If the D/A board does not have programmable ranges then this parameter will be
        ignored. Refer to board specific information for a list of the supported A/D ranges.
    data_value : int
        Value to set D/A to. Must be in the range 0-n where n is the value 2**Resolution - 1 of the
        converter. Exception: using 16-bit boards with Basic range is -32,768 to 32,767. Refer to
        the discussion on 16-bit values using a signed integer data type for more information.
    """
    _check_err(_cbw.cbAOut(board_num, channel, ul_range, data_value))


_cbw.cbAOutScan.argtypes = [c_int, c_int, c_int, c_long, POINTER(c_long),
                            c_int, HGLOBAL, c_int]


def a_out_scan(board_num, low_chan, high_chan, num_points, rate, ul_range, memhandle, options):
    """Outputs values to a range of D/A channels. This function can be used for paced analog output
    on hardware that supports paced output. It can also be used to update all analog outputs at the
    same time when the SIMULTANEOUS option is used.

    Parameters
    ----------
    board_num : int
        The number associated with the board when it was installed with InstaCal or created
        with :func:`.create_daq_device`.
    low_chan : int
        First D/A channel of scan.
    high_chan : int
        Last D/A channel of scan.
    num_points : int
        Number of D/A values to output. Specifies the total number of D/A values that will
        be output. Most D/A boards do not support timed outputs. For these boards, set the count to
        the number of channels in the scan.
    rate : int
        Sample rate in scans per second. For many D/A boards the rate is ignored and can be set
        to NOTUSED. For D/A boards with trigger and transfer methods which allow fast output rates,
        such as the CIO-DAC04/12-HS, rate should be set to the D/A output rate (in scans/sec).

        The actual sampling rate in some cases will vary a small amount from the requested rate.
        The actual rate is returned.

        If supported, this is the rate at which scans are triggered. If you are updating 4
        channels, 0-3, then specifying a rate of 10,000 scans per second (10 kHz) will result in
        the D/A converter rates of 10 kHz (one D/A per channel). The data transfer rate is 40,000
        words per second; 4 channels * 10,000 updates per scan.

        The maximum update rate depends on the D/A board that is being used. It is also dependent
        on the sampling mode options.
    ul_range : ULRange
        The D/A range. The output range of the D/A channel can be set to any of those supported by
        the board. If the D/A board does not have a programmable gain, this parameter is ignored.
    memhandle : int
        Handle for the Windows buffer from which data is output. This buffer must have been
        previously allocated and data values loaded.

        For 16-bit data, create the buffer with :func:`.win_buf_alloc`. For data that is > 16-bit
        and <= 32-bit, use :func:`.win_buf_alloc_32`. For data that is > 32-bit and <= 64-bit, use
        :func:`.win_buf_alloc_64`. When using scaled data, use :func:`.scaled_win_buf_alloc`. You
        can load the data values with :func:`.win_array_to_buf` or :func:`.scaled_win_array_to_buf`
        (for scaled data).

        When the device supports output scanning of scaled data, such as :func:`.a_out_scan` using
        the :const:`~mcculw.enums.SCALEDATA` option, create the buffer with
        :func:`.scaled_win_buf_alloc`. See hardware- specific information to determine if the
        device supports scaled data.

        Note: when scanning to multiple channels, the data must be interleaved into a 1-D array.
    options : ScanOptions
        Flags that control various options. May contain any combination of non-contradictory
        choices in the "options parameter values" table below.

    Returns
    -------
    int
        The actual rate set, which may be different from the user specified rate due to pacer
        limitations.


    .. table:: **options parameter values**

        ==============  ===========================================================================
        ADCCLOCK        Paces the data output operation using the ADC clock.
        --------------  ---------------------------------------------------------------------------
        ADCCLOCKTRIG    Triggers a data output operation when the ADC clock starts.
        --------------  ---------------------------------------------------------------------------
        BACKGROUND      This option may only be used with boards which support interrupt, DMA or
                        REP-INSW transfer methods. When this option is used the D/A operations will
                        begin running in the background and control will immediately return to the
                        next line of your program. Use :func:`.get_status` with AOFUNCTION to check
                        the status of background operation. Alternatively, some boards support
                        :func:`.enable_event` for event notification of changes in status of
                        BACKGROUND scans. Use :func:`.stop_background` with AOFUNCTION to terminate
                        background operations before they are completed. :func:`.stop_background`
                        should be executed after normal termination of all background functions in
                        order to clear variables and flags.
        --------------  ---------------------------------------------------------------------------
        CONTINUOUS      This option may only be used with boards which support interrupt, DMA or
                        REP-INSW transfer methods. This option puts the method in an endless loop.

                        Once it outputs the specified number (num_points) of D/A values, it resets
                        to the start of the buffer and begins again. The only way to stop this
                        operation is by calling :func:`.stop_background` with AOFUNCTION. This
                        option should only be used in combination with BACKGROUND so that your
                        program can regain control.
        --------------  ---------------------------------------------------------------------------
        EXTCLOCK        If this option is specified, conversions will be paced by the signal on the
                        external clock input rather than by the internal pacer clock. Each
                        conversion will be triggered on the appropriate edge of the clock input
                        signal (refer to board-specific information contained in the Universal
                        Library Users Guide).

                        When this option is used the rate parameter is ignored. The sampling rate
                        is dependent on the clock signal. Options for the board default to transfer
                        types that allow the maximum conversion rate to be attained unless
                        otherwise specified.
        --------------  ---------------------------------------------------------------------------
        EXTTRIGGER      If this option is specified the sampling will not begin until the trigger
                        condition is met. On many boards, this trigger condition is programmable
                        (refer to the :func:`.set_trigger` function and board-specific information
                        contained in the Universal Library Users Guide for details).
        --------------  ---------------------------------------------------------------------------
        HIGHRESRATE     Acquires data at a high resolution rate. When specified, the rate at which
                        samples are acquired is in "samples per 1000 seconds per channel". When
                        this option is not specified, the rate at which samples are acquired is in
                        "samples per second per channel" (refer to the rate parameter above).
        --------------  ---------------------------------------------------------------------------
        NONSTREAMEDIO   When this option is used, you can output non-streamed data to a specific
                        DAC output channel. The aggregate size of the data output buffer must be
                        less than or equal to the size of the internal data output FIFO in the
                        device. This allows the data output buffer to be loaded into the device's
                        internal output FIFO. Once the sample updates are transferred or downloaded
                        to the device, the device is responsible for outputting the data. You can't
                        make any changes to the output buffer once the output begins.

                        With NONSTREAMEDIO mode, you do not have to periodically feed output data
                        through the program to the device for the data output to continue. However,
                        the size of the buffer is limited.

                        NONSTREAMEDIO can only be used with the number of samples (count) set equal
                        to the size of the FIFO or less.
        --------------  ---------------------------------------------------------------------------
        RETRIGMODE      Re-arms the trigger after a trigger event is performed. With this mode, the
                        scan begins when a trigger event occurs. When the scan completes, the
                        trigger is re-armed to generate the next the batch of data. You can specify
                        the number of samples to generate for each trigger event (described below).
                        The RETRIGMODE option can be used with the CONTINUOUS option to continue
                        arming the trigger until :func:`.stop_background` is called.

                        You can specify the number of samples to generate with each trigger event.
                        This is the trigger count. Use the :func:`.set_config` config_item option
                        BIDACTRIGCOUNT to set the trigger count. If you specify a trigger count
                        that is either zero or greater than the value of the num_points parameter,
                        the trigger count will be set to the value of num_points.
        --------------  ---------------------------------------------------------------------------
        SCALEDATA       Gets scaled data, such as voltage, temperature, and so on, from the user
                        buffer, and converts it to raw data. The user buffer should have been
                        allocated with :func:`.scaled_win_buf_alloc`.
        --------------  ---------------------------------------------------------------------------
        SIMULTANEOUS    When this option is used (if the board supports it and the appropriate
                        switches are set on the board) all of the D/A voltages will be updated
                        simultaneously when the last D/A in the scan is updated. This generally
                        means that all the D/A values will be written to the board, then a read of
                        a D/A address causes all D/As to be updated with new values simultaneously.
        ==============  ===========================================================================

    **Caution!**

    You will generate an error if you specify a total D/A rate beyond the capability of
    the board. The maximum update rate depends on the D/A board that is being used and on the
    sampling mode options.
    """
    rate_internal = c_long(rate)
    _check_err(_cbw.cbAOutScan(
        board_num, low_chan, high_chan, num_points, byref(rate_internal),
        ul_range, memhandle, options))
    return rate_internal.value


APretrigResult = collections.namedtuple(
    "APretrigResult",
    "err_code actual_pretrig_count actual_total_count actual_rate")
_cbw.cbAPretrig.argtypes = [c_int, c_int, c_int, POINTER(c_long), POINTER(c_long),
                            POINTER(c_long), c_int, HGLOBAL, c_int]


def a_pretrig(board_num, low_chan, high_chan, pretrig_count, total_count, rate,
              ul_range, memhandle, options):
    """Waits for a trigger to occur and then returns a specified number of analog samples before
    and after the trigger occurred. If only 'polled gate' triggering is supported, the trigger
    input line (refer to the user's manual for the board) must be at TTL low before this function
    is called, or a TRIGSTATE error will occur. The trigger occurs when the trigger condition is
    met. Refer to the :func:`.set_trigger` function for more details.

    Parameters
    ----------
    board_num : int
        The number associated with the board when it was installed with InstaCal or created
        with :func:`.create_daq_device`.
    low_chan : int
        First A/D channel of scan.
    high_chan : int
        Last A/D channel of scan.
    pretrig_count : int
        Number of pre-trigger A/D samples to collect. Specifies the number of samples to collect
        before the trigger occurs.

        For products using a hardware implementation of pre-trigger (most products), pretrig_count
        must be less than (total_count - 512). For these devices, if the trigger occurs too early,
        fewer than the requested number of pre-trigger samples will be collected, an
        ErrorCode.TOOFEW value will be returned as the first return value. The second return value
        will indicate how many samples were actually collected. The post trigger samples will still
        be collected.

        For software implementations of pre-trigger, pretrig_count must be less than total_count.
        For these devices, triggers that occur before the requested number of pre-trigger samples
        are collected are ignored. See board-specific information contained in the UL Users Guide
        for details.

        pretrig_count must be evenly divisible by the number of channels being scanned. If it is
        not, this function will adjust the number (up) to the next valid value. The return value
        actual_pretrig_count will contain the new value.
    total_count : int
        Total number of A/D samples to collect. Specifies the total number of samples that will be
        collected and stored in the buffer.

        For products using a hardware implementation of pre-trigger (most products), total_count
        must be greater than or equal to the pretrig_count + 512. If the trigger occurs too early,
        fewer than the requested number of samples will be collected, and an ErrorCode.TOOFEW value
        will be returned as the first value. The third return value will indicate how many samples
        were actually collected.

        For software implementations of pre-trigger, total_count must be greater than
        pretrig_count. For these devices, triggers that occur before the requested number of
        pre-trigger samples are collected are ignored. See board-specific information contained in
        the UL Users Guide for details.

        total_count must be evenly divisible by the number of channels being scanned. If it is not,
        this function will adjust the number (down) to the next valid value. The return value
        actual_total_count will contain the new value.
    rate : int
        Sample rate in scans per second. The actual sampling rate in some cases will vary a small
        amount from the requested rate. The actual rate is returned in the actual_rate return
        value.
    ul_range : ULRange
        A/D Range code. If the selected A/D board does not have a programmable gain feature,
        this parameter is ignored. Otherwise, set to any range that is supported by the selected
        A/D board. Refer to board specific information for a list of the supported A/D ranges
        of each board.
    memhandle : int
        Handle for Windows buffer to store data. This buffer must have been previously allocated
        with the :func:`.win_buf_alloc` function.

        For hardware trigger types, the buffer referenced by MemHandle must be big enough to hold
        at least total_count + 512 integers.
    options : ScanOptions
        Flags that control various options. May contain any combination of non-contradictory
        choices in the "options parameter values" table below.


    ..table:: **options parameter values**

        ===========  ==============================================================================
        BACKGROUND   If the BACKGROUND option is not used, the :func:`.a_pretrig` function will not
                     return to your program until all of the requested data has been collected and
                     returned to the buffer. When the BACKGROUND option is used, control returns
                     immediately to the next line in your program, and the data collection from the
                     A/D into the buffer will continue in the background. Use :func:`.get_status`
                     with AIFUNCTION to check on the status of the background operation.
                     Alternatively, some boards support :func:`.enable_event` for event
                     notification of changes in status of BACKGROUND scans. Use
                     :func:`.stop_background` with AIFUNCTION to terminate the background process
                     before it has completed.

                     Call :func:`.stop_background` after normal termination of all background
                     functions to clear variables and flags.
        -----------  ------------------------------------------------------------------------------
        EXTCLOCK     This option is available only for boards that have separate inputs for
                     external pacer and external trigger. See your hardware manual or
                     board-specific information.
        ===========  ==============================================================================

    Returns
    -------
    err_code : int
        The error code, which will either be ErrorCode.TOOFEW or ErrorCode.NOERRORS. See the
        pretrig_count parameter for more information. All other errors will raise a ULError
        as usual.
    actual_pretrig_count : int
        The actual pretrig count (see pretrig_count parameter)
    actual_total_count : int
        The actual total count (see total_count parameter)
    actual_rate : int
        The actual rate set, which may be different from the user specified rate due to pacer
        limitations.

    Notes
    -----
    For hardware trigger types, the buffer referenced by MemHandle must be big enough to hold
    at least total_count + 512 integers.
    """
    pretrig_count_internal = c_long(pretrig_count)
    total_count_internal = c_long(total_count)
    rate_internal = c_long(rate)
    err_code = _cbw.cbAPretrig(
        board_num, low_chan, high_chan, byref(pretrig_count_internal),
        byref(total_count_internal), byref(rate_internal), ul_range,
        memhandle, options)
    if err_code != ErrorCode.TOOFEW:
        _check_err(err_code)

    return APretrigResult(
        err_code, pretrig_count_internal.value, total_count_internal.value, rate_internal.value)


_cbw.cbATrig.argtypes = [c_int, c_int, c_int,
                         c_ushort, c_int, POINTER(c_ushort)]


def a_trig(board_num, channel, trig_type, trig_value, ul_range):
    """Waits for a specified analog input channel to go above or below a specified value.
    :func:`.a_trig` continuously reads the specified channel and compares its value to trig_value.
    Depending on whether trig_type is set to TrigType.TRIG_ABOVE or TrigType.TRIG_BELOW, it waits
    for the first A/D sample that is above or below trig_value. The first sample that meets the
    trigger criteria is returned.

    Parameters
    ----------
    board_num : int
        The number associated with the board when it was installed with InstaCal or created
        with :func:`.create_daq_device`.
    channel : int
        A/D channel number. The maximum allowable channel depends on which type of A/D board is
        being used. When a board has both single ended and differential inputs, the maximum
        allowable channel number also depends on how the board is configured (such as 8 channels
        for DIFF inputs, and 16 channels for SE inputs).
    trig_type : TrigType
        TrigType.TRIG_ABOVE or TrigType.TRIGBELOW. Specifies whether to wait for the analog input
        to be ABOVE or BELOW the specified trigger value.
    trig_value : int
        The threshold value that all A/D values are compared to. Must be in the range 0 to 4,095
        for 12-bit A/D boards, or 0 to 65,535 for 16-bit A/D boards.
    ul_range : ULRange
        A/D Range code. If the selected A/D board does not have a programmable gain feature, this
        parameter is ignored. If the A/D board does have programmable gain, set the ul_range
        parameter to the desired A/D range.

    Returns
    -------
    int
        The value of the first A/D sample to meet the trigger criteria.
    """
    data_value = c_ushort()
    _check_err(_cbw.cbATrig(
        board_num, channel, trig_type, trig_value, ul_range, byref(data_value)))
    return data_value.value


_cbw.cbCClear.argtypes = [c_int, c_int]


def c_clear(board_num, counter_num):
    """Clears a scan counter value (sets it to zero). This function only works with counter boards
    that have counter scan capability.

    Parameters
    ----------
    board_num : int
        The number associated with the board when it was installed with InstaCal or created
        with :func:`.create_daq_device`.
    counter_num : int
        The counter to clear. Note: This parameter is zero-based (the first counter number to clear
        is "0").
    """
    _check_err(_cbw.cbCClear(board_num, counter_num))


_cbw.cbCConfigScan.argtypes = [c_int, c_int,
                               c_int, c_int, c_int, c_int, c_int, c_int]


def c_config_scan(board_num, counter_num, mode, debounce_time, debounce_mode,
                  edge_detection, tick_size, mapped_channel):
    """Configures a counter channel. This function only works with counter boards that have counter
    scan capability.

    Parameters
    ----------
    board_num : int
        The number associated with the board when it was installed with InstaCal or created
        with :func:`.create_daq_device`.
    counter_num : int
        The counter number to configure. This parameter is zero-based, so the first counter number
        is "0".
    mode : CounterMode
        Flags that control various options. May contain any combination of non-contradictory
        choices in the "mode parameter values" section below.
    debounce_time : CounterDebounceTime
        Used to bypass the debounce mode, or to set a channel's comparator output to one of 16
        debounce times. Debounce is used to eliminate switch-induced transients typically
        associated with electromechanical devices including relays, proximity switches, and
        encoders.
    debounce_mode : CounterDebounceMode
        Sets the mode of the debounce module to CounterDebounceMode.TRIGGER_BEFORE_STABLE or
        CounterDebounceMode.TRIGGER_AFTER_STABLE.

        CounterDebounceMode.TRIGGER_BEFORE_STABLE: Use this mode when the input signal has groups
        of glitches and each group is to be counted as one. The trigger before stable mode will
        recognize and count the first glitch within a group but reject the subsequent glitches
        within the group if the debounce time is set accordingly. In this case the debounce time
        should be set to encompass one entire group of glitches.

        CounterDebounceMode.TRIGGER_AFTER_STABLE: This mode rejects glitches and only passes state
        transitions after a specified period of stability (the debounce time). This mode is used
        with electromechanical devices like encoders and mechanical switches to reject switch
        bounce and disturbances due to a vibrating encoder that is not otherwise moving. The
        debounce time should be set short enough to accept the desired input pulse but longer than
        the period of the undesired disturbance.
    edge_detection : CounterEdgeDetection
        Selects whether to detect a rising edge or falling edge. Choices are
        CounterEdgeDetection.RISING_EDGE and CounterEdgeDetection.FALLING_EDGE.

        For counter devices that use channel mapping, if a counter is configured for
        CounterEdgeDetection.FALLING_EDGE, calling :func:`.c_in` or :func:`.c_in_32` for that
        counter will result in a ULError with the error code ErrorCode.BADCOUNTERMODE.
    tick_size : CounterTickSize
        Sets the tick size, which is the fundamental unit of time for period, pulsewidth, and
        timing measurements.
    mapped_channel : int
        Used to select the mapped channel. A mapped channel is a counter input channel other than
        CounterNum that can participate with the input signal of the counter defined by CounterNum
        by gating the counter or decrementing the counter.


    **mode parameter values**

    - *TOTALIZE mode*
      Sets the specified counter to totalize mode. This mode may contain any combination of
      non-contradictory choices from the following list of options:

      =========================  ==================================================================
      BIT_32                     Selects a 32-bit counter for asynchronous mode. This parameter
                                 value only affects :func:`.c_in`, :func:`.c_in_32` and
                                 :func:`.c_in_64`. Recommended for use only with :func:`.c_in_32`.
                                 (Using the BIT_32 option with :func:`.c_in` is not very useful,
                                 since the value returned by :func:`.c_in` is only 16 bits. The
                                 effect is that the value returned by :func:`.c_in` rolls over
                                 65,535 times before stopping.)

                                 Refer to board-specific information for the product you are using
                                 for details on how this affects asynchronous reads on a specific
                                 device.
      -------------------------  ------------------------------------------------------------------
      BIT_48                     Selects a 48-bit counter for asynchronous mode. This parameter
                                 value only affects :func:`.c_in`, :func:`.c_in_32` and
                                 :func:`.c_in_64`. Using the BIT_48 option with :func:`.c_in` and
                                 :func:`.c_in_32` is not very useful, since the value returned by
                                 :func:`.c_in` is only 16 bits, and the value returned by
                                 :func:`.c_in_32` is only 32 bits. The effect is that the value
                                 returned by :func:`.c_in` rolls over 4,294,967,295 times before
                                 stopping, and the value returned by :func:`.c_in_32` rolls over
                                 65,535 times before stopping.)

                                 Refer to board-specific information for the product you are using
                                 for details on how this affects asynchronous reads on a specific
                                 device.
      -------------------------  ------------------------------------------------------------------
      CLEAR_ON_READ              The counter is cleared after every read.
      -------------------------  ------------------------------------------------------------------
      COUNT_DOWN_OFF             The counter counts up.
      -------------------------  ------------------------------------------------------------------
      COUNT_DOWN_ON              The counter counts down.
      -------------------------  ------------------------------------------------------------------
      DECREMENT_ON               Allows the mapped channel to decrement the counter. With this
                                 option, the main counter input channel will increment the counter,
                                 and the mapped channel can be used to decrement the counter. By
                                 default, the counter decrement option is set to "off."

                                 This mode is not compatible with :func:`.c_in` or :func:`.c_in_32`.
                                 If a counter is configured for DECREMENT_ON, calling :func:`.c_in`
                                 or :func:`.c_in_32` for that counter will result in a
                                 BADCOUNTERMODE error.
      -------------------------  ------------------------------------------------------------------
      GATE_CLEARS_CTR            The gate input clears the counter. By default, the counter is
                                 cleared when the gate input is high.
      -------------------------  ------------------------------------------------------------------
      GATE_CONTROLS_DIR          The gate input controls the direction of the counter. By default,
                                 the counter increments when the gate pin is high, and decrements
                                 when the gate pin is low.
      -------------------------  ------------------------------------------------------------------
      GATE_TRIG_SRC              The counter starts counting when the gate input goes active. By
                                 default, active is on the rising edge. The gate is re-armed when
                                 the counter is loaded and when :func:`.c_config_scan` is called.
      -------------------------  ------------------------------------------------------------------
      GATING_ON                  Selects gating "on." When "on", the counter is enabled when the
                                 mapped channel or the gate pin that is used to gate the counter is
                                 high. When the mapped channel/gate pin is low, the counter is
                                 disabled but holds the count value. By default, the counter gating
                                 option is set to "off."

                                 For counter devices that use channel mapping, this mode is not
                                 compatible with :func:`.c_in` or :func:`.c_in_32`. If a counter is
                                 configured for GATING_ON, calling :func:`.c_in` or :func:`.c_in_32`
                                 for that counter will result in a BADCOUNTERMODE error.
      -------------------------  ------------------------------------------------------------------
      INVERT_GATE                Inverts the polarity of the gate input.
      -------------------------  ------------------------------------------------------------------
      LATCH_ON_MAP               Causes the count to be latched by the signal on the mapped
                                 channel. By default, the count is latched by the internal "start
                                 of scan" signal, so the count is updated each time it's read.

                                 This mode is not compatible with :func:`.c_in` or :func:`.c_in_32`.
                                 If a counter is configured for LATCH_ON_MAP, calling :func:`.c_in`
                                 or :func:`.c_in_32` for that counter will result in a
                                 BADCOUNTERMODE error.
      -------------------------  ------------------------------------------------------------------
      MODULO_N_ON                Enables Modulo-N counting mode. In Modulo-N mode, an upper limit
                                 is set by loading the max limit register with a maximum count.
                                 When counting up, the counter will roll-over to 0 when the maximum
                                 count is reached, and then continue counting up. Likewise, when
                                 counting down, the counter will roll over to the maximum count
                                 (in the max limit register) whenever the count reaches 0, and then
                                 continue counting down.
      -------------------------  ------------------------------------------------------------------
      NO_RECYCLE_ON              Enables Non-recycle counting mode. In Non-recycle mode, the
                                 counter stops counting whenever a count overflow or underflow
                                 takes place. Counting restarts when a clear or a load operation is
                                 performed on the counter, or the count direction changes.
      -------------------------  ------------------------------------------------------------------
      OUTPUT_INITIAL_STATE_HIGH  Sets the initial state of the counter output pin high.
      -------------------------  ------------------------------------------------------------------
      OUTPUT_INITIAL_STATE_LOW   Sets the initial state of the counter output pin low.
      -------------------------  ------------------------------------------------------------------
      OUTPUT_ON                  Enables the counter output. By default, the counter output goes
                                 high when the counter reaches the value of output register 0, and
                                 low when the counter reaches the value of output register 1. Use
                                 :func:`.c_load`, :func:`.c_load_32`, or :func:`.c_load_64` to set
                                 or read the value of the output registers.
      -------------------------  ------------------------------------------------------------------
      RANGE_LIMIT_ON             Enables Range Limit counting mode. In Range Limit mode, an upper
                                 and lower limit is set, mimicking limit switches in the mechanical
                                 counterpart. Use :func:`.c_load`, :func:`.c_load_32`, or
                                 :func:`.c_load_64` to set the upper and lower limits - set the
                                 upper limit by loading the max limit register, and the lower limit
                                 by loading the min limit register. Note that on some devices the
                                 lower limit is programmable, but on other devices the lower limit
                                 is always 0.

                                 When counting up, the counter rolls over to min limit when the max
                                 limit is reached. When counting down, the counter rolls over to
                                 max limit when the min limit is reached. When counting up with
                                 NO_RECYCLE_ON enabled, the counter freezes whenever the count
                                 reaches the value that was loaded into the max limit register.
                                 When counting down with NO_RECYCLE_ON enabled, the counter freezes
                                 whenever the count reaches the value that was loaded into the min
                                 limit register. Counting resumes if the counter is reset or the
                                 direction changes.
      -------------------------  ------------------------------------------------------------------
      STOP_AT_MAX                The counter will stop at the top of its count. For the
                                 :func:`.c_in_32` function, the top of the count depends on whether
                                 the BIT_32 option is used. If it is, the top of the count is
                                 FFFFFFFF hex. If not, the top of the count is FFFF hex. By default,
                                 the counter counts upward and rolls over on the 32-bit boundary.
      -------------------------  ------------------------------------------------------------------
      UPDOWN_ON                  Enables Up/down counting mode.
      =========================  ==================================================================

    - *ENCODER mode*
      Sets the specified counter to encoder measurement mode. This mode may contain any combination
      of non-contradictory choices from the following list of options:


      ===========================  ================================================================
      ENCODER_MODE_BIT_16          Selects a 16-bit counter for asynchronous mode. This parameter
                                   value only affects :func:`.c_in`, :func:`.c_in_32` and
                                   :func:`.c_in_64`. Recommended for use only with :func:`.c_in`.
      ---------------------------  ----------------------------------------------------------------
      ENCODER_MODE_BIT_32          Selects a 32-bit counter for asynchronous mode. This parameter
                                   value only affects :func:`.c_in`, :func:`.c_in_32` and
                                   :func:`.c_in_64`. Recommended for use only with :func:`.c_in_32`.
                                   (Using the ENCODER_MODE_BIT_32 option with :func:`.c_in` is not
                                   very useful, since the value returned by :func:`.c_in` is only 16
                                   bits. The effect is that the value returned by :func:`.c_in`
                                   rolls over 65,535 times before stopping.)
      ---------------------------  ----------------------------------------------------------------
      ENCODER_MODE_BIT_48          Selects a 48-bit counter for asynchronous mode.This parameter
                                   value only affects :func:`.c_in`, :func:`.c_in_32` and
                                   :func:`.c_in_64`. Recommended for use only with :func:`.c_in_64`.
                                   (Using the ENCODER_MODE_BIT_48 option with :func:`.c_in` and
                                   :func:`.c_in_32` is not very useful, since the value returned by
                                   :func:`.c_in` is only 16 bits, and the value returned by
                                   :func:`.c_in_32` is only 32 bits. The effect is that the value
                                   returned by :func:`.c_in` rolls over 4,294,967,295 times before
                                   stopping, and the value returned by :func:`.c_in_32` rolls over
                                   65,535 times before stopping.)
      ---------------------------  ----------------------------------------------------------------
      ENCODER_MODE_CLEAR_ON_Z_ON   Selects "clear on Z" on. The counter is cleared on the rising
                                   edge of the mapped (Z) channel. By default, the "clear on Z"
                                   option is off, and the counter is not cleared.
      ---------------------------  ----------------------------------------------------------------
      ENCODER_MODE_LATCH_ON_Z      Selects the Encoder Z mapped signal to latch the counter
                                   outputs. This allows the user to know the exact counter value
                                   when an edge is present on another counter.
      ---------------------------  ----------------------------------------------------------------
      ENCODER_MODE_MODULO_N_ON     Enables Modulo-N counting mode. In Modulo-N mode, an upper limit
                                   is set by loading the max limit register with a maximum count.
                                   When counting up, the counter will roll-over to 0 when the
                                   maximum count is reached, and then continue counting up.
                                   Likewise when counting down, the counter will roll over to the
                                   maximum count (in the max limit register) whenever the count
                                   reaches 0, and then continue counting down.
      ---------------------------  ----------------------------------------------------------------
      ENCODER_MODE_NO_RECYCLE_ON   Enables Non-recycle counting mode. In Non-recycle mode, the
                                   counter is disabled whenever a count overflow or underflow takes
                                   place. The counter is re-enabled when a clear or a load
                                   operation is performed on the counter
      ---------------------------  ----------------------------------------------------------------
      ENCODER_MODE_RANGE_LIMIT_ON  Enables Range Limit counting mode. In Range Limit mode, an upper
                                   and lower limit is set, mimicking limit switches in the
                                   mechanical counterpart. The upper limit is set by loading the
                                   max limit register with the :func:`.c_load`, :func:`.c_load_32`
                                   or :func:`.c_load_64` functions. The lower limit is always 0.
                                   When counting up, the counter freezes whenever the count reaches
                                   the value that was loaded into the max limit register.
      ---------------------------  ----------------------------------------------------------------
      ENCODER_MODE_X1               Sets the encoder measurement mode to X1.
      ---------------------------  ----------------------------------------------------------------
      ENCODER_MODE_X2               Sets the encoder measurement mode to X2.
      ---------------------------  ----------------------------------------------------------------
      ENCODER_MODE_X4               Sets the encoder measurement mode to X4.
      ===========================  ================================================================

    - *PERIOD mode*
      Sets the specified counter to period measurement mode. This mode may contain any combination
      of non-contradictory choices from the following list of options:


      =======================  ====================================================================
      PERIOD_MODE_BIT_16       Selects a 16-bit counter for asynchronous mode. This parameter value
                               only affects :func:`.c_in`, :func:`.c_in_32` and :func:`.c_in_64`.
                               Recommended for use only with :func:`.c_in`.
      -----------------------  --------------------------------------------------------------------
      PERIOD_MODE_BIT_32       Selects a 32-bit counter for asynchronous mode. This parameter value
                               only affects :func:`.c_in`, :func:`.c_in_32` and :func:`.c_in_64`.
                               Recommended for use only with :func:`.c_in_32`. (Using the
                               PERIOD_MODE_BIT_32 option with :func:`.c_in` is not very useful,
                               since the value returned by :func:`.c_in` is only 16 bits. The effect
                               is that the value returned by :func:`.c_in` rolls over at 65,535
                               times before stopping.)
      -----------------------  --------------------------------------------------------------------
      PERIOD_MODE_BIT_48       Selects a 48-bit counter for asynchronous mode. This parameter value
                               only affects :func:`.c_in`, :func:`.c_in_32` and :func:`.c_in_64`.
                               Recommended for use only with :func:`.c_in_64`. (Using the
                               PERIOD_MODE_BIT_48 option with :func:`.c_in` and :func:`.c_in_32`
                               is not very useful, since the value returned by :func:`.c_in` is only
                               16 bits, and the value returned by :func:`.c_in_32` is only 32 bits.
                               The effect is that the value returned by :func:`.c_in` rolls over
                               4,294,967,295 times before stopping, and the value returned by
                               :func:`.c_in_32` rolls over 65,535 times before stopping.)
      -----------------------  --------------------------------------------------------------------
      PERIOD_MODE_GATING_ON    Selects gating "on." When "on", the counter is enabled when the
                               mapped channel or the gate pin that is used to gate the counter is
                               high. When the mapped channel/gate pin is low, the counter is
                               disabled but holds the count value. By default, the counter gating
                               option is set to "off."

                               For counter devices that use channel mapping, this mode is not
                               compatible with :func:`.c_in` or :func:`.c_in_32`. If a counter is
                               configured for PERIOD_MODE_GATING_ON, calling :func:`.c_in` or
                               :func:`.c_in_32` for that counter will result in a BADCOUNTERMODE
                               error.
      -----------------------  --------------------------------------------------------------------
      PERIOD_MODE_INVERT_GATE  Inverts the polarity of the gate input.
      -----------------------  --------------------------------------------------------------------
      PERIOD_MODE_X1           The measurement is latched each time one complete period is
                               observed.
      -----------------------  --------------------------------------------------------------------
      PERIOD_MODE_X10          The measurement is latched each time 10 complete periods are
                               observed.
      -----------------------  --------------------------------------------------------------------
      PERIOD_MODE_X100         The measurement is latched each time 100 complete periods are
                               observed.
      -----------------------  --------------------------------------------------------------------
      PERIOD_MODE_X1000        The measurement is latched each time 1000 complete periods are
                               observed.
      =======================  ====================================================================

    - *PULSEWIDTH mode*
      Sets the specified counter to pulsewidth measurement mode. This mode may contain any
      combination of non-contradictory choices from the following list of options:


      ===========================  ================================================================
      PULSEWIDTH_MODE_BIT_16       Selects a 16-bit counter for asynchronous mode. This parameter
                                   value only affects :func:`.c_in`, :func:`.c_in_32` and
                                   :func:`.c_in_64`. Recommended for use only with :func:`.c_in`.
      ---------------------------  ----------------------------------------------------------------
      PULSEWIDTH_MODE_BIT_32       Selects a 32-bit counter for asynchronous mode. This parameter
                                   value only affects :func:`.c_in`, :func:`.c_in_32` and
                                   :func:`.c_in_64`. Recommended for use only with :func:`.c_in_32`.
                                   (Using the PULSEWIDTH_MODE_BIT_32 option with :func:`.c_in` is
                                   not very useful, since the value returned by :func:`.c_in` is
                                   only 16 bits. The effect is that the value returned by
                                   :func:`.c_in` rolls over 65,535 times before stopping.)
      ---------------------------  ----------------------------------------------------------------
      PULSEWIDTH_MODE_BIT_48       Selects a 48-bit counter for asynchronous mode. This parameter
                                   value only affects :func:`.c_in`, :func:`.c_in_32` and
                                   :func:`.c_in_64`. Recommended for use only with :func:`.c_in_64`.
                                   (Using the PULSEWIDTH_MODE_BIT_48 option with :func:`.c_in` and
                                   :func:`.c_in_32` is not very useful, since the value returned by
                                   :func:`.c_in` is only 16 bits, and the value returned by
                                   :func:`.c_in_32` is only 32 bits. The effect is that the value
                                   returned by :func:`.c_in` rolls over 4,294,967,295 times before
                                   stopping, and the value returned by :func:`.c_in_32` rolls over
                                   65,535 times before stopping.)
      ---------------------------  ----------------------------------------------------------------
      PULSEWIDTH_MODE_GATING_ON    Selects gating "on." When "on", the counter is enabled when the
                                   mapped channel or the gate pin that is used to gate the counter
                                   is high. When the mapped channel/gate pin is low, the counter is
                                   disabled but holds the count value. By default, the counter
                                   gating option is set to "off."

                                   For counter devices that use channel mapping, this mode is not
                                   compatible with :func:`.c_in` or :func:`.c_in_32`. If a counter
                                   is configured for PULSEWIDTH_MODE_GATING_ON, calling
                                   :func:`.c_in` or :func:`.c_in_32` for that counter will result in
                                   a BADCOUNTERMODE error.
      ---------------------------  ----------------------------------------------------------------
      PULSEWIDTH_MODE_INVERT_GATE  Inverts the polarity of the gate input.
      ===========================  ================================================================

    - *TIMING mode*
      Sets the specified counter to timing mode. This mode supports the following options:


      =======================  ====================================================================
      TIMING_MODE_BIT_16       Selects a 16-bit counter for asynchronous mode. This parameter value
                               only affects :func:`.c_in`, :func:`.c_in_32` and :func:`.c_in_64`.
                               Recommended for use only with :func:`.c_in`.
      -----------------------  --------------------------------------------------------------------
      TIMING_MODE_BIT_32       Selects a 32-bit counter for asynchronous mode. This parameter value
                               only affects :func:`.c_in`, :func:`.c_in_32` and :func:`.c_in_64`.
                               Recommended for use only with :func:`.c_in_32`. (Using the
                               TIMING_MODE_BIT_32 option with :func:`.c_in` is not very useful,
                               since the value returned by :func:`.c_in` is only 16 bits. The effect
                               is that the value returned by :func:`.c_in` rolls over 65,535 times
                               before stopping.)
      -----------------------  --------------------------------------------------------------------
      TIMING_MODE_BIT_48       Selects a 48-bit counter for asynchronous mode.This parameter value
                               only affects :func:`.c_in`, :func:`.c_in_32` and :func:`.c_in_64`.
                               Recommended for use only with :func:`.c_in_64`. (Using the
                               TIMING_MODE_BIT_48 option with :func:`.c_in` and :func:`.c_in_32` is
                               not very useful, since the value returned by :func:`.c_in` is only 16
                               bits, and the value returned by :func:`.c_in_32` is only 32 bits. The
                               effect is that the value returned by :func:`.c_in` rolls over
                               4,294,967,295 times before stopping, and the value returned by
                               :func:`.c_in_32` rolls over 65,535 times before stopping.)
      -----------------------  --------------------------------------------------------------------
      TIMING_MODE_INVERT_GATE  Inverts the polarity of the gate input.
      =======================  ====================================================================
    """
    _check_err(_cbw.cbCConfigScan(
        board_num, counter_num, mode, debounce_time, debounce_mode,
        edge_detection, tick_size, mapped_channel))


_cbw.cbCIn.argtypes = [c_int, c_int, POINTER(c_ushort)]


def c_in(board_num, counter_num):
    """Reads the current count from a counter channel.

    Parameters
    ----------
    board_num : int
        The number associated with the board when it was installed with InstaCal or created
        with :func:`.create_daq_device`.
    counter_num : int
        The counter to read the current count from. Valid values are in the range of 0 to 20,
        depending on the device and the number of counters available on the device. See
        product-specific information in the Universal Library User's Guide.

    Returns
    -------
    int
        The counter value

    Notes
    -----
    Although the :func:`.c_in`, :func:`.c_in_32`, and :func:`.c_in_64` functions perform the same
    operation, :func:`.c_in_32` is the preferred method to use in most situations.

    The only difference between the three is that :func:`.c_in` returns a 16-bit count value,
    :func:`.c_in_32` returns a 32-bit value, and :func:`.c_in_64` returns a 64-bit value. Both
    :func:`.c_in` and :func:`.c_in_32` can be used, but :func:`.c_in_64` is required whenever you
    need to read count values greater than 32-bits (counts > 4,294,967,295) or the upper (more
    significant) bits will be truncated.

    """
    count = c_ushort()
    _check_err(_cbw.cbCIn(board_num, counter_num, byref(count)))
    return count.value


_cbw.cbCIn32.argtypes = [c_int, c_int, POINTER(c_ulong)]


def c_in_32(board_num, counter_num):
    """Reads the current count from a counter channel.

    Parameters
    ----------
    board_num : int
        The number associated with the board when it was installed with InstaCal or created
        with :func:`.create_daq_device`.
    counter_num : int
        The counter to read the current count from. Valid values are in the range of 0 to 20,
        depending on the device and the number of counters available on the device. See
        product-specific information in the Universal Library User's Guide.

    Returns
    -------
    int
        The counter value

    Notes
    -----
    Although the :func:`.c_in`, :func:`.c_in_32`, and :func:`.c_in_64` functions perform the same
    operation, :func:`.c_in_32` is the preferred method to use in most situations.

    The only difference between the three is that :func:`.c_in` returns a 16-bit count value,
    :func:`.c_in_32` returns a 32-bit value, and :func:`.c_in_64` returns a 64-bit value. Both
    :func:`.c_in` and :func:`.c_in_32` can be used, but :func:`.c_in_64` is required whenever you
    need to read count values greater than 32-bits (counts > 4,294,967,295) or the upper (more
    significant) bits will be truncated.

    """
    count = c_ulong()
    _check_err(_cbw.cbCIn32(board_num, counter_num, byref(count)))
    return count.value


_cbw.cbCIn64.argtypes = [c_int, c_int, POINTER(c_ulonglong)]


def c_in_64(board_num, counter_num):
    """Reads the current count from a counter channel.

    Parameters
    ----------
    board_num : int
        The number associated with the board when it was installed with InstaCal or created
        with :func:`.create_daq_device`.
    counter_num : int
        The counter to read the current count from. Valid values are in the range of 0 to 20,
        depending on the device and the number of counters available on the device. See
        product-specific information in the Universal Library User's Guide.

    Returns
    -------
    int
        The counter value

    Notes
    -----
    Although the :func:`.c_in`, :func:`.c_in_32`, and :func:`.c_in_64` functions perform the same
    operation, :func:`.c_in_32` is the preferred method to use in most situations.

    The only difference between the three is that :func:`.c_in` returns a 16-bit count value,
    :func:`.c_in_32` returns a 32-bit value, and :func:`.c_in_64` returns a 64-bit value. Both
    :func:`.c_in` and :func:`.c_in_32` can be used, but :func:`.c_in_64` is required whenever you
    need to read count values greater than 32-bits (counts > 4,294,967,295) or the upper (more
    significant) bits will be truncated.
    """
    count = c_ulonglong()
    _check_err(_cbw.cbCIn64(board_num, counter_num, byref(count)))
    return count.value


_cbw.cbCInScan.argtypes = [c_int, c_int, c_int, c_long, POINTER(c_long),
                           HGLOBAL, c_ulong]


def c_in_scan(board_num, first_ctr, last_ctr, count, rate, memhandle, options):
    """Scans a range of counter channels, and stores the samples in an array.

    Parameters
    ----------
    board_num : int
        The number associated with the board when it was installed with InstaCal or created
        with :func:`.create_daq_device`.
    first_ctr : int
        First counter channel of the scan. This parameter is zero-based, so the first counter
        number is "0".
    last_ctr : int
        Last counter channel of the scan. This parameter is zero-based, so the first counter number
        is "0".

        The maximum allowable channel for both first_ctr and last_ctr depends on how many scan
        counters are available on the Measurement Computing device in use.
    count : int
        The total number of counter samples to collect. If more than one channel is being sampled
        then the number of samples collected per channel is equal to
        count / (last_ctr - first_ctr + 1).
    rate : int
        The rate at which samples are taken in samples per second. The actual sampling rate in some
        cases will vary a small amount from the requested rate. The actual rate is returned.
    memhandle : int
        The handle for the Windows buffer to store data. This buffer must have been previously
        allocated with the :func:`.win_buf_alloc_32` function.
    options : ScanOptions
        Flags that control various options. May contain any combination of non-contradictory
        choices in the "options parameter values" table below.


    .. table:: **options parameter values**

        ===========  ==============================================================================
        BACKGROUND   When the BACKGROUND option is used, control returns immediately to the next
                     line in your program and the data collection from the counters into the buffer
                     continues in the background. If the BACKGROUND option is not used, the
                     :func:`.c_inScan` function does not return to your program until all of the
                     requested data has been collected and returned to the buffer.

                     Use :func:`.get_status` with CTRFUNCTION to check on the status of the
                     background operation. Use :func:`.stop_background` with CTRFUNCTION to
                     terminate the background process before it has completed. Execute
                     :func:`.stop_background` after normal termination of all background functions
                     in order to clear variables and flags.
        -----------  ------------------------------------------------------------------------------
        BLOCKIO      A/D transfers are handled in blocks (by REP-INSW for example). BLOCKIO is not
                     recommended for slow acquisition rates. If the rate of acquisition is very
                     slow (for example less than 200 Hz) BLOCKIO may not be the best transfer mode,
                     as the operation status is not available until one packet of data is collected
                     (typically 512 samples). For example, when acquiring 100 samples at 100 Hz
                     using BLOCKIO, the operation will not complete until 5.12 seconds has elapsed.
        -----------  ------------------------------------------------------------------------------
        CONTINUOUS   This option puts the function in an endless loop. Once it collects the
                     required number of samples, it resets to the start of the buffer and begins
                     again. The only way to stop this operation is by using
                     :func:`.stop_background` with CTRFUNCTION. Normally, you should use this
                     option with BACKGROUND so that your program regains control.
        -----------  ------------------------------------------------------------------------------
        CTR16BIT     Sets the counter resolution to 16-bits. When using devices that return data in
                     a 16-bit format, create the buffer using :func:`.win_buf_alloc`.
        -----------  ------------------------------------------------------------------------------
        CTR32BIT     Sets the counter resolution to 32-bits. When using devices that return data in
                     a 32-bit format, create the buffer using :func:`.win_buf_alloc32`.
        -----------  ------------------------------------------------------------------------------
        CTR48BIT     Sets the counter resolution to 48-bits. When using devices that return data in
                     a 64-bit format, create the buffer using :func:`.win_buf_alloc64`.
        -----------  ------------------------------------------------------------------------------
        CTR64BIT     Sets the counter resolution to 64-bits. When using devices that return data in
                     a 64-bit format, create the buffer using :func:`.win_buf_alloc64`.
        -----------  ------------------------------------------------------------------------------
        EXTCLOCK     If this option is specified, conversions will be controlled by the signal on
                     the external clock input rather than by the internal pacer clock. Each
                     conversion will be triggered on the appropriate edge of the clock input signal
                     (refer to board-specific information in the UL User's Guide). When this option
                     is used the rate parameter is ignored. The sampling rate is dependent on the
                     clock signal. Options for the board will default to a transfer mode that will
                     allow the maximum conversion rate to be attained unless otherwise specified.
        -----------  ------------------------------------------------------------------------------
        EXTTRIGGER   If this option is specified, sampling does not begin until the trigger
                     condition is met. You can set the trigger condition to rising edge, falling
                     edge, or the level of the digital trigger input with the :func:`.set_trigger`
                     function. Refer to board-specific information in the UL User's Guide.
        -----------  ------------------------------------------------------------------------------
        HIGHRESRATE  Acquires data at a high resolution rate. When specified, the rate at which
                     samples are acquired is in "samples per 1000 seconds per channel". When this
                     option is not specified, the rate at which samples are acquired is in "samples
                     per second per channel" (refer to the rate parameter above).
        -----------  ------------------------------------------------------------------------------
        NOCLEAR      Disables the clearing of counters when the scan starts.
        -----------  ------------------------------------------------------------------------------
        RETRIGMODE   Re-arms the trigger after a trigger event is performed. With this mode, the
                     scan begins when a trigger event occurs. When the scan completes, the trigger
                     is re-armed to acquire the next the batch of data. You can specify the number
                     of samples in the scan for each trigger event (described below). The
                     RETRIGMODE option can be used with the CONTINUOUS option to continue arming
                     the trigger until :func:`.stop_background` is called.

                     You can specify the number of samples to acquire with each trigger event. This
                     is the trigger count (retrigCount). Use the :func:`.set_config` config_item
                     option BICTRTRIGCOUNT to set the trigger count. If you specify a trigger count
                     that is either zero or greater than the value of the :func:`.c_inScan` count
                     parameter, the trigger count is set to the value of count.

                     Specify the CONTINUOUS option with the trigger count set to zero to fill the
                     buffer with count samples, re-arm the trigger, and refill the buffer upon the
                     next trigger.
        -----------  ------------------------------------------------------------------------------
        SINGLEIO     A/D data is transferred to memory one sample at a time. Rates attainable using
                     SINGLEIO are PC-dependent and generally less than 4 kHz.
        ===========  ==============================================================================

    Returns
    -------
    int
        The actual rate set, which may be different from the user specified rate due to pacer
        limitations.
    """
    rate_internal = c_long(rate)
    _check_err(_cbw.cbCInScan(
        board_num, first_ctr, last_ctr, count, byref(rate_internal),
        memhandle, options))
    return rate_internal.value


_cbw.cbCLoad.argtypes = [c_int, c_int, c_uint]


def c_load(board_num, reg_num, load_value):
    """Loads a value into the specified counter register. For some devices, the value is directly
    loaded into the count register. For other devices, the value is first loaded into the load or
    hold register. Once the counter is enabled, the count is loaded from the appropriate register,
    generally on the first valid pulse.

    Parameters
    ----------
    board_num : int
        The number associated with the board when it was installed with InstaCal or created
        with and :func:`.create_daq_device`.
    reg_num : int
        The register to load the count to. Set it to one of the constants in the "reg_num parameter
        values" section below.
    load_value : int
        The value to be loaded. Must be between 0 and 2**resolution - 1 of the counter. For
        example, a 16-bit counter is 2**16 - 1, or 65,535.


    .. table:: **reg_num parameter values**

        ================================  =========================================================
        LOADREG0 to LOADREG20             Load registers 0 through 20. This may span several chips.
        --------------------------------  ---------------------------------------------------------
        MINLIMITREG0 to MINLIMITREG7      Min limit register. (USB-CTR Series and USB-QUAD08 only)
        --------------------------------  ---------------------------------------------------------
        MAXLIMITREG0 to MAXLIMITREG7      Max limit register. (USB-CTR Series and USB-QUAD08 only)
        --------------------------------  ---------------------------------------------------------
        OUTPUTVAL0REG0 to OUTPUTVAL0REG7  Output register 0. (USB-CTR Series only)
        --------------------------------  ---------------------------------------------------------
        OUTPUTVAL1REG0 to OUTPUTVAL1REG7  Output register 1. (USB-CTR Series only)
        ================================  =========================================================

    Notes
    -----
    - You cannot load a count-down-only counter with less than 2.

    - Counter Types: There are several counter types supported. Refer to the counter chip's data
      sheet for the registers that are available.

    - :func:`.c_load` vs :func:`.c_load_32`

      Although the :func:`.c_load` and :func:`.c_load_32` functions perform the same operation,
      :func:`.c_load_32` is the preferred function to use.

      The only difference between the two is that :func:`.c_load` loads a 16-bit count value, and
      :func:`.c_load_32` loads a 32-bit value. The only time you need to use :func:`.c_load_32` is
      to load counts that are larger than 32-bits (counts > 4,294,967,295).
    """
    _check_err(_cbw.cbCLoad(board_num, reg_num, load_value))


_cbw.cbCLoad32.argtypes = [c_int, c_int, c_ulong]


def c_load_32(board_num, reg_num, load_value):
    """Loads a value into the specified counter register. For some devices, the value is directly
    loaded into the count register. For other devices, the value is first loaded into the load or
    hold register. Once the counter is enabled, the count is loaded from the appropriate register,
    generally on the first valid pulse.

    Parameters
    ----------
    board_num : int
        The number associated with the board when it was installed with InstaCal or created
        with :func:`.create_daq_device`.
    reg_num : int
        The register to load the count to. Set it to one of the constants in the "reg_num parameter
        values" section below.
    load_value : int
        The value to be loaded. Must be between 0 and 2**resolution - 1 of the counter. For
        example, a 16-bit counter is 2**16 - 1, or 65,535.


    .. table:: **reg_num parameter values**

        ================================  =========================================================
        LOADREG0 to LOADREG20             Load registers 0 through 20. This may span several chips.
        --------------------------------  ---------------------------------------------------------
        MINLIMITREG0 to MINLIMITREG7      Min limit register. (USB-CTR Series and USB-QUAD08 only)
        --------------------------------  ---------------------------------------------------------
        MAXLIMITREG0 to MAXLIMITREG7      Max limit register. (USB-CTR Series and USB-QUAD08 only)
        --------------------------------  ---------------------------------------------------------
        OUTPUTVAL0REG0 to OUTPUTVAL0REG7  Output register 0. (USB-CTR Series only)
        --------------------------------  ---------------------------------------------------------
        OUTPUTVAL1REG0 to OUTPUTVAL1REG7  Output register 1. (USB-CTR Series only)
        ================================  =========================================================

    Notes
    -----
    - You cannot load a count-down-only counter with less than 2.

    - Counter Types: There are several counter types supported. Refer to the counter chip's data
      sheet for the registers that are available.

    - :func:`.c_load` vs :func:`.c_load_32`

      Although the :func:`.c_load` and :func:`.c_load_32` functions perform the same operation,
      :func:`.c_load_32` is the preferred function to use.

      The only difference between the two is that :func:`.c_load` loads a 16-bit count value, and
      :func:`.c_load_32` loads a 32-bit value. The only time you need to use :func:`.c_load_32` is
      to load counts that are larger than 32-bits (counts > 4,294,967,295).
    """
    _check_err(_cbw.cbCLoad32(board_num, reg_num, load_value))


_cbw.cbCLoad64.argtypes = [c_int, c_int, c_ulonglong]


def c_load_64(board_num, reg_num, load_value):
    """Loads a value into the specified counter register. For some devices, the value is directly
    loaded into the count register. For other devices, the value is first loaded into the load or
    hold register. Once the counter is enabled, the count is loaded from the appropriate register,
    generally on the first valid pulse.

    Parameters
    ----------
    board_num : int
        The number associated with the board when it was installed with InstaCal or created
        with :func:`.create_daq_device`.
    reg_num : int
        The register to load the count to. Set it to one of the constants in the "reg_num parameter
        values" section below.
    load_value : int
        The value to be loaded. Must be between 0 and 2**resolution - 1 of the counter. For
        example, a 16-bit counter is 2**16 - 1, or 65,535.


    .. table:: **reg_num parameter values**

        ================================  =========================================================
        LOADREG0 to LOADREG20             Load registers 0 through 20. This may span several chips.
        --------------------------------  ---------------------------------------------------------
        MINLIMITREG0 to MINLIMITREG7      Min limit register. (USB-CTR Series and USB-QUAD08 only)
        --------------------------------  ---------------------------------------------------------
        MAXLIMITREG0 to MAXLIMITREG7      Max limit register. (USB-CTR Series and USB-QUAD08 only)
        --------------------------------  ---------------------------------------------------------
        OUTPUTVAL0REG0 to OUTPUTVAL0REG7  Output register 0. (USB-CTR Series only)
        --------------------------------  ---------------------------------------------------------
        OUTPUTVAL1REG0 to OUTPUTVAL1REG7  Output register 1. (USB-CTR Series only)
        ================================  =========================================================

    Notes
    -----
    - You cannot load a count-down-only counter with less than 2.

    - Counter Types: There are several counter types supported. Refer to the counter chip's data
      sheet for the registers that are available.

    - :func:`.c_load` vs :func:`.c_load_32`

      Although the :func:`.c_load` and :func:`.c_load_32` functions perform the same operation,
      :func:`.c_load_32` is the preferred function to use.

      The only difference between the two is that :func:`.c_load` loads a 16-bit count value, and
      :func:`.c_load_32` loads a 32-bit value. The only time you need to use :func:`.c_load_32` is
      to load counts that are larger than 32-bits (counts > 4,294,967,295).
    """
    _check_err(_cbw.cbCLoad64(board_num, reg_num, load_value))


_cbw.cbCreateDaqDevice.argtypes = [c_int, DaqDeviceDescriptor]


def create_daq_device(board_num, descriptor):
    """Creates a device object within the Universal Library for the DAQ device specified by the
    descriptor, and assigns the specified board number to the DAQ device.

    :func:`.create_daq_device` fails if the specified DAQ device has already been created. The UL
    automatically adds any DAQ device stored in the cb.cfg file by InstaCal. If you want runtime
    control over device creation, invoke the :func:`.ignore_instacal` function first. Refer to
    :func:`.ignore_instacal` for more information.

    Parameters
    ----------
    board_num : int
        The number you wish to associate with the board when created with
        :func:`.create_daq_device`. board_num may be 0 to 99, and must not be associated with any
        other installed device.
    descriptor : DaqDeviceDescriptor
        The descriptor of the DAQ device
    """
    _check_err(_cbw.cbCreateDaqDevice(board_num, descriptor))


DaqInScanResult = collections.namedtuple(
    "DaqInScanResult", "actual_rate actual_pretrig_count actual_total_count")
_cbw.cbDaqInScan.argtypes = [c_int, POINTER(c_short), POINTER(c_short), POINTER(c_short),
                             c_int, POINTER(c_long), POINTER(
                                 c_long), POINTER(c_long),
                             HGLOBAL, c_int]


def daq_in_scan(board_num, chan_list, chan_type_list, gain_list, chan_count,
                rate, pretrig_count, total_count, memhandle, options):
    """Scans analog, digital, counter, and temperature input channels synchronously, and stores the
    samples in an array. This function only works with boards that support synchronous input.

    Parameters
    ----------
    board_num : int
        The number associated with the board when it was installed with InstaCal or created
        with :func:`.create_daq_device`.
    chan_list : list of int or DigitalPortType
        List containing channel values. Valid channel values are analog input channels, digital
        ports, counter input channels, and temperature input channels of the device.
    chan_type_list : list of ChannelType
        List containing channel types. Each element of this list defines the type of the
        corresponding element in the chan_list. Set to one of the constants in the "chan_type_list
        parameter values" section below.
    gain_list : list of ULRange
        List containing A/D range codes. If the corresponding element in the chan_list is not an
        analog input channel, the range code for this channel is ignored.
    chan_count : int
        Number of elements in each of the three lists - chan_list, chan_type_list, and gain_list.
    rate : int
        The sample rate at which samples are acquired, in samples per second per channel.

        The actual sampling rate in some cases will vary a small amount from the requested rate.
        The actual rate is returned.
    pretrig_count : int
        Sets the number of pre-trigger samples to collect. Specifies the number of samples to
        collect before the trigger occurs. This function won't run in pre-trigger mode if
        pre_trig_count is set to zero. pre_trig_count is ignored if the EXTTRIGGER option is not
        specified.

        The actual pre-trigger count set will be the second value returned, which may be
        different from the requested pre-trigger count, because pre-trigger count must be a
        multiple of chan_count.

        pre_trig_count must be evenly divisible by the number of channels being scanned
        (chan_count). If it is not, this function adjusts the number (up) to the next valid value,
        and returns that value as the second return value.
    total_count : int
        Total number of samples to collect. Specifies the total number of samples to collect and
        store in the buffer. total_count must be greater than pretrig_count.

        The actual total_count set will will be the third value returned, which may be different
        from the requested total count because total count must be a multiple of chan_count.

        total_count must be evenly divisible by the number of channels being scanned (chan_count).
        If it is not, this function adjusts the number (down) to the next valid value, and returns
        that value as the third return value.
    memhandle : int
        Handle for the Windows buffer to store data. This buffer must have been previously
        allocated. For 16-bit data, create the buffer with :func:`.win_buf_alloc`. For data that is
        > 16-bit and <= 32-bit, use :func:`.win_buf_alloc_32`. For data that is > 32-bit and <=
        64-bit, use :func:`.win_buf_alloc_64`. When using scaled data, use
        :func:`.scaled_win_buf_alloc`.
    options : ScanOptions
        Flags that control various options. May contain any combination of non-contradictory
        choices in the "options parameter values" table below.


    .. table:: **chan_type_list parameter values**

        ===============  ==========================================================================
        ANALOG           Analog input channel
        ---------------  --------------------------------------------------------------------------
        DIGITAL8         8-bit digital input port
        ---------------  --------------------------------------------------------------------------
        DIGITAL16        16-bit digital input port. (FIRSTPORTA only)
        ---------------  --------------------------------------------------------------------------
        PADZERO          Placeholder channel; fills the corresponding data elements with zero
        ---------------  --------------------------------------------------------------------------
        CJC              CJC channel
        ---------------  --------------------------------------------------------------------------
        CTR16            16-bit counter
        ---------------  --------------------------------------------------------------------------
        CTR32LOW         Lower 16-bits of a 32-bit counter
        ---------------  --------------------------------------------------------------------------
        CTR32HIGH        Upper 16-bits of a 32-bit counter
        ---------------  --------------------------------------------------------------------------
        CTRBANK0         Bank 0 of a counter
        ---------------  --------------------------------------------------------------------------
        CTRBANK1         Bank 1 of a counter
        ---------------  --------------------------------------------------------------------------
        CTRBANK2         Bank 2 of a counter
        ---------------  --------------------------------------------------------------------------
        CTRBANK3         Bank 3 of a counter
        ---------------  --------------------------------------------------------------------------
        SETPOINTSTATUS   The setpoint status register. This is a bit field indicating the state of
                         each of the setpoints. A "1" indicates that the setpoint criteria has been
                         met.
        ---------------  --------------------------------------------------------------------------          
        TC               Thermocouple channel

                         The :func:`.get_tc_values` function can be used to convert raw
                         thermocouple data to data on a temperature scale (CELSIUS, FAHRENHEIT, or
                         KELVIN). Note: If at least one TC channel is listed in the channel array,
                         and averaging is enabled for that channel, the averaging will be applied
                         to all of the channels listed in the channel array.
        ---------------  --------------------------------------------------------------------------
        SETPOINT_ENABLE  Enables a setpoint. When this option is specified, it must be OR'ed with
                         the chan_type_list parameter values. 

                         You set the setpoint criteria with the :func:`.daq_set_setpoints`
                         function. The number of channels set with the SETPOINT_ENABLE flag must
                         match the number of setpoints set by the :func:`.daq_set_setpoints`
                         function's setpoint_count parameter. 
        ===============  ==========================================================================


    .. table:: **options parameter values**

        ===========  ==============================================================================
        BACKGROUND   When the BACKGROUND option is used, control returns immediately to the next
                     line in your program, and the data collection into the buffer continues in the
                     background. If the BACKGROUND option is not used, the :func:`.daq_in_scan`
                     function does not return control to your program until all of the requested 
                     data has been collected and returned to the buffer. 

                     Use :func:`.get_status` with DAQIFUNCTION to check on the status of the 
                     background operation. Use :func:`.stop_background` with DAQIFUNCTION to 
                     terminate the background process before it has completed. Execute 
                     :func:`.stop_background` after normal termination of all background 
                     functions, in order to clear variables and flags. 
        -----------  ------------------------------------------------------------------------------
        BLOCKIO      A/D transfers are handled in blocks (by REP-INSW for example). BLOCKIO is not 
                     recommended for slow acquisition rates. If the rate of acquisition is very 
                     slow (for example less than 200 Hz) BLOCKIO is probably not the best choice 
                     for transfer mode. The reason for this is that status for the operation is not 
                     available until one packet of data has been collected (typically 512 samples). 
                     The implication is that if acquiring 100 samples at 100 Hz using BLOCKIO, the 
                     operation will not complete until 5.12 seconds has elapsed.
        -----------  ------------------------------------------------------------------------------
        CONTINUOUS   This option puts the function in an endless loop. Once it collects the 
                     required number of samples, it resets to the start of the buffer and begins 
                     again. The only way to stop this operation is by using 
                     :func:`.stop_background` with DAQIFUNCTION. Normally this option should be 
                     used in combination with BACKGROUND so that your program will regain control.
        -----------  ------------------------------------------------------------------------------
        EXTCLOCK     Conversions will be controlled by the signal on the external clock input 
                     rather than by the internal pacer clock. Each conversion will be triggered on 
                     the appropriate edge of the clock input signal. When this option is used, the 
                     rate parameter is ignored. The sampling rate is dependent on the clock signal. 
                     Options for the board will default to a transfer mode that will allow the 
                     maximum conversion rate to be attained unless otherwise specified. 
        -----------  ------------------------------------------------------------------------------
        EXTTRIGGER   Sampling will not begin until the trigger condition is met (refer to the 
                     :func:`.daq_set_trigger` function). 
        -----------  ------------------------------------------------------------------------------
        HIGHRESRATE  Acquires data at a high resolution rate. When specified, the rate at 
                     which samples are acquired is in "samples per 1000 seconds per channel". 
                     When this option is not specified, the rate at which samples are 
                     acquired is in "samples per second per channel" (refer to the rate 
                     parameter above). 
        -----------  ------------------------------------------------------------------------------
        NOCLEAR      Disables the clearing of counters when the scan starts. 
        -----------  ------------------------------------------------------------------------------
        SINGLEIO     A/D transfers to memory are initiated by an interrupt. One interrupt per 
                     conversion. Rates attainable using SINGLEIO are PC-dependent and 
                     generally less than 10 kHz. 
        ===========  ==============================================================================

    Returns
    -------
    actual_rate : int
        The actual rate set, which may be different from the user specified rate due to pacer
        limitations.
    actual_pretrig_count : int
        The actual pretrig count (see pretrig_count parameter)
    actual_total_count : int
        The actual total count (see total_count parameter)
    """
    rate_internal = c_long(rate)
    pretrig_count_internal = c_long(pretrig_count)
    total_count_internal = c_long(total_count)
    _check_err(_cbw.cbDaqInScan(
        board_num, _to_ctypes_array(chan_list, c_short),
        _to_ctypes_array(chan_type_list, c_short),
        _to_ctypes_array(gain_list, c_short), chan_count, byref(rate_internal),
        byref(pretrig_count_internal), byref(total_count_internal),
        memhandle, options))
    return DaqInScanResult(
        rate_internal.value, pretrig_count_internal.value, total_count_internal.value)


_cbw.cbDaqOutScan.argtypes = [c_int, POINTER(c_short), POINTER(c_short),
                              POINTER(c_short), c_int, POINTER(c_long), c_long, HGLOBAL, c_int]


def daq_out_scan(board_num, chan_list, chan_type_list, gain_list, chan_count,
                 rate, count, memhandle, options):
    """Outputs values synchronously to analog output channels and digital output ports. This
    function only works with boards that support synchronous output.

    Parameters
    ----------
    board_num : int
        The number associated with the board when it was installed with InstaCal or created
        with :func:`.create_daq_device`.
    chan_list : list of int or DigitalPortType
        list containing channel values. Valid channel values are analog output channels and digital
        ports.
    chan_type_list : list of ChannelType
        Array containing channel types. Each element of this array defines the type of the
        corresponding element in the chan_list. Set to one of the constants in the "chan_type_list
        parameter values" section below.
    gain_list : list of ULRange
        List containing D/A range codes. If the corresponding element in the chan_list is not an
        analog input channel, the range code for this channel is ignored.
    chan_count : int
        Number of elements in each of the three lists - chan_list, chan_type_list, and gain_list.
    rate : int
        Sample rate in scans per second. The actual sampling rate in some cases will vary a small
        amount from the requested rate. The actual rate is returned.
    count : int
        Sets the total number of values to output
    memhandle : int
        Handle for the Windows buffer from which data is output. This buffer must have been
        previously allocated and data values loaded.

        For 16-bit data, create the buffer with :func:`.win_buf_alloc`. For data that is > 16-bit
        and <= 32-bit, use :func:`.win_buf_alloc_32`. For data that is > 32-bit and <= 64-bit, use
        :func:`.win_buf_alloc_64`. When using scaled data, use :func:`.scaled_win_buf_alloc`. You
        can load the data values with :func:`.win_array_to_buf` or :func:`.scaled_win_array_to_buf`
        (for scaled data).
    options : ScanOptions
        Flags that control various options. May contain any combination of non-contradictory
        choices in the "options parameter values" table below.


    .. table:: **chan_type_list parameter values**

        =========  ================================================================================
        ANALOG     Analog output channel. 
        ---------  --------------------------------------------------------------------------------
        DIGITAL16  16-bit digital output port. (FIRSTPORTA only) 
        =========  ================================================================================


    .. table:: **options parameter values**

        =============  ============================================================================
        ADCCLOCK       When this option is used, the data output operation will be paced by the ADC 
                       clock. 
        -------------  ----------------------------------------------------------------------------
        ADCCLOCKTRIG   If this option is used, the data output operation will be triggered upon the 
                       start of the ADC clock. 
        -------------  ----------------------------------------------------------------------------
        BACKGROUND     When this option is used, the output operations will begin running in 
                       the background and control will immediately return to the next line of 
                       your program. Use :func:`.get_status` with the DAQOFUNCTION option to 
                       check the status of background operation. Use the 
                       :func:`.stop_background` function with the DAQOFUNCTION option to 
                       terminate background operations before they are completed. Execute 
                       :func:`.stop_background` with DAQOFUNCTION after normal termination of 
                       all background functions in order to clear variables and flags. 
        -------------  ----------------------------------------------------------------------------
        CONTINUOUS     This option puts the function in an endless loop. Once it outputs the 
                       specified number (count) of output values, it resets to the start of the 
                       buffer and begins again. The only way to stop this operation is by 
                       calling :func:`.stop_background` with DAQOFUNCTION. This option should 
                       only be used in combination with BACKGROUND so that your program can 
                       regain control. 
        -------------  ----------------------------------------------------------------------------
        EXTCLOCK       If this option is used, conversions will be paced by the signal on the 
                       external clock input rather than by the internal pacer clock. Each 
                       conversion will be triggered on the appropriate edge of the clock input 
                       signal. 

                       When this option is used, the rate parameter is ignored. The sampling 
                       rate is dependent on the clock signal. Options for the board will 
                       default to transfer types that allow the maximum conversion rate to be 
                       attained unless otherwise specified. 
        -------------  ----------------------------------------------------------------------------
        NONSTREAMEDIO  This option allows non-streamed data output to be generated to a 
                       specified output channel.

                       In this mode, the aggregate size of data output buffer must be less than 
                       or equal to the size of the internal data output FIFO on the Measurement 
                       Computing device. This allows the data output buffer to be loaded into 
                       the device's internal output FIFO. 

                       Once the sample updates are transferred (or downloaded) to the device, 
                       the device is responsible for outputting the data. While the size is 
                       limited, and the output buffer cannot be changed once the output is 
                       started, this mode has the advantage being able to continue data output 
                       without having to periodically feed output data through the program to 
                       the device. 
        =============  ============================================================================

    Returns
    -------
    int
        The actual rate set, which may be different from the user specified rate due to pacer
        limitations.
    """
    rate_internal = c_long(rate)
    _check_err(_cbw.cbDaqOutScan(
        board_num, _to_ctypes_array(chan_list, c_short),
        _to_ctypes_array(chan_type_list, c_short),
        _to_ctypes_array(gain_list, c_short), chan_count, byref(rate_internal),
        count, memhandle, options))
    return rate_internal.value


_cbw.cbDaqSetSetpoints.argtypes = [c_int, POINTER(c_float), POINTER(c_float),
                                   POINTER(c_float), POINTER(
                                       c_int), POINTER(c_int),
                                   POINTER(c_float), POINTER(
                                       c_float), POINTER(c_float),
                                   POINTER(c_float), c_int]


def daq_set_setpoints(board_num, limit_a_list, limit_b_list, setpoint_flags_list,
                      setpoint_output_list, output_1_list, output_2_list,
                      output_mask_1_list, output_mask_2_list, setpoint_count):
    """Outputs values synchronously to analog output channels and digital output ports. This
    function only works with boards that support synchronous output.

    Parameters
    ----------
    board_num : int
        The number associated with the board when it was installed with InstaCal or created
        with :func:`.create_daq_device`.
    limit_a_list : list of int
        list containing the limit A values for the input channels used for the setpoint. Limit A
        specifies a value used to determine if the setpoint criteria are met.
    limit_b_list : list of int
        list containing the limit B values for the input channels used for the setpoint. Limit B
        specifies a value used to determine if the setpoint criteria are met.
    setpoint_flags_list : list of SetpointFlag
        list containing the setpoint flags. Set to one of the constants in the "setpoint_flags_list
        parameter values" section below.
    setpoint_output_list : list of SetpointOutput
        list containing output sources. Set to one of the constants in the "setpoint_output_list
        parameter values" section below.
    output_1_list : list of int
        list containing the values for the output channels used for the setpoint.
    output_2_list : list of int
        list containing the values for the output channels used for the setpoint.
    output_mask_1_list : list of int
        list containing the output masks for output value 1 (for FIRSTPORTC only).
    output_mask_2_list : list of int
        list containing the output masks for output value 2 (for FIRSTPORTC only).
    setpoint_count : int
        Number of setpoints to configure (0 to 16). Set to 0 to disable the setpoints.


    .. table:: **setpoint_flags_list parameter values**

        =====================  ====================================================================
        Flag                   Description
        =====================  ====================================================================
        EQUAL_LIMITA           Setpoint criteria: The input channel = limit A.
        ---------------------  --------------------------------------------------------------------
        LESSTHAN_LIMITA        Setpoint criteria: The input channel < limit A.
        ---------------------  --------------------------------------------------------------------
        GREATERTHAN_LIMITB     Setpoint criteria: The input channel >limit B. 
        ---------------------  --------------------------------------------------------------------
        INSIDE_LIMITS          Setpoint criteria: The input channel > limit A and < limit B. 
        ---------------------  --------------------------------------------------------------------
        OUTSIDE_LIMITS         Setpoint criteria: The input channel < limit A and > limit B. 
        ---------------------  --------------------------------------------------------------------
        HYSTERESIS             Setpoint criteria: If the input channel > limit A then output value
                               1.

                               If the input channel < limit B then output value 2.
        ---------------------  --------------------------------------------------------------------
        UPDATEON_TRUEONLY      If the criteria is met then output value 1. 
        UPDATEON_TRUEANDFALSE  If the criteria is met then output value 1, else output value 2. 
        =====================  ====================================================================


    .. table:: **setpoint_output_list parameter values**

        =============  =============================================================================
        Output source  Description
        =============  =============================================================================
        NONE           Perform no outputs.
        -------------  -----------------------------------------------------------------------------
        FIRSTPORTC     Output to FIRSTPORTC when the criteria is met.
        -------------  -----------------------------------------------------------------------------
        DIGITALPORT    Output to digital port when the criteria is met.
        -------------  -----------------------------------------------------------------------------
        DAC0           Output to DAC0 when the criteria is met. You must have a device with DAC0.
        -------------  -----------------------------------------------------------------------------
        DAC1           Output to DAC1 when the criteria is met. You must have a device with DAC1.
        -------------  -----------------------------------------------------------------------------
        DAC2           Output to DAC2 when the criteria is met. You must have a device with DAC2.
        -------------  -----------------------------------------------------------------------------
        DAC3           Output to DAC3 when the criteria is met. You must have a device with DAC3.
        -------------  -----------------------------------------------------------------------------
        TMR0           Output to timer 0 when the criteria is met.
        -------------  -----------------------------------------------------------------------------
        TMR1           Output to timer 1 when the criteria is met.
        =============  ============================================================================= 
    """
    _check_err(_cbw.cbDaqSetSetpoints(
        board_num, _to_ctypes_array(limit_a_list, c_float),
        _to_ctypes_array(limit_b_list, c_float), None,
        _to_ctypes_array(setpoint_flags_list, c_int),
        _to_ctypes_array(setpoint_output_list, c_int),
        _to_ctypes_array(output_1_list, c_float),
        _to_ctypes_array(output_2_list, c_float),
        _to_ctypes_array(output_mask_1_list, c_float),
        _to_ctypes_array(output_mask_2_list, c_float),
        setpoint_count))


_cbw.cbDaqSetTrigger.argtypes = [c_int, c_int, c_int, c_int, c_int, c_int, c_float,
                                 c_float, c_int]


def daq_set_trigger(board_num, trig_source, trig_sense, trig_chan, chan_type,
                    gain, level, variance, trig_event):
    """Selects the trigger source and sets up its parameters. This trigger is used to initiate or
    terminate an acquisition using the :func:`.daq_in_scan` function if the EXTTRIGGER option is
    selected. This function only works with boards that support synchronous output.

    Parameters
    ----------
    board_num : int
        The number associated with the board when it was installed with InstaCal or created
        with :func:`.create_daq_device`.
    trig_source : TriggerSource
        Specifies the type of triggering based on the external trigger source. Set to one of the
        constants specified in "trig_source parameter values" section below.
    trig_sense : TriggerSensitivity
        Specifies the trigger sensitivity. The trigger sensitivity normally defines the way in
        which a trigger event is detected based upon the characteristics of the trigger input
        signal. However, it often defines the way in which the trigger input signal(s) should be
        compared to the trigger level parameter value. Set to of the constants specified in
        "trig_sense parameter values" section below.
    trig_chan : int or DigitalPortType
        Specifies the trigger channel. The trigger channel must be a configured channel in the
        channel array (refer to :func:`.daq_in_scan`).
    chan_type : ChannelType
        Specifies the channel type and should match the channel type setting for the trigger
        channel configured using the :func:`.daq_in_scan` function.
    gain : ULRange
        Specifies the trigger channel gain code. If the device has programmable gain, this
        parameter should match the gain code setting when the channel is configured using the
        :func:`.daq_in_scan` function. The Gain parameter is ignored if trig_chan is not an analog
        channel.
    level : float
        The level at or around which the trigger event should be detected, in engineering units.

        This option is used for trigger types that depend on an input channel comparison to detect
        the start trigger or stop trigger event.

        The actual level at which the trigger event is detected depends upon trigger sensing and
        variability. Refer to the "Trigger Levels" section below for more information.
    variance : float
        The amount that the trigger event can vary from the level parameter, in engineering units.

        While the trig_sense parameter indicates the direction of the input signal relative to the
        Level parameter, the variance parameter specifies the degree to which the input signal can
        vary relative to the level parameter.
    trig_event : TriggerEvent
        Specifies the trigger event type. Valid values indicate either a start trigger event
        (TriggerEvent.START) or a stop trigger event (TriggerEvent.STOP).

        TriggerEvent.START: The start trigger event defines the conditions under which
        post-trigger acquisition data collection should be initiated or triggered. The start
        trigger event can vary in complexity from starting immediately, to starting on complex
        channel value definitions.

        TriggerEvent.STOP: The stop trigger event signals the current data acquisition
        process to terminate. The stop event can be as simple as that of a scan count, or as
        complex as involving a channel value level condition.


    .. table:: **trig_source parameter values**

        ==========  ===============================================================================
        IMMEDIATE   Start trigger event only. Acquisition begins immediately upon invocation the
                    :func:`.daq_in_scan` function. No pre-trigger data acquisition is possible with
                    this trigger type.
        ----------  -------------------------------------------------------------------------------
        EXTTTL      Start trigger event only. Acquisition begins on the selectable edge of an
                    external TTL signal. No pre-trigger data acquisition is possible with this
                    trigger type. 
        ----------  -------------------------------------------------------------------------------
        ANALOGHW    Start trigger event only. Data acquisition begins upon a selectable criteria of
                    the input signal (above level, below level, rising edge, etc.) trig_chan must
                    be defined as the first channel in the channel scan group. No pre-trigger data
                    acquisition is possible with this trigger type. 
        ----------  -------------------------------------------------------------------------------
        ANALOGSW    Post-trigger data acquisition begins upon a selectable criteria of the input
                    signal (above level, below level, rising edge, etc.) 
        ----------  -------------------------------------------------------------------------------
        DIGPATTERN  Post-trigger data acquisition beings upon receiving a specified digital pattern
                    on the specified digital port. 
        ----------  -------------------------------------------------------------------------------
        COUNTER     Post-trigger data acquisition begins upon detection of specified counter
                    criteria. 
        ----------  -------------------------------------------------------------------------------
        SCANCOUNT   Stop trigger event only. Stops collecting post-trigger data when the specified
                    number of post-trigger scans are completed. 
        ==========  ===============================================================================


    .. table:: **trig_sense parameter values**

        ============  =============================================================================
        RISING_EDGE   Triggers when the signal goes from low to high (TTL trigger) or rises through 
                      a specified level (hardware analog, software analog, and counter).
        ------------  -----------------------------------------------------------------------------
        FALLING_EDGE  Triggers when the signal goes from high to low (TTL trigger) or falls through 
                      a specified level (hardware analog, software analog, and counter).
        ------------  -----------------------------------------------------------------------------
        ABOVE_LEVEL   Triggers when the signal is above a specified level (hardware analog, 
                      software analog, counter, and digital pattern).
        ------------  -----------------------------------------------------------------------------
        BELOW_LEVEL   Triggers when the signal is below a specified level (hardware analog, 
                      software analog, counter, and digital pattern).
        ------------  -----------------------------------------------------------------------------
        EQ_LEVEL      Triggers when the signal equals a specified level (hardware analog, software 
                      analog, counter, and digital pattern).
        ------------  -----------------------------------------------------------------------------
        NE_LEVEL      Triggers when the signal does not equal a specified level (hardware analog, 
                      software analog, counter, and digital pattern).
        ------------  -----------------------------------------------------------------------------
        HIGH_LEVEL    Triggers when the signal is 5V (logic HIGH or "1").
        ------------  -----------------------------------------------------------------------------
        LOW_LEVEL     Triggers when the signal is 0V (logic LOW or "0").
        ============  =============================================================================


    .. table:: **Trigger levels**

        ==========  ===============================================================================
        ANALOG_HW   The voltage used to define the trigger level. Trigger detection is
                         performed in hardware.
        ----------  -------------------------------------------------------------------------------
        ANALOG_SW   The voltage used to define the trigger level. Trigger detection is
                         performed in software.
        ----------  -------------------------------------------------------------------------------
        DIGPATTERN  Sets the bit pattern for the digital channel trigger. Choices are: 
                         * 0.0 (no bits set): 255.0 (all bits set) for 8-bit digital ports. 
                         * 0.0 (no bits set): 65,535.0 (all bits set) for 16-bit digital ports.
        ----------  -------------------------------------------------------------------------------                      
        COUNTER     Selects either Pulse or Totalize counter values (0.0 65,535).
        ----------  -------------------------------------------------------------------------------
        IMMEDIATE   Ignored
        ----------  -------------------------------------------------------------------------------
        SCANCOUNT   Ignored
        ==========  ===============================================================================

    The table below lists the trigger start and stop criteria based on the selected trigger type
    and sensitivity.


    .. table:: **Trigger start and stop criteria**

        +----------------------+---------------------+--------------------------------------------+
        | Trigger Start/Stop   | Trigger Sensitivity | Trigger Start/Stop Criteria                |
        | Source (trig_source) | (trig_sense)        |                                            |
        +======================+=====================+============================================+
        | ANALOGHW             | RISING_EDGE         | Triggers when the signal value < (level -  |
        | (Start trigger event |                     | variance). Then, the signal value > level. |
        | only)                +---------------------+--------------------------------------------+
        |                      | FALLING_EDGE        | Triggers when the signal value > (level +  |
        |                      |                     | variance). Then, the signal value < level. |
        |                      +---------------------+--------------------------------------------+
        |                      | ABOVE_LEVEL         | Triggers when the signal value > (level).  |
        |                      +---------------------+--------------------------------------------+
        |                      | BELOW_LEVEL         | Triggers when the signal value < (level).  |
        +----------------------+---------------------+--------------------------------------------+
        | ANALOGSW             | RISING_EDGE         | Triggers/stops when the signal value <     |
        |                      |                     | (level - variance). Then, the signal value |
        |                      |                     | > level.                                   |
        |                      +---------------------+--------------------------------------------+
        |                      | FALLING_EDGE        | Triggers/stops when the signal value >     |
        |                      |                     | (level + variance). Then, the signal value |
        |                      |                     | < level.                                   |
        |                      +---------------------+--------------------------------------------+
        |                      | ABOVE_LEVEL         | Triggers/stops when the signal value >     |
        |                      |                     | (level).                                   |
        |                      +---------------------+--------------------------------------------+
        |                      | BELOW_LEVEL         | Triggers/stops when the signal value <     |
        |                      |                     | (level).                                   |
        |                      +---------------------+--------------------------------------------+
        |                      | EQ_LEVEL            | Triggers/stops when the (level - variance) |
        |                      |                     | < signal value < (level + variance).       |
        |                      +---------------------+--------------------------------------------+
        |                      | NE_LEVEL            | Triggers/stops when the signal value <     |
        |                      |                     | (level - variance) OR when the signal      |
        |                      |                     | value > (level + variance).                |
        +----------------------+---------------------+--------------------------------------------+
        | TRIG_DIGPATTERN      | ABOVE_LEVEL         | Triggers/stops when the (digital port      |
        |                      |                     | value AND (bitwise) variance) > (level AND |
        |                      |                     | (bitwise) variance).                       |
        |                      +---------------------+--------------------------------------------+
        |                      | BELOW_LEVEL         | Triggers/stops when the (digital port      |
        |                      |                     | value AND (bitwise) variance) < (level AND |
        |                      |                     | (bitwise) variance).                       |
        |                      +---------------------+--------------------------------------------+
        |                      | EQ_LEVEL            | Triggers/stops when the (digital port      |
        |                      |                     | value AND (bitwise) variance) = (level AND |
        |                      |                     | (bitwise) variance).                       |
        |                      +---------------------+--------------------------------------------+
        |                      | NE_LEVEL            | Triggers/stops when the (digital port      |
        |                      |                     | value AND (bitwise) variance) != (level    |
        |                      |                     | AND (bitwise) variance).                   |
        +----------------------+---------------------+--------------------------------------------+
        | TRIG_COUNTER         | RISING_EDGE         | Triggers/stops when the counter channel <  |
        |                      |                     | (level - variance). Then, the counter      |
        |                      |                     | channel > level.                           |
        |                      +---------------------+--------------------------------------------+
        |                      | FALLING_EDGE        | Triggers/stops when the counter channel >  |
        |                      |                     | (level + variance). Then, the counter      |
        |                      |                     | channel < level.                           |
        |                      +---------------------+--------------------------------------------+
        |                      | ABOVE_LEVEL         | Triggers/stops when the counter channel >  |
        |                      |                     | (level - variance).                        |
        |                      +---------------------+--------------------------------------------+
        |                      | BELOW_LEVEL         | Triggers/stops when the counter channel <  |
        |                      |                     | (level + variance).                        |
        |                      +---------------------+--------------------------------------------+
        |                      | EQ_LEVEL            | Triggers/stops when (level - variance) <   |
        |                      |                     | counter channel < (level + variance).      |
        |                      +---------------------+--------------------------------------------+
        |                      | NE_LEVEL            | Triggers/stops when the counter channel <  |
        |                      |                     | (level - variance) OR when the counter     |
        |                      |                     | channel > (level + variance).              |
        +----------------------+---------------------+--------------------------------------------+
    """
    _check_err(_cbw.cbDaqSetTrigger(
        board_num, trig_source, trig_sense, trig_chan, chan_type, gain, level,
        variance, trig_event))


_cbw.cbDBitIn.argtypes = [c_int, c_int, c_int, POINTER(c_ushort)]


def d_bit_in(board_num, port_type, bit_num):
    """Reads the state of a single digital input bit.

    This function treats all of the DIO ports of a particular type on a board as a single port.
    It lets you read the state of any individual bit within this port. Note that with some port
    types, such as 8255 ports, if the port is configured for DigitalIODirection.OUT,
    d_bit_in provides readback of the last output value.

    Parameters
    ----------
    board_num : int
        The number associated with the board when it was installed with InstaCal or created
        with :func:`.create_daq_device`.
    port_type : DigitalPortType
        There are three general types of digital ports - ports that are programmable as input or
        output, ports that are fixed input or output, and ports for which each bit may be
        programmed as input or output. For the first of these types, set PortType to
        DigitalPortType.FIRSTPORTA. For the latter two types, set PortType to
        DigitalPortType.AUXPORT. For devices with both types of digital ports, set PortType to
        either DigitalPortType.FIRSTPORTA or DigitalPortType.AUXPORT, depending on which digital
        inputs you wish to read.
    bit_num : int
        Specifies the bit number within the single large port.

    Returns
    -------
    int
        The value of the bit. Value will be 0 (logic low) or 1 (logic high). Logic high does not
        necessarily mean 5 V - refer to the device hardware user guide for chip input
        specifications.
    """
    bit_value = c_ushort()
    _check_err(_cbw.cbDBitIn(board_num, port_type, bit_num, byref(bit_value)))
    return bit_value.value


_cbw.cbDBitOut.argtypes = [c_int, c_int, c_int, c_ushort]


def d_bit_out(board_num, port_type, bit_num, bit_value):
    """Sets the state of a single digital output bit.

    This function treats all of the DIO ports of a particular type on a board as a single large
    port. It lets you set the state of any individual bit within this large port.

    Most configurable ports require configuration before writing. Check board-specific information
    to determine if the port should be configured for your hardware. When configurable, use
    :func:`.d_config_port` to configure a port for output, and :func:`.d_config_bit` to configure a
    bit for output.

    Parameters
    ----------
    board_num : int
        The number associated with the board when it was installed with InstaCal or created
        with :func:`.create_daq_device`.
    port_type : DigitalPortType
        There are three general types of digital ports - ports that are programmable as input or
        output, ports that are fixed input or output, and ports for which each bit may be
        programmed as input or output. For the first of these types, set PortType to
        DigitalPortType.FIRSTPORTA. For the latter two types, set PortType to
        DigitalPortType.AUXPORT. For devices with both types of digital ports, set PortType to
        either DigitalPortType.FIRSTPORTA or DigitalPortType.AUXPORT, depending on which digital
        outputs you wish to set.
    bit_num : int
        Specifies the bit number within the single large port. The specified bit must be in a port
        that is configured for output.
    bit_value : int
        The value to set the bit to. Value will be 0 (logic low) or 1 (logic high). Logic high does
        not necessarily mean 5 V - refer to the device hardware user guide for chip input
        specifications.
    """
    _check_err(_cbw.cbDBitOut(board_num, port_type, bit_num, bit_value))


_cbw.cbDClearAlarm.argtypes = [c_int, c_int, c_uint]


def d_clear_alarm(board_num, port_type, mask):
    """Clears the alarm state for specified bits when alarms are configured to latch. Once the
    alarm condition is resolved, this function can be used to clear the latched alarm.

    Parameters
    ----------
    board_num : int
        The number associated with the board when it was installed with InstaCal or created
        with :func:`.create_daq_device`.
    port_type : DigitalPortType
        The port containing the bit(s) to clear. The specified port must be configurable for
        alarm output.
    mask : int
        The mask that determines which bits to clear. Set to all 1s to clear all bits in the port.
    """
    _check_err(_cbw.cbDClearAlarm(board_num, port_type, mask))


_cbw.cbDConfigBit.argtypes = [c_int, c_int, c_int, c_int]


def d_config_bit(board_num, port_type, bit_num, direction):
    """Configures a specific digital bit for input or output. This function treats all DIO ports
    on a board as a single port (DigitalPortType.AUXPORT); it is not supported by 8255 type DIO
    ports.

    Parameters
    ----------
    board_num : int
        The number associated with the board when it was installed with InstaCal or created
        with :func:`.create_daq_device`.
    port_type : DigitalPortType
        The port (DigitalPortType.AUXPORT) whose bits are to be configured. The port specified must
        be bitwise configurable.
    bit_num : int
        The bit number to configure as input or output
    direction : DigitalIODirection
        DigitalIODirection.OUT or DigitalIODirection.IN configures the specified bit for output or
        input, respectively.
    """
    _check_err(_cbw.cbDConfigBit(board_num, port_type, bit_num, direction))


_cbw.cbDConfigPort.argtypes = [c_int, c_int, c_int]


def d_config_port(board_num, port_type, direction):
    """Configures a digital port as input or output.

    This function is for use with ports that may be programmed as input or output, such as those on
    the 82C55 chips and 8536 chips. Refer to the 82C55A data sheet (82C55A.pdf) for details of chip
    operation. This document is installed in the Documents subdirectory where the UL is installed.
    Refer to the Zilog 8536 manual for details of 8536 chip operation.

    Parameters
    ----------
    board_num : int
        The number associated with the board when it was installed with InstaCal or created
        with :func:`.create_daq_device`.
    port_type : DigitalPortType
        The port to configure. The port must be configurable. For most boards, AUXPORT is not
        configurable. Check the board-specific information in the Universal Library User's Guide
        for details.
    direction : DigitalIODirection
        DigitalIODirection.OUT or DigitalIODirection.IN configures the entire eight or four bit
        port for output or input.

    Notes
    -----
    When used on ports within an 8255 chip, this function will reset all ports on that chip
    configured for output to a zero state. This means that if you set an output value on FIRSTPORTA
    and then change the configuration on FIRSTPORTB from OUTPUT to INPUT, the output value at
    FIRSTPORTA will be all zeros. You can, however, set the configuration on SECONDPORTx without
    affecting the value at FIRSTPORTA. For this reason, this function is usually called at the
    beginning of the program for each port requiring configuration.
    """
    _check_err(_cbw.cbDConfigPort(board_num, port_type, direction))


_cbw.cbDeviceLogin.argtypes = [c_int, c_char_p, c_char_p]


def device_login(board_num, user_name, password):
    """Opens a device session with a shared device.

    Parameters
    ----------
    board_num : int
        The number associated with the board when it was installed with InstaCal or created
        with :func:`.create_daq_device`.
    user_name : string
        A string that identifies the user name used to log in to a device session.
    password : string
        A string that identifies the password used to log in to a device session.

    Notes
    -----
    - If the user name or password is invalid, the function raises a ULError with an errorcode of
      ErrorCode.INVALIDLOGIN.

    - If the session is already opened by another user, the function raises a ULError with an
      errorcode of ErrorCode.SESSIONINUSE.
    """
    _check_err(_cbw.cbDeviceLogin(board_num, user_name, password))


_cbw.cbDeviceLogout.argtypes = [c_int]


def device_logout(board_num):
    """Releases the device session with a shared device.

    Parameters
    ----------
    board_num : int
        The number associated with the board when it was installed with InstaCal or created
        with :func:`.create_daq_device`.
    """
    _check_err(_cbw.cbDeviceLogout(board_num))


_cbw.cbDIn.argtypes = [c_int, c_int, POINTER(c_ushort)]


def d_in(board_num, port_type):
    """Reads a digital input port.

    Note that for some port types, such as 8255 ports, if the port is configured for DIGITALOUT,
    this function will provide readback of the last output value.

    Parameters
    ----------
    board_num : int
        The number associated with the board when it was installed with InstaCal or created
        with :func:`.create_daq_device`.
    port_type : DigitalPortType
        The digital port to read. Some hardware allows readback of the state of the output using
        this function; refer to the board-specific information in the Universal Library User's
        Guide.

    Returns
    -------
    int
        The digital input value

    Notes
    -----
    - Port size can vary. The return value is 0 to 65,535 for a 16-bit port, 0 to 255 for an 8-bit
      port, and 0 to 15 for a 4-bit port. To read ports larger than 16-bit, use :func:`.d_in_32`.

    - Refer to the board-specific information for valid PortType values.
    """
    data_value = c_ushort()
    _check_err(_cbw.cbDIn(board_num, port_type, byref(data_value)))
    return data_value.value


_cbw.cbDIn32.argtypes = [c_int, c_int, POINTER(c_uint)]


def d_in_32(board_num, port_type):
    """Reads a 32-bit digital input port.

    Note that for some port types, such as 8255 ports, if the port is configured for DIGITALOUT,
    this function will provide readback of the last output value.

    Parameters
    ----------
    board_num : int
        The number associated with the board when it was installed with InstaCal or created
        with :func:`.create_daq_device`.
    port_type : DigitalPortType
        The digital port to read. Some hardware allows readback of the state of the output using
        this function; refer to the board-specific information in the Universal Library User's
        Guide.

    Returns
    -------
    int
        The digital input value

    Notes
    -----
    - Port size can vary. The return value is 0 to 65535 for a 16-bit port, 0 to 255 for an 8-bit
      port, and 0 to 15 for a 4-bit port. Port size can vary. The return value is 0 to 2**32 - 1 for
      a 32-bit port, 0 to 2**24 - 1 for a 24-bit port, 0 to 65,535 for a 16-bit port, 0 to 255 for
      an 8-bit port, and 0 to 15 for a 4-bit port.

    - Refer to the board-specific information for valid PortType values.
    """
    data_value = c_uint()
    _check_err(_cbw.cbDIn32(board_num, port_type, byref(data_value)))
    return data_value.value


_cbw.cbDInArray.argtypes = [c_int, c_int, c_int, POINTER(c_uint)]


def d_in_array(board_num, low_port, high_port, data_array=None):
    """Reads a range of digital ports simultaneously, and returns the data in an array.

    Parameters
    ----------
    board_num : int
        The number associated with the board when it was installed with InstaCal or created
        with :func:`.create_daq_device`.
    low_port : DigitalPortType
        The first port in the scan
    high_port : DigitalPortType
        The last port in the scan
    data_array : POINTER(c_uint), optional
        Pointer to the digital input data array. If this parameter is omitted (or None), the array
        will be allocated by this function. Reusing the array by passing it in as the parameter may
        be useful as an optimization to prevent excessive allocations, saving memory and CPU time.

    Returns
    -------
    POINTER(c_uint)
        A pointer to the C array containing the digital input data
    """
    if high_port < low_port:
        raise ULError(ErrorCode.BADPORTNUM)

    if data_array == None:
        data_array = (c_uint * (high_port - low_port + 1))()
    _check_err(_cbw.cbDInArray(board_num, low_port, high_port, data_array))
    return data_array


_cbw.cbDInScan.argtypes = [c_int, c_int,
                           c_long, POINTER(c_long), HGLOBAL, c_int]


def d_in_scan(board_num, port_type, count, rate, memhandle, options):
    """Performs multiple reads of a digital input port on a device with a pacer clock.

    Parameters
    ----------
    board_num : int
        The number associated with the board when it was installed with InstaCal or created
        with :func:`.create_daq_device`.
    port_type : DigitalPortType
        The digital port to read, usually DigitalPortType.FIRSTPORTA or DigitalPortType.FIRSTPORTB.
    count : int
        The number of times to read the digital port
    rate : int
        Number of times per second (Hz) to read the port.

        The actual sampling rate in some cases will vary a small amount from the requested rate.
        The actual rate is returned.
    memhandle : int
        Handle for the Windows buffer to store data. This buffer must have been previously
        allocated with :func:`.win_buf_alloc` or :func:`.win_buf_alloc_32`.
    options : ScanOptions
        Flags that control various options. Refer to the constants in the "options parameter values"
        section below.


    .. table:: **options parameter values**

        ===========  ==============================================================================
        BACKGROUND   If the BACKGROUND option is not used then the :func:`.d_in_scan` function will 
                     not return to your program until all of the requested data has been collected 
                     and returned to memhandle. 

                     When the BACKGROUND option is used, control returns immediately to the next 
                     line in your program and the transfer from the digital input port to memhandle 
                     will continue in the background. Use :func:`.get_status` with DIFUNCTION to 
                     check on the status of the background operation. Use :func:`.stop_background` 
                     with DIFUNCTION to terminate the background process before it has completed. 
        -----------  ------------------------------------------------------------------------------
        BLOCKIO      Data transfers are handled in blocks (by REP-INSW for example). BLOCKIO is not 
                     recommended for slow acquisition rates. If the rate of acquisition is very 
                     slow (for example less than 200 Hz) BLOCKIO may not be the best transfer mode, 
                     as the operation status is not available until one packet of data is collected 
                     (typically 512 samples). For example, when acquiring 100 samples at 100 Hz 
                     using BLOCKIO, the operation will not complete until 5.12 seconds has elapsed. 
        -----------  ------------------------------------------------------------------------------
        CONTINUOUS   This option puts the function in an endless loop. Once it transfers the 
                     required number of bytes it resets to the start of the buffer and begins 
                     again. The only way to stop this operation is with :func:`.stop_background` 
                     with DIFUNCTION. Normally this option should be used in combination with 
                     BACKGROUND so that your program will regain control. 
        -----------  ------------------------------------------------------------------------------
        DWORDXFER    Normally this function reads a single (byte) 16-bit port. When DWORDXFER is 
                     specified, this function reads two adjacent 16-bit ports at a time, and stores 
                     the value of both ports together as the low and high byte of a single array 
                     element in the buffer. It is usually required to set port_type to AUXPORT0. 
        -----------  ------------------------------------------------------------------------------
        EXTCLOCK     If this option is used then transfers will be controlled by the signal on the 
                     trigger input line rather than by the internal pacer clock. Each transfer will 
                     be triggered on the appropriate edge of the trigger input signal (refer to 
                     board-specific information in the Universal Library User's Guide). When this 
                     option is used the rate parameter is ignored. The transfer rate is dependent
                     on the trigger signal. 
        -----------  ------------------------------------------------------------------------------
        EXTTRIGGER   If this option is used, then the scan will not begin until the signal on the 
                     trigger input line meets the trigger criteria. 
        -----------  ------------------------------------------------------------------------------
        HIGHRESRATE  Acquires data at a high resolution rate. When specified, the rate at which 
                     samples are acquired is in "samples per 1000 seconds per channel". When this 
                     option is not specified, the rate at which samples are acquired is in "samples 
                     per second per channel" (refer to the rate parameter above). 
        -----------  ------------------------------------------------------------------------------
        RETRIGMODE   Re-arms the trigger after a trigger event is performed. With this mode, the 
                     scan begins when a trigger event occurs. When the scan completes, the trigger 
                     is re-armed to acquire the next the batch of data. You can specify the number 
                     of digital input samples to acquire per trigger - this is the trigger count. 
                     The RETRIGMODE option can be used with the CONTINUOUS option to continue 
                     arming the trigger until :func:`.stop_background` is called. 

                     You specify the trigger count with the :func:`.set_config` config_item option 
                     BIDITRIGCOUNT. If you specify a trigger count that is either zero or greater 
                     than the value of the :func:`.d_in_scan` count parameter, the trigger count is 
                     set to the value of the count parameter. 

                     Specify the CONTINUOUS option with the trigger count set to zero to fill the 
                     buffer with count samples, re-arm the trigger, and refill the buffer upon the 
                     next trigger. 
        -----------  ------------------------------------------------------------------------------
        SINGLEIO     Data is transferred to memory one sample at a time. Rates attainable using 
                     SINGLEIO are PC-dependent and generally less than 4 kHz. 
        -----------  ------------------------------------------------------------------------------
        WORDXFER     Normally this function reads a single (byte) 8-bit port. When WORDXFER is 
                     specified, this function reads two adjacent 8-bit ports at a time, and stores 
                     the value of both ports together as the low and high byte of a single array 
                     element in the buffer. It is usually required to set PortType to FIRSTPORTA. 
        ===========  ==============================================================================

    Returns
    -------
    int
        The actual rate set, which may be different from the requested rate because of pacer
        limitations.
    """
    rate_internal = c_long(rate)
    _check_err(_cbw.cbDInScan(
        board_num, port_type, count, byref(rate_internal), memhandle, options))
    return rate_internal.value


_cbw.cbDisableEvent.argtypes = [c_int, c_uint]


def disable_event(board_num, event_type):
    """Disables one or more event conditions and disconnects their user-defined handlers.

    Parameters
    ----------
    board_num : int
        The number associated with the board when it was installed with InstaCal or created
        with :func:`.create_daq_device`.
    event_type : EventType
        Specifies one or more event conditions to disable. More than one event type can be
        specified by adding the event types. Note that specifying an event that has not been
        enabled is benign and will not cause any errors. Refer to :func:`.enable_event` for valid
        event_type settings.

        To disable all events in a single call, use EventType.ALL_EVENT_TYPES.

    Notes
    -----
    For most event types, this function cannot be called while any background operations
    (:func:`.a_in_scan`, :func:`.a_pretrig`, or :func:`.a_out_scan`) are active. Perform a
    stop_background before calling :func:`.disable_event`. However, for
    EventType.ON_EXTERNAL_INTERRUPT events, you can call :func:`.disable_event` while the board is
    actively generating events.
    """
    _check_err(_cbw.cbDisableEvent(board_num, event_type))


_cbw.cbDOut.argtypes = [c_int, c_int, c_ushort]


def d_out(board_num, port_type, data_value):
    """Writes a byte to a digital output port.

    Most configurable ports require configuration before writing. Check the board-specific
    information in the Universal Library User's Guide to determine if the port should be configured
    for your hardware. When configurable, use :func:`.d_config_port` to configure a port for output.

    Parameters
    ----------
    board_num : int
        The number associated with the board when it was installed with InstaCal or created
        with :func:`.create_daq_device`.
    port_type : DigitalPortType
        The digital port type. There are three general types of digital ports - ports that are
        programmable as input or output, ports that are fixed input or output, and ports for which
        each bit may be programmed as input or output. For the first of these types, set port_type
        to DigitalPortType.FIRSTPORTA. For the latter two types, set port_type to
        DigitalPortType.AUXPORT. For devices with both types of digital ports, set port_type to
        either DigitalPortType.FIRSTPORTA or DigitalPortType.AUXPORT, depending on the digital port
        you want to set.
    data_value : int
        Digital value to write

    Notes
    -----
    - Port size can vary. The output value is 0 to 65,535 for a 16-bit port, 0 to 255 for an 8-bit
      port, and 0 to 15 for a 4-bit port. To write to ports larger than 16-bit, use
      :func:`.d_out_32`.

    - Refer to the example programs and the board-specific information in the Universal Library
      User's Guide for clarification of valid port_type values.
    """
    _check_err(_cbw.cbDOut(board_num, port_type, data_value))


_cbw.cbDOut32.argtypes = [c_int, c_int, c_uint]


def d_out_32(board_num, port_type, data_value):
    """Writes a byte to a 32-bit digital output port.

    Most configurable ports require configuration before writing. Check the board-specific
    information in the Universal Library User's Guide to determine if the port should be configured
    for your hardware. When configurable, use :func:`.d_config_port` to configure a port for output.

    Parameters
    ----------
    board_num : int
        The number associated with the board when it was installed with InstaCal or created
        with :func:`.create_daq_device`.
    port_type : DigitalPortType
        The digital port type. There are three general types of digital ports - ports that are
        programmable as input or output, ports that are fixed input or output, and ports for which
        each bit may be programmed as input or output. For the first of these types, set port_type
        to DigitalPortType.FIRSTPORTA. For the latter two types, set port_type to
        DigitalPortType.AUXPORT. For devices with both types of digital ports, set port_type to
        either DigitalPortType.FIRSTPORTA or DigitalPortType.AUXPORT, depending on the digital port
        you want to set.
    data_value : int
        Digital value to write

    Notes
    -----
    - Port size can vary. The output value is 0 to 2**32 - 1 for a 32-bit port, 0 to 2**24 - 1 for
      a 24-bit port, 0 to 65,535 for a 16-bit port, 0 to 255 for an 8-bit port, and 0 to 15 for a
      4-bit port.

    - Refer to the example programs and the board-specific information in the Universal Library
      User's Guide for clarification of valid port_type values.
    """
    _check_err(_cbw.cbDOut32(board_num, port_type, data_value))


_cbw.cbDOutArray.argtypes = [c_int, c_int, c_int, POINTER(c_uint)]


def d_out_array(board_num, low_port, high_port, data_list):
    """Sets the values of specified ports simultaneously.

    Parameters
    ----------
    board_num : int
        The number associated with the board when it was installed with InstaCal or created
        with :func:`.create_daq_device`.
    low_port : DigitalPortType
        The first port in the scan
    high_port : DigitalPortType
        The last port in the scan
    data_list : list of int
        Digital output data list
    """
    _check_err(_cbw.cbDOutArray(
        board_num, low_port, high_port, _to_ctypes_array(data_list, c_uint)))


_cbw.cbDOutScan.argtypes = [c_int, c_int,
                            c_long, POINTER(c_long), HGLOBAL, c_int]


def d_out_scan(board_num, port_type, count, rate, memhandle, options):
    """Writes a series of bytes or words to the digital output port on a board with a pacer clock.

    Parameters
    ----------
    board_num : int
        The number associated with the board when it was installed with InstaCal or created
        with :func:`.create_daq_device`.
    port_type : DigitalPortType
        Specifies which digital I/O port to write to (usually DigitalPortType.FIRSTPORTA or
        DigitalPortType.FIRSTPORTB). The port must be configured for output.
    rate : int
        Number of times per second (Hz) to write to the port. The actual update rate in some cases
        will vary a small amount from the requested rate. The actual rate is returned.
    count : int
        The number of times to write the digital output.
    memhandle : int
        Handle for the Windows buffer to store data. This buffer must have been previously
        allocated with :func:`.win_buf_alloc`.
    options : ScanOptions
        Flags that control various options. Refer to the constants in the "options parameter values"
        section below.


    .. table:: **options parameter values**

        =============  ============================================================================
        ADCCLOCK       Paces the data output operation using the ADC clock.
        -------------  ----------------------------------------------------------------------------
        ADCCLOCKTRIG   Triggers a data output operation when the ADC clock starts.
        -------------  ----------------------------------------------------------------------------
        BACKGROUND     If the BACKGROUND option is not used, then the :func:`.d_out_scan` function 
                       will not return control to your program until all of the requested data has 
                       been output.

                       When the BACKGROUND option is used, control returns immediately to the next 
                       line in your program and the transfer to the digital output port from 
                       memhandle will continue in the background. Use :func:`.get_status` with 
                       DOFUNCTION to check on the status of the background operation. Use 
                       :func:`.stop_background` with DOFUNCTION to terminate the background process 
                       before it has completed.
        -------------  ----------------------------------------------------------------------------
        CONTINUOUS     This option puts the function in an endless loop. Once it transfers the 
                       required number of bytes, it resets to the start of the buffer and begins 
                       again. The only way to stop this operation is with :func:`.stop_background` 
                       with DOFUNCTION. Normally this option should be used in combination with 
                       BACKGROUND so that your program will regain control.
        -------------  ----------------------------------------------------------------------------
        DWORDXFER      Normally this function writes to a single (byte) 16-bit port. When DWORDXFER 
                       is specified, it writes to two adjacent 16-bit ports at a time as the low 
                       and high byte of a single array element in the buffer. It is usually 
                       required to set port_type to AUXPORT0.
        -------------  ----------------------------------------------------------------------------
        EXTCLOCK       When this option is used, transfers are controlled by the signal on the 
                       external clock input rather than by the internal pacer clock. Each transfer 
                       will be triggered on the appropriate edge of the clock input signal (refer 
                       to board-specific information contained in the UL Users Guide). 

                       When this option is used, the rate parameter is used for reference only. The 
                       transfer rate is dependent on the clock signal. An approximation of the 
                       external clock rate is used to determine the size of the packets to transfer 
                       from the board. Set the rate parameter to an approximate maximum value. 
        -------------  ----------------------------------------------------------------------------
        NONSTREAMEDIO  When this option is used, you can output non-streamed data to a specific DAC 
                       output channel. 

                       To load the data output buffer into the device's internal output FIFO, the 
                       aggregate size of the data output buffer must be <= the size of the 
                       internal data output FIFO in the device. Once the sample data are 
                       transferred or downloaded to the device, the device is responsible for 
                       outputting the data. You can't make any changes to the output buffer once 
                       the output begins. 

                       With NONSTREAMEDIO mode, you do not have to periodically feed output data 
                       through the program to the device for the data output to continue. However, 
                       the size of the buffer is limited. 
        -------------  ----------------------------------------------------------------------------
        RETRIGMODE     Re-arms the trigger after a trigger event is performed. With this mode, the 
                       scan begins when a trigger event occurs. When the scan completes, the 
                       trigger is re-armed to acquire the next the batch of data. You can specify 
                       the number of digital output samples to generate per trigger - this is the 
                       trigger count. The RETRIGMODE option can be used with the CONTINUOUS option 
                       to continue arming the trigger until :func:`.stop_background` is called.

                       You specify the trigger count with the :func:`.set_config` config_item
                       option DOTRIGCOUNT. If you specify a trigger count that is either zero or
                       greater than the value of the :func:`.d_in_scan` count parameter, the
                       trigger count is set to the value of the count parameter.

                       Specify the CONTINUOUS option with the trigger count set to zero to fill the 
                       buffer with count samples, re-arm the trigger, and refill the buffer upon 
                       the next trigger.
        -------------  ----------------------------------------------------------------------------
        WORDXFER       Normally this function writes to a single (byte) 8-bit port. When WORDXFER 
                       is specified, it writes to two adjacent 8-bit ports as the low and high byte 
                       of a single array element in the buffer. When WORDXFER is used, it is 
                       generally required to set port_type to FIRSTPORTA. 
        =============  ============================================================================

    Returns
    -------
    int
        The actual rate set, which may be different from the requested rate because of pacer
        limitations.

    Notes
    -----
    - :const:`~mcculw.enums.ScanOptions.BYTEXFER` is the default option. Make sure you are using an
      array when your data is arranged in bytes. Use the :const:`~mcculw.enums.ScanOptions.WORDXFER`
      option for word array transfers.

    - :const:`~mcculw.enums.ScanOptions.NONSTREAMEDIO` can only be used with the number of samples
      (count) set equal to the size of the FIFO or less.

    - Transfer Method may not be specified. DMA is used.
    """
    rate_internal = c_long(rate)
    _check_err(_cbw.cbDOutScan(
        board_num, port_type, count, byref(rate_internal), memhandle, options))
    return rate_internal.value


ULEventCallback = WINFUNCTYPE(None, c_int, c_uint, c_uint, c_void_p)

_cbw.cbEnableEvent.argtypes = [
    c_int, c_uint, c_uint, ULEventCallback, c_void_p]


def enable_event(board_num, event_type, event_param, callback_func, c_user_data):
    """Binds one or more event conditions to a user-defined callback function. Upon detection of an
    event condition, the user-defined function is invoked with board- and event-specific data.
    Detection of event conditions occurs in response to interrupts. Typically, this function is
    used in conjunction with interrupt driven processes such as :func:`.a_in_scan`,
    :func:`.a_pretrig`, or :func:`.a_out_scan`.

    Parameters
    ----------
    board_num : int
        The number associated with the board when it was installed with InstaCal or created
        with :func:`.create_daq_device`.
    event_type : EventType
        Specifies one or more event conditions that will be bound to the user-defined callback
        function. More than one event type can be specified by adding the event types. Refer to the
        constants in the "event_type parameter values" section below.
    event_param : int
        Additional data required to specify some event conditions, such as an
        EventType.ON_DATA_AVAILABLE event or EventType.ON_EXTERNAL_INTERRUPT event.

        For EventType.ON_DATA_AVAILABLE events, event_param is used to determine the minimum number
        of samples to acquire during an analog input scan before generating the event. For
        EventType.ON_EXTERNAL_INTERRUPT events, event_param is used to latch digital bits on
        supported hardware by setting it to one of the constants in the "event_param parameter
        values" section below.

        Most event conditions ignore this value.
    callback_func : ULEventCallback
        A ULEventCallback instance used to handle the above event type(s).

        No reference to the ULEventCallback object is stored internally. The ULEventCallback object
        must remain allocated until no more events will occur, otherwise the next callback will
        cause a crash. It is up to the user of this function to ensure that Python will
        not garbage-collect the object. Typically, assigning the ULEventCallback to a member
        variable or making it a global variable is sufficient.

        The function passed to ULEventCallback's constructor should accept 4 parameters (not
        including ``self`` if it is a member function): board_num, event_type, event_data,
        c_user_data. See the "Callback function parameters" section below for more information.
    c_user_data
        User-defined data that will be passed to the callback function.

        The data may be any C type object. Care must be taken to cast back to the same type in the
        callback method. In most cases, py_object is recommended.

        No reference to the c_user_data object is stored internally. It is up to the user of this
        function to ensure that Python will not garbage-collect the object. Typically, assigning
        the c_user_data to a member variable is sufficient.


    .. table:: **event_type parameter values**

        =====================  ====================================================================
        ON_DATA_AVAILABLE      Generates an event whenever the number of samples acquired during an 
                               analog input scan increases by event_param samples or more. Note 
                               that for BLOCKIO scans, events will be generated on packet 
                               transfers; for example, even if event_param is set to 1, events will 
                               only be generated every packet-size worth of data (256 samples for 
                               the PCI-DAS1602) for aggregate rates greater than 1 kHz for the 
                               default :func:`.a_in_scan` mode. 

                               For :func:`.a_pretrig`, the first event is not generated until a 
                               minimum of EventParam samples after the pretrigger. 
        ---------------------  --------------------------------------------------------------------
        ON_END_OF_INPUT_SCAN   Generates an event upon completion or fatal error of 
                               :func:`.a_in_scan` or :func:`.a_pretrig`. 

                               Some devices, such as the USB-1208FS and USB-1408FS, will generate 
                               an end of scan event after :func:`.stop_background` is called, but 
                               most devices do not. Handle post-scan tasks directly after calling 
                               :func:`.stop_background`. 
        ---------------------  --------------------------------------------------------------------
        ON_END_OF_OUTPUT_SCAN  Generates an event upon completion or fatal error of 
                               :func:`.a_out_scan`. 

                               Some devices, such as the USB-1208FS and USB-1408FS, will generate 
                               an end of scan event after :func:`.stop_background` is called, but 
                               most devices do not. Handle post-scan tasks directly after calling 
                               :func:`.stop_background`. 
        ---------------------  --------------------------------------------------------------------
        ON_EXTERNAL_INTERRUPT  For some digital and counter boards, generates an event upon 
                               detection of a pulse at the External Interrupt pin. 
        ---------------------  --------------------------------------------------------------------
        ON_PRETRIGGER          For :func:`.a_pretrig`, generates an event upon detection of the 
                               first trigger. 
        ---------------------  --------------------------------------------------------------------
        ON_SCAN_ERROR          Generates an event upon detection of a driver error during 
                               BACKGROUND input and output scans. This includes OVERRUN, UNDERRUN, 
                               and TOOFEW errors. 
        =====================  ====================================================================


    .. table:: **event_param parameter values**

        ========  =======================================================================
        LATCH_DI  Returns the data that was latched in at the most recent interrupt edge.
        --------  -----------------------------------------------------------------------
        LATCH_DO  Latches out the data most recently written to the hardware.
        ========  =======================================================================


    **Callback function parameters**

    - **board_num** (int) - Indicates which board caused the event.

    - **event_type** (EventType) - Indicates which event occurred.

    - **event_data** (int) - Board-specific data associated with this event. Returns a value based
      on the event_type as listed in the "Callback event_data parameter values" section below.


      .. table:: **Callback event_data parameter values**

          =====================  ==================================================================
          event_type              Value of event_data
          =====================  ==================================================================
          ON_DATA_AVAILABLE      The number of samples acquired since the start of the scan.
          ---------------------  ------------------------------------------------------------------
          ON_END_OF_INPUT_SCAN   The total number of samples acquired upon the scan completion or
                                 end.
          ---------------------  ------------------------------------------------------------------
          ON_END_OF_OUTPUT_SCAN  The total number of samples output upon the scan completion or
                                 end.
          ---------------------  ------------------------------------------------------------------
          ON_EXTERNAL_INTERRUPT  The number of interrupts generated since enabling the
                                 ON_EXTERNAL_INTERRUPT event.
          ---------------------  ------------------------------------------------------------------
          ON_PRETRIGGER          The number of pretrigger samples available at the time of
                                 pretrigger.

                                 This value is invalid for some boards when a TOOFEW error occurs.
                                 Refer to board details.
          ---------------------  ------------------------------------------------------------------
          ON_SCAN_ERROR          The error code of the scan error.
          =====================  ==================================================================

    - **c_user_data** - The C type object supplied by the user_data parameter in
      :func:`.enable_event`. Note that before use, this parameter must be cast to the same data
      type as passed in to :func:`.enable_event`.

    Notes
    -----
    - This function cannot be called while any background operations (:func:`.a_in_scan`,
      :func:`.a_pretrig`, or :func:`.a_out_scan`) are active. If a background operation is in
      progress when :func:`.enable_event` is called, the function raises a ULError with the
      error code ErrorCode.ALREADYACTIVE. Perform a :func:`.stop_background` call before calling
      :func:`.enable_event`.

    - Events will not be generated faster than the user callback function can handle them. If an
      event type becomes multi-signaled before the event handler returns, events are merged. The
      event handler is called once per event type, and is supplied with the event data
      corresponding to the latest event. When more than one event type is generated, the event
      handler for each event type is called in the same order in which they are enabled.

    - Events are generated while handling board-generated interrupts. Therefore, using
      :func:`.stop_background` to abort background operations does not generate
      EventType.ON_END_OF_INPUT_SCAN or EventType.ON_END_OF_OUTPUT_SCAN events. However, the event
      handlers can be called immediately after calling :func:`.stop_background`.
    """
    _check_err(_cbw.cbEnableEvent(
        board_num, event_type, event_param, callback_func, byref(c_user_data)))


_cbw.cbFlashLED.argtypes = [c_int]


def flash_led(board_num):
    """Causes the LED on a USB device to flash.

    Parameters
    ----------
    board_num : int
        The number associated with the board when it was installed with InstaCal or created
        with :func:`.create_daq_device`.

    Notes
    -----
    After calling :func:`.flash_led`, wait a few seconds before calling additional functions, or
    execution of the next function may fail.
    """
    _check_err(_cbw.cbFlashLED(board_num))


_cbw.cbFromEngUnits.argtypes = [c_int, c_int, c_float, POINTER(c_ushort)]


def from_eng_units(board_num, ul_range, eng_units_value):
    """Converts a single precision voltage (or current) value in engineering units to an integer
    count value. This function is typically used to obtain a data value from a voltage value for
    output to a D/A with functions such as :func:`.a_out`.

    Parameters
    ----------
    board_num : int
        The number associated with the board when it was installed with InstaCal or created
        with :func:`.create_daq_device`.
    ul_range : ULRange
        The voltage (or current) range to use for the conversion to counts. When using this
        function to obtain a value to send to a D/A board, keep in mind that some D/A boards
        have programmable voltage ranges, and others set the voltage range via switches on the
        board. In either case, the desired range must be passed to this function.

        Refer to board-specific information in the Universal Library User's Guide for a list of the
        supported A/D ranges of each board.
    eng_units_value : float
        The single precision voltage (or current) value to use for the conversion to counts. Set
        the value to be within the range specified by the ul_range parameter.

    Returns
    -------
    int
        An integer count that is equivalent to the eng_units_value parameter using the resolution of
        the D/A on the board referenced by board_num

    Notes
    -----
    - This function is not supported for hardware with resolution greater than 16 bits.

    - The default resolution of this function is 12 bits. If the device referenced by
      board_num has neither analog input nor analog output, the result is a 12 bit conversion.

    - If the device referenced by board_num has both analog input and analog output, the resolution
      and transfer function of the D/A converter on the device is used.
    """
    data_value = c_ushort()
    _check_err(_cbw.cbFromEngUnits(board_num, ul_range,
                                   eng_units_value, byref(data_value)))
    return data_value.value


_cbw.cbGetBoardName.argtypes = [c_int, c_char_p]


def get_board_name(board_num):
    """Returns the board name of a specified board, or iterates through a list of all supported
    boards.

    Parameters
    ----------
    board_num : int
        Either:

        a. The number associated with the board when it was installed with InstaCal or created
           with :func:`.create_daq_device`.
        b. Iterator.GET_FIRST or Iterator.GET_NEXT to refer to the list of UL supported boards

    Returns
    -------
    string
        Based on the board_num arguement, either:

        a. The board name for the installed board at the given board_num
        b. Set board_num to Iterator.GET_FIRST or Iterator.GET_NEXT to get a list of all board
           types that are supported by the library. Set board_num to Iterator.GET_FIRST to get the
           first board type in the list of supported boards. Subsequent calls with board_num set to
           Iterator.GET_NEXT returns each of the other board types supported by the library. When you
           reach the end of the list, an empty string is returned. Refer to the ULGT04 example program
           for more details.

    Notes
    -----
    - Using the Iterator version of this function will list all boards supported by the base
      Universal Library, and does not necessarily reflect those supported by the Python layer.
    """
    name = create_string_buffer(_BOARDNAMELEN)
    _check_err(_cbw.cbGetBoardName(board_num, name))
    return name.value.decode('utf-8')


_cbw.cbGetBoardNumber.argtypes = [DaqDeviceDescriptor]


def get_board_number(descriptor):
    """Returns the board number of the DAQ device specified by the descriptor, or -1 if the DAQ
    device hasn't been created in the library yet.

    Parameters
    ----------
    descriptor : DaqDeviceDescriptor
        The device descriptor of the DAQ device. Each descriptor is a structure containing
        information describing a unique DAQ device. Refer to the
        :class:`~mcculw.structs.DaqDeviceDescriptor` section for more information.

    Returns
    -------
    int
        The board number, or -1 if the DAQ device hasn't been created in the library yet
    """
    return _cbw.cbGetBoardNumber(descriptor)


_cbw.cbGetConfig.argtypes = [c_int, c_int, c_int, c_int, POINTER(c_int)]


def get_config(info_type, board_num, dev_num, config_item):
    """Returns a configuration option currently set for a board. By default, the configuration
    settings are loaded from the cb.cfg file created by InstaCal. If :func:`.ignore_instacal` is
    called first, the configuration settings will be the default values for the board in use. For
    either case, you can change the current configuration within a running program with the
    :func:`.set_config` function.

    Parameters
    ----------
    info_type : InfoType
        The configuration information for each board is grouped into different categories. This
        parameter specifies which category you want. Set it to one of the constants listed in the
        "info_type parameter values" below.
    board_num : int
        The number associated with the board when it was installed with InstaCal or created
        with :func:`.create_daq_device`.
    dev_num : int
        The purpose of the DevNum parameter depends on  on the value of the config_item parameter.
        It can serve as a channel number, an index into the config_item, or it can be ignored. See
        "specific config_item values" below.
    config_item : GlobalInfo, BoardInfo, DigitalInfo, CounterInfo, or ExpansionInfo
        Specifies which configuration item you wish to retrieve. Set it in conjunction with the
        info_type parameter using one of the constants listed in the "config_item parameter values"
        below.

    Returns
    -------
    int
        The specified configuration item


    .. table:: **info_type parameter values**

        =============  ===============================================
        info_type      Description
        =============  ===============================================
        GLOBALINFO     Information about the configuration file.
        BOARDINFO      General information about a board.
        DIGITALINFO    Information about a digital device. 
        COUNTERINFO    Information about a counter device.
        EXPANSIONINFO  Information about an expansion device.
        MISCINFO       One of the miscellaneous options for the board.
        =============  ===============================================


    .. table:: **config_item parameter values**

        +---------------+--------------------+----------------------------------------------------+
        | info_type     | config_item        | Description                                        |
        +===============+====================+====================================================+
        | GLOBALINFO    | VERSION            | cb.cfg file format; used by the library to         |
        |               |                    | determine compatibility.                           |
        |               |                    |                                                    |
        |               |                    | dev_num is ignored.                                |
        |               +--------------------+----------------------------------------------------+
        |               | NUMBOARDS          | Maximum number of boards that can be installed.    |
        |               |                    |                                                    |
        |               |                    | dev_num is ignored.                                |
        |               +--------------------+----------------------------------------------------+
        |               | NUMEXPBOARDS       | Maximum number of expansion boards that can be     |
        |               |                    | installed.                                         |
        |               |                    |                                                    |
        |               |                    | dev_num is ignored.                                |
        +---------------+--------------------+----------------------------------------------------+
        | BOARDINFO     | ADAIMODE           | Analog input mode.                                 |
        |               |                    |                                                    |
        |               |                    | dev_num is ignored.                                |
        |               +--------------------+----------------------------------------------------+
        |               | ADCHANAIMODE       | Analog input mode.                                 |
        |               |                    |                                                    |
        |               |                    | dev_num indicates the channel number.              |
        |               +--------------------+----------------------------------------------------+
        |               | ADCHANTYPE         | Analog input channel type. Use this setting with   |
        |               |                    | devices that have configurable input types.        |
        |               |                    | dev_num indicates the channel number.              |
        |               +--------------------+----------------------------------------------------+
        |               | ADCSETTLETIME      | ADC settling time.                                 |
        |               |                    |                                                    |
        |               |                    | dev_num is ignored.                                |
        |               +--------------------+----------------------------------------------------+
        |               | ADDATARATE         | A/D data rate.                                     |
        |               |                    |                                                    |
        |               |                    | dev_num indicates the channel number.              |
        |               +--------------------+----------------------------------------------------+
        |               | ADRES              | A/D resolution.                                    |
        |               |                    |                                                    |
        |               |                    | dev_num is ignored.                                |
        |               +--------------------+----------------------------------------------------+
        |               | ADXFERMODE         | Data transfer mode.                                |
        |               |                    |                                                    |
        |               |                    | dev_num is ignored.                                |
        |               +--------------------+----------------------------------------------------+
        |               | ADTIMINGMODE       | Timing mode.                                       |
        |               |                    |                                                    |
        |               |                    | dev_num is ignored.                                |
        |               +--------------------+----------------------------------------------------+
        |               | ADTRIGCOUNT        | Number of analog input samples to acquire per      |
        |               |                    | trigger.                                           |
        |               |                    |                                                    |
        |               |                    | dev_num is ignored.                                |
        |               +--------------------+----------------------------------------------------+
        |               | ADTRIGSRC          | A/D trigger source.                                |
        |               |                    |                                                    |
        |               |                    | dev_num indicates the channel number.              |
        |               +--------------------+----------------------------------------------------+
        |               | BASEADR            | Base address of the device.                        |
        |               |                    |                                                    |
        |               |                    | dev_num is ignored.                                |
        |               +--------------------+----------------------------------------------------+
        |               | BOARDTYPE          | Unique number from 0 to 8000 Hex which describes   |
        |               |                    | the type of board installed.                       |
        |               |                    |                                                    |
        |               |                    | dev_num is ignored.                                |
        |               +--------------------+----------------------------------------------------+
        |               | CALTABLETYPE       | The coefficients table used for calibration.       |
        |               |                    | 0 = Factory, 1 = Field.                            |
        |               |                    |                                                    |
        |               |                    | dev_num is either ignored or specifies a base or   |
        |               |                    | expansion board.                                   |
        |               +--------------------+----------------------------------------------------+
        |               | CHANRTDTYPE        | RTD sensor type.                                   |
        |               |                    |                                                    |
        |               |                    | dev_num indicates the channel number.              |
        |               +--------------------+----------------------------------------------------+
        |               | CHANTCTYPE         | Thermocouple sensor type.                          |
        |               |                    |                                                    |
        |               |                    | dev_num indicates the channel number.              |
        |               +--------------------+----------------------------------------------------+
        |               | CINUMDEVS          | Number of counter devices.                         |
        |               |                    |                                                    |
        |               |                    | dev_num is ignored.                                |
        |               +--------------------+----------------------------------------------------+
        |               | CLOCK              | Clock frequency in megahertz (MHz) (40, 10, 8, 6,  |
        |               |                    | 5, 4, 3, 2, 1) or 0 for not supported.             |
        |               |                    |                                                    |
        |               |                    | dev_num is ignored.                                |
        |               +--------------------+----------------------------------------------------+
        |               | CTRTRIGCOUNT       | Number of counter samples to acquire per trigger.  |
        |               |                    |                                                    |
        |               |                    | dev_num is ignored.                                |
        |               +--------------------+----------------------------------------------------+
        |               | DACFORCESENSE      | Remote sensing state of an analog output channel   |
        |               |                    | (ENABLED or DISABLED.)                             |
        |               |                    |                                                    |
        |               |                    | dev_num indicates the channel number.              |
        |               +--------------------+----------------------------------------------------+
        |               | DACRANGE           | Analog output voltage range.                       |
        |               |                    |                                                    |
        |               |                    | dev_num is ignored.                                |
        |               +--------------------+----------------------------------------------------+
        |               | DACRES             | D/A resolution.                                    |
        |               |                    |                                                    |
        |               |                    | dev_num is ignored.                                |
        |               +--------------------+----------------------------------------------------+
        |               | DACSTARTUP         | Configuration register STARTUP bit setting.        |
        |               |                    |                                                    |
        |               |                    | dev_num indicates the channel number.              |
        |               |                    |                                                    |
        |               |                    | Refer to the Notes section below for more          |
        |               |                    | information.                                       |
        |               +--------------------+----------------------------------------------------+
        |               | DACTRIGCOUNT       | Number of analog output samples to acquire per     |
        |               |                    | trigger.                                           |
        |               |                    |                                                    |
        |               |                    | dev_num is ignored.                                |
        |               +--------------------+----------------------------------------------------+
        |               | DACUPDATEMODE      | Update mode for a digital-to-analog converter      |
        |               |                    | (DAC).                                             |
        |               |                    |                                                    |
        |               |                    | dev_num is ignored.                                |
        |               |                    |                                                    |
        |               |                    | Refer to the Notes section below for more          |
        |               |                    | information.                                       |
        |               +--------------------+----------------------------------------------------+
        |               | DETECTOPENTC       | Open thermocouple detection setting. 0 = disabled, |
        |               |                    |  1 = enabled.                                      |
        |               |                    |                                                    |
        |               |                    | dev_num is either ignored or specifies a base or   |
        |               |                    | expansion board; refer to device-specific          |
        |               |                    | information.                                       |
        |               +--------------------+----------------------------------------------------+
        |               | DINUMDEVS          | Number of digital devices.                         |
        |               |                    |                                                    |
        |               |                    | dev_num is ignored.                                |
        |               +--------------------+----------------------------------------------------+
        |               | DISOFILTER         | AC filter setting. 0 = disabled, 1 = enabled.      |
        |               |                    |                                                    |
        |               |                    | dev_num is the bit number.                         |
        |               +--------------------+----------------------------------------------------+
        |               | DITRIGCOUNT        | Number of digital input samples to acquire per     |
        |               |                    | trigger.                                           |
        |               |                    |                                                    |
        |               |                    | dev_num is ignored.                                |
        |               +--------------------+----------------------------------------------------+
        |               | DMACHAN            | DMA channel - 0, 1, or 3.                          |
        |               |                    |                                                    |
        |               |                    | dev_num is ignored.                                |
        |               +--------------------+----------------------------------------------------+
        |               | DOTRIGCOUNT        | Number of digital output samples to generate per   |
        |               |                    | trigger.                                           |
        |               |                    |                                                    |
        |               |                    | dev_num is ignored.                                |
        |               +--------------------+----------------------------------------------------+
        |               | DTBOARD            | Board number of the connected DT board.            |
        |               |                    |                                                    |
        |               |                    | dev_num is ignored.                                |
        |               +--------------------+----------------------------------------------------+
        |               | EXTCLKTYPE         | External clock type.                               |
        |               |                    |                                                    |
        |               |                    | dev_num is ignored.                                |
        |               +--------------------+----------------------------------------------------+
        |               | EXTINPACEREDGE     | Input scan clock edge.                             |
        |               |                    |                                                    |
        |               |                    | dev_num is ignored.                                |
        |               +--------------------+----------------------------------------------------+
        |               | EXTOUTPACEREDGE    | Output scan clock edge.                            |
        |               |                    |                                                    |
        |               |                    | dev_num is ignored.                                |
        |               +--------------------+----------------------------------------------------+
        |               | INPUTPACEROUT      | Input pacer clock state.                           |
        |               |                    |                                                    |
        |               |                    | dev_num is ignored.                                |
        |               +--------------------+----------------------------------------------------+
        |               | INTEDGE            | Interrupt edge. 0 = rising, 1 = falling.           |
        |               |                    |                                                    |
        |               |                    | dev_num is ignored.                                |
        |               +--------------------+----------------------------------------------------+
        |               | INTLEVEL           | Interrupt level. 0 for none, or 1 to 15.           |
        |               |                    |                                                    |
        |               |                    | dev_num is ignored.                                |
        |               +--------------------+----------------------------------------------------+
        |               | NETCONNECTCODE     | Code used to connect with a device over a network  |
        |               |                    | connection.                                        |
        |               |                    |                                                    |
        |               |                    | dev_num is ignored.                                |
        |               +--------------------+----------------------------------------------------+
        |               | NETIOTIMEOUT       | Amount of time (in milliseconds) to wait for a WEB |
        |               |                    | device to acknowledge a command or query sent to   |
        |               |                    | the device over a network connection. If no        |
        |               |                    | acknowledgement is received in this time a timeout |
        |               |                    | occurs.                                            |
        |               |                    |                                                    |
        |               |                    | dev_num is ignored.                                |
        |               +--------------------+----------------------------------------------------+
        |               | NUMADCHANS         | Number of A/D channels                             |
        |               |                    |                                                    |
        |               |                    | dev_num is ignored.                                |
        |               +--------------------+----------------------------------------------------+
        |               | NUMDACHANS         | Number of D/A channels.                            |
        |               |                    |                                                    |
        |               |                    | dev_num is ignored.                                |
        |               +--------------------+----------------------------------------------------+
        |               | NUMIOPORTS         | Number of I/O ports used by the device.            |
        |               |                    |                                                    |
        |               |                    | dev_num is ignored.                                |
        |               +--------------------+----------------------------------------------------+
        |               | NUMTEMPCHANS       | Number of temperature channels.                    |
        |               |                    |                                                    |
        |               |                    | dev_num is ignored.                                |
        |               +--------------------+----------------------------------------------------+
        |               | PANID              | Personal Area Network (PAN) identifier for a USB   |
        |               |                    | device that supports wireless communication.       |
        |               |                    |                                                    |
        |               |                    | dev_num is ignored.                                |
        |               +--------------------+----------------------------------------------------+
        |               | PATTERNTRIGPORT    | Pattern trigger port.                              |
        |               |                    |                                                    |
        |               |                    | dev_num is ignored.                                |
        |               +--------------------+----------------------------------------------------+
        |               | RANGE              | Selected voltage range.                            |
        |               |                    |                                                    |
        |               |                    | dev_num is ignored.                                |
        |               |                    |                                                    |
        |               |                    | For switch selectable gains only. If the selected  |
        |               |                    | A/D board does not have a programmable gain        |
        |               |                    | feature, this argument returns the range as        |
        |               |                    | defined by the install settings.                   |
        |               +--------------------+----------------------------------------------------+
        |               | RFCHANNEL          | RF channel number used to transmit/receive data by |
        |               |                    | a USB device that supports wireless communication. |
        |               |                    |                                                    |
        |               |                    | dev_num is ignored.                                |
        |               +--------------------+----------------------------------------------------+
        |               | RSS                | Received signal strength in dBm of a remote        |
        |               |                    | device.                                            |
        |               |                    |                                                    |
        |               |                    | dev_num is ignored.                                |
        |               +--------------------+----------------------------------------------------+
        |               | SERIALNUM          | Custom serial number assigned by a user to a USB   |
        |               |                    | device. To retrieve the factory serial number, use |
        |               |                    | :func:`.get_config_string` with DEVUNIQUEID.       |
        |               |                    |                                                    |
        |               |                    | dev_num is ignored.                                |
        |               +--------------------+----------------------------------------------------+
        |               | SYNCMODE           | Simultaneous mode setting. 0 = master, 1 = slave.  |
        |               |                    |                                                    |
        |               |                    | dev_num is ignored.                                |
        |               +--------------------+----------------------------------------------------+
        |               | TEMPAVG            | Number of temperature samples per average.         |
        |               |                    |                                                    |
        |               |                    | dev_num is ignored.                                |
        |               +--------------------+----------------------------------------------------+
        |               | TEMPSCALE          | Temperature scale.                                 |
        |               |                    |                                                    |
        |               |                    | dev_num is ignored.                                |
        |               +--------------------+----------------------------------------------------+
        |               | TEMPREJFREQ        | Temperature rejection frequency.                   |
        |               |                    |                                                    |
        |               |                    | dev_num is either ignored or specifies a base or   |
        |               |                    | expansion board.                                   |
        |               +--------------------+----------------------------------------------------+
        |               | TERMCOUNTSTATBIT   | Terminal count output status for a specified bit.  |
        |               |                    |                                                    |
        |               |                    | dev_num indicates the bit number. 0 = enabled,     |
        |               |                    | 1 = disabled.                                      |
        |               +--------------------+----------------------------------------------------+
        |               | WAITSTATE          | Wait State jumper setting. 0 = disabled,           |
        |               |                    | 1 = enabled.                                       |
        |               |                    |                                                    |
        |               |                    | dev_num is ignored.                                |
        |               +--------------------+----------------------------------------------------+
        |               | USESEXPS           | Expansion board support. TRUE/FALSE value is       |
        |               |                    | returned.                                          |
        |               |                    |                                                    |
        |               |                    | dev_num is ignored.                                |
        |               +--------------------+----------------------------------------------------+
        |               | USERDEVIDNUM       | User-configured string that identifies a USB       |
        |               |                    | device.                                            |
        |               |                    |                                                    |
        |               |                    | dev_num is ignored.                                |
        +---------------+--------------------+----------------------------------------------------+
        | DIGITALINFO   | DEVTYPE            | Device Type - AUXPORT, FIRSTPORTA, and so on.      |
        |               |                    |                                                    |
        |               |                    | dev_num indicates a zero-based index that          |
        |               |                    | specifies the device.                              |
        |               +--------------------+----------------------------------------------------+
        |               | CONFIG             | Current configuration INPUT or OUTPUT.             |
        |               |                    |                                                    |
        |               |                    | dev_num indicates a zero-based index that          |
        |               |                    | specifies the device.                              |
        |               +--------------------+----------------------------------------------------+
        |               | NUMBITS            | Number of bits in the port.                        |
        |               |                    |                                                    |
        |               |                    | dev_num indicates a zero-based index that          |
        |               |                    | specifies the device.                              |
        |               +--------------------+----------------------------------------------------+
        |               | CURVAL             | Current value of outputs.                          |
        |               |                    |                                                    |
        |               |                    | dev_num indicates a zero-based index that          |
        |               |                    | specifies the device.                              |
        |               +--------------------+----------------------------------------------------+
        |               | DISABLEDIRCHECK    | The direction check setting for a specified port   |
        |               |                    | or bit when calling :func:`.d_out`,                |
        |               |                    | :func:`.d_bit_out`, and :func:`.d_out_array`.      |
        |               |                    | 0 = enabled, 1 = disabled.                         |
        |               |                    |                                                    |
        |               |                    |                                                    |
        |               +--------------------+----------------------------------------------------+
        |               | INMASK             | Bit configuration of the specified port. Any bits  |
        |               |                    | that return a value of 1 are configured for input. |
        |               |                    | Refer to the Notes section below for additional    |
        |               |                    | information about using the INMASK option.         |
        |               |                    |                                                    |
        |               |                    | dev_num indicates a zero-based index that          |
        |               |                    | specifies the device.                              |
        |               +--------------------+----------------------------------------------------+
        |               | OUTMASK            | Bit configuration of the specified port. Any bits  |
        |               |                    | that return a value of 1 are configured for        |
        |               |                    | output. Refer to the Notes section below for       |
        |               |                    | additional information about using the OUTMASK     |
        |               |                    | option.                                            |
        |               |                    |                                                    |
        |               |                    | dev_num indicates a zero-based index that          |
        |               |                    | specifies the device.                              |
        +---------------+--------------------+----------------------------------------------------+
        | COUNTERINFO   | CTRNUM             | Counter number associated with the given dev_num.  |
        |               |                    |                                                    |
        |               |                    |                                                    |
        |               +--------------------+----------------------------------------------------+
        |               | CTRTYPE            | Counter type, where:                               |
        |               |                    |                                                    |
        |               |                    | 1 = 8254, 2 = 9513, 3 = 8536, 4 = 7266, 5 = event  |
        |               |                    | counter, 6 = scan counter, 7 = timer counter,      |
        |               |                    | 8 = quadrature counter, and 9 = pulse counter.     |
        |               |                    |                                                    |
        |               |                    | dev_num indicates a zero-based index that          |
        |               |                    | specifies the device.                              |
        +---------------+--------------------+----------------------------------------------------+
        | EXPANSIONINFO | BOARDTYPE          | Board type (refer to the "Measurement Computing    |
        |               |                    | Device IDs topic in the Universal Library User's   |
        |               |                    | Guide)                                             |
        |               +--------------------+----------------------------------------------------+
        |               | MUXADCHAN1         | First A/D channel connected to the EXP board.      |
        |               +--------------------+----------------------------------------------------+
        |               | MUXADCHAN2         | Second A/D channel connected to the EXP board.     |
        |               +--------------------+----------------------------------------------------+
        |               | RANGE1             | Range (gain) of the low 16 channels.               |
        |               +--------------------+----------------------------------------------------+
        |               | RANGE2             | Range (gain) of the high 16 channels.              |
        |               +--------------------+----------------------------------------------------+
        |               | CJCCHAN            | A/D channel connected to the CJC.                  |
        |               +--------------------+----------------------------------------------------+
        |               | THERMTYPE          | Sensor type. Use one of the sensor types listed    |
        |               |                    | below:                                             |
        |               |                    |                                                    |
        |               |                    | 1 = J, 2 = K, 3 = T, 4 = E, 5 = R, 6 = S, 7 = B,   |
        |               |                    | 257 = Platinum .00392, 258 = Platinum .00391,      |
        |               |                    | 259 = Platinum .00385, 260 = Copper .00427,        |
        |               |                    | 261 = Nickel/Iron .00581, 262 = Nickel/Iron .00527 |
        |               +--------------------+----------------------------------------------------+
        |               | NUMEXPCHANS        | Number of channels on the expansion board.         |
        |               |                    |                                                    |
        |               |                    | dev_num is ignored.                                |
        |               +--------------------+----------------------------------------------------+
        |               | PARENTBOARD        | Board number of the base A/D board.                |
        |               |                    |                                                    |
        |               |                    | dev_num is ignored.                                |
        +---------------+--------------------+----------------------------------------------------+

    Notes
    -----
    - Use the BoardInfo.DACSTARTUP option to determine whether a board's DAC values before the last
      power down are stored.

      With config_item set to BoardInfo.DACSTARTUP, this function returns 0 when the startup bit is
      disabled. Current DAC settings are stored as startup values.

      This function returns 1 when the startup bit is enabled. The last DAC values are stored as
      startup values.

      Refer to the :func:`.set_config` Notes section for information about how to store the current
      or last DAC values as start-up values.

    - Use the BoardInfo.DACUPDATEMODE option to check the update mode for a DAC board.

      With config_item set to BoardInfo.DACUPDATEMODE, this function returns 0 when the DAC update
      mode is immediate. Values written with :func:`.a_out` are automatically output by the DAC 
      channels.

      This function returns 1 when the DAC update mode is set to on command. Values written with
      :func:`.a_out` are not output by the DAC channels until a :func:`.set_config` call is made
      with its config_item parameter set to BoardInfo.DACUPDATECMD.

    - Use the DigitalInfo.INMASK and DigitalInfo.OUTMASK options to determine if an AUXPORT is
      configurable. Execute :func:`.get_config` twice to the same port - once using
      DigitalInfo.INMASK and once using DigitalInfo.OUTMASK. If the calls return input and output
      bits that overlap, the port is not configurable.

      You can determine overlapping bits by ANDing both parameters.

      Example: for a device with seven bits of digital I/O (four outputs and three inputs), the
      result of DigitalInfo.INMASK is always 7 (0000 0111), while the result of DigitalInfo.OUTMASK
      is always 15 (0000 1111). When you AND both results together, you get a non-zero number (7).
      Any non-zero number indicates that input and output bits overlap for the specified port, and
      the port is a non-configurable AUXPORT.
    """
    config_val = c_int32()
    _check_err(_cbw.cbGetConfig(
        info_type, board_num, dev_num, config_item, byref(config_val)))
    return config_val.value


_cbw.cbGetConfigString.argtypes = [
    c_int, c_int, c_int, c_int, c_char_p, POINTER(c_int)]


def get_config_string(info_type, board_num, dev_num, config_item, max_config_len):
    """Returns configuration or device information as a null-terminated string.

    Parameters
    ----------
    info_type : InfoType
        The configuration information for each board is grouped into different categories. This
        parameter specifies which category you want. Always set this parameter to
        InfoType.BOARDINFO.
    board_num : int
        The number associated with the board when it was installed with InstaCal or created
        with :func:`.create_daq_device`.
    dev_num : int
        The purpose of the dev_num parameter depends on the value of the config_item parameter. It
        can serve as a channel number, an index into the config_item, or it can be ignored.

        Unless otherwise noted in the "config_item parameter values" section below, this value is
        ignored.
    config_item : BoardInfo
        The type of information to read from the device. Set it to one of the constants listed in
        the "config_item parameter values" section below.
    max_config_len : int
        The maximum number of bytes to be read from the device into config_val.

    Returns
    -------
    string
        The specified configuration item


    .. table:: **config_item parameter values**

        ============  =============================================================================
        config_item   Description
        ============  =============================================================================
        DEVMACADDR     MAC address of an Ethernet device.
        ------------  -----------------------------------------------------------------------------
        DEVSERIALNUM   Factory serial number of a USB or Bluetooth device.

                       dev_num specifies either a base board (0) or an expansion board (1). 
        ------------  -----------------------------------------------------------------------------
        DEVUNIQUEID    Unique identifier of a discoverable device, such as the serial number of a
                       USB device or MAC address of an Ethernet device. 
        ------------  -----------------------------------------------------------------------------
        DEVVERSION     Firmware version and FPGA version installed on a device.

                       Use this setting in conjunction with one of these dev_num settings: 
                       - MAIN (main firmware version) 
                       - MEASUREMENT (measurement firmware version) 
                       - MEASUREMENT_EXP (expansion board measurement firmware version) 
                       - RADIO (radio firmware version) 
                       - FPGA (FPGA version) 
        ------------  -----------------------------------------------------------------------------
        USERDEVID      User-configured string identifier of up to maxConfigLen character/bytes from
                       an Ethernet, Bluetooth, or USB device. 
        ============  =============================================================================
    """
    config_val = create_string_buffer(max_config_len)
    _check_err(_cbw.cbGetConfigString(
        info_type, board_num, dev_num, config_item,
        config_val, byref(c_int(max_config_len))))
    return config_val.value.decode('utf-8')


_cbw.cbGetDaqDeviceInventory.argtypes = [
    c_uint, POINTER(DaqDeviceDescriptor), POINTER(c_int)]


def get_daq_device_inventory(interface_type, number_of_devices=100):
    """Detects USB, Bluetooth and/or Ethernet DAQ devices, and returns device descriptors of the
    detected devices.

    This function detects Ethernet DAQ devices on the same subnet as the host PC. To detect
    Ethernet DAQ devices on a different subnet than the host PC, use
    :func:`.get_net_device_descriptor`.

    interface_type : InterfaceType
        Flags that specify the interface type of the DAQ device(s) to be detected. This parameter
        may contain any combination of the values listed in the "interface_type parameter values"
        section below.
    number_of_devices : int, optional
        Maximum number of elements that the result can hold. This value defaults to 100.

    Returns
    -------
    list of DaqDeviceDescriptor
        A list of DaqDeviceDescriptor objects that describe the detected DAQ devices


    .. table:: **interface_type parameter values**

        =========  =============================
        ANY        Any supported interface type.
        BLUETOOTH  Bluetooth device.
        ETHERNET   Ethernet device.
        USB        USB device.
        =========  =============================
    """
    # Create a c array to hold the descriptors
    devices = (DaqDeviceDescriptor * number_of_devices)()
    number_of_devices = c_int(number_of_devices)
    _check_err(_cbw.cbGetDaqDeviceInventory(
        interface_type, devices, byref(number_of_devices)))
    # Build a Python list from the c array
    devices_list = [devices[i] for i in range(number_of_devices.value)]
    return devices_list


def get_err_msg(error_code):
    """Returns the error message associated with an error code. It is usually unnecessary to use
    this method externally, since ULError errors raised by this module assign the value to the
    message property. Some functions do return an error code in cases where it is used as a
    warning. Call this function to convert the returned error code to a descriptive error message.

    Parameters
    ----------
    error_code
        The error code that is returned by some functions in this library.

    Returns
    -------
    string
        The error message associated with the given error_code
    """
    msg = create_string_buffer(_ERRSTRLEN)
    _check_err(_cbw.cbGetErrMsg(error_code, msg))
    return msg.value.decode('utf-8')


StatusResult = collections.namedtuple(
    "StatusResult", "status cur_count cur_index")
_cbw.cbGetIOStatus.argtypes = [c_int, POINTER(
    c_short), POINTER(c_long), POINTER(c_long), c_int]


def get_status(board_num, function_type):
    """Returns the status about the background operation currently running.

    Parameters
    ----------
    board_num : int
        The number associated with the board when it was installed with InstaCal or created
        with :func:`.create_daq_device`.
    function_type : FunctionType
        Specifies which scan to retrieve status information about. Refer to the "function_type
        parameter values" section below.

    Returns
    -------
    status : Status
        Value indicating whether or not a background process is currently executing.
    cur_count : int
        The number of points that have been input or output since the Background process started.
        Use it to gauge how far along the operation is towards completion. Generally, cur_count
        is the total number of samples transferred between the DAQ board and the Windows data
        buffer at the time :func:`.get_status` was called.

        When you set both the :const:`~mcculw.enums.ScanOptions.CONTINUOUS` and
        :const:`~mcculw.enums.ScanOptions.BACKGROUND` options, cur_count's behavior depends on the
        board model. Refer to the board-specific information in the Universal Library User's Guide
        for the behavior of your board.

        With recent MCC DAQ designs, the cur_count parameter continually increases in increments of
        the packet size as Windows' circular data buffer recycles, until it reaches 2**31. Since
        the count parameter is a signed integer, at 2,147,483,647 + 1, the count rolls back to a
        negative number (-2,147,483,647). The count parameter resumes incrementing, eventually
        reaching 0 and increasing back up to 2,147,483,647.

        The cur_index value is usually more useful than cur_count in managing data collected when
        you set both the :const:`~mcculw.enums.ScanOptions.CONTINUOUS` and
        :const:`~mcculw.enums.ScanOptions.BACKGROUND` options.
    cur_index : int
        The cur_index value is an index into the Windows data buffer. This index points to the
        start of the last completed channel scan that was transferred between the DAQ board and
        the Windows data buffer. If no points in the buffer have been transferred, cur_index equals
        -1 in most cases.

        For :const:`~mcculw.enums.ScanOptions.CONTINUOUS` operations, cur_index rolls over when the
        Windows data buffer is full. This rollover indicates that "new" data is now overwriting
        "old" data. Your goal is to process the old data before it gets overwritten. You can keep
        ahead of the data flow by copying the old data out of the buffer before new data overwrites
        it.

        The cur_index value can help you access the most recently transferred data. Your
        application does not have to process the data exactly when it becomes available in the
        buffer - in fact, you should avoid doing so unless absolutely necessary. The cur_index
        parameter generally increments by the packet size, but in some cases the cur_index
        increment can vary within the same scan. One instance of a variable increment is when the
        packet size is not evenly divisible by the number of channels.

        You should determine the best size of the "chunks" of data that your application can most
        efficiently process, and then periodically check on the cur_index parameter value to
        determine when that amount of additional data has been transferred.

        Refer to the Universal Library User's Guide for information on your board, particularly
        when using pre-trigger.


    .. table:: **function_type parameter values**

        ============  =============================================================================
        AIFUNCTION    Specifies analog input scans started with :func:`.a_in_scan` or
                      :func:`.a_pretrig`. 
        AOFUNCTION    Specifies analog output scans started with :func:`.a_out_scan`. 
        DIFUNCTION    Specifies digital input scans started with :func:`.d_in_scan`. 
        DOFUNCTION    Specifies digital output scans started with :func:`.d_out_scan`. 
        CTRFUNCTION   Specifies counter background operations started with :func:`.c_in_scan`. 
        DAQIFUNCTION  Specifies a synchronous input scan started with :func:`.daq_in_scan`. 
        DAQOFUNCTION  Specifies a synchronous output scan started with :func:`.daq_out_scan`. 
        ============  =============================================================================
    """
    status = c_short()
    cur_count = c_long()
    cur_index = c_long()
    _check_err(_cbw.cbGetIOStatus(
        board_num, byref(status), byref(cur_count), byref(cur_index), function_type))
    return StatusResult(Status(status.value), cur_count.value, cur_index.value)


_cbw.cbGetNetDeviceDescriptor.argtypes = [
    c_char_p, c_int, POINTER(DaqDeviceDescriptor), c_int]


def get_net_device_descriptor(host, port, timeout):
    """Returns the DAQ device descriptor at the specified IP address or host name.

    This function can detect Ethernet DAQ devices on a different subnet than the host PC. To detect
    Ethernet DAQ devices on the same subnet as the host PC, it's more convenient to use
    :func:`.get_daq_device_inventory`.

    Parameters
    ----------
    host : string
        The name of the host, or the IP address of the host.
    port : int
        The port number, for example 54211; refer to board-specific information.
    timeout : int
        The timeout value in milliseconds (ms).

    Returns
    -------
    DaqDeviceDescriptor
        The device descriptor of the detected device
    """
    result = DaqDeviceDescriptor()
    _check_err(_cbw.cbGetNetDeviceDescriptor(
        host.encode('utf8'), port, byref(result), timeout))
    return result


TCValuesResult = collections.namedtuple(
    "TCValuesResult", "err_code data_array")
_cbw.cbGetTCValues.argtypes = [c_int, POINTER(c_short), POINTER(c_short), c_int,
                               HGLOBAL, c_int, c_long, c_int, POINTER(c_float)]


def get_tc_values(board_num, chan_list, chan_type_list, chan_count, memhandle, first_point,
                  count, scale, data_array=None):
    """Converts raw thermocouple data collected using the :func:`.daq_in_scan` function to data on a
    temperature scale (Celsius, Fahrenheit, or Kelvin).

    Parameters
    ----------
    board_num : int
        The number associated with the board when it was installed with InstaCal or created
        with :func:`.create_daq_device`.
    chan_list : list of int or DigitalPortType
        list containing channel values. Valid channel values are analog and temperature input
        channels and digital ports. chan_list must match the channel list used with the
        :func:`.daq_in_scan` function.
    chan_type_list : list of ChannelType
        list containing channel types. Each element of this list defines the type of the
        corresponding element in the chan_list. chan_type_list must match the channel type settings
        used with the :func:`.daq_in_scan` function
    chan_count :int
        Number of elements in each of the two lists - chan_list and chan_type_list
    memhandle : int
        This must be a memory handle that was returned by :func:`.win_buf_alloc` when the buffer was
        allocated. The buffer should contain the data that you want to convert.
    first_point : int
        The index into the raw data memory buffer that holds the first sample of the first channel
        to be converted. The index into the raw memory is (first_point x chan_count) so that
        converted data always starts with the first channel specified in the scan. For example, if
        first_point is 14 and the number of channels is 8, the index of the first converted sample
        is 112.
    count : int
        The number of samples per channel to convert to engineering units. count should not exceed
        Windows buffer size / chan_count - first_point.
    scale : TempScale
        Specifies the temperature scale that the input will be converted to. Choices are
        TempScale.CELSIUS, TempScale.FAHRENHEIT and TempScale.KELVIN.
    data_array : POINTER(c_float), optional
        Pointer to the temperature data array. If this parameter is omitted (or None), the array
        will be allocated by this function. Reusing the array by passing it in as the parameter may
        be useful as an optimization to prevent excessive allocations, saving memory and CPU time.

        This array must be large enough to hold count samples * the number of temperature channels.

    Returns
    -------
    err_code : int
        The error code, which will either be ErrorCode.OUTOFRANGE or ErrorCode.NOERRORS.
        ErrorCode.OUTOFRANGE will be returned if any of the converted data is out of range. This
        typically indicates an open TC connection. All other errors will raise a ULError as usual.
    data_array : POINTER(c_float)
        A pointer to the C array containing the converted temperature data
    """

    if data_array == None:
        # Find the number of TC channels
        num_tc_chans = sum(
            chan_type == ChannelType.TC for chan_type in chan_type_list)
        # Create the buffer
        data_array = (c_float * int(num_tc_chans * count))()

    err_code = _cbw.cbGetTCValues(
        board_num, _to_ctypes_array(chan_list, c_short),
        _to_ctypes_array(
            chan_type_list, c_short), chan_count, memhandle, first_point,
        count, scale, data_array)
    if err_code != ErrorCode.OUTOFRANGE:
        _check_err(err_code)
    return TCValuesResult(err_code, data_array)


def ignore_instacal():
    """Prevents the Universal Library from automatically adding a DAQ device that has been stored
    in the cb.cfg file by InstaCal. This function must be the first Universal Library function
    invoked in the application. Devices can then be added and configured at runtime using the
    device discovery features. Refer to the "InstaCal, API Detection, or Both?" section of the
    Universal Library User's Guide for additional information.
    """
    _check_err(_cbw.cbIgnoreInstaCal())


PulseOutStartResult = collections.namedtuple(
    "PulseOutStartResult",
    "actual_frequency actual_duty_cycle actual_initial_delay")
_cbw.cbPulseOutStart.argtypes = [c_int, c_int, POINTER(c_double), POINTER(c_double),
                                 c_uint, POINTER(c_double), c_int, c_int]


def pulse_out_start(board_num, timer_num, frequency, duty_cycle, pulse_count=0, initial_delay=0,
                    idle_state=TimerIdleState.LOW, options=PulseOutOptions.NONE):
    """Starts a timer to generate digital pulses at a specified frequency and duty cycle. Use
    :func:`.pulse_out_stop` to stop the output.

    Parameters
    ----------
    board_num : int
        The number associated with the board when it was installed with InstaCal or created
        with :func:`.create_daq_device`.
    timer_num : int
        The timer to start output pulses. Valid values are zero (0) up to the number of timers on
        the board - 1.
    frequency : float
        The desired square wave frequency in Hz. The timer clock will be divided down by integer
        values to calculate the frequency. The actual frequency output will be returned. Valid
        values are dependent on the timer's clock and the timer resolution.
    duty_cycle : float
        The width of the pulse divided by the pulse period. This ratio is used with the frequency
        value to determine the pulse width and the interval between pulses.
    pulse_count : int, optional
        The number of pulses to generate. Setting the pulse count to zero (0) will result in pulses
        being generated until the :func:`.pulse_out_stop` function is called. Defaults to 0.
    initial_delay : float, optional
        The amount of time in seconds to delay before starting the timer output after enabling the
        output. Defaults to 0.
    idle_state : TimerIdleState, optional
        The resting state of the output. Defaults to TimerIdleState.LOW
    options : PulseOutOptions, optional
        Flags that control various options. This field may contain any combination of
        non-contradictory choices from the values listed in the "options parameter values" section
        below. Defaults to PulseOutOptions.NONE

    Returns
    -------
    actual_frequency : float
        The actual frequency set, which may be different from the requested frequency because of
        pacer limitations.
    actual_duty_cycle : float
        The actual duty cycle set, which may be different from the requested duty cycle because of
        pacer limitations.
    actual_initial_delay : float
        The actual initial delay set, which may be different from the requested initial delay
        because of pacer limitations.


    .. table:: **options parameter values**

        ==========  ===============================================================================
        EXTTRIGGER  If this option is specified, output pulses are not generated until the trigger
                    condition is met. You can set the trigger condition to rising edge, falling
                    edge, or the level of the digital trigger input (TTL) with the
                    :func:`.set_trigger` function. Refer to board-specific information. 
        ==========  ===============================================================================
    """
    frequency_internal = c_double(frequency)
    duty_cycle_internal = c_double(duty_cycle)
    initial_delay_internal = c_double(initial_delay)
    _check_err(_cbw.cbPulseOutStart(
        board_num, timer_num, byref(
            frequency_internal), byref(duty_cycle_internal),
        pulse_count, byref(initial_delay_internal), idle_state, options))
    return PulseOutStartResult(
        frequency_internal.value, duty_cycle_internal.value, initial_delay_internal.value)


_cbw.cbPulseOutStop.argtypes = [c_int, c_int]


def pulse_out_stop(board_num, timer_num):
    """Stops a timer output. Use :func:`.pulse_out_start` to start the output.

    Parameters
    ----------
    board_num : int
        The number associated with the board when it was installed with InstaCal or created
        with :func:`.create_daq_device`.
    timer_num : int
        The timer to stop. Valid values are zero (0) up to the number of timers on the board - 1.
    """
    _check_err(_cbw.cbPulseOutStop(board_num, timer_num))


_cbw.cbReleaseDaqDevice.argtypes = [c_int]


def release_daq_device(board_num):
    """Removes the specified DAQ device from the Universal Library, and releases all resources
    associated with that device.

    Parameters
    ----------
    board_num : int
        The number associated with the board when it was installed with InstaCal or created
        with :func:`.create_daq_device`.
    """
    _cbw.cbReleaseDaqDevice(board_num)


_cbw.cbScaledWinArrayToBuf.argtypes = [
    POINTER(c_double), HGLOBAL, c_long, c_long]


def scaled_win_array_to_buf(data_array, memhandle, first_point, count):
    """Copies double precision values from an array into a Windows memory buffer.

    The buffer is used by devices that support output scanning of scaled data, for example devices
    that call :func:`.a_out_scan` using the :const:`~mcculw.enums.ScanOptions.SCALEDATA` option.
    Create the buffer with :func:`.scaled_win_buf_alloc`. See hardware-specific information to
    determine if the device supports scaled data.

    Parameters
    ----------
    data_array : POINTER(c_double)
        The C array containing the data to be copied.
    memhandle : int
        This must be a memory handle that was returned by :func:`.scaled_win_buf_alloc` when the
        buffer was allocated. The data will be copied into this buffer.
    first_point : int
        Index of the first point in the memory buffer where the data will be copied.
    count : int
        Number of data points to copy.

    Notes
    -----
    This function is used in conjunction with the :const:`~mcculw.enums.ScanOptions.SCALEDATA` scan 
    option and :func:`.scaled_win_buf_alloc`.
    """
    _check_err(_cbw.cbScaledWinArrayToBuf(
        data_array, memhandle, first_point, count))


_cbw.cbScaledWinBufAlloc.argtypes = [c_long]
_cbw.cbScaledWinBufAlloc.restype = HGLOBAL


def scaled_win_buf_alloc(num_points):
    """Allocates a Windows global memory buffer large enough to hold scaled data obtained from scan
    operations in which the :const:`~mcculw.enums.ScanOptions.SCALEDATA` scan option is selected,
    and returns a memory handle for it.

    The buffer is used by devices that support scanning of scaled data, for example devices that
    call :func:`.a_out_scan` using the :const:`~mcculw.enums.ScanOptions.SCALEDATA` option. See
    hardware-specific information to determine if the device supports scaled data.

    Parameters
    ----------
    num_points
        The size of the buffer to allocate. Specifies the number of double precision values
        (8-byte or 64-bit) that the buffer will hold.

    Returns
    -------
    int
        0 if the buffer could not be allocated, or a non-zero integer handle to the buffer.

    Notes
    -----
    - This function is used in conjunction with the :const:`~mcculw.enums.ScanOptions.SCALEDATA`
      scan option and :func:`.scaled_win_buf_to_array` or :func:`.scaled_win_array_to_buf`.

    - Unlike most other functions in the library, this function does not raise a ULError. It
      returns a Windows global memory handle which can then be passed to the scan functions in the
      library. If an error occurs, the handle will come back as 0 to indicate that the buffer was
      not allocated.
    """
    return _cbw.cbScaledWinBufAlloc(num_points)


_cbw.cbScaledWinBufToArray.argtypes = [
    HGLOBAL, POINTER(c_double), c_long, c_long]


def scaled_win_buf_to_array(memhandle, data_array, first_point, count):
    """Copies double precision values from a Windows memory buffer into an array.

    The buffer is used by devices that support scanning of scaled data, for example devices that
    call :func:`.a_in_scan` using the :const:`~mcculw.enums.ScanOptions.SCALEDATA` option. See
    hardware-specific information to determine if the device supports scaled data.

    Parameters
    ----------
    memhandle : int
        This must be a memory handle that was returned by :func:`.scaled_win_buf_alloc` when the
        buffer was allocated. The buffer should contain the data that you want to copy.
    data_array : POINTER(c_double)
        A pointer to the start of the destination array to which the data samples are copied.
    first_point : int
        The buffer index of the first sample to copy from the buffer.
    count : int
        The number of samples to copy into data_array.

    Notes
    -----
    This function is used in conjunction with the :const:`~mcculw.enums.ScanOptions.SCALEDATA`
    scan option and :func:`.scaled_win_buf_alloc`.
    """
    _check_err(_cbw.cbScaledWinBufToArray(
        memhandle, data_array, first_point, count))


_cbw.cbSetConfig.argtypes = [c_int, c_int, c_int, c_int, c_int]


def set_config(info_type, board_num, dev_num, config_item, config_val):
    """Changes board configuration options at runtime.

    By default, the configuration settings are loaded from the cb.cfg file created by InstaCal.
    If :func:`.ignore_instacal` is called first, the configuration settings will be the default
    values for the board in use. For either case, you can change the current configuration within a
    running program using this function.

    Parameters
    ----------
    info_type : InfoType
        The configuration information for each board is grouped into different categories. InfoType
        specifies which category you want. Set it to one of the constants listed in the "info_type
        parameter values" section below.
    board_num : int
        The number associated with the board when it was installed with InstaCal or created
        with :func:`.create_daq_device`.
    dev_num : int
        The purpose of the dev_num parameter depends on the value of the config_item parameter. It
        can serve as a channel number, an index into the config_item, or it can be ignored. See
        "config_item parameter values" below.
    config_item :
        Specifies which configuration item you wish to set. Set it in conjunction with the
        info_type parameter using the table under config_item parameter values section below.
    config_val : BoardInfo, DigitalInfo, CounterInfo, or ExpansionInfo
        The value to set the specified configuration item to.


    .. table:: **info_type parameter values**

        =============  ===============================================
        info_type      Description
        =============  ===============================================
        GLOBALINFO     Information about the configuration file.
        BOARDINFO      General information about a board.
        DIGITALINFO    Information about a digital device. 
        COUNTERINFO    Information about a counter device.
        EXPANSIONINFO  Information about an expansion device.
        MISCINFO       One of the miscellaneous options for the board.
        =============  ===============================================


    .. table:: **config_item parameter values**

        +---------------+-------------------+-----------------------------------------------------+
        | info_type     | config_item       | Explanation                                         |
        +===============+===================+=====================================================+
        | BOARDINFO     | ADCHANTYPE        | Analog input channel type. Use this setting with    |
        |               |                   | devices that have configurable input types.         |
        |               |                   |                                                     |
        |               |                   | dev_num indicates the channel number.               |
        |               |                   |                                                     |
        |               |                   | Set config_val to one of the                        |
        |               |                   | :class:`~mcculw.enums.AiChanType` enum values.     |
        |               +-------------------+-----------------------------------------------------+
        |               | ADCSETTLETIME     | ADC settling time.                                  |
        |               |                   | dev_num is ignored.                                 |
        |               |                   |                                                     |
        |               |                   |                                                     |
        |               |                   | Set config_val to one of the                        |
        |               |                   | :class:`~mcculw.enums.SettleTime` enum values.     |
        |               +-------------------+-----------------------------------------------------+
        |               | ADDATARATE        | A/D data rate.                                      |
        |               |                   |                                                     |
        |               |                   | dev_num indicates the channel number.               |
        |               +-------------------+-----------------------------------------------------+
        |               | ADTIMINGMODE      | ADC timing mode.                                    |
        |               |                   |                                                     |
        |               |                   | dev_num is ignored.                                 |
        |               |                   |                                                     |
        |               |                   | Set config_val to one of the                        |
        |               |                   | :class:`~mcculw.enums.AdTimingMode` enum values.   |
        |               +-------------------+-----------------------------------------------------+
        |               | ADTRIGCOUNT       | ADC trigger count.                                  |
        |               |                   |                                                     |
        |               |                   | dev_num is ignored.                                 |
        |               |                   |                                                     |
        |               |                   | For use with the :func:`.a_in_scan`                 |
        |               |                   | :const:`~mcculw.enums.ScanOptions.RETRIGMODE`      |
        |               |                   | option to set up repetitive trigger events.         |
        |               +-------------------+-----------------------------------------------------+
        |               | ADTRIGSRC         | A/D trigger source.                                 |
        |               |                   |                                                     |
        |               |                   | dev_num indicates the channel number.               |
        |               |                   |                                                     |
        |               |                   | Set config_val to 0, 1, 2, or 3.                    |
        |               +-------------------+-----------------------------------------------------+
        |               | ADXFERMODE        | Sets the data transfer mode to either kernel mode   |
        |               |                   | (default) or user mode.                             |
        |               |                   |                                                     |
        |               |                   | dev_num is ignored.                                 |
        |               |                   |                                                     |
        |               |                   | Set config_val to one of the                        |
        |               |                   | :class:`~mcculw.enums.XferMode` enum values.       |
        |               +-------------------+-----------------------------------------------------+
        |               | BASEADR           | Base address of the device.                         |
        |               |                   |                                                     |
        |               |                   | dev_num is ignored.                                 |
        |               +-------------------+-----------------------------------------------------+
        |               | CALTABLETYPE      | Coefficients table used for calibration.            |
        |               |                   |                                                     |
        |               |                   | dev_num is ignored.                                 |
        |               |                   |                                                     |
        |               |                   | Set config_val to one of the                        |
        |               |                   | :class:`~mcculw.enums.CalTable` enum values.       |
        |               +-------------------+-----------------------------------------------------+
        |               | CALOUTPUT         | Cal pin voltage on supported USB devices.           |
        |               |                   |                                                     |
        |               |                   | dev_num is ignored.                                 |
        |               +-------------------+-----------------------------------------------------+
        |               | CHANRTDTYPE       | RTD sensor type.                                    |
        |               |                   |                                                     |
        |               |                   | dev_num indicates the channel number.               |
        |               |                   |                                                     |
        |               |                   | Set config_val to one of the                        |
        |               |                   | :class:`~mcculw.enums.PlatinumRTDType` enum values.|
        |               +-------------------+-----------------------------------------------------+
        |               | CHANTCTYPE        | Thermocouple sensor type.                           |
        |               |                   |                                                     |
        |               |                   | dev_num indicates the channel number.               |
        |               |                   |                                                     |
        |               |                   | Set config_val to one of the                        |
        |               |                   | :class:`~mcculw.enums.TcType` enum values.         |
        |               +-------------------+-----------------------------------------------------+
        |               | CLOCK             | Clock frequency in megahertz (MHz)                  |
        |               |                   |                                                     |
        |               |                   | dev_num indicates the channel number.               |
        |               |                   |                                                     |
        |               |                   | Set config_val to one of the following values:      |
        |               |                   |                                                     |
        |               |                   | 1, 4, 6 or 10.                                      |
        |               +-------------------+-----------------------------------------------------+
        |               | CTRTRIGCOUNT      | Number of counter samples to acquire per trigger.   |
        |               |                   |                                                     |
        |               |                   | dev_num is ignored.                                 |
        |               |                   |                                                     |
        |               |                   | For use with the :func:`.c_in_scan`                 |
        |               |                   | :const:`~mcculw.enums.ScanOptions.RETRIGMODE`      |
        |               |                   | option to set up repetitive trigger events.         |
        |               +-------------------+-----------------------------------------------------+
        |               | DACFORCESENSE     | Enables or disables remote sensing of an analog     |
        |               |                   | output channel.                                     |
        |               |                   |                                                     |
        |               |                   | dev_num indicates the channel number.               |
        |               |                   |                                                     |
        |               |                   | Set config_val to one of the                        |
        |               |                   | :class:`~mcculw.enums.State` enum values.          |
        |               +-------------------+-----------------------------------------------------+
        |               | DACSTARTUP        | Configuration register STARTUP bit setting.         |
        |               |                   |                                                     |
        |               |                   | dev_num is ignored.                                 |
        |               |                   |                                                     |
        |               |                   | Set to 0 or 1 to enable/disable the storing of      |
        |               |                   | digital-to-analog converter (DAC) startup values.   |
        |               |                   | Current or last stored values are written to the    |
        |               |                   | DACs each time the board is powered up.             |
        |               +-------------------+-----------------------------------------------------+
        |               | DACRANGE          | D/A range code.                                     |
        |               |                   |                                                     |
        |               |                   | dev_num indicates the channel number.               |
        |               |                   | Refer to board-specific information for a list of   |
        |               |                   | the supported ranges.                               |
        |               +-------------------+-----------------------------------------------------+
        |               | DACTRIGCOUNT      | DAC trigger count.                                  |
        |               |                   |                                                     |
        |               |                   | dev_num is ignored.                                 |
        |               |                   |                                                     |
        |               |                   | For use with the :func:`.a_out_scan`                |
        |               |                   | :const:`~mcculw.enums.ScanOptions.RETRIGMODE`      |
        |               |                   | option to set up repetitive trigger events.         |
        |               +-------------------+-----------------------------------------------------+
        |               | DACUPDATECMD      | Updates all analog output channels.                 |
        |               |                   |                                                     |
        |               |                   | dev_num and config_val are ignored.                 |
        |               +-------------------+-----------------------------------------------------+
        |               | DACUPDATEMODE     | Update mode for a digital-to-analog converter       |
        |               |                   | (DAC).                                              |
        |               |                   |                                                     |
        |               |                   | dev_num is ignored.                                 |
        |               |                   |                                                     |
        |               |                   | Set config_val to one of the                        |
        |               |                   | :class:`~mcculw.enums.DACUpdate` enum values.      |
        |               +-------------------+-----------------------------------------------------+
        |               | DACSETTLETIME     | DAC settling time.                                  |
        |               |                   |                                                     |
        |               |                   | dev_num is ignored.                                 |
        |               +-------------------+-----------------------------------------------------+
        |               | DETECTOPENTC      | Open thermocouple detection setting.                |
        |               |                   |                                                     |
        |               |                   | dev_num is either ignored or specifies a base or    |
        |               |                   | expansion board; refer to device-specific           |
        |               |                   | information.                                        |
        |               |                   |                                                     |
        |               |                   | Set config_val to one of the                        |
        |               |                   | :class:`~mcculw.enums.State` enum values.          |
        |               +-------------------+-----------------------------------------------------+
        |               | DIDEBOUNCESTATE   | State of the digital inputs when debounce timing is |
        |               |                   | set.                                                |
        |               |                   |                                                     |
        |               |                   | dev_num is ignored.                                 |
        |               +-------------------+-----------------------------------------------------+
        |               | DIDEBOUNCETIME    | Debounce time of digital inputs.                    |
        |               |                   |                                                     |
        |               |                   | dev_num is ignored.                                 |
        |               +-------------------+-----------------------------------------------------+
        |               | DISOFILTER        | AC filter setting. 0 = disable, 1 = enable.         |
        |               |                   |                                                     |
        |               |                   | dev_num is the bit number.                          |
        |               |                   |                                                     |
        |               |                   | Set config_val to one of the                        |
        |               |                   | :class:`~mcculw.enums.State` enum values.          |
        |               +-------------------+-----------------------------------------------------+
        |               | DITRIGCOUNT       | Number of digital input samples to acquire per      |
        |               |                   | trigger.                                            |
        |               |                   |                                                     |
        |               |                   | dev_num is ignored.                                 |
        |               +-------------------+-----------------------------------------------------+
        |               | DMACHAN           | DMA channel.                                        |
        |               |                   |                                                     |
        |               |                   | dev_num is ignored.                                 |
        |               +-------------------+-----------------------------------------------------+
        |               | DOTRIGCOUNT       | Number of digital output samples to generate per    |
        |               |                   | trigger.                                            |
        |               |                   |                                                     |
        |               |                   | dev_num is ignored.                                 |
        |               +-------------------+-----------------------------------------------------+
        |               | EXTCLKTYPE        | External clock type.                                |
        |               |                   |                                                     |
        |               |                   | dev_num is ignored.                                 |
        |               |                   |                                                     |
        |               |                   | Set config_val to one of the                        |
        |               |                   | :class:`~mcculw.enums.ExtClkType` enum values.     |
        |               +-------------------+-----------------------------------------------------+
        |               | EXTINPACEREDGE    | The input pacer clock edge.                         |
        |               |                   |                                                     |
        |               |                   | dev_num is ignored.                                 |
        |               |                   |                                                     |
        |               |                   | Set config_val to one of the                        |
        |               |                   | :class:`~mcculw.enums.ExtPacerEdge` enum values.   |
        |               +-------------------+-----------------------------------------------------+
        |               | EXTOUTPACEREDGE    | The output pacer clock edge.                       |
        |               |                   |                                                     |
        |               |                   | dev_num is ignored.                                 |
        |               |                   |                                                     |
        |               |                   | Set config_val to one of the                        |
        |               |                   | :class:`~mcculw.enums.ExtPacerEdge` enum values.   |
        |               +-------------------+-----------------------------------------------------+
        |               | INPUTPACEROUT     | Input pacer clock output enable/disable setting.    |
        |               |                   |                                                     |
        |               |                   | dev_num is ignored.                                 |
        |               |                   |                                                     |
        |               |                   | Set config_val to one of the                        |
        |               |                   | :class:`~mcculw.enums.State` enum values. When     |
        |               |                   | enabled, the input clock is set for output.         |
        |               +-------------------+-----------------------------------------------------+
        |               | INTEDGE           | Interrupt edge. 0 = rising, 1 = falling.            |
        |               |                   |                                                     |
        |               |                   | dev_num is ignored.                                 |
        |               +-------------------+-----------------------------------------------------+
        |               | INTLEVEL          | Interrupt level.                                    |
        |               |                   |                                                     |
        |               |                   | dev_num is ignored.                                 |
        |               +-------------------+-----------------------------------------------------+
        |               | HIDELOGINDLG      | Enables or disables the Device Login dialog.        |
        |               |                   |                                                     |
        |               |                   | dev_num is ignored.                                 |
        |               |                   |                                                     |
        |               |                   | Set config_val to one of the                        |
        |               |                   | :class:`~mcculw.enums.State` enum values. When     |
        |               |                   | disabled, the :func:`.device_login` function must   |
        |               |                   | be used to log in to a device session.              |
        |               +-------------------+-----------------------------------------------------+
        |               | NETCONNECTIONCODE | Code used to connect with a device over a network   |
        |               |                   | connection.                                         |
        |               |                   |                                                     |
        |               |                   | dev_num is ignored.                                 |
        |               +-------------------+-----------------------------------------------------+
        |               | NETIOTIMEOUT      | Amount of time (in milliseconds) to wait for a WEB  |
        |               |                   | device to acknowledge a command or query sent to    |
        |               |                   | the device over a network connection. If no         |
        |               |                   | acknowledgement is received in this time a timeout  |
        |               |                   | occurs.                                             |
        |               |                   |                                                     |
        |               |                   | dev_num is ignored.                                 |
        |               +-------------------+-----------------------------------------------------+
        |               | NUMADCHANS        | Number of A/D channels.                             |
        |               |                   |                                                     |
        |               |                   | dev_num is ignored.                                 |
        |               +-------------------+-----------------------------------------------------+
        |               | OUTPUTPACEROUT    | Enables or disables the output pacer clock signal.  |
        |               |                   | When enabled, the output clock is set for output.   |
        |               |                   |                                                     |
        |               |                   |                                                     |
        |               +-------------------+-----------------------------------------------------+
        |               | PANID             | The Personal Area Network (PAN) identifier set for  |
        |               |                   | a USB device that supports wireless communication.  |
        |               |                   |                                                     |
        |               |                   | dev_num is ignored.                                 |
        |               +-------------------+-----------------------------------------------------+
        |               | PATTERNTRIGPORT   | The pattern trigger port.                           |
        |               |                   |                                                     |
        |               |                   | dev_num is ignored.                                 |
        |               |                   |                                                     |
        |               |                   | Use this setting in conjunction with one of these   |
        |               |                   | config_val settings:                                |
        |               |                   |                                                     |
        |               |                   | - :const:`~mcculw.enums.DigitalPortType.AUXPORT0`  |
        |               |                   |   (default)                                         |
        |               |                   |                                                     |
        |               |                   | - :const:`~mcculw.enums.DigitalPortType.AUXPORT1`  |
        |               +-------------------+-----------------------------------------------------+
        |               | RANGE             | The selected voltage range. Refer to board-specific |
        |               |                   | information for the ranges supported by a device.   |
        |               |                   |                                                     |
        |               |                   | dev_num is ignored.                                 |
        |               +-------------------+-----------------------------------------------------+
        |               | RFCHANNEL         | RF channel number used to transmit/receive data by  |
        |               |                   | a USB device that supports wireless communication.  |
        |               |                   |                                                     |
        |               |                   | dev_num is ignored.                                 |
        |               +-------------------+-----------------------------------------------------+
        |               | RSS               | Received signal strength in dBm of a remote device. |
        |               |                   |                                                     |
        |               |                   | dev_num is ignored.                                 |
        |               +-------------------+-----------------------------------------------------+
        |               | SERIALNUM         | User-configured identifier of a supported USB       |
        |               |                   | device.                                             |
        |               |                   |                                                     |
        |               |                   | dev_num is ignored.                                 |
        |               +-------------------+-----------------------------------------------------+
        |               | SYNCMODE          | The simultaneous mode setting.                      |
        |               |                   |                                                     |
        |               |                   | dev_num is ignored                                  |
        |               |                   |                                                     |
        |               |                   | Set config_val to either 0 (master) or 1 (slave).   |
        |               +-------------------+-----------------------------------------------------+
        |               | TEMPAVG           | Number of samples per average.                      |
        |               |                   |                                                     |
        |               |                   | Set config_val to one of the following values:      |
        |               |                   |                                                     |
        |               |                   | - 1 to 16384 (if the TEMPREJFREQ rejection          |
        |               |                   |   frequency is off (0)                              |
        |               |                   | - 16 to 16384 (if the TEMPREJFREQ rejection         |
        |               |                   |   frequency is on (50 or 60)                        |
        |               |                   |                                                     |
        |               |                   | When specified, multiple readings are acquired,     |
        |               |                   | averaged, and converted to temperature.             |
        |               +-------------------+-----------------------------------------------------+
        |               | TEMPSCALE         | Temperature scale.                                  |
        |               |                   |                                                     |
        |               |                   | dev_num is ignored.                                 |
        |               |                   |                                                     |
        |               |                   | Set config_val to one of the following values:      |
        |               |                   |                                                     |
        |               |                   | - :const:`~mcculw.enums.TempScale.CELSIUS`         |
        |               |                   | - :const:`~mcculw.enums.TempScale.FAHRENHEIT`      |
        |               |                   | - :const:`~mcculw.enums.TempScale.KELVIN`          |
        |               +-------------------+-----------------------------------------------------+
        |               | TEMPREJFREQ       | Rejection frequency. Use this setting in            |
        |               |                   | conjunction with these settings:                    |
        |               |                   |                                                     |
        |               |                   | dev_num:                                            |
        |               |                   |                                                     |
        |               |                   | - 0 (base board)                                    |
        |               |                   | - 1 (expansion board)                               |
        |               |                   |                                                     |
        |               |                   | config_val:                                         |
        |               |                   |                                                     |
        |               |                   | - 0 (off)                                           |
        |               |                   | - 50 (50 Hz noise rejection)                        |
        |               |                   | - 60 (60 Hz noise rejection)                        |
        |               +-------------------+-----------------------------------------------------+
        |               | TERMCOUNTSTATBIT  | Terminal count output status.                       |
        |               |                   |                                                     |
        |               |                   | dev_num indicates the bit number.                   |
        |               |                   |                                                     |
        |               |                   | Set config_val to one of the                        |
        |               |                   | :class:`~mcculw.enums.State` enum values.          |
        |               +-------------------+-----------------------------------------------------+
        |               | WAITSTATE         | Wait State jumper setting.                          |
        |               |                   |                                                     |
        |               |                   | dev_num is ignored.                                 |
        |               |                   |                                                     |
        |               |                   | Set config_val to one of the                        |
        |               |                   | :class:`~mcculw.enums.State` enum values.          |
        +---------------+-------------------+-----------------------------------------------------+
        | DIGITALINFO   | DISABLEDIRCHECK   | The direction check setting for a specified port or |
        |               |                   | bit when calling :func:`.d_out`,                    |
        |               |                   | :func:`.d_bit_out`, and :func:`.d_out_array`.       |
        |               |                   |                                                     |
        |               |                   | Set config_val to one of the following values:      |
        |               |                   |                                                     |
        |               |                   | - 0 (enables the direction check)                   |
        |               |                   | - 1 (disables the direction check)                  |
        +---------------+-------------------+-----------------------------------------------------+
        | EXPANSIONINFO | MUXADCHAN1        | First A/D channel connected to the board            |
        |               +-------------------+-----------------------------------------------------+
        |               | MUXADCHAN2        | Second A/D channel connected to the board.          |
        |               +-------------------+-----------------------------------------------------+
        |               | RANGE1            | Range (gain) of the low 16 channels.                |
        |               +-------------------+-----------------------------------------------------+
        |               | RANGE2            | Range (gain) of the high 16 channels.               |
        |               +-------------------+-----------------------------------------------------+
        |               | CJCCHAN           | A/D channel connected to the CJC channel.           |
        |               +-------------------+-----------------------------------------------------+
        |               | THERMTYPE         | Thermocouple type                                   |
        +---------------+-------------------+-----------------------------------------------------+

    """
    _check_err(_cbw.cbSetConfig(info_type, board_num,
                                dev_num, config_item, config_val))


_cbw.cbSetConfigString.argtypes = [
    c_int, c_int, c_int, c_int, c_char_p, POINTER(c_int)]


def set_config_string(info_type, board_num, dev_num, config_item, config_val):
    """Changes board configuration options at runtime.

    By default, the configuration settings are loaded from the cb.cfg file created by InstaCal.
    If :func:`.ignore_instacal` is called first, the configuration settings will be the default
    values for the board in use. For either case, you can change the current configuration within a
    running program using this function.

    Parameters
    ----------
    info_type : InfoType
        The configuration information for each board is grouped into different categories. This
        parameter specifies which category you want. Always set this parameter to
        InfoType.BOARDINFO.
    board_num : int
        The number associated with the board when it was installed with InstaCal or created
        with :func:`.create_daq_device`.
    dev_num : int
        The purpose of the dev_num parameter depends on the value of the config_item parameter. It
        can serve as a channel number, an index into the config_item, or it can be ignored.
    config_item :
        Specifies which configuration item you wish to set. Set it in conjunction with the
        info_type parameter using the table under config_item parameter values section below.
    config_val : BoardInfo, DigitalInfo, CounterInfo, or ExpansionInfo
        The value to set the specified configuration item to.


    .. table:: **config_item parameter values**

        ============  =============================================================================
        config_item   Description
        ============  =============================================================================
        USERDEVID     Writes a user-configured string to an Ethernet, Bluetooth, or USB device.

                      DevNum is ignored.  
        ============  =============================================================================
    """
    _check_err(_cbw.cbSetConfigString(
        info_type, board_num, dev_num, config_item, config_val.encode('utf8'),
        len(config_val)))


_cbw.cbSetTrigger.argtypes = [c_int, c_int, c_ushort, c_ushort]


def set_trigger(board_num, trig_type, low_threshold, high_threshold):
    """Selects the trigger source and sets up its parameters. This trigger is used to initiate a
    scan using the following Universal Library functions:

    :func:`.a_in_scan`, if the :const:`~mcculw.enums.ScanOptions.EXTTRIGGER` option is selected.
    :func:`.d_in_scan`, if the :const:`~mcculw.enums.ScanOptions.EXTTRIGGER` option is selected.
    :func:`.c_in_scan`, if the :const:`~mcculw.enums.ScanOptions.EXTTRIGGER` option is selected.
    :func:`.a_pretrig`

    Parameters
    ----------
    board_num : int
        The number associated with the board when it was installed with InstaCal or created
        with :func:`.create_daq_device`.
    trig_type : TrigType
        Specifies the type of triggering based on the external trigger source. Set it to one of the
        constants in the "trig_type parameter values" section below.
    low_threshold : int
        Selects the low threshold used when the trigger input is analog. The range depends upon
        the resolution of the trigger circuitry. Must be 0 to 255 for 8-bit trigger circuits, 0 to
        4,095 for 12-bit trigger circuits, and 0 to 65,535 for 16-bit trigger circuits. Refer to
        the "Analog Trigger Notes" section below.

        When the trigger input is a digital pattern, low_threshold selects the pattern value.
    high_threshold : int
        Selects the high threshold used when the trigger input is analog. The range depends upon
        the resolution of the trigger circuitry. Must be 0 to 255 for 8-bit trigger circuits, 0 to
        4,095 for 12-bit trigger circuits, and 0 to 65,535 for 16-bit trigger circuits. Refer to
        the "Analog Trigger Notes" section below.

        When the trigger input is a digital pattern, high_threshold selects the port mask.


    .. table:: **trig_type parameter values**

        +---------+--------------------+----------------------------------------------------------+
        | Trigger | Type               | Explanation                                              |
        | source  |                    |                                                          |
        +=========+====================+==========================================================+
        | Analog  | GATE_NEG_HYS       | Scanning is enabled as long as the external analog       |
        |         |                    | trigger input is more positive than high_threshold.      |
        |         |                    | Hysteresis is the level between low_threshold and        |
        |         |                    | high_threshold.                                          |
        |         +--------------------+----------------------------------------------------------+
        |         | GATE_POS_HYS       | Scanning is enabled as long as the external analog       |
        |         |                    | trigger input is more negative than low_threshold.       |
        |         |                    | Hysteresis is the level between low_threshold and        |
        |         |                    | high_threshold.                                          |
        |         +--------------------+----------------------------------------------------------+
        |         | GATE_ABOVE         | Scanning is enabled as long as the external analog       |
        |         |                    | trigger input is more positive than high_threshold.      |
        |         +--------------------+----------------------------------------------------------+
        |         | GATE_BELOW         | Scanning is enabled as long as the external analog       |
        |         |                    | trigger input is more negative than low_threshold.       |
        |         +--------------------+----------------------------------------------------------+
        |         | GATE_IN_WINDOW     | Scanning is enabled as long as the external analog       |
        |         |                    | trigger is inside the region defined by low_threshold    |
        |         |                    | and high_threshold.                                      |
        |         +--------------------+----------------------------------------------------------+
        |         | GATE_OUT_WINDOW    | Scanning is enabled as long as the external analog       |
        |         |                    | trigger is outside the region defined by low_threshold   |
        |         |                    | and high_threshold.                                      |
        |         +--------------------+----------------------------------------------------------+
        |         | TRIG_ABOVE         | Scanning begins when the external analog trigger input   |
        |         |                    | transitions from below high_threshold to above. Once     |
        |         |                    | conversions are enabled, the external trigger is         |
        |         |                    | ignored.                                                 |
        |         +--------------------+----------------------------------------------------------+
        |         | TRIG_BELOW         | Scanning begins when the external analog trigger input   |
        |         |                    | transitions from above low_threshold to below. Once      |
        |         |                    | conversions are enabled, the external trigger is         |
        |         |                    | ignored.                                                 |
        |         +--------------------+----------------------------------------------------------+
        |         | TRIG_RISING        | Scanning begins when the external analog trigger input   |
        |         |                    | transitions from below low_threshold to above            |
        |         |                    | high_threshold. Once conversions are enabled, the        |
        |         |                    | external trigger is ignored.                             |
        |         +--------------------+----------------------------------------------------------+
        |         | TRIG_FALLING       | Scanning begins when the external analog trigger input   |
        |         |                    | transitions from above high_threshold to below           |
        |         |                    | low_threshold. Once conversions are enabled, the         |
        |         |                    | external trigger is ignored.                             |
        |         +--------------------+----------------------------------------------------------+
        |         | **Analog Trigger Notes**                                                      |
        |         |                                                                               |
        |         | - The value of the threshold must be within the range of the analog trigger   |
        |         |   circuit associated with the board. Refer to the board-specific information  |
        |         |   in the Universal Library User's Guide. For example, on the PCI-DAS1602/16   |
        |         |   the analog trigger circuit handles ±10 V. A value of 0 corresponds to       |
        |         |   -10 V, whereas a value of 65,535 corresponds to +10 V.                      |
        |         |                                                                               |
        |         |   If you are using signed integer types, the thresholds range from -32,768 to |
        |         |   32,767 for 16-bit boards, instead of from 0 to 65,535. In this case, the    |
        |         |   unsigned value of 65,535 corresponds to a value of -1, 65,534 corresponds   |
        |         |   to -2, ..., 32,768 corresponds to -32,768.                                  |
        |         |                                                                               |
        |         | - For most boards that support analog triggering, you can pass the required   |
        |         |   trigger voltage level and the appropriate range to :func:`.from_eng_units`  |
        |         |   function to calculate the high_threshold and low_threshold values.          |
        |         |                                                                               |
        |         |   For some boards, you must manually calculate the threshold: first calculate |
        |         |   the least significant bit (LSB) for a particular range for the trigger      |
        |         |   resolution of your hardware, then use the LSB to find the threshold in      |
        |         |   counts based on an analog voltage trigger threshold. Refer below to the     |
        |         |   "Manually calculating the threshold" example for details. For               |
        |         |   board-specific information, refer to the Universal Library User's Guide     |
        |         |   section of the Help.                                                        |
        +---------+--------------------+----------------------------------------------------------+
        | Digital | GATE_HIGH          | Scanning is enabled as long as the external digital      |
        |         |                    | trigger input is 5V (logic HIGH or '1').                 | 
        |         +--------------------+----------------------------------------------------------+
        |         | GATE_LOW           | Scanning is enabled as long as the external digital      |
        |         |                    | trigger input is 0V (logic LOW or '0').                  |
        |         +--------------------+----------------------------------------------------------+
        |         | TRIG_HIGH          | Scanning begins when the external digital trigger is 5V  |
        |         |                    | (logic HIGH or '1'). Once conversions are enabled, the   |
        |         |                    | external trigger is ignored.                             |
        |         +--------------------+----------------------------------------------------------+
        |         | TRIG_LOW           | Scanning begins when the external digital trigger is 0V  |
        |         |                    | (logic LOW or '0'). Once conversions are enabled, the    |
        |         |                    | external trigger is ignored.                             |
        |         +--------------------+----------------------------------------------------------+
        |         | TRIG_PATTERN_EQ    | Scanning begins when the digital port value AND bitwise  |
        |         |                    | mask are equal to the pattern value AND bitwise mask.    |
        |         |                    | Once conversions are enabled, the external trigger is    |
        |         |                    | ignored.                                                 |
        |         +--------------------+----------------------------------------------------------+
        |         | TRIG_PATTERN_NE    | Scanning begins when the digital port value AND bitwise  |
        |         |                    | mask are not equal to the pattern value AND bitwise      |
        |         |                    | mask. Once conversions are enabled, the external trigger |
        |         |                    | is ignored.                                              |
        |         +--------------------+----------------------------------------------------------+
        |         | TRIG_PATTERN_ABOVE | Scanning begins when the digital port value AND bitwise  |
        |         |                    | mask are greater than the pattern value AND bitwise      |
        |         |                    | mask. Once conversions are enabled, the external trigger |
        |         |                    | is ignored.                                              |
        |         +--------------------+----------------------------------------------------------+
        |         | TRIG_PATTERN_BELOW | Scanning begins when the digital port value AND bitwise  |
        |         |                    | mask are less than the pattern value AND bitwise mask.   |
        |         |                    | Once conversions are enabled, the external trigger is    |
        |         |                    | ignored.                                                 |
        |         +--------------------+----------------------------------------------------------+
        |         | TRIG_POS_EDGE      | Scanning begins when the external digital trigger        |
        |         |                    | transitions from 0V to 5V (logic LOW to HIGH). Once      |
        |         |                    | conversions are enabled, the external trigger is         |
        |         |                    | ignored.                                                 |
        |         +--------------------+----------------------------------------------------------+
        |         | TRIG_NEG_EDGE      | Scanning begins when the external digital trigger        |
        |         |                    | transitions from 5V to 0V (logic HIGH to LOW). Once      |
        |         |                    | conversions are enabled, the external trigger is         |
        |         |                    | ignored.                                                 |
        |         +--------------------+----------------------------------------------------------+
        |         | **Digital Trigger Notes**                                                     |
        |         |                                                                               |
        |         | - For pattern trigger types, the low_threshold argument represents the        |
        |         |   pattern value, and the high_threshold argument represents the port mask.    |
        |         |   Use the :func:`.set_config` config_item                                     |
        |         |   :const:`~pmcculwenums.BaordInfo.PATTERNTRIGPORT` to set the pattern        |
        |         |   trigger port.                                                               |
        +---------+-------------------------------------------------------------------------------+

    **Manually calculating the threshold**

    To calculate the threshold, do the following:

    1. Calculate the LSB by dividing the full scale range (FSR) by 2resolution. FSR is the entire
       span from -FS to +FS of your hardware for a particular range. For example, the full scale
       range of ±10 V is 20 V.
    2. Calculate how many times you need to add the LSB calculated in step 1 to the negative full
       scale (-FS) to reach the trigger threshold value.

    The maximum threshold value is 2 resolution - 1. The formula is shown here:

    Abs(-FS - threshold in volts) / (LSB) = threshold in counts

    Here are two examples that use this formula - one for 8-bit trigger resolution, and one for
    12-bit trigger resolution:

    - 8-bit example using the ±10 V range with a -5 V threshold:

      Calculate the LSB: LSB = 20 / 28 = 20 / 256 = 0.078125

      Calculate the threshold: Abs(-10 - (-5)) / 0.078125 = 5 / 0.078125 = 64 (round this result if
      it is not an integer). A count of 64 translates to a voltage threshold of -5.0 V.

    - 12-bit example using the ±10 V range with a +1 V threshold:

      Calculate the LSB: LSB = 20 / 212 = 20 / 4096 = 0.00488

      Calculate the threshold: Abs(-10 - 1) / 0.00488 = 11 / 0.00488 = 2254 (rounded from 2254.1).
      A count of 2254 translates to a voltage threshold of 0.99952 V.
    """
    _check_err(_cbw.cbSetTrigger(
        board_num, trig_type, low_threshold, high_threshold))


_cbw.cbStopIOBackground.argtypes = [c_int, c_int]


def stop_background(board_num, function_type):
    """Stops one or more subsystem background operations that are in progress for the specified
    board. Use this function to stop any function that is running in the background. This includes
    any function that was started with the :const:`~pyulmcculwms.ScanOptions.BACKGROUND` option.

    Execute :func:`.stop_background` after normal termination of all background functions to clear
    variables and flags.

    Parameters
    ----------
    board_num : int
        The number associated with the board when it was installed with InstaCal or created
        with :func:`.create_daq_device`.
    function_type : FunctionType
        Specifies which background operation to stop. Specifies which scan to retrieve status
        information about. Refer to the "function_type parameter values" section below.


    .. table:: **function_type parameter values**

        ============  =============================================================================
        AIFUNCTION    Specifies analog input scans started with :func:`.a_in_scan` or
                      :func:`.a_pretrig`. 
        AOFUNCTION    Specifies analog output scans started with :func:`.a_out_scan`. 
        DIFUNCTION    Specifies digital input scans started with :func:`.d_in_scan`. 
        DOFUNCTION    Specifies digital output scans started with :func:`.d_out_scan`. 
        CTRFUNCTION   Specifies counter background operations started with :func:`.c_in_scan`. 
        DAQIFUNCTION  Specifies a synchronous input scan started with :func:`.daq_in_scan`. 
        DAQOFUNCTION  Specifies a synchronous output scan started with :func:`.daq_out_scan`. 
        ============  =============================================================================
    """
    _check_err(_cbw.cbStopIOBackground(board_num, function_type))


TedsReadResult = collections.namedtuple(
    "TedsReadResult", "data_array actual_count")
_cbw.cbTEDSRead.argtypes = [c_int, c_int,
                            POINTER(c_byte), POINTER(c_long), c_int]


def teds_read(board_num, channel, count, data_array=None, options=0):
    """Reads data from a TEDS sensor into an array.

    Parameters
    ----------
    board_num : int
        The number associated with the board when it was installed with InstaCal or created
        with :func:`.create_daq_device`.
    channel : int
        A/D channel number.
    data_array : POINTER(c_byte), optional
        Pointer to the TEDS data array. If this parameter is omitted (or None), the array
        will be allocated by this function. Reusing the array by passing it in as the parameter may
        be useful as an optimization to prevent excessive allocations, saving memory and CPU time.
    options : int, optional
        Reserved for future use.

    Returns
    -------
    data_array : POINTER(c_uint)
        A pointer to the C array containing the digital input data
    actual_count : int
        The actual number of data points read
    """
    if data_array == None:
        data_array = (c_byte * count)()
    count_internal = c_long(count)
    _check_err(_cbw.cbTEDSRead(board_num, channel, data_array,
                               byref(count_internal), options))
    return TedsReadResult(data_array, count_internal.value)


_cbw.cbTimerOutStart.argtypes = [c_int, c_int, POINTER(c_double)]


def timer_out_start(board_num, timer_num, frequency):
    """Starts a timer square wave output. Use :func:`.timer_out_stop` to stop the output.

    Parameters
    ----------
    board_num : int
        The number associated with the board when it was installed with InstaCal or created
        with :func:`.create_daq_device`.
    timer_num : int
        The timer to output the square wave from. Valid values are zero (0) up to the number of
        timers - 1 on the board.
    frequency : float
        The desired square wave frequency. The timers clock will be divided down by integer values
        to produce the frequency. The actual frequency output will be returned. Valid values are
        dependent on the timer's clock and the timer resolution.

    Returns
    -------
    float
        The actual frequency set
    """
    frequency_internal = c_double(frequency)
    _check_err(_cbw.cbTimerOutStart(
        board_num, timer_num, byref(frequency_internal)))
    return frequency_internal.value


_cbw.cbTimerOutStop.argtypes = [c_int, c_int]


def timer_out_stop(board_num, timer_num):
    """Stops a timer square wave output. Use :func:`.timer_out_start` to start the output.

    Parameters
    ----------
    board_num : int
        The number associated with the board when it was installed with InstaCal or created
        with :func:`.create_daq_device`.
    timer_num : int
        The timer to stop. Valid values are zero up to the number of timers on the board - 1.
    """
    _check_err(_cbw.cbTimerOutStop(board_num, timer_num))


_cbw.cbTIn.argtypes = [c_int, c_int, c_int, POINTER(c_float), c_int]


def t_in(board_num, channel, scale, options=TInOptions.FILTER):
    """Reads an analog input channel, linearizes it according to the selected temperature sensor
    type, if required, and returns the temperature in units determined by the scale parameter.

    Parameters
    ----------
    board_num : int
        The number associated with the board when it was installed with InstaCal or created
        with :func:`.create_daq_device`.
    channel : int
        Input channel to read.
    scale : TempScale
        Specifies the temperature scale that the input will be converted to
    options : TInOptions, optional
        Flags that control various options. Refer to the constants in the "options parameter values"
        section below.

    Returns
    -------
    float
        The temperature value


    .. table:: **options parameter values**

        ==============  ===========================================================================
        FILTER          When selected, a smoothing function is applied to temperature readings,
                        very much like the electrical smoothing inherent in all hand held
                        temperature sensor instruments. This is the default. When selected, 10
                        samples are read from the specified channel and averaged. The average is
                        the reading returned. Averaging removes normally distributed signal line
                        noise. 
        --------------  ---------------------------------------------------------------------------
        NOFILTER        If you use the NOFILTER option then the readings will not be smoothed and
                        you will see a scattering of readings around a mean. 
        --------------  ---------------------------------------------------------------------------
        WAITFORNEWDATA  Waits for new data to become available. 
        ==============  ===========================================================================



    Notes
    -----
    **Scale options**

    - Specify the TempScale.NOSCALE to the scale parameter to retrieve raw data from the device.
      When TempScale.NOSCALE is specified, calibrated data is returned, although a cold junction
      compensation (CJC) correction factor is not applied to the returned values.

    - Specify the :const:`~pyulmcculwms.TempScale.VOLTS` option to read the voltage input of a
      thermocouple.

    Refer to board-specific information in the Universal Library User's Guide to determine if your
    hardware supports these options.
    """
    temp_value = c_float()
    _check_err(_cbw.cbTIn(board_num, channel,
                          scale, byref(temp_value), options))
    return temp_value.value


TInScanResults = collections.namedtuple(
    "TInScanResults", "err_code data_array")
_cbw.cbTInScan.argtypes = [c_int, c_int, c_int, c_int, POINTER(c_float), c_int]


def t_in_scan(board_num, low_chan, high_chan, scale, options=0, data_array=None):
    """Reads a range of channels from an analog input board, linearizes them according to
    temperature sensor type, if required, and returns the temperatures to an array in units
    determined by the scale parameter.

    Parameters
    ----------
    board_num : int
        The number associated with the board when it was installed with InstaCal or created
        with :func:`.create_daq_device`.
    low_chan : int
        Low channel of the scan.
    high_chan : int
        High channel of the scan.
    scale : TempScale
        Specifies the temperature scale that the input will be converted to.
    options : TInOptions, optional
        Flags that control various options. Refer to the constants in the
        "options parameter values" section below.
    data_array : POINTER(c_float)
        Pointer to the temperature data array. If this parameter is omitted (or None), the array
        will be allocated by this function. Reusing the array by passing it in as the parameter may
        be useful as an optimization to prevent excessive allocations, saving memory and CPU time.

    Returns
    -------
    err_code : int
        The error code, which will either be ErrorCode.OUTOFRANGE, ErrorCode.OPENCONNECTION, or
        ErrorCode.NOERRORS. ErrorCode.OUTOFRANGE will be returned if any of the converted data is
        out of range. This typically indicates an open TC connection. All other errors will raise
        a ULError as usual.
    data_array : POINTER(c_float)
        A pointer to the C array containing the converted temperature data


    .. table:: **options parameter values**

        ==============  ===========================================================================
        FILTER          When selected, a smoothing function is applied to temperature readings,
                        very much like the electrical smoothing inherent in all hand held
                        temperature sensor instruments. This is the default. When selected, 10
                        samples are read from the specified channel and averaged. The average is
                        the reading returned. Averaging removes normally distributed signal line
                        noise. 
        --------------  ---------------------------------------------------------------------------
        NOFILTER        If you use the NOFILTER option then the readings will not be smoothed and
                        you will see a scattering of readings around a mean. 
        --------------  ---------------------------------------------------------------------------
        WAITFORNEWDATA  Waits for new data to become available. 
        ==============  ===========================================================================

    Notes
    -----
    **Scale options**

    - Specify :const:`~pyulmcculwms.TempScale.NOSCALE` to the scale parameter to retrieve raw data
      from the device. When :const:`~pyulmcculwms.TempScale.NOSCALE` is specified, calibrated data
      is returned, although a cold junction compensation (CJC) correction factor is not applied to
      the returned values.

    - Specify the :const:`~pyulmcculwms.TempScale.VOLTS` option to read the voltage input of a
      thermocouple.

    Refer to board-specific information in the Universal Library User's Guide to determine if your
    hardware supports these options.
    """
    if low_chan > high_chan:
        raise ULError(ErrorCode.BADADCHAN)

    if data_array == None:
        data_array = (c_float * (high_chan - low_chan + 1))()
    err_code = _cbw.cbTInScan(
        board_num, low_chan, high_chan, scale, data_array, options)
    if err_code != ErrorCode.OUTOFRANGE and err_code != ErrorCode.OPENCONNECTION:
        _check_err(err_code)
    return TInScanResults(err_code, data_array)


_cbw.cbToEngUnits.argtypes = [c_int, c_int, c_ushort, POINTER(c_float)]


def to_eng_units(board_num, ul_range, data_value):
    """Converts an integer count value to an equivalent single precision voltage (or current)
    value. This function is typically used to obtain a voltage value from data received from an A/D
    with functions such as :func:`.a_in`.

    Parameters
    ----------
    board_num : int
        The number associated with the board when it was installed with InstaCal or created
        with :func:`.create_daq_device`.
    ul_range : ULRange
        Voltage (or current) range to use for the conversion to engineering units. When using this
        function to obtain engineering units from a value received from an A/D board, keep in mind
        that some A/D boards have programmable voltage ranges, and others set the voltage range via
        switches on the board. In either case, the desired range must be passed to this function.

        Refer to board-specific information in the Universal Library User's Guide for a list of the
        supported A/D ranges of each board.
    data_value : int
        An integer count value (typically, one returned from an A/D board).

    Returns
    -------
    float
        The engineering units value equivalent to data_value

    Notes
    -----
    - This function is not supported for hardware with resolution greater than 16 bits.

    - The default resolution of this function is 12 bits, so if the device referenced by board_num
      has neither analog input nor analog output, the result will be a 12 bit conversion.

    - If the device referenced by board_num has both analog input and analog output, the resolution
      and transfer function of the A/D converter on the device is used.
    """
    eng_units = c_float()
    _check_err(_cbw.cbToEngUnits(
        board_num, ul_range, data_value, byref(eng_units)))
    return eng_units.value


_cbw.cbToEngUnits32.argtypes = [c_int, c_int, c_ulong, POINTER(c_double)]


def to_eng_units_32(board_num, ul_range, data_value):
    """Converts an integer count value to an equivalent double precision voltage (or current)
    value.

    Parameters
    ----------
    board_num : int
        The number associated with the board when it was installed with InstaCal or created
        with :func:`.create_daq_device`.
    ul_range : ULRange
        Voltage (or current) range to use for the conversion to engineering units. When using this
        function to obtain engineering units from a value received from an A/D board, keep in mind
        that some A/D boards have programmable voltage ranges, and others set the voltage range via
        switches on the board. In either case, the desired range must be passed to this function.

        Refer to board-specific information in the Universal Library User's Guide for a list of the
        supported A/D ranges of each board.
    data_value : int
        An integer count value (typically, one returned from an A/D board).

    Returns
    -------
    float
        The engineering units value equivalent to data_value

    Notes
    -----
    - This function is typically used to obtain a voltage (or current) value from data received
      from an A/D with functions such as :func:`.a_in_32`.
    - This function should be used for devices with a resolution of 20-bits or more.

      The default resolution of this function is 32 bits, so if the device referenced by board_num
      has neither analog input nor analog output, the result will be a 32 bit conversion.

      If the device referenced by board_num has both analog input and analog output, the resolution
      and transfer function of the A/D converter on the device is used.
    """
    eng_units = c_double()
    _check_err(_cbw.cbToEngUnits32(
        board_num, ul_range, data_value, byref(eng_units)))
    return eng_units.value


_cbw.cbVIn.argtypes = [c_int, c_int, c_int, POINTER(c_float), c_int]


def v_in(board_num, channel, ul_range, options=0):
    """Reads an A/D input channel, and returns a voltage value. If the specified A/D board has
    programmable gain, then this function sets the gain to the specified range.

    Parameters
    ----------
    board_num : int
        The number associated with the board when it was installed with InstaCal or created
        with :func:`.create_daq_device`.
    channel : int
        A/D channel number. The maximum allowable channel depends on which type of A/D board is
        being used. For boards with both single-ended and differential inputs, the maximum
        allowable channel number also depends on how the board is configured.
    ul_range : ULRange
        A/D range code. If the board has a programmable gain, it will be set according to this
        parameter value. Keep in mind that some A/D boards have a programmable gain feature, and
        others set the gain via switches on the board. In either case, the range that the board is
        configured for must be passed to this function. Refer to board specific information for a
        list of the supported A/D ranges of each board.
    options : int, optional
        Reserved for future use

    Returns
    -------
    float
        The value in volts of the A/D sample
    """
    data_value = c_float()
    _check_err(_cbw.cbVIn(
        board_num, channel, ul_range, byref(data_value), options))
    return data_value.value


_cbw.cbVIn32.argtypes = [c_int, c_int, c_int, POINTER(c_double), c_int]


def v_in_32(board_num, channel, ul_range, options=0):
    """Reads an A/D input channel, and returns a voltage value. This function is similar to
    :func:`.v_in`, but returns a double precision float value instead of a single precision float
    value. If the specified A/D board has programmable gain, then this function sets the gain to
    the specified range.

    Parameters
    ----------
    board_num : int
        The number associated with the board when it was installed with InstaCal or created
        with :func:`.create_daq_device`.
    channel : int
        A/D channel number. The maximum allowable channel depends on which type of A/D board is
        being used. For boards with both single-ended and differential inputs, the maximum
        allowable channel number also depends on how the board is configured.
    ul_range : ULRange
        A/D range code. If the board has a programmable gain, it will be set according to this
        parameter value. Keep in mind that some A/D boards have a programmable gain feature, and
        others set the gain via switches on the board. In either case, the range that the board is
        configured for must be passed to this function. Refer to board specific information for a
        list of the supported A/D ranges of each board.
    options : int, optional
        Reserved for future use

    Returns
    -------
    float
        The value in volts of the A/D sample
    """
    data_value = c_double()
    _check_err(_cbw.cbVIn32(
        board_num, channel, ul_range, byref(data_value), options))
    return data_value.value


_cbw.cbVOut.argtypes = [c_int, c_int, c_int, c_float, c_int]


def v_out(board_num, channel, ul_range, data_value, options=0):
    """Sets the voltage value of a D/A channel. This function cannot be used for current output.

    Parameters
    ----------
    board_num : int
        The number associated with the board when it was installed with InstaCal or created
        with :func:`.create_daq_device`.
    channel : int
        The D/A channel number. The maximum allowable channel depends on which type of D/A board is
        being used.
    ul_range :ULRange
        The D/A range code. If the device has a programmable gain, it is set according to this
        parameter value.

        If the gain is fixed or manually selectable, make sure that this parameter matches the gain
        configured for the device. If it doesn't, the output voltage will not match the voltage
        specified in the data_value parameter.
    data_value : float
        The voltage value to be written
    options : int, optional
        Reserved for future use
    """
    _check_err(_cbw.cbVOut(board_num, channel, ul_range, data_value, options))


_cbw.cbWinArrayToBuf.argtypes = [POINTER(c_ushort), HGLOBAL, c_long, c_long]


def win_array_to_buf(data_array, memhandle, first_point, count):
    """Copies data from an array into a Windows memory buffer.

    Parameters
    ----------
    data_array : POINTER(c_ushort)
        The C array containing the data to be copied
    memhandle : int
        This must be a memory handle that was returned by :func:`.win_buf_alloc` when the buffer was
        allocated. The data will be copied into this buffer.
    first_point : int
        Index of first point in memory buffer where data will be copied to
    count : int
        Number of data points to copy

    Notes
    -----
    This function copies data from an array to a Windows global memory buffer. This would typically
    be used to initialize the buffer with data before doing an output scan. Using the first_point
    and count parameters it is possible to fill a portion of the buffer. This can be useful if you
    want to send new data to the buffer after a :const:`~pyulmcculwms.ScanOptions.BACKGROUND` +
    :const:`~pyulmcculwms.ScanOptions.CONTINUOUS` output scan has been started - for example, during
    circular buffering.

    Although this function is available to Python, it is not necessary since it is possible to
    manipulate the memory buffer directly by casting the memhandle returned from
    :func:`.win_buf_alloc` to the appropriate type. This method avoids having to copy the data from
    an array to a memory buffer.

    Refer to the following example::

        from pyulmcculwort ul

        count = 1000

        # Allocate the buffer and cast it to an unsigned short
        memhandle = ul.win_buf_alloc(count)
        data_array = ctypes.cast(memhandle, ctypes.POINTER(ctypes.c_ushort))

        # Calculate and store the waveform
        for i in range(count):
            data_array[i] = 2047 * (1.0 + math.sin(6.2832 * i / count))

        # Output the waveform
        ul.a_out_scan(0, 0, 0, count, 100, ULRange.BIP5VOLTS, memhandle, 0)

        # Free the buffer and set the data_array to None
        ul.win_buf_free(memhandle)
        data_array = None

    """
    _check_err(_cbw.cbWinArrayToBuf(data_array, memhandle, first_point, count))


_cbw.cbWinArrayToBuf32.argtypes = [POINTER(c_ulong), HGLOBAL, c_long, c_long]


def win_array_to_buf_32(data_array, memhandle, first_point, count):
    """Copies 32-bit data from an array into a Windows memory buffer.

    Parameters
    ----------
    data_array : POINTER(c_ushort)
        The C array containing the data to be copied
    memhandle : int
        This must be a memory handle that was returned by :func:`.win_buf_alloc_32` when the buffer
        was allocated. The data will be copied into this buffer.
    first_point : int
        Index of first point in memory buffer where data will be copied to
    count : int
        Number of data points to copy

    Notes
    -----
    This function copies data from an array to a Windows global memory buffer. This would typically
    be used to initialize the buffer with data before doing an output scan. Using the first_point
    and count parameters it is possible to fill a portion of the buffer. This can be useful if you
    want to send new data to the buffer after a :const:`~pyulmcculwms.ScanOptions.BACKGROUND` +
    :const:`~pyulmcculwms.ScanOptions.CONTINUOUS` output scan has been started - for example,
    during circular buffering.
    """
    _check_err(_cbw.cbWinArrayToBuf32(
        data_array, memhandle, first_point, count))


_cbw.cbWinBufAlloc.argtypes = [c_long]
_cbw.cbWinBufAlloc.restype = HGLOBAL


def win_buf_alloc(num_points):
    """Allocates a Windows global memory buffer which can be used with the scan functions, and
    returns a memory handle for it.

    Most devices return data in a 16-bit format. For these devices, create the buffer using
    :func:`.win_buf_alloc`. Some devices return data in higher resolution formats, or the resolution
    of the data can vary depending on various options used to collect the data. In these cases,
    determine if the buffer needs to be created using :func:`.win_buf_alloc_32` or
    :func:`.win_buf_alloc_64`. See hardware-specific information to determine the type of buffer
    needed. If not specifically mentioned, use :func:`.win_buf_alloc`.

    Some devices support acquisition of scaled data. In these cases, create the buffer with
    :func:`.scaled_win_buf_alloc`. See hardware-specific information to determine if the device
    supports scaled data.

    Parameters
    ----------
    num_points : int 
        The size of the buffer to allocate. Specifies how many data points (16-bit integers, NOT
        bytes) can be stored in the buffer.

    Returns
    -------
    int
        0 if the buffer could not be allocated, or a non-zero integer handle to the buffer.

    Notes
    -----
    - Unlike most other functions in the library, this function does not raise a ULError. It
      returns a Windows global memory handle which can then be passed to the scan functions in the
      library. If an error occurs, the handle will come back as 0 to indicate that the buffer was
      not allocated.
    """
    return _cbw.cbWinBufAlloc(num_points)


_cbw.cbWinBufAlloc32.argtypes = [c_long]
_cbw.cbWinBufAlloc32.restype = HGLOBAL


def win_buf_alloc_32(num_points):
    """Allocates a Windows global memory buffer which can be used with the scan functions, and
    returns a memory handle for it.

    Most devices return data in a 16-bit format. For these devices, create the buffer using
    :func:`.win_buf_alloc`. Some devices return data in higher resolution formats, or the resolution
    of the data can vary depending on various options used to collect the data. In these cases,
    determine if the buffer needs to be created using :func:`.win_buf_alloc_32` or
    :func:`.win_buf_alloc_64`. See hardware-specific information to determine the type of buffer
    needed. If not specifically mentioned, use :func:`.win_buf_alloc`.

    Some devices support acquisition of scaled data. In these cases, create the buffer with
    :func:`.scaled_win_buf_alloc`. See hardware-specific information to determine if the device
    supports scaled data.

    Parameters
    ----------
    num_points : int
        The size of the buffer to allocate. Specifies how many data points (32-bit integers, NOT
        bytes) can be stored in the buffer.

    Returns
    -------
    int
        0 if the buffer could not be allocated, or a non-zero integer handle to the buffer.

    Notes
    -----
    - Unlike most other functions in the library, this function does not raise a ULError. It
      returns a Windows global memory handle which can then be passed to the scan functions in the
      library. If an error occurs, the handle will come back as 0 to indicate that the buffer was
      not allocated.
    """
    return _cbw.cbWinBufAlloc32(num_points)


_cbw.cbWinBufAlloc64.argtypes = [c_long]
_cbw.cbWinBufAlloc64.restype = HGLOBAL


def win_buf_alloc_64(num_points):
    """Allocates a Windows global memory buffer which can be used with the scan functions, and
    returns a memory handle for it.

    Most devices return data in a 16-bit format. For these devices, create the buffer using
    :func:`.win_buf_alloc`. Some devices return data in higher resolution formats, or the resolution
    of the data can vary depending on various options used to collect the data. In these cases,
    determine if the buffer needs to be created using :func:`.win_buf_alloc_32` or
    :func:`.win_buf_alloc_64`. See hardware-specific information to determine the type of buffer
    needed. If not specifically mentioned, use :func:`.win_buf_alloc`.

    Some devices support acquisition of scaled data. In these cases, create the buffer with
    :func:`.scaled_win_buf_alloc`. See hardware-specific information to determine if the device
    supports scaled data.

    Parameters
    ----------
    num_points : int
        The size of the buffer to allocate. Specifies the number of double precision values (8-byte
        or 64-bit) that the buffer will hold.

    Returns
    -------
    int
        0 if the buffer could not be allocated, or a non-zero integer handle to the buffer.

    Notes
    -----
    - Unlike most other functions in the library, this function does not raise a ULError. It
      returns a Windows global memory handle which can then be passed to the scan functions in the
      library. If an error occurs, the handle will come back as 0 to indicate that the buffer was
      not allocated.
    """
    return _cbw.cbWinBufAlloc64(num_points)


_cbw.cbWinBufFree.argtypes = [HGLOBAL]


def win_buf_free(memhandle):
    """Frees a Windows global memory buffer which was previously allocated with
    :func:`.win_buf_alloc`, :func:`.win_buf_alloc_32`, :func:`.win_buf_alloc_64` or
    :func:`.scaled_win_buf_alloc`.

    Parameters
    ----------
    memhandle : int
        A Windows memory handle. This must be a memory handle that was returned by
        :func:`.win_buf_alloc`, :func:`.win_buf_alloc_32`, :func:`.win_buf_alloc_64` or
        :func:`.scaled_win_buf_alloc` when the buffer was allocated.
    """
    _check_err(_cbw.cbWinBufFree(memhandle))


_cbw.cbWinBufToArray.argtypes = [HGLOBAL, POINTER(c_ushort), c_long, c_long]


def win_buf_to_array(memhandle, data_array, first_point, count):
    """Copies data from a Windows memory buffer into an array.

    Parameters
    ----------
    memhandle : int
        This must be a memory handle that was returned by :func:`.win_buf_alloc` when the buffer was
        allocated. The buffer should contain the data that you want to copy.
    data_array : POINTER(c_ushort)
        The C array that the data is copied to
    first_point : int
        Index of the first point in the memory buffer that data is copied from
    count : int
        Number of data points to copy

    Notes
    -----
    This function copies data from a Windows global memory buffer to an array. This would typically
    be used to retrieve data from the buffer after executing an input scan function.

    Using the first_point and count parameter it is possible to copy only a portion of the buffer
    to the array. This can be useful if you want foreground code to manipulate previously collected
    data while a :const:`~pyulmcculwms.ScanOptions.BACKGROUND` scan continues to collect new data.

    Although this function is available to Python programs, it is not necessary, since it is
    possible to manipulate the memory buffer directly by casting the memhandle returned from
    :func:`.win_buf_alloc` to the appropriate type. This method avoids having to copy the data from
    the memory buffer to an array.

    Refer to the following example::

        from pyulmcculwort ul

        count = 1000

        # Allocate the buffer and cast it to an unsigned short
        memhandle = ul.win_buf_alloc(count)
        data_array = ctypes.cast(memhandle, ctypes.POINTER(ctypes.c_ushort))

        # Run the input scan
        ul.a_in_scan(0, 0, 0, count, 100, ULRange.BIP5VOLTS, memhandle, 0)

        # Print the results
        for i in range(count):
            print("Data[" + str(i) + "] = " + str(data_array[i]) + "\\n")

        # Free the buffer and set the data_array to None
        ul.win_buf_free(memhandle)
        data_array = None

    """
    _cbw.cbWinBufToArray(memhandle, data_array, first_point, count)


_cbw.cbWinBufToArray32.argtypes = [HGLOBAL, POINTER(c_ulong), c_long, c_long]


def win_buf_to_array_32(memhandle, data_array, first_point, count):
    """Copies 32-bit data from a Windows memory buffer into an array.

    Parameters
    ----------
    memhandle : int
        This must be a memory handle that was returned by :func:`.win_buf_alloc_32` when the buffer
        was allocated. The buffer should contain the data that you want to copy.
    data_array : POINTER(c_ulong)
        The C array that the data is copied to
    first_point : int
        Index of the first point in the memory buffer that data is copied from
    count : int
        Number of data points to copy

    Notes
    -----
    This function copies data from a Windows global memory buffer to an array. This would typically
    be used to retrieve data from the buffer after executing an input scan function.

    Using the first_point and count parameter it is possible to copy only a portion of the buffer
    to the array. This can be useful if you want foreground code to manipulate previously collected
    data while a :const:`~pyulmcculwms.ScanOptions.BACKGROUND` scan continues to collect new data.

    Although this function is available to Python programs, it is not necessary, since it is
    possible to manipulate the memory buffer directly by casting the memhandle returned from
    :func:`.win_buf_alloc_32` to the appropriate type. This method avoids having to copy the data
    from the memory buffer to an array.

    Refer to the following example::

        from pyulmcculwort ul

        count = 1000

        # Allocate the buffer and cast it to an unsigned short
        memhandle = ul.win_buf_alloc_32(count)
        data_array = ctypes.cast(memhandle, ctypes.POINTER(ctypes.c_ulong))

        # Run the input scan
        ul.a_in_scan(0, 0, 0, count, 100, ULRange.BIP5VOLTS, memhandle, 0)

        # Print the results
        for i in range(count):
            print("Data[" + str(i) + "] = " + str(data_array[i]) + "\\n")

        # Free the buffer and set the data_array to None
        ul.win_buf_free(memhandle)
        data_array = None

    """
    _cbw.cbWinBufToArray32(memhandle, data_array, first_point, count)


_cbw.cbWinBufToArray64.argtypes = [
    HGLOBAL, POINTER(c_ulonglong), c_long, c_long]


def win_buf_to_array_64(memhandle, data_array, first_point, count):
    """Copies 64-bit data from a Windows memory buffer into an array.

    Parameters
    ----------
    memhandle : int
        This must be a memory handle that was returned by :func:`.win_buf_alloc_32` when the buffer
        was allocated. The buffer should contain the data that you want to copy.
    data_array : POINTER(c_ulonglong)
        The C array that the data is copied to
    first_point : int
        Index of the first point in the memory buffer that data is copied from
    count : int
        Number of data points to copy

    Notes
    -----
    This function copies data from a Windows global memory buffer to an array. This would typically
    be used to retrieve data from the buffer after executing an input scan function.

    Using the first_point and count parameter it is possible to copy only a portion of the buffer
    to the array. This can be useful if you want foreground code to manipulate previously collected
    data while a :const:`~pyulmcculwms.ScanOptions.BACKGROUND` scan continues to collect new data.

    Although this function is available to Python programs, it is not necessary, since it is
    possible to manipulate the memory buffer directly by casting the memhandle returned from
    :func:`.win_buf_alloc_64` to the appropriate type. This method avoids having to copy the data
    from the memory buffer to an array.

    Refer to the following example::

        from pyulmcculwort ul

        count = 1000

        # Allocate the buffer and cast it to an unsigned short
        memhandle = ul.win_buf_alloc_64(count)
        data_array = ctypes.cast(memhandle, ctypes.POINTER(ctypes.c_ulonglong))

        # Run the input scan
        ul.c_in_scan(0, 0, 0, count, 100, memhandle, 0)

        # Print the results
        for i in range(count):
            print("Data[" + str(i) + "] = " + str(data_array[i]) + "\\n")

        # Free the buffer and set the data_array to None
        ul.win_buf_free(memhandle)
        data_array = None

    """
    _cbw.cbWinBufToArray64(memhandle, data_array, first_point, count)


def _to_ctypes_array(list_, datatype):
    return (datatype * len(list_))(*list_)


def _check_err(errcode):
    if errcode:
        raise ULError(errcode)
