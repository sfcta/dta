.. Documentation master file, created by
   sphinx-quickstart on Mon Nov 01 16:54:32 2010.
   
   Updated by lmz 2011-May-23.  This file, along with make.bat and conf.py
   are the only non-generated files in doc/.  
   
   Run "make html" to generate
   the _generated/*.rst files and _build/* 
  

Network classes
===============
.. inheritance-diagram:: dta.Network dta.DynameqNetwork dta.CubeNetwork
   :parts: 1
   
.. autosummary::
   :nosignatures:
   :toctree: _generated
   
   dta.Network
   dta.DynameqNetwork
   dta.CubeNetwork
   
Scenario classes
================
.. inheritance-diagram:: dta.Scenario dta.DynameqScenario dta.VehicleType dta.VehicleClassGroup
   :parts: 1
   
.. autosummary::
   :nosignatures:
   :toctree: _generated
   
   dta.Scenario
   dta.DynameqScenario
   dta.VehicleType
   dta.VehicleClassGroup
   
Node classes
================
.. inheritance-diagram:: dta.Node dta.RoadNode dta.VirtualNode dta.Centroid
   :parts: 1
   
.. autosummary::
   :nosignatures:
   :toctree: _generated
   
   dta.Node
   dta.RoadNode
   dta.VirtualNode
   dta.Centroid
   
Link classes
================
.. inheritance-diagram:: dta.Link dta.RoadLink dta.VirtualLink dta.Connector
   :parts: 1
   
.. autosummary::
   :nosignatures:
   :toctree: _generated
   
   dta.Link
   dta.RoadLink
   dta.VirtualLink
   dta.Connector
   
Misc
================
.. autosummary::
   :nosignatures:
   :toctree: _generated
   
   dta.DtaError
   dta.DtaLogger
   dta.Movement

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
