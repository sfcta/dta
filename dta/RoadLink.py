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
    DEFAULT_LANE_WIDTH_FEET = 12
    
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

        self._label                     = label
        self._lanePermissions           = {}  #: lane id -> VehicleClassGroup reference
        self._outgoingMovements         = []  #: list of outgoing Movements
        self._incomingMovements         = []  #: list of incoming Movements
        self._startShift                = None
        self._endShift                  = None
        self._shapePoints               = {}  #: sequenceNum -> (x,y)
        self._centerline                = None
    
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

    def getNumOutgoingMovements(self):
        """
        Returns the number of outgoing movements
        """
        return len(self._outgoingMovements)
    
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

    def hasOutgoingMovement(self, nodeId):
        """
        Return True if the link has an outgoing movement towards nodeId
        """
        for mov in self.iterOutgoingMovements():
            if mov.getDestinationNode().getId() == nodeId:
                return True
        return False
    
    def addOutgoingMovement(self, movement):
        """
        Adds the given movement.
        """
        if not isinstance(movement, Movement):
            raise DtaError("RoadLink addOutgoingMovement() called with invalid movement %s" % str(movement))
        
        if movement.getIncomingLink() != self:
            raise DtaError("RoadLink addOutgoingMovement() called with inconsistent movement" % str(movement))

        if self.hasOutgoingMovement(movement.getDestinationNode().getId()):
            raise DtaError("RoadLink %s addOutgoingMovement() called to add already "
                           "existing movement" % str(movement))
        
        self._outgoingMovements.append(movement)
        movement.getOutgoingLink()._incomingMovements.append(movement)
    
    def iterOutgoingMovements(self):
        """
        Iterator for the outgoing movements of this link
        """
        return iter(self._outgoingMovements)

    def getNumIncomingMovements(self):
        """
        Returns the number of incoming movements
        """
        return len(self._incomingMovements)

    def removeOutgoingMovement(self, movementToRemove):
        """
        Delete the input movement
        """
        if not isinstance(movementToRemove, Movement):
            raise DtaError("RoadLink %s deleteOutgoingMovement() called with invalid movement %s" % str(movement))
        
        if movementToRemove.getIncomingLink() != self:
            raise DtaError("RoadLink %s deleteOutgoingMovement() called with inconsistent movement" % str(movementToRemove))

        if not movementToRemove in self._outgoingMovements:
            raise DtaError("RoadLink %s deleteOutgoingMovement() called to delete "
                           "inexisting movement" % str(movementToRemove))

        self._outgoingMovements.remove(movementToRemove)
        movementToRemove.getOutgoingLink()._incomingMovements.remove(movementToRemove)

    def iterIncomingMovements(self):
        """
        Iterator for the incoming movements of this link
        """
        return iter(self._incomingMovements)

    def getNumLanes(self):
        """
        Return the number of lanes.
        """
        return self._numLanes

    def getLength(self):
        """
        Return the  length of the link 
        """
        return self._length 

        
    def getCenterLine(self):
        """
        Offset the link to the right 0.5*numLanes*lane_width and return a tuple of two points
        representing the centerline. 
        """
        if self._centerline:
            return self._centerline
        else: 

            dx = self._endNode.getX() - self._startNode.getX()
            dy = self._endNode.getY() - self._startNode.getY() 

            length = self.getLength() # dx ** 2 + dy ** 2
            
            if length == 0:
                length = 1

            scale = self.getNumLanes() * RoadLink.DEFAULT_LANE_WIDTH_FEET / 2.0 / length 

            xOffset = dy * scale
            yOffset = - dx * scale 

            self._centerline = ((self._startNode.getX() + xOffset, self._startNode.getY() + yOffset),
                                (self._endNode.getX() + xOffset, self._endNode.getY() + yOffset))

            return self._centerline

    def isRoadLink(self):
        """
        Return True this Link is RoadLink
        """
        return True

    def isConnector(self):
        """
        Return True if this Link is a Connector
        """
        return False 

    def isVirtualLink(self):
        """
        Return True if this LInk is a VirtualLink
        """
        return False

    def getOutgoingMovement(self, nodeId):
        """
        Return True if the link has an outgoing movement towards nodeId
        """
        for mov in self.iterOutgoingMovements():
            if mov.getDestinationNode().getId() == nodeId:
                mov
        raise DtaError("RoadLink from %d to %d does not have a movement to node %d" % (self._startNode.getId(),
                                                                                       self._endNode.getId(),
                                                                                       nodeId))
def lineSegmentsCross(p1, p2, p3, p4):
    """
    Helper function that determines if line segments (p1,p2) and (p3,p4) intersect. 
    If so it returns True, otherwise False. A point is defined as the tuple (x, y)
    """
    
    def crossProduct(pl, pm):
        """Return the cross product of two points pl and pm 
        each of them defined as a tuple (x, y)
        """ 
        return pl[0]*pm[1] - pm[0]*pl[1]


    def direction(pi, pj, pk):
        
        return crossProduct((pk[0] - pi[0], pk[1] - pi[1]),
                            (pj[0] - pi[0], pj[1] - pi[1])) 

    d1 = direction(p3, p4, p1)
    d2 = direction(p3, p4, p2)
    d3 = direction(p1, p2, p3)
    d4 = direction(p1, p2, p4) 

    if ((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) and \
            ((d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0)):
        return True
    else:
        return False
    

        

