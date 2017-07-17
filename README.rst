======  ===========================================================================================
Info    Contains a Python API for interacting with Measurement Computing's Universal Library. See
        `GitHub <https://github.com/mccdaq/mcculw>`_ for the latest source.
Author  Measurement Computing
======  ===========================================================================================

About
=====
The **mcculw** package contains an API (Application Programming Interface) for interacting with the
I/O Library for Measurement Computing Data Acquisition products, Universal Library. This package
was created and is supported by MCC. The package is implemented in Python as a wrapper around the
Universal Library C API using the `ctypes <https://docs.python.org/3/library/ctypes.html>`_ Python
Library. 

**mcculw** is supported for Universal Library 6.55 and later. Some functions in the **mcculw**
package may be unavailable with earlier versions of Universal Library. Visit
`http://www.mccdaq.com/Software-Downloads.aspx <http://www.mccdaq.com/Software-Downloads.aspx>`_ to
upgrade your version of UL. 

**mcculw** supports only the Windows operating system.

**mcculw** supports CPython 2.7 and 3.4+.

The **mcculw** package is available on `GitHub <https://github.com/mccdaq/mcculw>`_ and
`PyPI <https://pypi.python.org/pypi/mcculw>`_.

Installation
============
Running **mcculw** requires InstaCal. Visit
`http://www.mccdaq.com/Software-Downloads.aspx <http://www.mccdaq.com/Software-Downloads.aspx>`_ to
download the latest version of InstaCal.

**mcculw** can be installed with pip::

  $ pip install mcculw
    
Examples
========
Download the examples from the **mcculw**
`GitHub Repository <https://github.com/mccdaq/mcculw/raw/master/examples.zip>`_.


Unzip the examples to a known location, such as::

  C:\Users\Public\Documents\Measurement Computing\DAQ\Python


Refer to the
`Universal Library Help <https://www.mccdaq.com/PDFs/Manuals/Mcculw_WebHelp/ULStart.htm>`_ for
detailed instructions on how to import examples into the Eclipse IDE or Visual Studio. 

Usage
=====
The following is a basic example of using the Universal Library to perform analog input. Further
examples may be found on `GitHub <https://github.com/mccdaq/mcculw>`_.

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
through `mccdaq.com/Support.aspx <http://www.mccdaq.com/Support.aspx>`_. Please include version
information for Python, Universal Library and the **mcculw** packages used as well as detailed
steps on how to reproduce the problem in your request.

Bugs/Feature Requests
=====================
To report a bug or submit a feature request, please use the **mcculw**
`GitHub issues <https://github.com/mccdaq/mcculw/issues>`_ page.

Documentation
=============
Documentation is available in the
`Universal Library Help <https://www.mccdaq.com/PDFs/Manuals/Mcculw_WebHelp/ULStart.htm>`_.

License
=======
mcculw is licensed under an MIT-style license. Other incorporated projects may be licensed under 
different licenses. All licenses allow for non-commercial and commercial use.