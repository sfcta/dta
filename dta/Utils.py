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
import copy  
import sys

import dta
import shapefile
from itertools import izip
from collections import defaultdict
import xml.etree.ElementTree as ET
from xml.dom.minidom import parseString

def writePoints(iterPoints, fileName):
    """
    Write the input points to a shapefile. Each point should be a tuple of (x, y) floats
    """
    w = shapefile.Writer(shapefile.POINT)
    w.field("ID", "N", 10) 
    i = 0
    for x,y in iterPoints:
        i += 1
        w.point(x,y)
        w.record(i)
    w.save(fileName)

def writePolygon(listOfPoints, fileName): 
    """
    Write the input points as a polygon. Each point should be a tuple of (x,y) coordinates
    """
    w = shapefile.Writer(shapefile.POLYGON)
    w.field("ID", "N", 10) 
    w.poly(parts=[listOfPoints])
    w.record(1) 
    w.save(fileName)

def isRightTurn(pi, pj, pk):
    
    if direction(pi, pj, pk) > 0:
        return True
    return False

def direction(point0, point1, point2):
    
    return crossProduct((point2[0] - point0[0], point2[1] - point0[1]),
                        (point1[0] - point0[0], point1[1] - point0[1])) 

def crossProduct(p1, p2):
    """Return the cross product of two points pl and pm 
    each of them defined as a tuple (x, y)
    """ 
    return p1[0]*p2[1] - p2[0]*p1[1]

