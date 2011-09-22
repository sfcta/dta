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

import dta
import shapefile 

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

def onSegment(pi, pj, pk):
    """
    Determines whether a point known to be colinear with a segment lies on that
    segment
    """
    if min(pi[0], pj[0]) <= pk[0] <= min(pi[0], pj[0]) and \
            min(pi[1], pj[1]) <= pk[1] <= min(pi[1], pj[1]):
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


