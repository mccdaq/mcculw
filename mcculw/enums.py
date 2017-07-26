# -*- coding: UTF-8 -*-

from __future__ import absolute_import, division, print_function

try:
    # Prefer the Python 3.6+ IntFlag
    from enum import IntFlag
except ImportError:
    # Fall back to aenum's IntFlag if necessary
    from aenum import IntFlag
from builtins import *  # @UnusedWildImport
from enum import IntEnum


class ErrorCode(IntEnum):
    # System error code
    NOERRORS = 0  # No error occurred
    BADBOARD = 1  # Invalid board number specified
    DEADDIGITALDEV = 2  # Digital I/O device is not responding
    DEADCOUNTERDEV = 3  # Counter I/O device is not responding
    DEADDADEV = 4  # D/A is not responding
    DEADADDEV = 5  # A/D is not responding
    NOTDIGITALCONF = 6  # Specified board does not have digital I/O
    NOTCOUNTERCONF = 7  # Specified board does not have a counter
    NOTDACONF = 8  # Specified board is does not have D/A
    NOTADCONF = 9  # Specified board does not have A/D
    NOTMUXCONF = 10  # Specified board does not have thermocouple inputs
    BADPORTNUM = 11  # Invalid port number specified
    BADCOUNTERDEVNUM = 12  # Invalid counter device
    BADDADEVNUM = 13  # Invalid D/A device
    BADSAMPLEMODE = 14  # Invalid sampling mode option specified
    BADINT = 15  # Board configured for invalid interrupt level
    BADADCHAN = 16  # Invalid A/D channel Specified
    BADCOUNT = 17  # Invalid count specified
    BADCNTRCONFIG = 18  # invalid counter configuration specified
    BADDAVAL = 19  # Invalid D/A output value specified
    BADDACHAN = 20  # Invalid D/A channel specified
    ALREADYACTIVE = 22  # A background process is already in progress
    PAGEOVERRUN = 23  # DMA transfer crossed page boundary, may have gaps in data
    BADRATE = 24  # Inavlid sampling rate specified
    COMPATMODE = 25  # Board switches set for "compatible" mode
    TRIGSTATE = 26  # Incorrect intial trigger state D0 must=TTL low)
    ADSTATUSHUNG = 27  # A/D is not responding
    TOOFEW = 28  # Too few samples before trigger occurred
    OVERRUN = 29  # Data lost due to overrun, rate too high
    BADRANGE = 30  # Invalid range specified
    NOPROGGAIN = 31  # Board does not have programmable gain
    BADFILENAME = 32  # Not a legal DOS filename
    DISKISFULL = 33  # Couldn't complete, disk is full
    COMPATWARN = 34  # Board is in compatible mode, so DMA will be used
    BADPOINTER = 35  # Invalid pointer (NULL)
    TOOMANYGAINS = 36  # Too many gains
    RATEWARNING = 37  # Rate may be too high for interrupt I/O
    CONVERTDMA = 38  # CONVERTDATA cannot be used with DMA I/O
    DTCONNECTERR = 39  # Board doesn't have DT Connect
    FORECONTINUOUS = 40  # CONTINUOUS can only be used with BACKGROUND
    BADBOARDTYPE = 41  # This function can not be used with this board
    WRONGDIGCONFIG = 42  # Digital I/O is configured incorrectly
    NOTCONFIGURABLE = 43  # Digital port is not configurable
    BADPORTCONFIG = 44  # Invalid port configuration specified
    BADFIRSTPOINT = 45  # First point argument is not valid
    ENDOFFILE = 46  # Attempted to read past end of file
    NOT8254CTR = 47  # This board does not have an 8254 counter
    NOT9513CTR = 48  # This board does not have a 9513 counter
    BADTRIGTYPE = 49  # Invalid trigger type
    BADTRIGVALUE = 50  # Invalid trigger value
    BADOPTION = 52  # Invalid option specified for this function
    BADPRETRIGCOUNT = 53  # Invalid pre-trigger count sepcified
    BADDIVIDER = 55  # Invalid fout divider value
    BADSOURCE = 56  # Invalid source value
    BADCOMPARE = 57  # Invalid compare value
    BADTIMEOFDAY = 58  # Invalid time of day value
    BADGATEINTERVAL = 59  # Invalid gate interval value
    BADGATECNTRL = 60  # Invalid gate control value
    BADCOUNTEREDGE = 61  # Invalid counter edge value
    BADSPCLGATE = 62  # Invalid special gate value
    BADRELOAD = 63  # Invalid reload value
    BADRECYCLEFLAG = 64  # Invalid recycle flag value
    BADBCDFLAG = 65  # Invalid BCD flag value
    BADDIRECTION = 66  # Invalid count direction value
    BADOUTCONTROL = 67  # Invalid output control value
    BADBITNUMBER = 68  # Invalid bit number
    NONEENABLED = 69  # None of the counter channels are enabled
    BADCTRCONTROL = 70  # Element of control array not ENABLED/DISABLED
    BADEXPCHAN = 71  # Invalid EXP channel
    WRONGADRANGE = 72  # Wrong A/D range selected for cbtherm
    OUTOFRANGE = 73  # Temperature input is out of range
    BADTEMPSCALE = 74  # Invalid temperate scale
    BADERRCODE = 75  # Invalid error code specified
    NOQUEUE = 76  # Specified board does not have chan/gain queue
    CONTINUOUSCOUNT = 77  # CONTINUOUS can not be used with this count value
    UNDERRUN = 78  # D/A FIFO hit empty while doing output
    BADMEMMODE = 79  # Invalid memory mode specified
    FREQOVERRUN = 80  # Measured frequency too high for gating interval
    NOCJCCHAN = 81  # Board does not have CJC chan configured
    BADCHIPNUM = 82  # Invalid chip number used with c_9513_init
    DIGNOTENABLED = 83  # Digital I/O not enabled
    CONVERT16BITS = 84  # CONVERT option not allowed with 16 bit A/D
    NOMEMBOARD = 85  # EXTMEMORY option requires memory board
    DTACTIVE = 86  # Memory I/O while DT Active
    NOTMEMCONF = 87  # Specified board is not a memory board
    ODDCHAN = 88  # First chan in queue can not be odd
    CTRNOINIT = 89  # Counter was not initialized
    NOT8536CTR = 90  # Specified counter is not an 8536
    FREERUNNING = 91  # A/D sampling is not timed
    INTERRUPTED = 92  # Operation interrupted with CTRL-C
    NOSELECTORS = 93  # Selector could not be allocated
    NOBURSTMODE = 94  # Burst mode is not supported on this board
    NOTWINDOWSFUNC = 95  # This function not available in Windows lib
    NOTSIMULCONF = 96  # Not configured for simultaneous update
    EVENODDMISMATCH = 97  # Even channel in odd slot in the queue
    M1RATEWARNING = 98  # DAS16/M1 sample rate too fast
    NOTRS485 = 99  # Board is not an RS-485 board
    NOTDOSFUNC = 100  # This function not avaliable in DOS
    RANGEMISMATCH = 101  # Unipolar and Bipolar can not be used together in A/D que
    CLOCKTOOSLOW = 102  # Sample rate too fast for clock jumper setting
    BADCALFACTORS = 103  # Cal factors were out of expected range of values
    BADCONFIGTYPE = 104  # Invalid configuration type information requested
    BADCONFIGITEM = 105  # Invalid configuration item specified
    NOPCMCIABOARD = 106  # Can't acces PCMCIA board
    NOBACKGROUND = 107  # Board does not support background I/O
    STRINGTOOSHORT = 108  # String passed to get_board_name is to short
    CONVERTEXTMEM = 109  # Convert data option not allowed with external memory
    BADEUADD = 110  # e_ToEngUnits addition error
    DAS16JRRATEWARNING = 111  # use 10 MHz clock for rates > 125KHz
    DAS08TOOLOWRATE = 112  # DAS08 rate set too low for AInScan warning
    AMBIGSENSORONGP = 114  # more than one sensor type defined for EXP-GP
    NOSENSORTYPEONGP = 115  # no sensor type defined for EXP-GP
    NOCONVERSIONNEEDED = 116  # 12 bit board without chan tags - converted in ISR
    NOEXTCONTINUOUS = 117  # External memory cannot be used in CONTINUOUS mode
    # a_convert_pretrig_data was called after failure in a_pretrig
    INVALIDPRETRIGCONVERT = 118
    BADCTRREG = 119  # bad arg to CLoad for 9513
    BADTRIGTHRESHOLD = 120  # Invalid trigger threshold specified in set_trigger
    BADPCMSLOTREF = 121  # No PCM card in specified slot
    AMBIGPCMSLOTREF = 122  # More than one CBI PCM card in slot
    BADSENSORTYPE = 123  # Bad sensor type selected in Instacal
    DELBOARDNOTEXIST = 124  # tried to delete board number which doesn't exist
    NOBOARDNAMEFILE = 125  # board name file not found
    CFGFILENOTFOUND = 126  # configuration file not found
    NOVDDINSTALLED = 127  # CBUL.386 device driver not installed
    NOWINDOWSMEMORY = 128  # No Windows memory available
    OUTOFDOSMEMORY = 129  # ISR data struct alloc failure
    OBSOLETEOPTION = 130  # Obsolete option for get_config/set_config
    NOPCMREGKEY = 131  # No registry entry for this PCMCIA board
    NOCBUL32SYS = 132  # CBUL32.SYS device driver is not loaded
    NODMAMEMORY = 133  # No DMA buffer available to device driver
    IRQNOTAVAILABLE = 134  # IRQ in being used by another device
    NOT7266CTR = 135  # This board does not have an LS7266 counter
    BADQUADRATURE = 136  # Invalid quadrature specified
    BADCOUNTMODE = 137  # Invalid counting mode specified
    BADENCODING = 138  # Invalid data encoding specified
    BADINDEXMODE = 139  # Invalid index mode specified
    BADINVERTINDEX = 140  # Invalid invert index specified
    BADFLAGPINS = 141  # Invalid flag pins specified
    NOCTRSTATUS = 142  # This board does not support c_status()
    NOGATEALLOWED = 143  # Gating and indexing not allowed simultaneously
    NOINDEXALLOWED = 144  # Indexing not allowed in non-quadratue mode
    OPENCONNECTION = 145  # Temperature input has open connection
    # Count must be integer multiple of packetsize for recycle mode.
    BMCONTINUOUSCOUNT = 146
    BADCALLBACKFUNC = 147  # Invalid pointer to callback function passed as arg
    MBUSINUSE = 148  # MetraBus in use
    MBUSNOCTLR = 149  # MetraBus I/O card has no configured controller card
    BADEVENTTYPE = 150  # Invalid event type specified for this board.
    ALREADYENABLED = 151  # An event handler has already been enabled for this event type
    BADEVENTSIZE = 152  # Invalid event count specified.
    CANTINSTALLEVENT = 153  # Unable to install event handler
    BADBUFFERSIZE = 154  # Buffer is too small for operation
    BADAIMODE = 155  # Invalid Analog Input Mode specified

    BADSIGNAL = 156
    BADCONNECTION = 157
    BADINDEX = 158
    NOCONNECTION = 159

    BADBURSTIOCOUNT = 160  # Count cannot be greater than FIFO size for BURSTIO scans
    DEADDEV = 161  # Device no longer responding
    BADCONFIGVAL = 162

    INVALIDACCESS = 163  # Invalid access or privilege for specified operation
    # Device unavailable at time of request. Please repeat operation.
    UNAVAILABLE = 164
    # Device is not ready to send data. Please repeat operation.
    NOTREADY = 165
    OWNERSHIPREFUSED = 166  # Current device owner refused to release device.
    OWNERSHIPFAILED = 167  # No response from current device owner,
    NETERROR = 168  # Network error.
    BITUSEDFORALARM = 169  # The specified bit is used for alarm.
    # One or more bits on the specified port are used for alarm.
    PORTUSEDFORALARM = 170
    PACEROVERRUN = 171  # Pacer overrun, external clock rate too fast.
    BADCHANTYPE = 172  # Invalid channel type specified
    BADTRIGSENSE = 173  # Invalid trigger sensitivity specified
    BADTRIGCHAN = 174  # Invalid trigger channel specified
    BADTRIGLEVEL = 175  # Invalid trigger level specified
    NOPRETRIGMODE = 176  # Pre-trigger mode is not supported for the specified trigger type
    BADDEBOUNCETIME = 177  # Invalid debounce time specified
    BADDEBOUNCETRIGMODE = 178  # Invalid debounce trigger mode specified
    BADMAPPEDCOUNTER = 179  # Invalid mapped counter specified
    # This function can not be used with the current mode of the specified
    # counter
    BADCOUNTERMODE = 180
    BADTCCHANMODE = 181  # Single-Ended mode can not be used for temperature input
    BADFREQUENCY = 182  # Invalid frequency specified.
    BADEVENTPARAM = 183  # Invalid event parameter specified.
    NONETIFC = 184  # No interface cards with specified PAN and channel.
    DEADNETIFC = 185
    NOREMOTEACK = 186
    INPUTTIMEOUT = 187
    # Number of Setpoints not equal to number of channels with setpoint flag
    # set
    MISMATCHSETPOINTCOUNT = 188
    INVALIDSETPOINTLEVEL = 189  # Setpoint Level is outside channel range
    INVALIDSETPOINTOUTPUTTYPE = 190  # Setpoint Output Type is invalid
    INVALIDSETPOINTOUTPUTVALUE = 191  # Setpoint Output Value is outside channel range
    INVALIDSETPOINTLIMITS = 192  # Setpoint Comparison limit B greater than Limit A
    STRINGTOOLONG = 193
    INVALIDLOGIN = 194
    SESSIONINUSE = 195
    NOEXTPOWER = 196  # External power is not connected.
    BADDUTYCYCLE = 197  # Invalid duty cycle specified.
    INVALIDPASSWORD = 198
    BADINITIALDELAY = 199  # Invalid initial delay specified
    # No TEDS sensor was detected on the specified channel.
    NOTEDSSENSOR = 1000
    # Connected TEDS sensor to the specified channel is not supported
    INVALIDTEDSSENSOR = 1001
    CALIBRATIONFAILED = 1002  # Calibration failed
    # The specified bit is used for terminal count stauts.
    BITUSEDFORTERMINALCOUNTSTATUS = 1003
    # One or more bits on the specified port are used for terminal count
    # stauts.
    PORTUSEDFORTERMINALCOUNTSTATUS = 1004
    BADEXCITATION = 1005  # Invalid excitation specified
    BADBRIDGETYPE = 1006  # Invalid bridge type specified
    BADLOADVAL = 1007  # Invalid load value specified
    BADTICKSIZE = 1008  # Invalid tick size specified
    MINSLOPEVALREACHED = 1009  # Minimum slope value reached
    MAXSLOPEVALREACHED = 1010  # Maximum slope value reached
    MINOFFSETVALREACHED = 1011  # Minimum offset value reached
    MAXOFFSETVALREACHED = 1012  # Maximum offset value reached
    BTHCONNECTIONFAILED = 1013  # Bluetooth connection failed
    INVALIDBTHFRAME = 1014  # Invalid Bluetooth frame
    BADTRIGEVENT = 1015  # Invalid trigger event specified
    NETCONNECTIONFAILED = 1016  # Network connection failed
    DATASOCKETCONNECTIONFAILED = 1017  # Data socket connection failed
    INVALIDNETFRAME = 1018  # Invalid Network frame
    NETTIMEOUT = 1019  # Network device did not respond within expected time
    NETDEVNOTFOUND = 1020  # Network device not found
    INVALIDCONNECTIONCODE = 1021  # Invalid connection code
    CONNECTIONCODEIGNORED = 1022  # Connection code ignored
    NETDEVINUSE = 1023  # Network device already in use
    NETDEVINUSEBYANOTHERPROC = 1024  # Network device already in use by another process
    SOCKETDISCONNECTED = 1025  # Socket Disconnected
    BOARDNUMINUSE = 1026  # Board Number already in use
    DEVALREADYCREATED = 1027  # Specified DAQ device already created
    BOARDNOTEXIST = 1028  # Tried to release a board which doesn't exist
    INVALIDNETHOST = 1029  # Invalid host specified
    INVALIDNETPORT = 1030  # Invalid port specified
    INVALIDIFC = 1031  # Invalid interface specified
    INVALIDAIINPUTMODE = 1032  # Invalid input mode specified
    AIINPUTMODENOTCONFIGURABLE = 1033  # Input mode not configurable
    INVALIDEXTPACEREDGE = 1034  # Invalid external pacer edge
    CMREXCEEDED = 1035  # Common-mode voltage range exceeded
    BADTRIGSRC = 1036  # Invalid trigger source

    # Internal errors returned by 16 bit library
    INTERNALERR = 200  # 200-299 Internal library error
    CANT_LOCK_DMA_BUF = 201  # DMA buffer could not be locked
    DMA_IN_USE = 202  # DMA already controlled by another VxD
    BAD_MEM_HANDLE = 203  # Invalid Windows memory handle
    NO_ENHANCED_MODE = 204  # Windows Enhance mode is not running
    MEMBOARDPROGERROR = 211  # Program error getting memory board source

    # Internal errors returned by 32 bit library
    INTERNAL32_ERR = 300  # 300-399 32 bit library internal errors
    # 32 bit - default buffer allocation when no user buffer used with file
    NO_MEMORY_FOR_BUFFER = 301
    WIN95_CANNOT_SETUP_ISR_DATA = 302  # 32 bit - failure on INIT_ISR_DATA IOCTL call
    WIN31_CANNOT_SETUP_ISR_DATA = 303  # 32 bit - failure on INIT_ISR_DATA IOCTL call
    CFG_FILE_READ_FAILURE = 304  # 32 bit - error reading board configuration file
    CFG_FILE_WRITE_FAILURE = 305  # 32 bit - error writing board configuration file
    CREATE_BOARD_FAILURE = 306  # 32 bit - failed to create board
    DEVELOPMENT_OPTION = 307  # 32 bit - Config Option item used in development only
    CFGFILE_CANT_OPEN = 308  # 32 bit - cannot open configuration file.
    CFGFILE_BAD_ID = 309  # 32 bit - incorrect file id.
    CFGFILE_BAD_REV = 310  # 32 bit - incorrect file version.
    CFGFILE_NOINSERT = 311  # ;
    CFGFILE_NOREPLACE = 312  # ;
    BIT_NOT_ZERO = 313  # ;
    BIT_NOT_ONE = 314  # ;
    BAD_CTRL_REG = 315  # No control register at this location.
    BAD_OUTP_REG = 316  # No output register at this location.
    BAD_RDBK_REG = 317  # No read back register at this location.
    NO_CTRL_REG = 318  # No control register on this board.
    NO_OUTP_REG = 319  # No control register on this board.
    NO_RDBK_REG = 320  # No control register on this board.
    CTRL_REG_FAIL = 321  # internal ctrl reg test failed.
    OUTP_REG_FAIL = 322  # internal output reg test failed.
    RDBK_REG_FAIL = 323  # internal read back reg test failed.
    FUNCTION_NOT_IMPLEMENTED = 324
    BAD_RTD_CONVERSION = 325  # Overflow in RTD calculation
    NO_PCI_BIOS = 326  # PCI BIOS not present in the PC
    BAD_PCI_INDEX = 327  # Invalid PCI board index passed to PCI BIOS
    NO_PCI_BOARD = 328  # Specified PCI board not detected
    PCI_ASSIGN_FAILED = 329  # PCI resource assignment failed
    PCI_NO_ADDRESS = 330  # No PCI address returned
    PCI_NO_IRQ = 331  # No PCI IRQ returned
    CANT_INIT_ISR_INFO = 332  # IOCTL call failed on VDD_API_INIT_ISR_INFO
    CANT_PASS_USER_BUFFER = 333  # IOCTL call failed on VDD_API_PASS_USER_BUFFER
    CANT_INSTALL_INT = 334  # IOCTL call failed on VDD_API_INSTALL_INT
    CANT_UNINSTALL_INT = 335  # IOCTL call failed on VDD_API_UNINSTALL_INT
    CANT_START_DMA = 336  # IOCTL call failed on VDD_API_START_DMA
    CANT_GET_STATUS = 337  # IOCTL call failed on VDD_API_GET_STATUS
    CANT_GET_PRINT_PORT = 338  # IOCTL call failed on VDD_API_GET_PRINT_PORT
    CANT_MAP_PCM_CIS = 339  # IOCTL call failed on VDD_API_MAP_PCM_CIS
    CANT_GET_PCM_CFG = 340  # IOCTL call failed on VDD_API_GET_PCM_CFG
    CANT_GET_PCM_CCSR = 341  # IOCTL call failed on VDD_API_GET_PCM_CCSR
    CANT_GET_PCI_INFO = 342  # IOCTL call failed on VDD_API_GET_PCI_INFO
    NO_USB_BOARD = 343  # Specified USB board not detected
    NOMOREFILES = 344  # No more files in the directory
    BADFILENUMBER = 345  # Invalid file number
    INVALIDSTRUCTSIZE = 346  # Invalid structure size
    LOSSOFDATA = 347  # EOF marker not found, possible loss of data
    INVALIDBINARYFILE = 348  # File is not a valid MCC binary file
    INVALIDDELIMITER = 349  # Invlid delimiter specified for CSV file
    NO_BTH_BOARD = 350  # Specified Bluetooth board not detected
    NO_NET_BOARD = 351  # Specified Network board not detected

    # DOS errors are remapped by adding DOS_ERR_OFFSET to them */
    DOS_ERR_OFFSET = 500
    # These are the commonly occurring remapped DOS error codes
    DOSBADFUNC = 501
    DOSFILENOTFOUND = 502
    DOSPATHNOTFOUND = 503
    DOSNOHANDLES = 504
    DOSACCESSDENIED = 505
    DOSINVALIDHANDLE = 506
    DOSNOMEMORY = 507
    DOSBADDRIVE = 515
    DOSTOOMANYFILES = 518
    DOSWRITEPROTECT = 519
    DOSDRIVENOTREADY = 521
    DOSSEEKERROR = 525
    DOSWRITEFAULT = 529
    DOSREADFAULT = 530
    DOSGENERALFAULT = 531  # Windows internal error codes
    WIN_CANNOT_ENABLE_INT = 603
    WIN_CANNOT_DISABLE_INT = 605
    WIN_CANT_PAGE_LOCK_BUFFER = 606
    NO_PCM_CARD = 630


