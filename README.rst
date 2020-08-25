===========  ===================================================================================================================================
Info         Contains a Python API for interacting with Measurement Computing's Universal Library in Windows. See GitHub_ for the latest source.
Author       Measurement Computing
===========  ===================================================================================================================================

About
=====

The **mcculw** package contains an API (Application Programming Interface) for interacting with the
I/O Library for Measurement Computing Data Acquisition products, Universal Library. This package
was created and is supported by MCC. The package is implemented in Python as a wrapper around the
Universal Library C API using the ctypes_ Python Library.

    Note: The **mcculw** examples included in version 1.0.0 and later are not backward compatible with pre-release
    versions of the **mcculw** Python package.  See the `Examples`_ section for more details.

**mcculw** is supported for Universal Library 6.55 and later. Some functions in the **mcculw**
package may be unavailable with earlier versions of Universal Library. Visit
http://www.mccdaq.com/Software-Downloads.aspx to upgrade your version of UL.

**mcculw** supports only the Windows operating system.

**mcculw** supports CPython 2.7 and 3.4+.

The **mcculw** package is available on GitHub_ and PyPI_.

Installation
============
1. Install Python version 2.7, 3.4, or later from https://www.python.org/downloads/ .
2. Install the latest version of InstaCal from http://www.mccdaq.com/Software-Downloads.aspx .
3. Install the the MCC UL Python API for Windows (mcculw) and any dependencies using pip:

   a. Open the Windows command prompt: press Win+R, type cmd.exe and press Enter.
   b. Upgrade pip to the latest version by entering the following command::

        pip install --upgrade pip

   c. Install the mcculw library by entering the following command::

        pip install mcculw

   Note: If you get a message like "pip is not recognized as an internal or external command...", or
   if you have multiple Python installations, enter the full path to the pip executable, such as
   *C:\\Python27\\Scripts\\pip install --upgrade pip* or *C:\\Python27\\Scripts\\pip install mcculw*.
   The pip command is in the Scripts subdirectory of your Python install location.

Examples
========
Download the `examples zip file`_ from the **mcculw** GitHub repository.

Unzip the examples to a known location, such as::

  C:\Users\Public\Documents\Measurement Computing\DAQ\Python

Refer to the knowledgebase article `Importing Python for Windows example programs into an IDE`_
for detailed instructions on how to import examples into popular IDEs such as Eclipse and Visual
Studio.

    Note: The latest examples take advantage of the **mcculw.device_info** subpackage
    added in version 1.0.0. Software developed using the props subpackage included in
    the examples folder of pre-release versions will continue to work with version 1.0.0
    and later of the **mcculw** Python package, but requires the inclusion of the props subdirectory.
    See the mcculw GitHub `Releases`_ page for a complete archive of previous releases.

Usage
=====
The following is a basic example of using the Universal Library to perform analog input. Further
examples may be found on `GitHub`_.

.. code-block:: python

  from mcculw import ul
  from mcculw.enums import ULRange
  from mcculw.ul import ULError

  board_num = 0
  channel = 0
  ai_range = ULRange.BIP5VOLTS

  try:
      # Get a value from the device
      value = ul.a_in(board_num, channel, ai_range)
      # Convert the raw value to engineering units
      eng_units_value = ul.to_eng_units(board_num, ai_range, value)

      # Display the raw value
      print("Raw Value: " + str(value))
      # Display the engineering value
      print("Engineering Value: " + '{:.3f}'.format(eng_units_value))
  except ULError as e:
      # Display the error
      print("A UL error occurred. Code: " + str(e.errorcode)
            + " Message: " + e.message)

Support/Feedback
================
The **mcculw** package is supported by MCC. For support for **mcculw**, contact technical support
through http://www.mccdaq.com/Support.aspx . Please include version information for Python,
Universal Library and the **mcculw** packages used as well as detailed steps on how to reproduce the
problem in your request.

Bugs/Feature Requests
=====================
To report a bug or submit a feature request, please use the **mcculw** `GitHub Issues`_ page.

Documentation
=============
Documentation is available in the `Universal Library Help`_.


.. Links:
.. _GitHub: https://github.com/mccdaq/mcculw
.. _PyPI: https://pypi.python.org/pypi/mcculw
.. _ctypes: https://docs.python.org/3/library/ctypes.html
.. _`Universal Library Help`: https://www.mccdaq.com/PDFs/Manuals/Mcculw_WebHelp/ULStart.htm
.. _`GitHub Issues`: https://github.com/mccdaq/mcculw/issues
.. _`examples zip file`: https://github.com/mccdaq/mcculw/raw/master/examples.zip
.. _`Importing Python for Windows example programs into an IDE`: http://kb.mccdaq.com/KnowledgebaseArticle50716.aspx
.. _`Releases`: https://github.com/mccdaq/mcculw/releases
