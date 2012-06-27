.. Documentation master file, created by
   sphinx-quickstart on Mon Nov 01 16:54:32 2010.
   
   Updated by lmz 2011-May-23.  This file, along with make.bat and conf.py
   are the only non-generated files in doc/.  
   
   Run "make html" to generate
   the _generated/*.rst files and _build/* 
  
Overview
========
.. automodule:: dta
   :no-members:
   :no-undoc-members:
   :no-inherited-members:
   :no-show-inheritance:

Installation
============
Required python modules:
 * `numpy <http://numpy.scipy.org/>`_ Efficient multi-dimensional container of generic data.  Used for Demand data.
 * `la <http://pypi.python.org/pypi/la>`_ Labeled numpy arrays.  Used for Demand data.
 * `Bottleneck <http://pypi.python.org/pypi/Bottleneck>`_ Fast NumPy array functions. Required by la.  Note: It might be easier to install a pre-compiled version of this, as directed on the documentation page.
 * `pyshp <http://code.google.com/p/pyshp/>`_ Python Shapefile Library for interpretting shapefiles for road geometry and for exporting shapefiles.
 * `pyparsing <http://pyparsing.wikispaces.com/>`_  Enables parsing using simple grammars.  Used for parsing TPPlus transit line files.

Optional python modules:
 * `sphinx <http://sphinx.pocoo.org>`_ Python documentation generator.
 * `nose <http://pypi.python.org/pypi/nose>`_ For unit tests.

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
   
Transit classes
=================
.. autosummary::
   :nosignatures:
   :toctree: _generated
   
   dta.TPPlusTransitNode
   dta.TPPlusTransitRoute
   dta.TransitLine
   dta.TransitSegment

Movement and Path classes
=========================
.. autosummary::
   :nosignatures:
   :toctree: _generated

   dta.Movement
   dta.Path
   dta.ShortestPaths
   
Misc
================
.. autosummary::
   :nosignatures:
   :toctree: _generated

   dta.Demand
   dta.DtaError
   dta.DtaLogger
   dta.MultiArray
   dta.Time
   dta.Utils

Scripts
=======
.. toctree::
   :maxdepth: 1
   
   script_createSFNetworkFromCubeNetwork
   script_importTPPlusTransitRoutes
   script_importExcelSignals
   script_importUnsignalizedIntersections
   script_importCubeDemand
   script_attachCountsFromCountDracula

TODOs
=====

.. toctree::

   todos
         
Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
