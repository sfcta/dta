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

import pdb 
import math

from .DtaError import DtaError
from .Link import Link
from .Movement import Movement
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

        if numLanes <= 0: 
            raise DtaError("RoadLink %d cannot have number of lanes = %d" % (self.getId(), numLanes))

        self._numLanes                  = numLanes
        self._roundAbout                = roundAbout
        if level:
            self._level                 = level
        else:
            self._level                 = RoadLink.DEFAULT_LEVEL

        self._lanePermissions           = {}  #: lane id -> VehicleClassGroup reference
        self._outgoingMovements         = []  #: list of outgoing Movements
        self._incomingMovements         = []  #: list of incoming Movements
        self._startShift                = None
        self._endShift                  = None
        self._shapePoints               = {}  #: sequenceNum -> (x,y)
        self._centerline                = self.getCenterLine()
    
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
            raise DtaError("RoadLink %s deleteOutgoingMovement() "
                           "called with invalid movement %s" % str(movementToRemove))
        
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

        dx = self._endNode.getX() - self._startNode.getX()
        dy = self._endNode.getY() - self._startNode.getY() 

        length = self.euclideanLength() # dx ** 2 + dy ** 2

        if length == 0:
            length = 1

        scale = self.getNumLanes() * RoadLink.DEFAULT_LANE_WIDTH_FEET / 2.0 / length 

        xOffset = dy * scale
        yOffset = - dx * scale 

        self._centerline = ((self._startNode.getX() + xOffset, self._startNode.getY() + yOffset),
                            (self._endNode.getX() + xOffset, self._endNode.getY() + yOffset))

        return self._centerline

    def getMidPoint(self):
        """
        Return the midpoint of the link's centerline as a tuple of two floats
        """
        
        return ((self._centerline[0][0] + self._centerline[1][0]) / 2.0,
                (self._centerline[0][1] + self._centerline[1][1]) / 2.0)
                
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
    def setNumLanes(self, numLanes):
        """
        Sets the number of lanes to the given value
        """ 
        self._numLanes = numLanes 
    
    def getAcuteAngle(self, other):
        """
        Return the acute angle (0, 180) between this link and the input one.
        Both links are considered as line segments from start to finish (shapepoints 
        are not taken into account).
        """

        if self == other:
            return 0

        if self.getStartNode().getX() == other.getStartNode().getX() and \
                self.getStartNode().getY() == other.getEndNode().getY() and \
                self.getEndNode().getX() == other.getEndNode().getX() and \
                self.getEndNode().getY() == other.getEndNode().getY():
            return 0

        if self.getStartNode() == other.getEndNode() and \
                self.getEndNode() == other.getStartNode():
            return 180 

        dx1 = self.getEndNode().getX() - self.getStartNode().getX()
        dy1 = self.getEndNode().getY() - self.getStartNode().getY()
        
        dx2 = other.getEndNode().getX() - other.getStartNode().getX()
        dy2 = other.getEndNode().getY() - other.getStartNode().getY()


        length1 = math.sqrt(dx1 ** 2 + dy1 ** 2)
        length2 = math.sqrt(dx2 ** 2 + dy2 ** 2)

        if length1 == 0:
            raise DtaError("The length of link %d cannot not be zero" % self.getId())
        if length2 == 0:
            raise DtaError("The length of link %d cannot not be zero" % other.getId())

        if abs((dx1 * dx2 + dy1 * dy2) / (length1 * length2)) > 1:
            if abs((dx1 * dx2 + dy1 * dy2) / (length1 * length2)) - 1 < 0.00001:
                return 0
            else:
                raise DtaError("cannot apply getAcute angle from %d to %d" % (self.getId(), other.getId()))            
        return abs(math.acos((dx1 * dx2 + dy1 * dy2) / (length1 * length2))) / math.pi * 180.0
    
    def isOverlapping(self, other):
        """
        Return True if the angle between the two links (measured using their endpoints) is less than 1 degree
        """
        if self.getAcuteAngle(other) <= 1.0:
            return True
        return False
        
        