def lineSegmentsCross(p1, p2, p3, p4, checkBoundryConditions=False):
    """
    Helper function that determines if line segments, 
    defined as a sequence of pairs 
    of points, (p1,p2) and (p3,p4) intersect. 
    If so it returns True, otherwise False. If the two 
    line segments touch each other the method will 
    return False.  
    """
    
    d1 = direction(p3, p4, p1)
    d2 = direction(p3, p4, p2)
    d3 = direction(p1, p2, p3)
    d4 = direction(p1, p2, p4) 

    if ((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) and \
            ((d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0)):
        return True
    if not checkBoundryConditions:
        return False
    if d1 == 0 and onSegment(p3, p4, p1):
        return True
    elif d2 == 0 and onSegment(p3, p4, p2):
        return True
    elif d3 == 0 and onSegment(p1, p2, p3):
        return True
    elif d4 == 0 and onSegment(p1, p2, p4):
        return True
    return False

def polylinesCross(polyline1, polyline2):
    """
    Return True if the two polylines cross.
    Each polyline is should be a list of two point tuples
    """
    for p1, p2 in izip(polyline1, polyline1[1:]):
        for p3, p4 in izip(polyline2, polyline2[1:]):
            if lineSegmentsCross(p1, p2, p3, p4):
                return True
    if lineSegmentsCross(polyline1[-2], polyline1[-1],
                         polyline2[-2], polyline2[-1],
                         checkBoundryConditions=True):
        return True
    return False
            
def onSegment(pi, pj, pk):
    """
    Determines whether point k known to be colinear with a segment pi pj
    segment lies inside segment pi pj. It does so by examining if
    point k is inside the boundary box of segment pi, pj
    """
    if min(pi[0], pj[0]) <= pk[0] <= max(pi[0], pj[0]) and \
            min(pi[1], pj[1]) <= pk[1] <= max(pi[1], pj[1]):
        return True
    return False
    
def getMidPoint(p1, p2):
    """
    Return the the point in the middle of p1 and p2 as a (x,y) tuple.
    """
    return ((p1[0] + p2[0]) / 2.0, (p1[1] + p2[1]) / 2.0)

def getReverseNetwork(net):
    """
    Returns a network copy that has all the links reversed
    """
    rNet = dta.Network(net.getScenario())

    for node in net.iterNodes():
        cNode = copy.copy(node) 
        cNode._incomingLinks = []
        cNode._outgoingLinks = []
        rNet.addNode(cNode)

    for link in net.iterLinks():
        rLink = dta.Link(link._id,
                     rNet.getNodeForId(link.getEndNode().getId()),
                     rNet.getNodeForId(link.getStartNode().getId()), 
                     "")                                       
        rNet.addLink(rLink)
        
    return rNet 

class MappingError(Exception):
    pass

class NetworkMapping(object):
    """
    Contains the node and link mappings of two network objects
    """
    def __init__(self, netOne, netTwo):
        """
        netOne and netTwo are the two network objects to be mapped
        """
        self._netOne = netOne
        self._netTwo = netTwo

        self._mapNodesOneToTwo = dict()
        self._mapNodesTwoToOne = dict() 
        self._mapLinksOneToTwo = defaultdict(dict)
        self._mapLinksTwoToOne = defaultdict(dict)

    def mapNodesById(self):
        """
        Map the nodes of the two objects based on node ids
        """
        for nodeOne in self._netOne.iterNodes():
            if self._netTwo.hasNodeForId(nodeOne.getId()):
                nodeTwo = self._netTwo.getNodeForId(nodeOne.getId())
                self.setMappedNode(nodeOne, nodeTwo)

    def mapLinksByOrientation(self, maxAngle):
        """
        Map the links based on the input maxAngle for all the
        pair of nodes that have already been mapped
        """
        def getMinAngle(node1, edge1, node2, edge2):
            """
            Returns a positive number in degrees always in [0, 180]
            that corresponds to the
            acute angle between the two edges
            """
            orientation1 = node1.getOrientation(edge1.getMidPoint())
            orientation2 = node2.getOrientation(edge2.getMidPoint())
            if orientation2 > orientation1:
                angle1 = orientation2 - orientation1
                angle2 = 360 - orientation2 + orientation1
                return min(angle1, angle2)
            elif orientation1 > orientation2:
                angle1 = orientation1 - orientation2 
                angle2 = 360 - orientation1 + orientation2
                return min(angle1, angle2)
            else:
                return 0
            
        for nodeOne, nodeTwo in self._mapNodesOneToTwo.iteritems():            
            #incoming edges
            edges2 = list(nodeTwo.iterIncomingEdges())
            for edge1 in nodeOne.iterIncomingEdges():
                #pick the closest
                if len(edges2) == 0:
                    break 
                edges2 = sorted(edges2, key = lambda edge2: getMinAngle(nodeOne, edge1, nodeTwo, edge2))
                closestEdge = edges2[0]

                if getMinAngle(nodeOne, edge1, nodeTwo, closestEdge) < maxAngle:
                    self.setMappedLink(nodeOne, edge1, nodeTwo, closestEdge)
                    edges2.pop(0)
                
            #outgoing edges
            edges2 = list(nodeTwo.iterOutgoingEdges())
            for edge1 in nodeOne.iterOutgoingEdges():
                if len(edges2) == 0:
                    break
                edges2 = sorted(edges2, key = lambda edge2: getMinAngle(nodeOne, edge1, nodeTwo, edge2))
                closestEdge = edges2[0]
                if getMinAngle(nodeOne, edge1, nodeTwo, closestEdge) < maxAngle:
                    self.setMappedLink(nodeOne, edge1, nodeTwo, closestEdge)
                    edges2.pop(0)
            
    def setMappedNode(self, nodeOne, nodeTwo):
        """
        Map the two input nodes to each other. A one to one mapping is
        being created for the two nodes.
        """
        if nodeOne in self._mapNodesOneToTwo:
            raise DtaError("Node one %s has already been mapped to a node"
                               % nodeOne.id)
        if nodeTwo in self._mapNodesTwoToOne:
            raise DtaError("Node two %s has already been mapped to a node"
                               % nodeTwo.id)
        
        self._mapNodesOneToTwo[nodeOne] = nodeTwo
        self._mapNodesTwoToOne[nodeTwo] = nodeOne
        #TODO: consider
        #self._mapLinksOneToTwo[nodeOne] = {}
            
    def getMappedNode(self, node):
        """
        Return the mapped node. If the input node is from networkOne the
        corresponding node from network two is being returned and vice
        versa 
        """        
        if isinstance(node, self._netOne.getNodeType()):
            if node not in self._mapNodesOneToTwo:
                raise DtaError("Node %s does not have a mapped node" % node.id)
            return self._mapNodesOneToTwo[node]            
        elif isinstance(node, self._netTwo.getNodeType()):
            if node not in self._mapNodesTwoToOne:
                raise DtaError("Node %s does not have a mapped node" % node.id)
            return self._mapNodesTwoToOne[node]
        else:
            raise DtaError("Node %s should belong to one of the mapped networks"
                               % node.id)
           
    def setMappedLink(self, nodeOne, linkOne, nodeTwo, linkTwo):
        """
        Map linkOne attached to nodeOne to linkTwo attached to nodeTwo
        """
        assert isinstance(nodeOne, self._netOne.getNodeType())
        assert isinstance(linkOne, self._netOne.getLinkType())

        assert isinstance(nodeTwo, self._netTwo.getNodeType())
        assert isinstance(linkTwo, self._netTwo.getLinkType())

        if nodeOne is not linkOne.startVertex and nodeOne is not linkOne.endVertex:
            raise DtaError("Node %s is not connected to link %s" %
                               (nodeOne.id, linkTwo.iid_))

        if nodeTwo is not linkTwo.startVertex and nodeTwo is not linkTwo.endVertex:
            raise DtaError("Node %s is not connected to link %s" %
                               (nodeTwo.id, linkTwo.iid_))
        
        if nodeOne not in self._mapNodesOneToTwo:
            raise DtaError("Node %s has not been mapped"
                               % nodeOne.id)
        
        if self._mapNodesOneToTwo[nodeOne] != nodeTwo:
            raise DtaError("Node %s is not mapped to node %s"
                               % nodeTwo.id) 
                                      
        if nodeOne in self._mapLinksOneToTwo and linkOne in self._mapLinksOneToTwo[nodeOne]:
            raise DtaError("Node %s and link %s have already been mapped" %
                               (nodeOne.id, linkOne.iid))

        if nodeTwo in self._mapLinksTwoToOne and linkTwo in self._mapLinksTwoToOne[nodeTwo]:
            raise DtaError("Node two %s and link two %s have already been mapped" %
                               (nodeTwo.id, linkTwo.iid))

        self._mapLinksOneToTwo[nodeOne][linkOne] = linkTwo
        #TODO: more error checks 
        self._mapLinksTwoToOne[nodeTwo][linkTwo] = linkOne

    def getMappedLink(self, node, link):

        if isinstance(node, self._netOne.getNodeType()) and \
           isinstance(link, self._netOne.getLinkType()):

            if node is not link.startVertex and node is not link.endVertex:
                raise DtaError("Node %s is not connected to link %s" %
                                   (node.id, linkTwo.iid_))        

            if node not in self._mapLinksOneToTwo or link not in self._mapLinksOneToTwo[node]:
                raise DtaError("Node %s and link %s have not been mapped" %
                                   (node.id, link.iid))

            return self._mapLinksOneToTwo[node][link]
        elif isinstance(node, self._netTwo.getNodeType()) and \
           isinstance(link, self._netTwo.getLinkType()):

            if node is not link.startVertex and node is not link.endVertex:
                raise DtaError("Node %s is not connected to link %s" %
                                   (node.id, linkTwo.iid_))        

            if node not in self._mapLinksTwoToOne or link not in self._mapLinksTwoToOne[node]:
                raise DtaError("Node %s and link %s have not been mapped" %
                                   (node.id, link.iid))

            return self._mapLinksTwoToOne[node][link]
        else:
            raise DtaError("Node %s and Link %s must belong to the same network"
                               % (node.id, link.iid_))

