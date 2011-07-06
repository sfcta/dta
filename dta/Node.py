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
# from .Link import Link

class Node(object):
    """
    Base class that represents a node in a network.
    
    """
    
    # Defaults
    DEFAULT_LABEL = ""
    DEFAULT_LEVEL = 0

    # Geometry types - how is this used?  Why is the centroid not in the type list?
    GEOMETRY_TYPE_INTERSECTION      = 1   # RoadNode geometry type
    GEOMETRY_TYPE_JUNCTION          = 2   # RoadNode geometry type
    GEOMETRY_TYPE_VIRTUAL           = 99  # VirtualNode geometry type
    GEOMETRY_TYPE_CENTROID          = 100 # Centroid geometry type
    GEOMETRY_TYPES                  = [GEOMETRY_TYPE_INTERSECTION,
                                       GEOMETRY_TYPE_JUNCTION,
                                       GEOMETRY_TYPE_VIRTUAL]
    
    def __init__(self, id, x, y, type, label=None, level=None):
        """
        Constructor.
        
         * id is a unique identifier (unique within the containing network), an integer
         * x and y are coordinates (what units?)
         * type is one of Node.GEOMETRY_TYPE_INTERSECTION, Node.GEOMETRY_TYPE_JUNCTION, or 
           Node.GEOMETRY_TYPE_VIRTUAL
         * label is a string, for readability.  If None passed, will default to "label [id]"
         * level is for vertical alignment.  More details TBD.  If None passed, will use default.  
        
        """
        #: unique identifier (integer)
        self.id      = id
        #: x-coordinate
        self.x       = x
        #: y-coordinate
        self.y       = y
        #: one of Node.GEOMETRY_TYPE_INTERSECTION, Node.GEOMETRY_TYPE_JUNCTION, or Node.GEOMETRY_TYPE_VIRTUAL
        self._type   = type
        
        if label:
            self._label = label
        else:
            self._label = Node.DEFAULT_LABEL
            
        if level:
            self._level = level
        else:
            self._level = Node.DEFAULT_LEVEL
        
        # Dictionary of Link objects, with Link -> angle between the link and (x+1,y) -> (x,y).
        self._incoming_links = {}
        
        # Dictionary of Link objects, with Link -> angle between the link and (x,y) -> (x+1,y).
        self._outgoing_links = {}
    
    def addIncomingLink(self, link):
        """
        Verify that the given link ends in this node, and adds it to the list of
        incoming links.
        """
        #if not isinstance(link, Link):
        #    raise DtaError("Node.addIncomingLink called with an invalid link: %s" % str(link))
        
        if link.nodeB != self:
            raise DtaError("Node.addIncomingLink called for link that doesn't end here: %s" % str(link))
        
        angle = math.acos( (self.x - link.nodeA.x) / link.euclideanLength() )
        self._incoming_links[link] = angle
    
    def addOutgoingLink(self, link):
        """
        Verify that the given link starts with this node, and adds it to the list of
        outgoing links.
        """
        #if not isinstance(link, Link):
        #    raise DtaError("Node.addOutgoingLink called with an invalid link: %s" % str(link))
        
        if link.nodeA != self:
            raise DtaError("Node.addOutgoingLink called for link that doesn't start here: %s" % str(link))
        
        angle = math.acos( (link.nodeB.x - self.x) / link.euclideanLength() )
        self._outgoing_links[link] = angle
