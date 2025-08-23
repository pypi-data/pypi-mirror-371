Installation
============


Python version support
----------------------

NetSSE requires a Python version of 3.12 (or any later version) to be installed in the environment. It is also required to have the `pip` package manager installed. 

If you do not have Python installed, you can download it from the `Python website <https://www.python.org/downloads/>`_.


.. _installation:

Installing NetSSE
-----------------

To use NetSSE, install it in a virtual environment using `pip`:

.. code-block:: console

   (.venv) $ python3 -m pip install netsse

This will also install or update the Python packages that NetSSE is dependent on, when needed.


Dependencies
------------

NetSSE depends on a number of other open-source Python packages, of which all of the necessary are automatically installed when using the ``pip install`` manager. The required package versions are as follows:

.. code-block:: text

   numpy>=2.0.0
   scipy>=1.14.0
   matplotlib>=3.8.4
   geopy>=2.4.1
   cartopy>=0.24.1
   cdsapi>=0.7.5