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

import math
from .DtaError import DtaError
from .Logger import DtaLogger
from .Node import Node
from .RoadNode import RoadNode
from .VehicleClassGroup import VehicleClassGroup

class Movement(object):
    """
    Base class that represents a movement.
    """
        
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
           of the lane closest to the inside of the roadway (that is, the one with the highest id number).
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
        
