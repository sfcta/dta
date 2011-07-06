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

from .DtaError import DtaError
from .Link import Link
from .Node import Node
from .VehicleClassGroup import VehicleClassGroup

class RoadLink(Link):
    """
    A RoadLink in a network.  Both nodes must be RoadNodes.
    
    """
    
    def __init__(self, id, nodeA, nodeB, reverseAttachedLinkId, facilityType, length,
                 freeflowSpeed, effectiveLengthFactor, responseTimeFactor, numLanes, 
                 roundAbout, level, label):
        """
        Constructor.
        
         * *id* is a unique identifier (unique within the containing network), an integer
         * *nodeA*, *nodeB* are Nodes
         * *reverseAttachedId* is the id of the reverse link, if attached; pass None if not
           attached
         * *facilityType* is a non-negative integer indicating the category of facility such
           as a freeway, arterial, collector, etc.  A lower number indicates a facility of
           higher priority, that is, higher capacity and speed.
         * *length* is the link length
         * *freeflowSpeed* is in km/h or mi/h
         * *effectiveLengthFactor* is applied to the effective length of a vehicle while it is
           on the link.  May vary over time with LinkEvents
         * *responseTimeFactor* is the applied to the response time of the vehicle while it is
           on the link.  May vary over time with LinkEvents
         * *numLanes* is an integer
         * *roundAbout* is true/false or 1/0
         * *level* is an indicator to attribute vertical alignment/elevation
         * *label* is a link label
         
        """
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