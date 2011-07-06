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
from .Link import Link
from .RoadNode import RoadNode
from .VirtualNode import VirtualNode

class Network(object):
    """
    Base class that represents a DTA Network.  Networks exist on a continuum between
    macro- and micro-simulation, and this network is meant to represent something
    "typical" for a mesosimulation.  Something to be aware of in case it becomes too complicated.
    
    Subclasses will be used to represent networks for different frameworks (Dynameq, Cube, etc)
    so this class should have no code to deal with any particular file formats.
    
    """
    
    def __init__(self):
        """
        Constructor.  Initializes to an empty network.
        
        """
        
        #: node id -> node; can be :py:class:`RoadNode`s or :py:class:`VirtualNode`s
        self._nodes     = {}
        #: node id -> :py:class:`Centroid` node
        self._centroids = {}
        #: link id -> :py:class:`Link`
        self._links     = {}
        
    def __del__(self):
        pass
    
    def addNode(self, newNode):
        """
        Verifies that *newNode* is a :py:class:`RoadNode` or a :py:class:`VirtualNode` and that the id is not
        already used; stores it.
        """
        if not isinstance(newNode, RoadNode) and not isinstance(newNode, VirtualNode):
            raise DtaError("Network.addNode called on non-RoadNode/VirtualNode: %s" % str(newNode))

        if newNode.id in self._nodes:
            raise DtaError("Network.addNode called on node with id %d already in the network (for a node)" % newNode.id)

        if newNode.id in self._centroids:
            raise DtaError("Network.addNode called on node with id %d already in the network (for a centroid)" % newNode.id)

        self._nodes[newNode.id] = newNode

    def getNodeForId(self, nodeId):
        """
        Accessor for node given the nodeId.  Looks at nodes, virtual nodes and centroids.
        Returns None if not found.
        """
        if nodeId in self._nodes:
            return self._nodes[nodeId]
        if nodeId in self._centroids:
            return self._centroids[nodeId]
        return None
    
    def addCentroid(self, newCentroid):
        """
        Verifies that *newCentroid* is a Centroid and that the id is not already used;
        stores it.
        """
        if not isinstance(newCentroid, Centroid):
            raise DtaError("Network.addCentroid called on a non-Centroid: %s" % str(newCentroid))

        if newCentroid.id in self._nodes:
            raise DtaError("Network.addCentroid called on node with id %d already in the network (for a node)" % newNode.id)

        if newCentroid.id in self._centroids:
            raise DtaError("Network.addCentroid called on node with id %d already in the network (for a centroid)" % newNode.id)
        
        self._centroids[newCentroid.id] = newCentroid

    def addLink(self, newLink):
        """
        Verifies that the *newLink* is a Link and that the id is not already used; stores it.
        """ 

        if not isinstance(newLink, Link):
            raise DtaError("Network.addLink called on a non-Link: %s" % str(newLink))

        if newLink.id in self._links:
            raise DtaError("Link with id %s already exists in the network" % newLink.id)
        
        self._links[newLink.id] = newLink
        