class FunctionType(IntEnum):
    AIFUNCTION = 1  # Analog Input Function
    AOFUNCTION = 2  # Analog Output Function
    DIFUNCTION = 3  # Digital Input Function
    DOFUNCTION = 4  # Digital Output Function
    CTRFUNCTION = 5  # Counter Function
    DAQIFUNCTION = 6  # Daq Input Function
    DAQOFUNCTION = 7  # Daq Output Function


class DeviceType(IntEnum):
    AIDEVICE = 1  # Analog Input Device
    AODEVICE = 2  # Analog Output Device
    DIODEVICE = 3  # Digital IO Device
    CTRDEVICE = 4  # Counter Device
    DAQIDEVICE = 5  # Daq Input Device
    DAQODEVICE = 6  # Daq Output Device


class FirmwareVersionType(IntEnum):
    MAIN = 0
    MEASUREMENT = 1
    RADIO = 2
    FPGA = 3
    MEASUREMENT_EXP = 4


class Status(IntEnum):
    IDLE = 0
    RUNNING = 1


class XferMode(IntEnum):
    KERNEL = 0
    USER = 1


class AdTimingMode(IntEnum):
    HIGH_SPEED = 1  # High Speed
    REJECTION_60HZ = 8  # 60 Hz rejection
    REJECTION_50HZ = 9  # 50 Hz rejection
    HIGH_RESOLUTION = 15  # High resolution


