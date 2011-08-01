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
# from .Link import Link


class Node(object):
    """
    Base class that represents a node in a network.
    
    """
    
    # Defaults
    DEFAULT_LABEL = ""
    DEFAULT_LEVEL = 0

    # Geometry types - how is this used?  Why is the centroid not in the type list?
    
    #: :py:class:`RoadNode` geometry type
    GEOMETRY_TYPE_INTERSECTION      = 1
    #: :py:class:`RoadNode` geometry type
    GEOMETRY_TYPE_JUNCTION          = 2
    #: :py:class:`VirtualNode` geometry type
    GEOMETRY_TYPE_VIRTUAL           = 99
    #: :py:class:`Centroid` geometry type
    GEOMETRY_TYPE_CENTROID          = 100
    GEOMETRY_TYPES                  = [GEOMETRY_TYPE_INTERSECTION,
                                       GEOMETRY_TYPE_JUNCTION,
                                       GEOMETRY_TYPE_VIRTUAL]
    
    def __init__(self, id, x, y, geometryType, label=None, level=None):
        """
        Constructor.
        
         * *id* is a unique identifier (unique within the containing network), an integer
         * *x* and *y* are coordinates (what units?)
         * *geometryType* is one of :py:attr:`Node.GEOMETRY_TYPE_INTERSECTION`, :py:attr:`Node.GEOMETRY_TYPE_JUNCTION`, or 
           :py:attr:`Node.GEOMETRY_TYPE_VIRTUAL`
         * *label* is a string, for readability.  If None passed, will use default. 
         * *level* is for vertical alignment.  More details TBD.  If None passed, will use default.  
        
        """
        self._id             = id   #: unique identifier (integer)
        self._x              = x    #: x-coordinate
        self._y              = y    #: y-coordinate
        self._geometryType   = geometryType #: one of Node.GEOMETRY_TYPE_INTERSECTION, Node.GEOMETRY_TYPE_JUNCTION, or Node.GEOMETRY_TYPE_VIRTUAL
        
        if label:
            self._label = label
        else:
            self._label = Node.DEFAULT_LABEL
            
        if level:
            self._level = level
        else:
            self._level = Node.DEFAULT_LEVEL
        
        #: List of incoming Link objects, in clockwise order starting from <1,0>
        self._incomingLinks = []
        
        #: List of outgoing link objects, in clockwise order starting from <1,0>
        self._outgoingLinks = []
    
    def __str__(self):
        """
        String representation
        """
        return "Node of type %s, id=%s, x,y=(%f,%f)" % (self.__class__, self._id, self._x, self._y)
    
    def _addIncomingLink(self, link):
        """
        Verify that the given link ends in this node, and adds it to the list of
        incoming links.
        """
        #if not isinstance(link, Link):
        #    raise DtaError("Node.addIncomingLink called with an invalid link: %s" % str(link))
        
        if link.getEndNode() != self:
            raise DtaError("Node.addIncomingLink called for link that doesn't end here: %s" % str(link))

        angle = link.getReferenceAngle()
        
        position = 0
        for i in range(len(self._incomingLinks)):
            if self._incomingLinks[i].getReferenceAngle() > angle: break
            position += 1
            
        self._incomingLinks.insert(position, link)
    
    def _removeIncomingLink(self, link):
        """
        Simple removal.
        """
        if link not in self._incomingLinks:
            raise DtaError("Node.removeIncomingLink called for link not in incoming links list: %s" % str(link))
        self._incomingLinks.remove(link)
    
    def _addOutgoingLink(self, link):
        """
        Verify that the given link starts with this node, and adds it to the list of
        outgoing links.
        """
        #if not isinstance(link, Link):
        #    raise DtaError("Node.addOutgoingLink called with an invalid link: %s" % str(link))
        
        if link.getStartNode() != self:
            raise DtaError("Node.addOutgoingLink called for link that doesn't start here: %s" % str(link))

        angle = link.getReferenceAngle()
        
        position = 0
        for i in range(len(self._outgoingLinks)):
            if self._outgoingLinks[i].getReferenceAngle() > angle: break
            position += 1
            
        self._outgoingLinks.insert(position, link)
        # print self._outgoingLinks
        
    def _removeOutgoingLink(self, link):
        """
        Simple removal.
        """
        if link not in self._outgoingLinks:
            raise DtaError("Node.removeOutgoingLink called for link not in outgoing links list: %s" % str(link))
        self._outgoingLinks.remove(link)

    def iterIncomingLinks(self):
        """
        Returns iterator for the incoming links.
        """
        return iter(self._incomingLinks)
    
    def iterOutgoingLinks(self):
        """
        Returns iterator for the outgoing links.
        """
        return iter(self._outgoingLinks)

    def getId(self): 
        """
        Returns the integer id for this node.
        """
        return self._id
    
    def getX(self):
        """
        Returns the x-coordinate for this node.
        """
        return self._x
    
    def getY(self):
        """
        Returns the y-coordinate for this node.
        """
        return self._y

    def hasIncomingLinkForId(self, linkId):
        """
        Returns True if there is an incoming link with the given id
        """
        for link in self.iterIncomingLinks():
            if link.getId() == linkId:
                return True
        return False

    def hasIncomingLinkForNodeId(self, nodeId):
        """
        Returns True if there is an incoming link starting from nodeId
        """
        for link in self.iterIncomingLinks():
            if link.getStartNode().getId() == nodeId:
                return True
        return False

    def hasOutgoingLinkForId(self, linkId):
        """
        Returns True if there is an outgoing link wwith the given id
        """
        for link in self.iterIncomingLinks():
            if link.getId() == linkId:
                return True
        return False

    def hasOutgoingLinkForNodeId(self, nodeId):
        """
        Returns True if there is a link towards the given node id
        """
        for link in self.iterOutgoingLinks():
            if link.getEndNode(). getId() == nodeId:
                return True
        return False
            
    def _removeIncomingLink(self, link):
        """
        Simple removal.
        """
        if link not in self._incomingLinks:
            raise DtaError("Node.removeIncomingLink called for link not in incoming links list: %#s" % str(link))
        self._incomingLinks.remove(link)
