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
from itertools import izip

from .DtaError import DtaError
from .Logger import DtaLogger
from .Node import Node
from .RoadNode import RoadNode
from .VehicleClassGroup import VehicleClassGroup
from .Utils import getMidPoint, lineSegmentsCross, polylinesCross


class Movement(object):
    """
    Base class that represents a movement.
    """

    DIR_UTURN = "UTURN"
    DIR_RT = 'RT'
    DIR_RT2 = 'RT2'
    DIR_LT2 = 'LT2'
    DIR_LT = 'LT'
    DIR_TH = 'TH'
    PROTECTED_CAPACITY_PER_HOUR_PER_LANE = 1900
    
    @classmethod
    def simpleMovementFactory(cls, incomingLink, outgoingLink, vehicleClassGroup):
        """
        Return a movement connecting the input links with the given permissions 
        defined by the vehicle class group.
        """
        return Movement(incomingLink.getEndNode(), 
                        incomingLink, 
                        outgoingLink, 
                        incomingLink._freeflowSpeed, 
                        vehicleClassGroup
                        )
                                
    def __init__(self, node, incomingLink, outgoingLink, freeflowSpeed, vehicleClassGroup,
                 numLanes=None, incomingLane=None, outgoingLane=None, followupTime=0):
        """
        Constructor.
        
         * *node* is a :py:class:`Node` instance (can it be a non-RoadNode?) where the movement is located
         * *incomingLink*, *outgoingLink* are :py:class:`Link` instances
         * *freeflowSpeed* is the maximum speed of the movement; pass None to use that of the *incomingLink*
         * *vehicleClassGroup* is the allowed group of vehicles that can use this Movement; it should be an
           instance of :py:class:`VehicleClassGroup`
         * *numLanes* is the width of the movement.  For a movement that has a different number of lanes
           upstream and downstream, the minimum of these two values should be used.  The number of lanes
           can vary over time.  Pass `None` to let the software choose.
         * *incomingLane*: Of the lanes associated with this movement on the *incomingLink*, the id number
           of tbhe lane closest to the inside of the roadway (that is, the one with the highest id number).
           This attribute can vary over time.  Pass `None` to let the software choose.
         * *outgoingLane*: Of the lanes associated with this movement on the *outgoingLink*, the id number
           of the lane closest to the inside of the roadway (that is, the one with the highest id number).
           This attribute can vary over time.  Pass `None` to let the software choose.
         * *followupTime* is the follow-up time for the movement.  This attribute can vary over time.
        """
        # type checking
        if not isinstance(node, RoadNode):
            DtaLogger.debug("Movement instantiated with non-RoadNode: %s" % str(node))
        #if not isinstance(incomingLink, RoadLink):
        #    DtaLogger.debug("Movement instantiated with non-RoadLink incomingLink: %s" % str(incomingLink))
        #if not isinstance(outgoingLink, RoadLink):
        #    DtaLogger.debug("Movement instantiated with non-RoadLink outgoingLink: %s" % str(outgoingLink))
        
        # DtaLogger.debug("Movement instantiated with links %s %s" % (str(incomingLink),str(outgoingLink)))

        if not isinstance(vehicleClassGroup, VehicleClassGroup):
            raise DtaError("Movement instantiated with invalid vehicleClassGroup: %s" % str(vehicleClassGroup))
        
        # todo: sanity checking on numLanes, incomingLane, outgoingLane
            
        self._node          = node
        self._incomingLink  = incomingLink
        self._outgoingLink  = outgoingLink
        self._freeflowSpeed = freeflowSpeed
        self._permission    = vehicleClassGroup
        self._numLanes      = numLanes
        self._incomingLane  = incomingLane
        self._outgoingLane  = outgoingLane
        self._followupTime  = followupTime
        
        self._countsList = []        
        self._centerline = self.getCenterLine()

    def getIncomingLink(self):
        """
        Returns the incomingLink, a :py:class:`Link` instance
        """
        return self._incomingLink
    
    def getOutgoingLink(self):
        """
        Returns the outgoung, a :py:class:`Link` instance
        """
        return self._outgoingLink
        
    def getAtNode(self):
        """
        Returns the node at which the movement is happening
        """
        
        return self._node  
    
    def getOriginNode(self):
        """
        Returns the start node of incomingLink, a :py:class:`Link` instance
        """
        return self._incomingLink.getStartNode()
    
    def getDestinationNode(self):
        """
        Returns the end node of outgoingLink, a :py:class:`Link` instance
        """
        return self._outgoingLink.getEndNode()
    
    def getCountList(self):
        """
        Returns countslist saved for the movement
        """
        return self._countsList
    
    def setCountsFromCountDracula(self, countsListFromCountDracula):
        """
        Inserts the countlist
        """
        self._countsList = countsListFromCountDracula
        
    def getStartNode(self):
        """
        Returns the start node of incomingLink, a :py:class:`Link` instance
        """
        return self._incomingLink.getStartNode()
    
    def getEndNode(self):
        """
        Returns the end node of outgoingLink, a :py:class:`Link` instance
        """
        return self._outgoingLink.getEndNode()

    def getStartNodeId(self):
        """
        Returns the start node of incomingLink, a :py:class:`Link` instance
        """
        return self._incomingLink.getStartNodeId()
    
    def getEndNodeId(self):
        """
        Returns the end node of outgoingLink, a :py:class:`Link` instance
        """
        return self._outgoingLink.getEndNodeId()

    def getId(self):
        """
        Return a string containing the three node ids that define the movement
        """
        return "%d %d %d" % (self.getStartNodeId(), self.getAtNode().getId(), self.getEndNodeId())

    def isUTurn(self):
        """
        Return True if the movement is a U-Turn
        """
        return True if self._incomingLink.getStartNode() == self._outgoingLink.getEndNode() else False

    def isThruTurn(self):
        """
        Return True if the movement is a Through movement
        """
        return True if self.getTurnType() == Movement.DIR_TH else False 

    def isLeftTurn(self):
        """
        Return True if the movement is a left turn
        """
        if self.getTurnType() == Movement.DIR_LT or \
           self.getTurnType() == Movement.DIR_LT2:
            return True
        return False

    def isRightTurn(self):
        """
        Return True if the movement is a right turn
        """
        if self.getTurnType() == Movement.DIR_RT or \
           self.getTurnType() == Movement.DIR_RT2:
            return True
        return False

    def getTurnType(self):
        """
        Return the type of the turn the movement makes as one of the following strings
        UTURN, RT, RT2, LT2, LT, TH
        """
        dx1 = self._incomingLink.getEndNode().getX() - self._incomingLink.getStartNode().getX()
        dy1 = self._incomingLink.getEndNode().getY() - self._incomingLink.getStartNode().getY()

        dx2 = self._outgoingLink.getEndNode().getX() - self._outgoingLink.getStartNode().getX()
        dy2 = self._outgoingLink.getEndNode().getY() - self._outgoingLink.getStartNode().getY()
           
        angle = (math.atan2(dy2, dx2) - math.atan2(dy1, dx1)) * 180 / math.pi
        if angle < 0:
            angle += 360

        turnType = None
        if self.isUTurn():
            turnType =  Movement.DIR_UTURN
        elif 135 <= angle < 180:
            turnType =  Movement.DIR_LT2
        elif 45 <= angle < 135:
            turnType =  Movement.DIR_LT
        elif 0 <= angle  < 45:
            turnType =  Movement.DIR_TH
        elif 315 <= angle < 360:
            turnType =  Movement.DIR_TH
        elif 225 <= angle < 315:
            turnType =  Movement.DIR_RT
        else:
            turnType =  Movement.DIR_RT2

        return turnType

    def getDirection(self):
        """
        Return the direction of the movement as a string
        """
        dx1 = self._incomingLink.getEndNode().getX() - self._incomingLink.getStartNode().getX()
        dy1 = self._incomingLink.getEndNode().getY() - self._incomingLink.getStartNode().getY()

        dx2 = self._outgoingLink.getEndNode().getX() - self._outgoingLink.getStartNode().getX()
        dy2 = self._outgoingLink.getEndNode().getY() - self._outgoingLink.getStartNode().getY()
           
        angle = (math.atan2(dy2, dx2) - math.atan2(dy1, dx1)) * 180 / math.pi
        if angle < 0:
            angle += 360

        turnType = None
        if self.isUTurn():
            turnType =  Movement.DIR_UTURN
        elif 135 <= angle < 180:
            turnType =  Movement.DIR_LT2
        elif 45 <= angle < 135:
            turnType =  Movement.DIR_LT
        elif 0 <= angle  < 45:
            turnType =  Movement.DIR_TH
        elif 315 <= angle < 360:
            turnType =  Movement.DIR_TH
        elif 225 <= angle < 315:
            turnType =  Movement.DIR_RT
        else:
            turnType =  Movement.DIR_RT2

        linkDir = self._incomingLink.getDirection()
        return linkDir + turnType
                
    def getCenterLine(self):
        """
        Get a list of points represeting the movement
        """
        line1 = self._incomingLink.getCenterLine()
        line2 = self._outgoingLink.getCenterLine()

        if lineSegmentsCross(line1[0], line1[-1], line2[0], line2[-1]):
            p1 = getMidPoint(*line1)
            p2 = getMidPoint(*line2) 
            self._centerLine = [line1[0], p1, p2, line2[-1]]
        else:
            self._centerLine = [line1[0], line1[-1], line2[0], line2[-1]]
            
        return self._centerLine

    def isInConflict(self, other):
        """
        Return true if the current movement is conflicting with the other one
        """
        line1 = self.getCenterLine()
        line2 = other.getCenterLine()

        if self.getIncomingLink() == other.getIncomingLink():
            return False 
        
        for p1, p2 in izip(line1, line1[1:]):
            for p3, p4 in izip(line2, line2[1:]):
                if lineSegmentsCross(p1, p2, p3, p4):
                    return True
                
        if lineSegmentsCross(line1[-2], line1[-1],
                            line2[-2], line2[-1],
                             checkBoundryConditions=True):            
            return True
        return False

    def getNumLanes(self):
        """
        Return the number of lanes the movement has
        """
        return self._numLanes

    def getProtectedCapacity(self, planInfo=None):
        """
        Return the capacity of the movement in vehicles per hour
        """
        if self._node.hasTimePlan(planInfo=planInfo):
            tp = self._node.getTimePlan(planInfo=planInfo)
            greenTime = 0
            for phase in tp.iterPhases():
                if phase.hasMovement(self.getStartNodeId(), self.getEndNodeId()):
                    greenTime += phase.getGreen()

            return greenTime / tp.getCycleLength() * self.getNumLanes() * Movement.PROTECTED_CAPACITY_PER_HOUR_PER_LANE
        else:
            return self.getNumLanes() * Movement.PROTECTED_CAPACITY_PER_HOUR_PER_LANE
        
        
    