class CalTable(IntEnum):
    FACTORY = 0
    FIELD = 1


class ScanOptions(IntFlag):
    FOREGROUND = 0x0000  # Run in foreground, don't return till done
    BACKGROUND = 0x0001  # Run in background, return immediately

    SINGLEEXEC = 0x0000  # One execution
    CONTINUOUS = 0x0002  # Run continuously until cbstop() called

    TIMED = 0x0000  # Time conversions with internal clock
    EXTCLOCK = 0x0004  # Time conversions with external clock

    NOCONVERTDATA = 0x0000  # Return raw data
    CONVERTDATA = 0x0008  # Return converted A/D data

    SCALEDATA = 0x0010  # Scale counts to volts

    DEFAULTIO = 0x0000  # Use whatever makes sense for board
    SINGLEIO = 0x0020  # Interrupt per A/D conversion
    DMAIO = 0x0040  # DMA transfer
    BLOCKIO = 0x0060  # Interrupt per block of conversions
    BURSTIO = 0x010000  # Transfer upon scan completion
    RETRIGMODE = 0x020000  # Re-arm the trigger every N-sample acquisition
    NONSTREAMEDIO = 0x040000  # Non-streamed D/A output
    ADCCLOCKTRIG = 0x080000  # Output operation is triggered on ADC clock
    ADCCLOCK = 0x100000  # Output operation is paced by ADC clock
    HIGHRESRATE = 0x200000  # Use high resolution rate
    SHUNTCAL = 0x400000  # Enable Shunt Calibration
    RES_BLOCK_IO = 0x40000000  # Reserved for BLOCK_IO

    BYTEXFER = 0x0000  # Digital IN/OUT a byte at a time
    WORDXFER = 0x0100  # Digital IN/OUT a word at a time
    DWORDXFER = 0x0200  # Digital IN/OUT a double word at a time

    INDIVIDUAL = 0x0000  # Individual D/A output
    SIMULTANEOUS = 0x0200  # Simultaneous D/A output

    BURSTMODE = 0x1000  # Enable burst mode

    EXTTRIGGER = 0x4000  # A/D is triggered externally

    NOCALIBRATEDATA = 0x8000  # Return uncalibrated PCM data
    CALIBRATEDATA = 0x0000  # Return calibrated PCM A/D data

    CTR16BIT = 0x0000  # Return 16-bit counter data
    CTR32BIT = 0x0100  # Return 32-bit counter data
    CTR48BIT = 0x0200  # Return 48-bit counter data
    CTR64BIT = 0x0400  # Return 64-bit counter data
    NOCLEAR = 0x0800  # Disables clearing counters when scan starts


