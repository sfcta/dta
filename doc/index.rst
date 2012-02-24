.. Documentation master file, created by
   sphinx-quickstart on Mon Nov 01 16:54:32 2010.
   
   Updated by lmz 2011-May-23.  This file, along with make.bat and conf.py
   are the only non-generated files in doc/.  
   
   Run "make html" to generate
   the _generated/*.rst files and _build/* 
  
Installation
============
Required python modules:
 * `numpy <http://numpy.scipy.org/>`_ Efficient multi-dimensional container of generic data.  Used for Demand data.
 * `la <http://pypi.python.org/pypi/la>`_ Labeled numpy arrays.  Used for Demand data.
 * `Bottleneck <http://pypi.python.org/pypi/Bottleneck>`_ Fast NumPy array functions. Required by la.  Note: It might be easier to install a pre-compiled version of this, as directed on the documentation page.
 * `pyshp <http://code.google.com/p/pyshp/>`_ Python Shapefile Library for interpretting shapefiles for road geometry and for exporting shapefiles.

Optional python modules:
 * `sphinx <http://sphinx.pocoo.org>`_ Python documentation generator.
 * `nose <http://pypi.python.org/pypi/nose>`_ For unit tests.

Overview
========
.. automodule:: dta
   :no-members:
   :no-undoc-members:
   :no-inherited-members:
   :no-show-inheritance:

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
   
Signal classes
=================
.. autosummary::
   :nosignatures:
   :toctree: _generated
   
   dta.TimePlan
   dta.PlanCollectionInfo
   dta.Phase
   dta.PhaseMovement
   
Misc
================
.. autosummary::
   :nosignatures:
   :toctree: _generated
   
   dta.DtaError
   dta.DtaLogger
   dta.Movement
   dta.Network
   dta.Route
   dta.Algorithms
   dta.Demand
   dta.Utils
   
   
Example: Building a network using dta
==========================================
.. literalinclude:: ..\scripts\createSFNetworkFromCubeNetwork.py
   :linenos:

TODO List
=========
.. todolist::
         
Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
