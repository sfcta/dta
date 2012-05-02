"""

DTA Anyway is a python module that facilitates network coding, analysis and visualization for
DTA (Dynamic Traffic Assignment).  This is a stub file to illustrate header convention; this
module docstring will be improved during development.

"""

__copyright__   = "Copyright 2011 SFCTA"
__license__     = """
    This file is part of DTA.

    DTA is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    DTA is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with DTA.  If not, see <http://www.gnu.org/licenses/>.
"""

from .Centroid import Centroid
from .Connector import Connector
from .CorridorPlots import CountsVsVolumes
from .CubeNetwork import CubeNetwork
from .Demand import Demand
from .DtaError import DtaError
from .DynameqNetwork import DynameqNetwork
from .DynameqScenario import DynameqScenario
from .Link import Link
from .Logger import DtaLogger, setupLogging
from .Movement import Movement
from .MultiArray import MultiArray
from .Network import Network
from .Node import Node
from .Phase import Phase
from .RoadLink import RoadLink
from .RoadNode import RoadNode
from .Path import Path
from .Scenario import Scenario
from .TimePlan import PlanCollectionInfo, TimePlan
from .TPPlusTransitRoute import TPPlusTransitRoute
from .Utils import crossProduct, direction, lineSegmentsCross, onSegment, Time
from .VehicleClassGroup import VehicleClassGroup
from .VehicleType import VehicleType
from .VirtualLink import VirtualLink
from .VirtualNode import VirtualNode


from .Algorithms import dfs 

__all__ = ['DtaError', 'DtaLogger', 'setupLogging',
           'Network', 'DynameqNetwork', 'CubeNetwork',
           'Scenario', 'DynameqScenario', 'VehicleType', 'VehicleClassGroup',
           'Node', 'RoadNode', 'Centroid', 'VirtualNode',
           'Link', 'RoadLink', 'Connector', 'VirtualLink', 'DynameqDemand',
           'PlanCollectionInfo', 'TimePlan', 'TPPlusTransitRoute', 'Route', 'Phase', 'MultiArray',
           'crossProduct', 'direction', 'lineSegmentsCross', 'onSegment', 'Time', 'CountsVsVolumes'
]