class PulseOutOptions(IntFlag):
    NONE = 0
    EXTTRIGGER = 0x4000  # A/D is triggered externally
    RETRIGMODE = 0x020000  # Re-arm the trigger every N-sample acquisition


class TInOptions(IntFlag):
    FILTER = 0x0000  # Filter thermocouple inputs
    NOFILTER = 0x0400  # Disable filtering for thermocouple

    WAITFORNEWDATA = 0x2000  # Wait for new data to become available


class State(IntEnum):
    ENABLED = 1
    DISABLED = 0


class ExtClkType(IntEnum):
    CONTINUOUS = 1
    GATED = 2


class DACUpdate(IntEnum):
    IMMEDIATE = 0
    ONCOMMAND = 1


class ErrorReporting(IntEnum):
    DONTPRINT = 0
    PRINTWARNINGS = 1
    PRINTFATAL = 2
    PRINTALL = 3


class ChannelType(IntFlag):
    ANALOG = 0  # Analog channel
    DIGITAL8 = 1  # 8-bit digital port
    DIGITAL16 = 2  # 16-bit digital port
    CTR16 = 3  # 16-bit counter
    CTR32LOW = 4  # Lower 16-bits of 32-bit counter
    CTR32HIGH = 5  # Upper 16-bits of 32-bit counter
    CJC = 6  # CJC channel
    TC = 7  # Thermocouple channel
    ANALOG_SE = 8  # Analog channel, singel-ended mode
    ANALOG_DIFF = 9  # Analog channel, Differential mode
    SETPOINTSTATUS = 10  # Setpoint status channel
    CTRBANK0 = 11  # Bank 0 of counter
    CTRBANK1 = 12  # Bank 1 of counter
    CTRBANK2 = 13  # Bank 2 of counter
    CTRBANK3 = 14  # Bank 3 of counter
    PADZERO = 15  # Dummy channel. Fills the corresponding data elements with zero
    DIGITAL = 16
    CTR = 17
    SETPOINT_ENABLE = 0x100


class SetpointFlag(IntFlag):
    EQUAL_LIMITA = 0x00  # Channel = LimitA value
    LESSTHAN_LIMITA = 0x01  # Channel < LimitA value
    # Channel Inside LimitA and LimitB (LimitA < Channel < LimitB)
    INSIDE_LIMITS = 0x02
    GREATERTHAN_LIMITB = 0x03  # Channel > LimitB
    # Channel Outside LimitA and LimitB (LimitA < Channel or Channel > LimitB)
    OUTSIDE_LIMITS = 0x04
    HYSTERESIS = 0x05  # Use As Hysteresis
    # Latch output condition (output = output1 for duration of acquisition)
    UPDATEON_TRUEONLY = 0x00
    # Do not latch output condition (output = output1 when criteria met else
    # output = output2)
    UPDATEON_TRUEANDFALSE = 0x08


class SetpointOutput(IntEnum):
    NONE = 0  # No Output
    DIGITALPORT = 1  # Output to digital Port
    FIRSTPORTC = 1  # Output to first PortC
    DAC0 = 2  # Output to DAC0
    DAC1 = 3  # Output to DAC1
    DAC2 = 4  # Output to DAC2
    DAC3 = 5  # Output to DAC3
    TMR0 = 6  # Output to TMR0
    TMR1 = 7  # Output to TMR1


class TriggerSource(IntEnum):
    IMMEDIATE = 0
    EXTTTL = 1
    ANALOG_HW = 2
    ANALOG_SW = 3
    DIGPATTERN = 4
    COUNTER = 5
    SCANCOUNT = 6


class TriggerSensitivity(IntEnum):
    RISING_EDGE = 0
    FALLING_EDGE = 1
    ABOVE_LEVEL = 2
    BELOW_LEVEL = 3
    EQ_LEVEL = 4
    NE_LEVEL = 5
    HIGH_LEVEL = 6
    LOW_LEVEL = 7


class TriggerEvent(IntEnum):
    START = 0
    STOP = 1


class SettleTime(IntEnum):
    DEFAULT = 0
    SETTLE_1us = 1
    SETTLE_5us = 2
    SETTLE_10us = 3
    SETTLE_1ms = 4


class DigitalIODirection(IntEnum):
    OUT = 1
    IN = 2


class TempScale(IntEnum):
    CELSIUS = 0
    FAHRENHEIT = 1
    KELVIN = 2
    VOLTS = 4  # special scale for DAS-TC boards
    NOSCALE = 5


class BridgeType(IntEnum):
    FULL = 1
    HALF = 2
    QUARTER = 3


class DigitalPortType(IntEnum):
    AUXPORT = 1
    AUXPORT0 = 1
    AUXPORT1 = 2
    AUXPORT2 = 3
    FIRSTPORTA = 10
    FIRSTPORTB = 11
    FIRSTPORTC = 12
    FIRSTPORTCL = 12
    FIRSTPORTCH = 13
    SECONDPORTA = 14
    SECONDPORTB = 15
    SECONDPORTCL = 16
    SECONDPORTCH = 17
    THIRDPORTA = 18
    THIRDPORTB = 19
    THIRDPORTCL = 20
    THIRDPORTCH = 21
    FOURTHPORTA = 22
    FOURTHPORTB = 23
    FOURTHPORTCL = 24
    FOURTHPORTCH = 25
    FIFTHPORTA = 26
    FIFTHPORTB = 27
    FIFTHPORTCL = 28
    FIFTHPORTCH = 29
    SIXTHPORTA = 30
    SIXTHPORTB = 31
    SIXTHPORTCL = 32
    SIXTHPORTCH = 33
    SEVENTHPORTA = 34
    SEVENTHPORTB = 35
    SEVENTHPORTCL = 36
    SEVENTHPORTCH = 37
    EIGHTHPORTA = 38
    EIGHTHPORTB = 39
    EIGHTHPORTCL = 40
    EIGHTHPORTCH = 41


class AnalogInputMode(IntEnum):
    DIFFERENTIAL = 0
    SINGLE_ENDED = 1
    GROUNDED = 16


class ULRangeEnum(IntEnum):
    def __new__(cls, int_value, range_min, range_max):
        obj = super(IntEnum, cls).__new__(cls, int_value)
        obj._value_ = int_value
        obj._range_min = range_min
        obj._range_max = range_max
        return obj

    @property
    def range_min(self):
        return self._range_min

    @property
    def range_max(self):
        return self._range_max


