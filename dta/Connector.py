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
        
        if isinstance(startNode, RoadNode):
            self._fromRoadNode = True
        elif isinstance(endNode, RoadNode):
            self._fromRoadNode = False
        else:
            raise DtaError("Attempting to initialize a Connector without a RoadNode: %s - %s" % 
                           (str(startNode), str(endNode)))

        if (not isinstance(startNode, Centroid) and not isinstance(startNode, VirtualNode) and
            not isinstance(endNode, Centroid) and not isinstance(endNode, VirtualNode)):
            raise DtaError("Attempting to initialize a Connector without a Centroid/VirtualNode: %s - %s" % 
                           (str(startNode), str(endNode)))
       
        RoadLink.__init__(self, id=id, startNode=startNode, endNode=endNode, 
                          reverseAttachedLinkId=reverseAttachedLinkId, facilityType=Connector.FACILITY_TYPE, 
                          length=length, freeflowSpeed=freeflowSpeed, effectiveLengthFactor=effectiveLengthFactor, 
                          responseTimeFactor=responseTimeFactor, numLanes=numLanes,
                          roundAbout=roundAbout, level=level, label=label)

