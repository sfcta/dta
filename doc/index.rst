.. Documentation master file, created by
   sphinx-quickstart on Mon Nov 01 16:54:32 2010.
   
   Updated by lmz 2011-May-23.  This file, along with make.bat and conf.py
   are the only non-generated files in doc/.  
   
   Run "make html" to generate
   the _generated/*.rst files and _build/* 
   
dta classes
================
   
.. autosummary::
   :nosignatures:
   :toctree: _generated
   
   dta.Network
   dta.Node
   dta.RoadNode

Example: Building a network using dta
==========================================
.. literalinclude:: ..\scripts\createSFNetworkFromCubeNetwork.py
   :linenos:
   
.. comment! .. automodule:: Wrangler
   :members:
   :undoc-members:
   
         
Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