class ULRange(ULRangeEnum):
    NOTUSED = (-2, 0., 0.)
    UNKNOWN = (-1, 0., 0.)
    BIP60VOLTS = (20, -60., 60.)  # -60 to 60 Volts
    BIP30VOLTS = (23, -30., 30.)  # -30 to +30 Volts
    BIP20VOLTS = (15, -20., 20.)  # -20 to +20 Volts
    BIP15VOLTS = (21, -15., 15.)  # -15 to +15 Volts
    BIP10VOLTS = (1, -10., 10.)  # -10 to +10 Volts
    BIP5VOLTS = (0, -5., 5.)  # -5 to +5 Volts
    BIP4VOLTS = (16, -4., 4.)  # -4 to + 4 Volts
    BIP2PT5VOLTS = (2, -2.5, 2.5)  # -2.5 to +2.5 Volts
    BIP2VOLTS = (14, -2., 2.)  # -2.0 to +2.0 Volts
    BIP1PT25VOLTS = (3, -1.25, 1.25)  # -1.25 to +1.25 Volts
    BIP1VOLTS = (4, -1., 1.)  # -1 to +1 Volts
    BIPPT625VOLTS = (5, -.625, .625)  # -.625 to +.625 Volts
    BIPPT5VOLTS = (6, -.5, .5)  # -.5 to +.5 Volts
    BIPPT25VOLTS = (12, -.25, .25)  # -0.25 to +0.25 Volts
    BIPPT2VOLTS = (13, -.2, .2)  # -0.2 to +0.2 Volts
    BIPPT1VOLTS = (7, -.1, .1)  # -.1 to +.1 Volts
    BIPPT05VOLTS = (8, -.05, .05)  # -.05 to +.05 Volts
    BIPPT01VOLTS = (9, -.01, .01)  # -.01 to +.01 Volts
    BIPPT005VOLTS = (10, -.005, .005)  # -.005 to +.005 Volts
    BIP1PT67VOLTS = (11, -1.67, 1.67)  # -1.67 to +1.67 Volts
    BIPPT312VOLTS = (17, -.312, .312)  # -0.312 to +0.312 Volts
    BIPPT156VOLTS = (18, -.156, .156)  # -0.156 to +0.156 Volts
    BIPPT125VOLTS = (22, -.125, .125)  # -0.125 to +0.125 Volts
    BIPPT078VOLTS = (19, -.078, .078)  # -0.078 to +0.078 Volts
    UNI10VOLTS = (100, 0, 10.)  # 0 to 10 Volts
    UNI5VOLTS = (101, 0, 5.)  # 0 to 5 Volts
    UNI4VOLTS = (114, 0, 4.)  # 0 to 4 Volts
    UNI2PT5VOLTS = (102, 0, 2.5)  # 0 to 2.5 Volts
    UNI2VOLTS = (103, 0, 2.)  # 0 to 2 Volts
    UNI1PT67VOLTS = (109, 0, 1.67)  # 0 to 1.67 Volts
    UNI1PT25VOLTS = (104, 0, 1.25)  # 0 to 1.25 Volts
    UNI1VOLTS = (105, 0, 1.)  # 0 to 1 Volts
    UNIPT5VOLTS = (110, 0, .5)  # 0 to .5 Volts
    UNIPT25VOLTS = (111, 0, .25)  # 0 to 0.25 Volts
    UNIPT2VOLTS = (112, 0, .2)  # 0 to .2 Volts
    UNIPT1VOLTS = (106, 0, .1)  # 0 to .1 Volts
    UNIPT05VOLTS = (113, 0, .05)  # 0 to .05 Volts
    UNIPT02VOLTS = (108, 0, .02)  # 0 to .02 Volts
    UNIPT01VOLTS = (107, 0, .01)  # 0 to .01 Volts
    MA4TO20 = (200, 4., 20.)  # 4 to 20 ma
    MA2TO10 = (201, 2., 10.)  # 2 to 10 ma
    MA1TO5 = (202, 1., 5.)  # 1 to 5 ma
    MAPT5TO2PT5 = (203, .5, 2.5)  # .5 to 2.5 ma
    MA0TO20 = (204, 0., 20.)  # 0 to 20 ma
    BIPPT025AMPS = (205, -25., 25.)  # -0.025 A to 0.025 A = -25 to 25 ma
    BIPPT025VOLTSPERVOLT = (400, -.025, .025)  # -0.025 to +0.025 V/V


class CounterRegister(IntEnum):
    LOADREG0 = 0
    LOADREG1 = 1
    LOADREG2 = 2
    LOADREG3 = 3
    LOADREG4 = 4
    LOADREG5 = 5
    LOADREG6 = 6
    LOADREG7 = 7
    LOADREG8 = 8
    LOADREG9 = 9
    LOADREG10 = 10
    LOADREG11 = 11
    LOADREG12 = 12
    LOADREG13 = 13
    LOADREG14 = 14
    LOADREG15 = 15
    LOADREG16 = 16
    LOADREG17 = 17
    LOADREG18 = 18
    LOADREG19 = 19
    LOADREG20 = 20

    HOLDREG1 = 101
    HOLDREG2 = 102
    HOLDREG3 = 103
    HOLDREG4 = 104
    HOLDREG5 = 105
    HOLDREG6 = 106
    HOLDREG7 = 107
    HOLDREG8 = 108
    HOLDREG9 = 109
    HOLDREG10 = 110
    HOLDREG11 = 111
    HOLDREG12 = 112
    HOLDREG13 = 113
    HOLDREG14 = 114
    HOLDREG15 = 115
    HOLDREG16 = 116
    HOLDREG17 = 117
    HOLDREG18 = 118
    HOLDREG19 = 119
    HOLDREG20 = 120

    ALARM1CHIP1 = 201
    ALARM2CHIP1 = 202
    ALARM1CHIP2 = 301
    ALARM2CHIP2 = 302
    ALARM1CHIP3 = 401
    ALARM2CHIP3 = 402
    ALARM1CHIP4 = 501
    ALARM2CHIP4 = 502

    COUNT1 = 601
    COUNT2 = 602
    COUNT3 = 603
    COUNT4 = 604

    PRESET1 = 701
    PRESET2 = 702
    PRESET3 = 703
    PRESET4 = 704

    PRESCALER1 = 801
    PRESCALER2 = 802
    PRESCALER3 = 803
    PRESCALER4 = 804

    MINLIMITREG0 = 900
    MINLIMITREG1 = 901
    MINLIMITREG2 = 902
    MINLIMITREG3 = 903
    MINLIMITREG4 = 904
    MINLIMITREG5 = 905
    MINLIMITREG6 = 906
    MINLIMITREG7 = 907

    MAXLIMITREG0 = 1000
    MAXLIMITREG1 = 1001
    MAXLIMITREG2 = 1002
    MAXLIMITREG3 = 1003
    MAXLIMITREG4 = 1004
    MAXLIMITREG5 = 1005
    MAXLIMITREG6 = 1006
    MAXLIMITREG7 = 1007

    OUTPUTVAL0REG0 = 1100
    OUTPUTVAL0REG1 = 1101
    OUTPUTVAL0REG2 = 1102
    OUTPUTVAL0REG3 = 1103
    OUTPUTVAL0REG4 = 1104
    OUTPUTVAL0REG5 = 1105
    OUTPUTVAL0REG6 = 1106
    OUTPUTVAL0REG7 = 1107

    OUTPUTVAL1REG0 = 1200
    OUTPUTVAL1REG1 = 1201
    OUTPUTVAL1REG2 = 1202
    OUTPUTVAL1REG3 = 1203
    OUTPUTVAL1REG4 = 1204
    OUTPUTVAL1REG5 = 1205
    OUTPUTVAL1REG6 = 1206
    OUTPUTVAL1REG7 = 1207


class CounterMode(IntFlag):
    COUNTER = 0x0100
    TOTALIZE = 0x0000
    CLEAR_ON_READ = 0x0001
    ROLLOVER = 0x0000
    STOP_AT_MAX = 0x0002
    DECREMENT_OFF = 0x0000
    DECREMENT_ON = 0x0020
    BIT_16 = 0x0000
    BIT_32 = 0x0004
    BIT_48 = 0x10000
    GATING_OFF = 0x0000
    GATING_ON = 0x0010
    LATCH_ON_SOS = 0x0000
    LATCH_ON_MAP = 0x0008
    UPDOWN_OFF = 0x0000
    UPDOWN_ON = 0x1000
    RANGE_LIMIT_OFF = 0x0000
    RANGE_LIMIT_ON = 0x2000
    NO_RECYCLE_OFF = 0x0000
    NO_RECYCLE_ON = 0x4000
    MODULO_N_OFF = 0x0000
    MODULO_N_ON = 0x8000

    # USB-CTRX additional modes
    COUNT_DOWN_OFF = 0x00000
    COUNT_DOWN_ON = 0x10000
    INVERT_GATE = 0x20000
    GATE_CONTROLS_DIR = 0x40000
    GATE_CLEARS_CTR = 0x80000
    GATE_TRIG_SRC = 0x100000
    OUTPUT_ON = 0x200000
    OUTPUT_INITIAL_STATE_LOW = 0x000000
    OUTPUT_INITIAL_STATE_HIGH = 0x400000

    PERIOD = 0x0200
    PERIOD_MODE_X1 = 0x0000
    PERIOD_MODE_X10 = 0x0001
    PERIOD_MODE_X100 = 0x0002
    PERIOD_MODE_X1000 = 0x0003
    PERIOD_MODE_BIT_32 = 0x0004
    PERIOD_MODE_BIT_48 = 0x10000
    PERIOD_MODE_GATING_ON = 0x0010
    PERIOD_MODE_INVERT_GATE = 0x20000

    PULSEWIDTH = 0x0300
    PULSEWIDTH_MODE_BIT_32 = 0x0004
    PULSEWIDTH_MODE_BIT_48 = 0x10000
    PULSEWIDTH_MODE_GATING_ON = 0x0010
    PULSEWIDTH_MODE_INVERT_GATE = 0x20000

    TIMING = 0x0400
    TIMING_MODE_BIT_32 = 0x0004
    TIMING_MODE_BIT_48 = 0x10000
    TIMING_MODE_INVERT_GATE = 0x20000

    ENCODER = 0x0500
    ENCODER_MODE_X1 = 0x0000
    ENCODER_MODE_X2 = 0x0001
    ENCODER_MODE_X4 = 0x0002
    ENCODER_MODE_LATCH_ON_Z = 0x0008
    ENCODER_MODE_CLEAR_ON_Z_OFF = 0x0000
    ENCODER_MODE_CLEAR_ON_Z_ON = 0x0020
    ENCODER_MODE_RANGE_LIMIT_OFF = 0x0000
    ENCODER_MODE_RANGE_LIMIT_ON = 0x2000
    ENCODER_MODE_NO_RECYCLE_OFF = 0x0000
    ENCODER_MODE_NO_RECYCLE_ON = 0x4000
    ENCODER_MODE_MODULO_N_OFF = 0x0000
    ENCODER_MODE_MODULO_N_ON = 0x8000
    ENCODER_MODE_BIT_32 = 0x0004
    ENCODER_MODE_BIT_48 = 0x10000


