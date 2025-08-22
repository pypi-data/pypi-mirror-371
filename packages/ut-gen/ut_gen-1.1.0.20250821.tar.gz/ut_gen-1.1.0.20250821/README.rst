######
ut_gen
######

Overview
********

.. start short_desc

**General 'Utilities'**

.. end short_desc

Installation
************

.. start installation

The package ``ut_gen`` can be installed from PyPI.

To install with ``pip``:

.. code-block:: shell

	$ python -m pip install ut_gen

.. end installation

This requires that the ``readme`` extra is installed:

.. code-block:: shell

	$ python -m pip install ut_gen[readme]

Modules
*******

The Modules of Package ``ut_gen`` could be classified into the following module classes:

#. *System modules*
#. *Base modules*
#. *Command modules*

System modules
^^^^^^^^^^^^^^

  .. system-modules-label:
  .. table:: *System modules*

   +--------------------------------------------------------------------------+
   |Module                                                                    |
   +--------+----------------+------------------------------------------------+
   |Name    |Type            |Classes                                         |
   +========+================+================================================+
   |evt     |Event           |Event Handling Class: EvtHandle                 |
   |        |Handling        |                                                |
   +--------+----------------+------------------------------------------------+
   |exc     |Exception       |Exception Classes as child class of Exception:  |
   |        |Handling        |ArgumentError, ExcNo, ExcStop                   |
   |        |                |Exception Handling Classes: Exc,                |
   +--------+----------------+------------------------------------------------+
   |file    |File I/O        |File I/O Class: File                            |
   +--------+----------------+------------------------------------------------+
   |msg     |Message Handling|Message Handling Classes: Level, Msg, MsgFmt    |
   +--------+----------------+------------------------------------------------+
   |path    |Path Management |Path Management Class: Path                     |
   +--------+----------------+------------------------------------------------+

Base modules
^^^^^^^^^^^^

  .. Base-modules-label:
  .. table:: *Base modules*

   +--------+----------------+------------------------------------------------+
   |Module  |Type            |Classes                                         |
   +========+================+================================================+
   |col     |Color Handling  |Color Handling Class: Col                       |
   +--------+----------------+------------------------------------------------+
   |fnc     |Function        |Function Class: Fnc                             |
   |        |Utilities       |                                                |
   +--------+----------------+------------------------------------------------+
   |range   |Range Utilities |Range Utility Class: Range                      |
   +--------+----------------+------------------------------------------------+
   |ver     |Verificationn   |Verification Class: Ver                         |
   |        |Utilities       |                                                |
   +--------+----------------+------------------------------------------------+
   |utg     |other general   |General Utility Classes: GermanUmlaute, Int,    |
   |        |Utilities       |Date, Date_Range, Date_Range_Arr, Num, Mge,     |
   |        |                |Soup, d_Uri, Uri, Eq, D_Eq                      |
   +--------+----------------+------------------------------------------------+

Command modules
^^^^^^^^^^^^^^^

  .. Command-modules-label:
  .. table:: *Command modules*

   +--------+----------------+------------------------------------------------+
   |Module  |Type            |Description                                     |
   +========+================+================================================+
   |cmd     |Command         |Modul with classes ronous or syncronous         |
   |        |Utilities       |execution of commands                           |
   +--------+----------------+------------------------------------------------+
   |cmdline |Commandline     |Command Line Utility Class: Cmdline             |
   |        |Utilities       |                                                |
   +--------+----------------+------------------------------------------------+

Appendix
********

.. contents:: **Table of Content**
