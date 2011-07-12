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
from .Movement import Movement
from .Node import Node
from .VehicleClassGroup import VehicleClassGroup

class RoadLink(Link):
    """
    A RoadLink in a network.  Both nodes must be RoadNodes.
    
    """
    #: default level value
    DEFAULT_LEVEL = 0
    
    def __init__(self, id, startNode, endNode, reverseAttachedLinkId, facilityType, length,
                 freeflowSpeed, effectiveLengthFactor, responseTimeFactor, numLanes, 
                 roundAbout, level, label):
        """
        Constructor.
        
         * *id* is a unique identifier (unique within the containing network), an integer
         * *startNode*, *endNode* are Nodes
         * *reverseAttachedId* is the id of the reverse link, if attached; pass None if not
           attached
         * *facilityType* is a non-negative integer indicating the category of facility such
           as a freeway, arterial, collector, etc.  A lower number indicates a facility of
           higher priority, that is, higher capacity and speed.
         * *length* is the link length.  Pass None to automatically calculate it.
         * *freeflowSpeed* is in km/h or mi/h
         * *effectiveLengthFactor* is applied to the effective length of a vehicle while it is
           on the link.  May vary over time with LinkEvents
         * *responseTimeFactor* is the applied to the response time of the vehicle while it is
           on the link.  May vary over time with LinkEvents
         * *numLanes* is an integer
         * *roundAbout* is true/false or 1/0
         * *level* is an indicator to attribute vertical alignment/elevation. If None passed, will use default.
         * *label* is a link label. If None passed, will use default. 
         
        """
        Link.__init__(self, id, startNode, endNode, label)
        self._reverseAttachedLinkId     = reverseAttachedLinkId
        self._facilityType              = facilityType
        self._length                    = length
        self._freeflowSpeed             = freeflowSpeed
        self._effectiveLengthFactor     = effectiveLengthFactor
        self._responseTimeFactor        = responseTimeFactor
        self._numLanes                  = numLanes
        self._roundAbout                = roundAbout
        if level:
            self._level                 = level
        else:
            self._level                 = RoadLink.DEFAULT_LEVEL

        self._lanePermissions           = {}  #: lane id -> VehicleClassGroup reference
        self._outgoingMovements         = []  #: list of outgoing Movements
        self._startShift                = None
        self._endShift                  = None
        self._shapePoints               = {}  #: sequenceNum -> (x,y)
    
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
        
    def addShifts(self, startShift, endShift):
        """
         * *startShift*: the shift value of the first segment of the link, that is, the number of lanes from
           the center line of the roadway that the first segment is shifted.
         * *endShift*: End-shift: the shift value of the last segment of the link, that is, the number of 
           lanes from the center line of the roadway that the last segment is shifted.
        """
        self._startShift    = startShift
        self._endShift      = endShift
    
    def getShifts(self):
        """
        Returns the *startShift* and *endShift* ordered pair, or (None,None) if it wasn't set.
        See addShifts() for details.
        """
        return (self._startShift, self._endShift)
    
    def addShapePoint(self, sequenceNum, x, y):
        """
        Adds a shape point to the link for the given sequenceNum
        """
        self._shapePoints[sequenceNum] = (x,y)
    
    def addOutgoingMovement(self, movement):
        """
        Adds the given movement.
        """
        if not isinstance(movement, Movement):
            raise DtaError("RoadLink addOutgoingMovement() called with invalid movement %s" % str(movement))
        
        if movement.getIncomingLink() != self:
            raise DtaError("RoadLink addOutgoingMovement() called with inconsistent movement" % str(movement))
        
        self._outgoingMovements.append(movement)
    
    def iterOutgoingMovements(self):
        """
        Iterator for the outgoing movements of this link
        """
        return iter(self._outgoingMovements)