class CounterDebounceTime(IntEnum):
    DEBOUNCE500ns = 0
    DEBOUNCE1500ns = 1
    DEBOUNCE3500ns = 2
    DEBOUNCE7500ns = 3
    DEBOUNCE15500ns = 4
    DEBOUNCE31500ns = 5
    DEBOUNCE63500ns = 6
    DEBOUNCE127500ns = 7
    DEBOUNCE100us = 8
    DEBOUNCE300us = 9
    DEBOUNCE700us = 10
    DEBOUNCE1500us = 11
    DEBOUNCE3100us = 12
    DEBOUNCE6300us = 13
    DEBOUNCE12700us = 14
    DEBOUNCE25500us = 15
    DEBOUNCE_NONE = 16


class CounterDebounceMode(IntEnum):
    TRIGGER_AFTER_STABLE = 0
    TRIGGER_BEFORE_STABLE = 1


class CounterEdgeDetection(IntEnum):
    RISING_EDGE = 0
    FALLING_EDGE = 1


class CounterTickSize(IntEnum):
    TICK20PT83ns = 0
    TICK208PT3ns = 1
    TICK2083PT3ns = 2
    TICK20833PT3ns = 3


class TrigType(IntEnum):
    TRIG_ABOVE = 0
    TRIG_BELOW = 1
    GATE_NEG_HYS = 2
    GATE_POS_HYS = 3
    GATE_ABOVE = 4
    GATE_BELOW = 5
    GATE_IN_WINDOW = 6
    GATE_OUT_WINDOW = 7
    GATE_HIGH = 8
    GATE_LOW = 9
    TRIG_HIGH = 10
    TRIG_LOW = 11
    TRIG_POS_EDGE = 12
    TRIG_NEG_EDGE = 13
    TRIG_RISING = 14
    TRIG_FALLING = 15
    TRIG_PATTERN_EQ = 16
    TRIG_PATTERN_NE = 17
    TRIG_PATTERN_ABOVE = 18
    TRIG_PATTERN_BELOW = 19


class ExtPacerEdge(IntEnum):
    RISING = 1
    FALLING = 2


class TimerIdleState(IntEnum):
    LOW = 0
    HIGH = 1


class Iterator(IntEnum):
    GET_FIRST = -2
    GET_NEXT = -3


class InfoType(IntEnum):
    GLOBALINFO = 1
    BOARDINFO = 2
    DIGITALINFO = 3
    COUNTERINFO = 4
    EXPANSIONINFO = 5
    EXPINFOARRAY = 7


class GlobalInfo(IntEnum):
    VERSION = 36  # Config file format version number
    NUMBOARDS = 38  # Maximum number of boards
    NUMEXPBOARDS = 40  # Maximum number of expansion boards
    TRACEFLAGS = 42  # Internal logging flags
    INIT = 44


