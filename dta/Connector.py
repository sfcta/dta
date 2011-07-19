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
from .Movement import Movement
from .RoadLink import RoadLink
from .RoadNode import RoadNode
from .VehicleClassGroup import VehicleClassGroup
from .VirtualNode import VirtualNode

class Connector(RoadLink):
    """
    A Connector is a :py:class:`RoadLink` that connects a RoadNode with a Centroid or a VirtualNode.
    
    Why is a Connector a :py:class:`RoadLink` rather than a :py:class:`Link`?  
    Many centroid connectors are based on road links; all of them at the boundaries
    Therefore they have the same set of attributes and those attributes are meaningful.
    
    """
    #: default level value
    DEFAULT_LEVEL = 0
    
    #: connectors have a specific facility type
    FACILITY_TYPE = 99
        
    def __init__(self, id, startNode, endNode, reverseAttachedLinkId, length,
                 freeflowSpeed, effectiveLengthFactor, responseTimeFactor, numLanes, 
                 roundAbout, level, label):
        """
        Constructor. Verifies one node is a RoadNode and the other node is either
        a Centroid or a VirtualNode.
        
        See :py:meth:`RoadLink.__init__` for the arg descriptions.  
        """
        
        if isinstance(startNode, Centroid) or isinstance(startNode, VirtualNode):
            self._fromRoadNode = False
        elif isinstance(endNode, Centroid) or isinstance(endNode, VirtualNode):
            self._fromRoadNode = True
        else:
            raise DtaError("Attempting to initialize a Connector without a Centroid/VirtualNode: %s - %s" % 
                           (str(startNode), str(endNode)))
        
        if self._fromRoadNode and not isinstance(startNode, RoadNode):
            raise DtaError("Attempting to initialize a Connector without a start RoadNode: %s - %s" % 
                           (str(startNode), str(endNode)))
        elif not self._fromRoadNode and not isinstance(endNode, RoadNode):
            raise DtaError("Attempting to initialize a Connector without an end RoadNode: %s - %s" % 
                           (str(startNode), str(endNode)))
       
        RoadLink.__init__(self, id=id, startNode=startNode, endNode=endNode, 
                          reverseAttachedLinkId=reverseAttachedLinkId, facilityType=Connector.FACILITY_TYPE, 
                          length=length, freeflowSpeed=freeflowSpeed, effectiveLengthFactor=effectiveLengthFactor, 
                          responseTimeFactor=responseTimeFactor, numLanes=numLanes,
                          roundAbout=roundAbout, level=level, label=label)

    def startIsRoadNode(self):
        """
        Returns a boolean indicating wither the start node is the :py:class:`RoadNode` instance.
        """
        return self._fromRoadNode
    
    def endIsRoadNode(self):
        """
        Returns a boolean indicating wither the end node is the :py:class:`RoadNode` instance.
        """
        return not self._fromRoadNode
    
    def setStartNode(self, newStartNode):
        """
        This is a dumb method which allows the caller to substitute the newStartNode for the old one.
        It does update the the outgoing links for both the old and the new start nodes.

        .. warning:: This does not fix the :py:class:`Network` for this change so it is meant to be
                     called from the :py:class:`Network` itself 
                     (e.g. :py:meth:`Network.insertVirtualNodeBetweenCentroidsAndRoadNodes`)
        """
        # needs to stay this way
        if self._fromRoadNode and not isinstance(newStartNode, RoadNode):
            raise DtaError("Attempting to setStartNode on Connector without a start RoadNode: %s" % 
                           str(newStartNode))
        
        if not self._fromRoadNode and not(isinstance(newStartNode, Centroid) or isinstance(newStartNode, VirtualNode)):
            raise DtaError("Attempting to setStartNode on Connector without a Centroid/VirtualNode: %s" % 
                           str(newStartNode))
            
        self._startNode.removeOutgoingLink(self)
        self._startNode = newStartNode
        self._startNode.addOutgoingLink(self)
        
    def setEndNode(self, newEndNode):
        """
        This is a dumb method which allows the caller to substitute the newEndNode for the old one.
        It does update the the incoming links for both the old and the new end nodes.
        
        .. warning:: This does not fix the :py:class:`Network` for this change so it is meant to be
                     called from the :py:class:`Network` itself 
                     (e.g. :py:meth:`Network.insertVirtualNodeBetweenCentroidsAndRoadNodes`)
        """
        # needs to stay this way
        if not self._fromRoadNode and not isinstance(newEndNode, RoadNode):
            raise DtaError("Attempting to setEndNode on Connector without a start RoadNode: %s" % 
                           str(newEndNode))
        
        if self._fromRoadNode and not(isinstance(newEndNode, Centroid) or isinstance(newEndNode, VirtualNode)):
            raise DtaError("Attempting to setEndNode on Connector without a Centroid/VirtualNode: %s" % 
                           str(newEndNode))
            
        self._endNode.removeIncomingLink(self)
        self._endNode = newEndNode
        self._endNode.addIncomingLink(self)