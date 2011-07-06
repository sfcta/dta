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
from .DtaError import DtaError
from .Link import Link
from .RoadNode import RoadNode
from .VehicleClassGroup import VehicleClassGroup
from .VirtualNode import VirtualNode

class Connector(Link):
    """
    A Connector is a Link that connects a RoadNode with a Centroid or a VirtualNode.
    
    """
    
    def __init__(self, id, nodeA, nodeB, reverseAttachedLinkId, facilityType, length,
                 freeflowSpeed, effectiveLengthFactor, responseTimeFactor, numLanes, 
                 roundAbout, level, label):
        """
        Constructor. Verifies one node is a RoadNode and the other node is either
        a Centroid or a VirtualNode.
        
         * *id* is a unique identifier (unique within the containing network), an integer
         * *nodeA*, *nodeB* are Nodes
         * *label* is a string, or None 
         
        See RoadLink for the rest of the args.  Why do these make sense for centroid connectors?
        Answer: many centroid connectors are based on road links; all of them at the boundaries
        Therefore they have the same set of attributes and those attributes are meaningful.
        
        Putting RoadLink attributes heres for now, re-examine this (like should they go into the Link?) 
        """
        
        if isinstance(nodeA, RoadNode):
            self._fromRoadNode = True
        elif isinstance(nodeB, RoadNode):
            self._fromRoadNode = False
        else:
            raise DtaError("Attempting to initialize a Connector without a RoadNode: %s - %s" % 
                           (str(nodeA), str(nodeB)))

        if (not isinstance(nodeA, Centroid) and not isinstance(nodeA, VirtualNode) and
            not isinstance(nodeB, Centroid) and not isinstance(nodeB, VirtualNode)):
            raise DtaError("Attempting to initialize a Connector without a Centroid/VirtualNode: %s - %s" % 
                           (str(nodeA), str(nodeB)))
       
        Link.__init__(self, id, nodeA, nodeB, label)
        self._reverseAttachedLinkId     = reverseAttachedLinkId
        self._facilityType              = facilityType
        self._length                    = length
        self._freeflowSpeed             = freeflowSpeed
        self._effectiveLengthFactor     = effectiveLengthFactor
        self._responseTimeFactor        = responseTimeFactor
        self._numLanes                  = numLanes
        self._roundAbout                = roundAbout
        self._level                     = level

        self._lanePermissions           = {}  #: lane id -> VehicleClassGroup reference

    def addLanePermission(self, laneId, vehicleClassGroup):
        """
        Adds the lane permissions for the lane numbered by *laneId* (outside lane is lane 0, increases towards inside edge.)
        """
        if not isinstance(vehicleClassGroup, VehicleClassGroup):
            raise DtaError("RoadLink addLanePermission() called with invalid vehicleClassGroup %s" % str(vehicleClassGroup))
        
        if laneId < 0 or laneId >= self._numLanes:
            raise DtaError("RoadLink addLanePermission() called with invalid laneId %d; numLanes = %d" % 
                           (laneId, self._numLanes))
        
        self._lanePermissions[laneId] = vehicleClassGroup