class BoardInfo(IntEnum):
    BASEADR = 0  # Base Address
    BOARDTYPE = 1  # Board Type (0x101 - 0x7FFF)
    INTLEVEL = 2  # Interrupt level
    DMACHAN = 3  # DMA channel
    INITIALIZED = 4  # TRUE or FALSE
    CLOCK = 5  # Clock freq (1, 10 or bus)
    RANGE = 6  # Switch selectable range
    NUMADCHANS = 7  # Number of A/D channels
    USESEXPS = 8  # Supports expansion boards TRUE/FALSE
    DINUMDEVS = 9  # Number of digital devices
    DIDEVNUM = 10  # Index into digital information
    CINUMDEVS = 11  # Number of counter devices
    CIDEVNUM = 12  # Index into counter information
    NUMDACHANS = 13  # Number of D/A channels
    WAITSTATE = 14  # Wait state enabled TRUE/FALSE
    NUMIOPORTS = 15  # I/O address space used by board
    PARENTBOARD = 16  # Board number of parent board
    DTBOARD = 17  # Board number of connected DT board
    NUMEXPS = 18  # Number of EXP boards installed

    # NEW CONFIG ITEMS for 32 bit library
    NOITEM = 99  # NO-OP return no data and returns DEVELOPMENT_OPTION error code
    DACSAMPLEHOLD = 100  # DAC sample and hold jumper state
    DIOENABLE = 101  # DIO enable
    CTR0SRC = 104  # CTR 0 source
    CTR1SRC = 105  # CTR 1 source
    CTR2SRC = 106  # CTR 2 source
    PACERCTR0SRC = 107  # cer CTR 0 source
    DAC0VREF = 108  # DAC 0 voltage reference
    DAC1VREF = 109  # DAC 1 voltage reference
    INTP2LEVEL = 110  # P2 interrupt for CTR10 and CTR20HD
    WAITSTATEP2 = 111  # Wait state 2
    ADPOLARITY = 112  # DAS1600 Polarity state(UNI/BI)
    TRIGEDGE = 113  # DAS1600 trigger edge(RISING/FALLING)
    DACRANGE = 114  # DAC Range (DevNo is channel)
    DACUPDATE = 115  # DAC Update (INDIVIDUAL/SIMULTANEOUS) (DevNo)
    DACINSTALLED = 116  # DAC Installed
    ADCFG = 117  # AD Config (SE/DIFF) (DevNo)
    ADINPUTMODE = 118  # AD Input Mode (Voltage/Current)
    DACPOLARITY = 119  # DAC Startup state (UNI/BI)
    TEMPMODE = 120  # DAS-TEMP Mode (NORMAL/CALIBRATE)
    TEMPREJFREQ = 121  # DAS-TEMP reject frequency
    DISOFILTER = 122  # DISO48 line filter (EN/DIS) (DevNo)
    INT32SRC = 123  # INT32 Intr Src
    INT32PRIORITY = 124  # INT32 Intr Priority
    MEMSIZE = 125  # MEGA-FIFO module size
    MEMCOUNT = 126  # MEGA-FIFO # of modules
    PRNPORT = 127  # PPIO series printer port
    PRNDELAY = 128  # PPIO series printer port delay
    PPIODIO = 129  # PPIO digital line I/O state
    CTR3SRC = 130  # CTR 3 source
    CTR4SRC = 131  # CTR 4 source
    CTR5SRC = 132  # CTR 5 source
    CTRINTSRC = 133  # PCM-D24/CTR3 interrupt source
    CTRLINKING = 134  # PCM-D24/CTR3 ctr linking
    SBX0BOARDNUM = 135  # SBX #0 board number
    SBX0ADDRESS = 136  # SBX #0 address
    SBX0DMACHAN = 137  # SBX #0 DMA channel
    SBX0INTLEVEL0 = 138  # SBX #0 Int Level 0
    SBX0INTLEVEL1 = 139  # SBX #0 Int Level 1
    SBX1BOARDNUM = 140  # SBX #0 board number
    SBX1ADDRESS = 141  # SBX #0 address
    SBX1DMACHAN = 142  # SBX #0 DMA channel
    SBX1INTLEVEL0 = 143  # SBX #0 Int Level 0
    SBX1INTLEVEL1 = 144  # SBX #0 Int Level 1
    SBXBUSWIDTH = 145  # SBX Bus width
    CALFACTOR1 = 146  # DAS08/Jr Cal factor
    CALFACTOR2 = 147  # DAS08/Jr Cal factor
    DACTRIG = 148  # PCI-DAS1602 Dac trig edge
    CHANCFG = 149  # 801/802 chan config (devno =ch)
    PROTOCOL = 150  # 422 protocol
    COMADDR2 = 151  # dual 422 2nd address
    CTSRTS1 = 152  # dual 422 cts/rts1
    CTSRTS2 = 153  # dual 422 cts/rts2
    CTRLLINES = 154  # pcm com 422 ctrl lines
    WAITSTATEP1 = 155  # Wait state P1
    INTP1LEVEL = 156  # P1 interrupt for CTR10 and CTR20HD
    CTR6SRC = 157  # CTR 6 source
    CTR7SRC = 158  # CTR 7 source
    CTR8SRC = 159  # CTR 8 source
    CTR9SRC = 160  # CTR 9 source
    CTR10SRC = 161  # CTR 10 source
    CTR11SRC = 162  # CTR 11 source
    CTR12SRC = 163  # CTR 12 source
    CTR13SRC = 164  # CTR 13 source
    CTR14SRC = 165  # CTR 14 source
    TCGLOBALAVG = 166  # DASTC global average
    TCCJCSTATE = 167  # DASTC CJC State(=ON or OFF)
    TCCHANRANGE = 168  # DASTC Channel Gain
    TCCHANTYPE = 169  # Deprecated, use CHANTCTYPE /* DASTC Channel thermocouple type */
    FWVERSION = 170  # Firmware Version
    PHACFG = 180  # Quad PhaseA config (devNo =ch)
    PHBCFG = 190  # Quad PhaseB config (devNo =ch)
    INDEXCFG = 200  # Quad Index Ref config (devNo =ch)
    SLOTNUM = 201  # PCI/PCM card slot number
    AIWAVETYPE = 202  # analog input wave type (for demo board)
    PWRUPSTATE = 203  # DDA06 pwr up state jumper
    IRQCONNECT = 204  # DAS08 pin6 to 24 jumper
    TRIGPOLARITY = 205  # PCM DAS16xx Trig Polarity
    CTLRNUM = 206  # MetraBus controller board number
    PWRJMPR = 207  # MetraBus controller board Pwr jumper
    NUMTEMPCHANS = 208  # Number of Temperature channels
    ADTRIGSRC = 209  # A/D trigger source
    BNCSRC = 210  # BNC source
    BNCTHRESHOLD = 211  # BNC Threshold 2.5V or 0.0V
    BURSTMODE = 212  # Board supports BURSTMODE scans
    DITHERON = 213
    SERIALNUM = 214  # User Serial Number for HID boards
    DACUPDATEMODE = 215  # Update immediately or upon AOUPDATE command
    DACUPDATECMD = 216  # Issue D/A UPDATE command
    DACRESTORE = 217  # Restore last value written or reset to ground
    DACSTARTUP = DACRESTORE
    ACCOUPLED = 218  # A/D AC(=1) or DC(=0) coupling
    ADTRIGCOUNT = 219  # Number of samples to acquire per trigger
    ADFIFOSIZE = 220
    ADSOURCE = 221
    CALOUTPUT = 222  # CAL output pin setting
    SRCADPACER = 223  # Source A/D Pacer output
    MFGSERIALNUM = 224  # Manufacturers 8-byte serial number
    PCIREVID = 225  # Revision Number stored in PCI header
    BOARDTEMP = 226  # Internal board temperature. Could be used as CJC.
    EXTCLKTYPE = 227  # Free-running/Continuous or Gated/Synchronized
    RELAYLOGIC = 228  # ActiveLow = 1, ActiveHigh = 0
    OPENRELAYLEVEL = 229  # DefaultLow = 0, DefaultHigh = 1
    DIALARMMASK = 230  # ON_CHANGE_DIG_INPUT alarm event mask
    DEFAULTIP = 231
    CURRENTIP = 232
    DHCPENABLED = 233
    CURRENTPORT = 234
    TEMPSENSORTYPE = 235
    TEMPCONNECTIONTYPE = 236
    TEMPEXCITATION = 237
    TEMPCHANGAIN = 238
    OWNERNAME = 239
    OWNERIP = 240
    TBASERES = 241
    TEMPCALIBRATE = 242
    CURRENTGATEWAYIP = 243
    DEFAULTGATEWAYIP = 244
    CURRENTSUBNET = 245
    DEFAULTSUBNET = 246
    NETIOTIMEOUT = 247
    NETMINPORT = 248
    ADCHANAIMODE = 249
    DACFORCESENSE = 250
    SYNCMODE = 251  # master = 0, slave =1
    ADCPACEROUT = 252  # Enable/Disable A/D Pacer output
    DACPACEROUT = 253
    CALTABLETYPE = 254
    DIDEBOUNCESTATE = 255
    DIDEBOUNCETIME = 256
    BUSNUM = 257
    PANID = 258
    RFCHANNEL = 259
    POWERLEVEL = 260
    RSS = 261
    NODEID = 262
    DEVNOTES = 263
    PROGRAMDEV = 264
    INTEDGE = 265
    RFCHANENERGY = 266
    ADCCALIBRATE = 267
    ADCCALSTEPS = 268
    TEMPCALSTEPS = 269
    ADCSETTLETIME = 270
    WEBSERVERENABLE = 271
    FACTORYID = 272
    HTTPPORT = 273
    HIDELOGINDLG = 274
    ACTUALDAQSCANRATE = 275
    USBQUERY = 276
    DACXFERPRIMECOUNT = 277
    EXTPOWERSTATE = 278
    CHANBWMODE = 279
    TEMPSCALE = 280
    CALDACVREF = 281
    DACCALVOLT = 282
    USERADCSETTLETIME = 283
    DACTRIGCOUNT = 284
    ADTIMINGMODE = 285
    RTDCHANTYPE = 286  # Deprecated use CHANRTDTYPE
    TERMINALCOUNTSTATUSENABLE = 287
    ATRIGCALIBRATE = 288
    ADEXCITATION = 289  # Deprecated use EXCITATION
    ADBRIDGETYPE = 290  # Deprecated use CHANBRIDGETYPE
    ADRES = 291
    DACRES = 292
    CALTIMEOUT = 293
    ADLOADCALCOEFS = 294
    DACLOADCALCOEFS = 295
    CLOCKTIME = 296
    BUTTONSTATE = 297
    INTERFACEPATH = 298
    DACCALIBRATE = 299
    ATRIGRANGE = 300
    LEDPATTERN = 301
    ADCAVGCOUNT = 302  # ADC Averaging sample count
    DEVINST = 303  # retrieves DEVINST values to be used by CM_Device_Id etc...
    DIFILTERTIME = 304
    DISTATERETENTION = 305
    ADXFERMODE = 306
    CTRTRIGCOUNT = 307
    DAQITRIGCOUNT = 308

    HASEXTINFO = 309  # Indicates if devices has extended info
    NUMIODEVS = 310  # Number of IO devices
    IODEVTYPE = 311  # Type of IO device
    ADNUMCHANMODES = 312  # Number of channel modes
    ADCHANMODE = 313  # Channel mode
    ADNUMDIFFRANGES = 314  # Number of differncial ranges supported by devide
    ADDIFFRANGE = 315
    ADNUMSERANGES = 316  # Number of Single-Ended ranges supported by devide
    ADSERANGE = 317
    ADNUMTRIGTYPES = 318
    ADTRIGTYPE = 319
    ADMAXRATE = 320
    ADMAXTHROUGHPUT = 321
    ADMAXBURSTRATE = 322
    ADMAXBURSTTHROUGHPUT = 323
    ADHASPACER = 324
    ADCHANTYPES = 325
    ADSCANOPTIONS = 326
    ADMAXSEQUEUELENGTH = 327
    ADMAXDIFFQUEUELENGTH = 328
    ADQUEUETYPES = 329
    ADQUEUELIMITS = 330

    DACHASPACER = 331
    DACSCANOPTIONS = 332
    DACFIFOSIZE = 333
    DACNUMRANGES = 334  # Number of ranges supported by dac devide
    DACDEVRANGE = 335  # DACRANGE is already defined
    DACNUMTRIGTYPES = 336
    DACTRIGTYPE = 337
    DAQAMISUPPORTED = 338

    DISCONNECT = 340
    NETCONNECTCODE = 341

    CONNECTED = 342

    DITRIGCOUNT = 343  # Number of digital input samples to acquire per trigger
    DOTRIGCOUNT = 344  # Number of digital output samples to generate per trigger
    PATTERNTRIGPORT = 345

    CHANTCTYPE = 347  # Channel thermocouple type
    EXTINPACEREDGE = 348
    EXTOUTPACEREDGE = 349
    INPUTPACEROUT = 350  # Enable/Disable input Pacer output
    OUTPUTPACEROUT = 351  # Enable/Disable output Pacer output
    TEMPAVG = 352
    EXCITATION = 353
    CHANBRIDGETYPE = 354
    ADCHANTYPE = 355
    CHANRTDTYPE = 356
    # Unique identifier of DAQ device. Serial Number (USB devices), MAC
    # address (Ethernet devices)
    DEVUNIQUEID = 357
    USERDEVID = 358
    DEVVERSION = 359
    TERMCOUNTSTATBIT = 360
    DETECTOPENTC = 361
    ADDATARATE = 362
    DEVSERIALNUM = 363
    DEVMACADDR = 364
    USERDEVIDNUM = 365  # User device ID for HID devices
    NETBIOSNAME = 366
    DISCANOPTIONS = 367
    DOSCANOPTIONS = 368
    CTRSCANOPTIONS = 369
    DAQISCANOPTIONS = 370
    DAQOSCANOPTIONS = 371
    DEVCLASS = 372
    ADAIMODE = 373
    DEVIPADDR = 374
    DACDISABLERESTORE = 375

    DAQINUMCHANTYPES = 376
    DAQICHANTYPE = 377
    DAQONUMCHANTYPES = 378
    DAQOCHANTYPE = 379


