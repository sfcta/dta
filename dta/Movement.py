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
import copy
import math
from itertools import izip
from collections import defaultdict

from .DtaError import DtaError
from .Logger import DtaLogger
from .Node import Node
from .RoadNode import RoadNode
from .VehicleClassGroup import VehicleClassGroup
from .Utils import getMidPoint, lineSegmentsCross, polylinesCross
from .Algorithms import pairwise

class Movement(object):
    """
    Base class that represents a movement.
    """

    DIR_UTURN   = "UTURN"
    DIR_RT      = 'RT'
    DIR_RT2     = 'RT2'
    DIR_LT2     = 'LT2'
    DIR_LT      = 'LT'
    DIR_TH      = 'TH'
    PROTECTED_CAPACITY_PER_HOUR_PER_LANE = 1900

    PERMITTED_ALL = "all"
    PROHIBITED_ALL = "prohibited"
    
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
        
         * *node* is a :py:class:`RoadNode` instance where the movement is located
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
        
        self._centerline = self.getCenterLine()
        
        self._simOutVolume = defaultdict(int)      # indexed by timeperiod
        self._simInVolume = defaultdict(int)      # indexed by timeperiod
        self._simMeanTT = defaultdict(float)    # indexed by timeperiod
        self._penalty   = 0
        self._timeVaryingCosts = []
        self._timeStep  = None
        
        self.simTimeStepInMin = None
        self.simStartTimeInMin = None
        self.simEndTimeInMin = None
        
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
        if self.getOutoingLink() == other.getOutgoingLink():
            return False
        
        for p1, p2 in izip(line1, line1[1:]):
            for p3, p4 in izip(line2, line2[1:]):
                if lineSegmentsCross(p1, p2, p3, p4):
                    return True
                
        if lineSegmentsCross(line1[-2], line1[-1],
                            line2[-2], line2[-1],
                             checkBoundaryConditions=True):
            return True
        return False

    def getNumLanes(self):
        """
        Return the number of lanes the movement has
        """
        return self._numLanes

    def getProtectedCapacity(self, planInfo):
        """
        Return the capacity of the movement in vehicles per hour
        This method calulates the capacity of of the movement by
        adding the green times of all the phases this movement
        participates in. 
        """
        if self._node.hasTimePlan(planInfo=planInfo):
            tp = self._node.getTimePlan(planInfo=planInfo)
            greenTime = 0
            for phase in tp.iterPhases():                                
                if phase.hasMovement(self.getStartNodeId(), self.getEndNodeId()):
                    mov = phase.getMovement(self.getStartNodeId(), self.getEndNodeId())
                    if mov.isProtected:
                        greenTime += phase.getGreen()
            if greenTime > 0:                
                return float(greenTime) / tp.getCycleLength() * self.getNumLanes() * Movement.PROTECTED_CAPACITY_PER_HOUR_PER_LANE
        raise DtaError("The movement %s does does not operate under a protected phase"
                       % self.getId())
         #return self.getNumLanes() * Movement.PROTECTED_CAPACITY_PER_HOUR_PER_LANE
                
    def _checkInputTimeStep(self, startTimeInMin, endTimeInMin):
        """The input time step should always be equal to the sim time step"""
        if endTimeInMin - startTimeInMin != self.simTimeStepInMin:
            raise DtaError('Time period from %d to %d is not '
                                   'equal to the simulation time step %d'
                                   % (startTimeInMin, endTimeInMin, 
                                      self.simTimeStepInMin))
            

    def _checkOutputTimeStep(self, startTimeInMin, endTimeInMin):
        """Checks that the difference in the input times is in multiples 
        of the simulation time step"""
        if (endTimeInMin - startTimeInMin) % self.simTimeStepInMin != 0:
            raise DtaError('Time period from %d to %d is not '
                                   'is a multiple of the simulation time step ' 
                                    '%d' % (startTimeInMin, endTimeInMin,
                                                    self.simTimeStepInMin))


    def _validateInputTimes(self, startTimeInMin, endTimeInMin):
        """Checks that the start time is less than the end time and that both 
        times are in the simulation time window"""
        
        if startTimeInMin >= endTimeInMin:
            raise DtaError("Invalid time bin (%d %s). The end time cannot be equal or less "
                                "than the end time" % (startTimeInMin, endTimeInMin))

        if startTimeInMin < self.simStartTimeInMin or endTimeInMin > \
                self .simEndTimeInMin:
            raise DtaError('Time period from %d to %d is out of '
                                   'simulation time' % (startTimeInMin, endTimeInMin))
        
    def getSimOutVolume(self, startTimeInMin, endTimeInMin):
        """
        Return the outgoing flow from the start to end
        """

        self._validateInputTimes(startTimeInMin, endTimeInMin)
        self._checkOutputTimeStep(startTimeInMin, endTimeInMin)

        result = 0
        for stTime, enTime in pairwise(range(startTimeInMin, endTimeInMin + 1, 
                                             self.simTimeStepInMin)):
            result += self._simOutVolume[stTime, enTime]
        return result

    def getSimOutFlow(self, startTimeInMin, endTimeInMin):
        """
        Get the outgoing flow for the specified time period 
        in vph
        """
        volume = self.getSimOutVolume(startTimeInMin, endTimeInMin)
        return  60.0 / (endTimeInMin - startTimeInMin) * volume

    def getSimInVolume(self, startTimeInMin, endTimeInMin):
        """
        Return the incoming flow from the start to end
        """
        self._validateInputTimes(startTimeInMin, endTimeInMin)
        self._checkOutputTimeStep(startTimeInMin, endTimeInMin)

        result = 0
        for stTime, enTime in pairwise(range(startTimeInMin, endTimeInMin + 1, 
                                             self.simTimeStepInMin)):
            result += self._simInVolume[stTime, enTime]
        return result

    def getSimInFlow(self, startTimeInMin, endTimeInMin):
        """Get the simulated flow for the specified time period 
        in vph"""
        volume = self.getSimInVolume(startTimeInMin, endTimeInMin)
        return  60.0 / (endTimeInMin - startTimeInMin) * volume

    def getSimTTInMin(self, startTimeInMin, endTimeInMin):
        """Return the mean movement travel time in minutes of 
        for all the vehicles that entered the link between the 
        input times
        """
        self._validateInputTimes(startTimeInMin, endTimeInMin)
        self._checkOutputTimeStep(startTimeInMin, endTimeInMin)

        totalFlow = 0
        totalTime = 0
        
        if (startTimeInMin, endTimeInMin) in self._simMeanTT:
            return self._simMeanTT[startTimeInMin, endTimeInMin]

        for (stTime, enTime), flow in self._simOutVolume.iteritems():
            if stTime >= startTimeInMin and enTime <= endTimeInMin:
                binTT = self._simMeanTT[(stTime, enTime)]

                if binTT > 0 and flow > 0:
                    totalFlow += flow
                    totalTime += self._simMeanTT[(stTime, enTime)] * flow
                elif binTT == 0 and flow == 0:
                    continue
                else:
                    raise DtaError("Movement %s has flow:%f and TT:%f "
                                           "for time period from %d to %d"  % 
                                           (self.getId(), flow, binTT, 
                                            startTimeInMin, endTimeInMin))

        if totalFlow > 0:
            return totalTime / float(totalFlow) + self._penalty
        else:
            return (self._incomingLink.getLength() / 
                float(self._incomingLink.getFreeFlowSpeedInMPH()) * 60 + self._penalty)

    def getSimSpeedInMPH(self, startTimeInMin, endTimeInMin):
        """
        Return the travel time of the first edge of the movement in 
        miles per hour
        """
        self._validateInputTimes(startTimeInMin, endTimeInMin)
        self._checkOutputTimeStep(startTimeInMin, endTimeInMin)

        ttInMin = self.getSimTTInMin(startTimeInMin, endTimeInMin)
        lengthInMiles = self.upLink.getLengthInMiles()
        return lengthInMiles / (ttInMin / 60.)

    def getFreeFlowSpeedInMPH(self):
        """
        Return the free flow travel speed in mph
        """
        return self.incomingLink.getFreeFlowSpeedInMPH()

    def getFreeFlowTTInMin(self):
        """
        Return the free flow travel time in minutes
        """
        return self._incomingLink.getFreeFlowTTInMin()

    def getTimeVaryingCostAt(self, timeInMin):
        """
        Return the cost (in min) for the time period begining at the 
        input time
        """
        period = int((timeInMin - self.simStartTimeInMin) // self._timeStep)
        return self._timeVaryingCosts[period]

    def getTimeVaryingCostTimeStep(self):
        """
        Return the time step that is used for the time varying costs
        """
        return self._timeStep
    
    def setSimOutVolume(self, startTimeInMin, endTimeInMin, flow):
        """
        Specify the simulated outgoing flow (vehicles per HOUR) for the supplied time period
        """
        self._validateInputTimes(startTimeInMin, endTimeInMin)
        self._checkInputTimeStep(startTimeInMin, endTimeInMin)

        self._simOutVolume[startTimeInMin, endTimeInMin] = flow

    def setSimInVolume(self, startTimeInMin, endTimeInMin, flow):
        """
        Specify the simulated incoming flow (vehicles per HOUR) for the supplied time period
        """
        self._validateInputTimes(startTimeInMin, endTimeInMin)
        self._checkInputTimeStep(startTimeInMin, endTimeInMin)

        self._simInVolume[startTimeInMin, endTimeInMin] = flow

    def setSimTTInMin(self, startTimeInMin, endTimeInMin, averageTTInMin):
        """
        Specify the simulated average travel time for the 
        input time period
        """
        self._validateInputTimes(startTimeInMin, endTimeInMin)
        self._checkInputTimeStep(startTimeInMin, endTimeInMin)

        if averageTTInMin < 0:
            raise DtaError("The travel time on movement %s cannot be negative" %
                                   str(self.getId()))
        if averageTTInMin == 0:
            if self.getSimOutFlow(startTimeInMin, endTimeInMin) > 0:
                raise DtaError("The travel time on movement %s with flow %d from %d to %d "
                                       "cannot be 0" % (self.iid, 
                                                        self.getSimOutFlow(startTimeInMin, endTimeInMin),
                                                        startTimeInMin, endTimeInMin))
            else:
                return

        if self.getSimOutFlow(startTimeInMin, endTimeInMin) == 0:
            raise DtaError('Cannot set the travel time on a movement with zero flow')

        self._simMeanTT[startTimeInMin, endTimeInMin] = averageTTInMin

    def setTimeVaryingCosts(self, timeVaryingCosts, timeStep):
        """
        Inputs:timeVaryingCosts is an array containing the cost 
        of the edge in each time period. timeStep is the interval 
        length in minutes
        """
        #make sure the costs are positive. 
        self._timeStep = timeStep
        for cost in timeVaryingCosts:
            assert cost > 0
        self._timeVaryingCosts = timeVaryingCosts

    def setPenaltyInMin(self, penalty):
        """
        Add the input penalty to the simulated movement travel time
        """
        self._penalty = penalty

    def getVehicleClassGroup(self):
        """
        Return the vehicle class group
        """
        return self._permission

    def setVehicleClassGroup(self, vehicleClassGroup):
        """
        Set the vehicle class group for this movement
        """
        self._permission = vehicleClassGroup

    def isProhibitedToAllVehicleClassGroups(self):
        """
        Return True if the movement is prohibited for all vehicles
        """
        return self._permission.allowsNone()

    def prohibitAllVehicleClassGroups(self):
        """
        Set the movement to prohibited to all vehicles
        """
        self._permission = VehicleClassGroup.getProhibited()

