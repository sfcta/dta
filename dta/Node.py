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

from itertools import chain 
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

    def iterUpstreamNodes(self):
        """
        Returns an iterator to the upstream nodes
        """
        for link in self.iterIncomingLinks():
            yield link.getStartNode()
            
    def iterOutgoingLinks(self):
        """
        Returns iterator for the outgoing links.
        """
        return iter(self._outgoingLinks)

    def iterDownstreamNodes(self):
        """
        Returns an iterator to the downstream nodes
        """
        for link in self.iterOutgoingLinks():
            yield link.getEndNode() 

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
            
    def getNumAdjacentLinks(self):
        """
        Return the number of links adjacent to this node (either incoming or outgoing) 
        """
        return len(self._incomingLinks) + len(self._outgoingLinks) 

    def getNumAdjacentRoadLinks(self):
        """
        Return the number of RoadLinks adjacent to this node (either incoming or outgoing)
        """
        return sum([1 for link in self.iterAdjacentRoadLinks()])

    def iterAdjacentNodes(self):
        """
        Return an iterator to the adjacent Nodes
        """ 
        nodes = set()
        for link in self.iterIncomingLinks():
            nodes.add(link.getStartNode())

        for link in self.iterOutgoingLinks():
            nodes.add(link.getEndNode()) 
        return iter(nodes) 

    def getNumAdjacentNodes(self):
        """
        Return the number of nodes that are connected to this node.
        """ 
        return sum([1 for node in self.iterAdjacentNodes()])
        
    def iterAdjacentLinks(self):
        """
        Return an iterator to all links adjacent (incoming or outgoing)
        to this node
        """
        return chain(iter(self._incomingLinks), iter(self._outgoingLinks))

    def iterAdjacentRoadLinks(self):
        """
        Return an iterator to all RoadLinks adjacent to this Node (excluding Connectors)
        """
        for link in self.iterAdjacentLinks():
            if link.isRoadLink():
                yield link 

    def iterAdjacentRoadNodes(self):
        """
        Return an iterator to all RoadNodes adjacent to this Node
        """
        for node in self.iterAdjacentNodes():
            if node.isRoadNode():
                yield node

    def getNumAdjacentRoadNodes(self):
        """
        Return the number of nodes that are connected to this node.
        """ 
        return sum([1 for node in self.iterAdjacentRoadNodes()])

    def getIncomingLinkForId(self, linkId):
        """
        Returns True if there is an incoming link with the given id
        """
        for link in self.iterIncomingLinks():
            if link.getId() == linkId:
                return link 
        raise DtaError("Node %d does not have incoming link with id %d" % (self._id, linkId)) 

    def getIncomingLinkForNodeId(self, nodeId):
        """
        Returns True if there is an incoming link starting from nodeId
        """
        for link in self.iterIncomingLinks():
            if link.getStartNode().getId() == nodeId:
                return True
        raise DtaError("Node %d does not have an incoming link starting from" % (self._id, nodeId)) 

    def getNumIncomingLinks(self):
        """
        Returns the number of incoming links
        """
        return len(self._incomingLinks)

    def getNumOutgoingLinks(self):
        """
        Retruns the number of outoing links
        """
        return len(self._outgoingLinks)


    def hasConnector(self):
        """
        Return True if there is a connector atached to the node.
        """
        for link in self.iterIncomingLinks():
            if link.isConnector():
                return True

        for link in self.iterOutgoingLinks():
            if link.isConnector():
                return True

        return False 

    def getCardinality(self):
        """
        Return a pair of numbers representing the number of 
        incoming and outgoing links respectively
        """
        return (len(self._incomingLinks), len(self._outgoingLinks))
        
    def isIntersection(self):
        """
        Return True if this node is an intersection
        """
        return not self.isJunction() 

    def isJunction(self):
        """
        Return True if this node is a junction. 
        """
        if self.getNumOutgoingLinks() == 1 or self.getNumIncomingLinks() == 1:
            return True
        if self.isShapePoint():
            return True 

        return False 

    def isShapePoint(self, countRoadNodesOnly=False):
        """
        Return True if the node is a shape point (e.g. Node 51546 in the 
        following graph). 
        If countRoadNodesOnly is True the method will count only RoadLinks 
        attached to this Node and will disregard an connectors. 
        
        .. image:: /images/shapePoint.png
           :height: 300px
           
        """
        
        if not countRoadNodesOnly:
            if self.getNumAdjacentLinks() == 4 and self.getNumAdjacentNodes() == 2:
                return True
            if self.getNumAdjacentLinks() == 2 and self.getNumAdjacentNodes() == 2:
                return True
        else: 
            if self.getNumAdjacentRoadLinks() == 4 and self.getNumAdjacentRoadNodes() == 2:
                return True
            if self.getNumAdjacentRoadLinks() == 2 and self.getNumAdjacentRoadNodes() == 2:
                return True
 
        return False