class DigitalInfo(IntEnum):
    BASEADR = 0  # Base address
    INITIALIZED = 1  # TRUE or FALSE
    DEVTYPE = 2  # AUXPORT or xPORTA - CH
    MASK = 3  # Bit mask for this port
    READWRITE = 4  # Read required before write
    CONFIG = 5  # Current configuration
    NUMBITS = 6  # Number of bits in port
    CURVAL = 7  # Current value of outputs
    INMASK = 8  # Input bit-mask
    OUTMASK = 9  # Output bit mask
    INITPORTVAL = 10  # Initial output value of port upon DConfig
    HASPACER = 11
    PORTIOTYPE = 12
    # Disables checking port/bit direction in d_out and d_bit_out functions
    DISABLEDIRCHECK = 13


class CounterInfo(IntEnum):
    BASEADR = 0  # Base address
    INITIALIZED = 1  # TRUE or FALSE
    CTRTYPE = 2  # Counter type 8254, 9513 or 8536
    CTRNUM = 3  # Counter number
    CONFIGBYTE = 4  # Configuration byte


class ExpansionInfo(IntEnum):
    BOARDTYPE = 0  # Board type
    MUX_AD_CHAN1 = 1  # 0 - 7
    MUX_AD_CHAN2 = 2  # 0 - 7 or NOTUSED
    RANGE1 = 3  # Range (gain) of low 16 chans
    RANGE2 = 4  # Range (gain) of high 16 chans
    CJCCHAN = 5  # TYPE_8254_CTR or TYPE_9513_CTR
    THERMTYPE = 6  # TYPEJ, TYPEK, TYPET, TYPEE, TYPER, or TYPES
    NUMEXPCHANS = 7  # Number of expansion channels on board
    PARENTBOARD = 8  # Board number of parent A/D board
    SPARE0 = 9  # 16 words of misc options

    FIVEVOLTSOURCE = 100  # ICAL DATA - 5 volt source
    CHANCONFIG = 101  # exp Data - chan config 2/4 or 3-wire devNo=chan
    VSOURCE = 102  # ICAL DATA - voltage source
    VSELECT = 103  # ICAL Data - voltage select
    CHGAIN = 104  # exp Data - individual ch gain
    GND = 105  # ICAL DATA - exp grounding
    VADCHAN = 106  # ICAL DATA - Vexe A/D chan
    RESISTANCE = 107  # exp Data - resistance @0 (devNo =ch)
    FACGAIN = 108  # ICAL DATA - RTD factory gain
    CUSTOMGAIN = 109  # ICAL DATA - RTD custom gain
    CHCUSTOM = 110  # ICAL DATA - RTD custom gain setting
    IEXE = 111  # ICAL DATA - RTD Iexe


class AiChanType(IntEnum):
    VOLTAGE = 0  # Voltage mode, ±60 V, ±15 V, ±4 V, ±1 V, ±1.25 mV
    CURRENT = 100  # Current mode, ±25 mA
    RESISTANCE_10K4W = 201  # 4-wire Resistance mode, 10 kΩ
    RESISTANCE_1K4W = 202  # 4-wire Resistance mode, 1 kΩ
    RESISTANCE_10K2W = 203  # 2-wire Resistance mode, 10 kΩ
    RESISTANCE_1K2W = 204  # 2-wire Resistance mode, 1 kΩ
    TC = 300  # Thermocouple mode, ±125 mV
    RTD_1000OHM_4W = 401  # 4-wire RTD mode, 1000 Ω
    RTD_100OHM_4W = 402  # 4-wire RTD mode, 100 Ω
    RTD_1000OHM_3W = 403  # 3-wire RTD mode, 1000 Ω
    RTD_100OHM_3W = 404  # 3-wire RTD mode, 100 Ω
    QUART_BRIDGE_350OHM = 501  # Quarter-bridge mode, 350 Ω
    QUART_BRIDGE_120OHM = 502  # Quarter-bridge mode, 120 Ω
    HALF_BRIDGE = 503  # Half-bridge mode, 500 mV/V
    FULL_BRIDGE_62PT5mVV = 504  # Full-bridge mode, ±62.5 mV/V
    FULL_BRIDGE_7PT8mVV = 505  # Full-bridge mode, ±7.8 mV/V


class TempSensorType(IntEnum):
    RTD = 0x00
    THERMISTOR = 0x01
    THERMOCOUPLE = 0x02
    SEMICONDUCTOR = 0x03
    DISABLED = 0x04
    VOLTAGE = 0x05


class TempSensorConnectionType(IntEnum):
    CONN_2_WIRE = 0x00
    CONN_2_WIRE_2 = 0x01
    CONN_3_WIRE = 0x02
    CONN_4_WIRE = 0x03


class ExcitationLevel(IntEnum):
    NONE = 0x00
    THERMISTOR = 0x01
    RTD = 0x02
    PLUS = 0x03


class TcType(IntEnum):
    J = 0x01
    K = 0x02
    T = 0x03
    E = 0x04
    R = 0x05
    S = 0x06
    B = 0x07
    N = 0x08


class SemiconductorTempSensorType(IntEnum):
    CUSTOM = 0x00
    TMP35 = 0x01
    TMP36 = 0x02
    TMP37 = 0x03


class PlatinumRTDType(IntEnum):
    CUSTOM = 0x00
    PT_3750 = 0x01
    PT_3851 = 0x02
    PT_3911 = 0x03
    PT_3916 = 0x04
    PT_3920 = 0x05
    PT_3928 = 0x06
    PT_3850 = 0x07


class EventType(IntFlag):
    ON_SCAN_ERROR = 0x0001
    ON_EXTERNAL_INTERRUPT = 0x0002
    ON_PRETRIGGER = 0x0004
    ON_DATA_AVAILABLE = 0x0008
    ON_END_OF_AI_SCAN = 0x0010
    ON_END_OF_AO_SCAN = 0x0020
    ON_CHANGE_DI = 0x0040
    # Since we can have only one input scan running at a time created this
    # constant with the same value as ON_END_OF_AI_SCAN
    ON_END_OF_INPUT_SCAN = 0x0010
    # Since we can have only one output scan running at a time created this
    # constant with the same value as ON_END_OF_AO_SCAN
    ON_END_OF_OUTPUT_SCAN = 0x0020
    ALL_AI_EVENT_TYPES = 0x001d
    ALL_AO_EVENT_TYPES = 0x0021
    ALL_EVENT_TYPES = 0xffff


class InterfaceType(IntFlag):
    USB = 1 << 0
    BLUETOOTH = 1 << 1
    ETHERNET = 1 << 2
    ANY = USB | BLUETOOTH | ETHERNET


class CounterChannelType(IntEnum):
    CTR8254 = 1
    CTR9513 = 2
    CTR8536 = 3
    CTR7266 = 4
    CTREVENT = 5
    CTRSCAN = 6
    CTRTMR = 7
    CTRQUAD = 8
    CTRPULSE = 9
