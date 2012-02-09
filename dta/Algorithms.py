"""

Algorithms for use throughout DTA Anyway

"""

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

import sys
import pdb 
import math 

from dta.Utils import isRightTurn, lineSegmentsCross
from itertools import izip, tee, cycle, ifilter, ifilterfalse

def all2(seq, pred=None):
    "Returns True if pred(x) is true for every element in the iterable"
    for elem in ifilterfalse(pred, seq):
        return False
    return True

def any2(seq, pred=None):
    "Returns True if pred(x) is true for at least one element in the iterable"
    for elem in ifilter(pred, seq):
        return True
    return False

def pairwise(iterable):
    
    a, b = tee(iterable)
    b = cycle(b) 
    b.next()
    return izip(a, b)
    
def dfs(net, root=None):
    """
    Non-Recursive depth first search algorithm with 
    pre and post orderings. At the end of the execution
    all nodes in the network have a pre and post numbers
    and predecessor nodes assigned to them.
    """
    
    time = 0
    for node in net.iterNodes():
        node.pre = 0
        node.post = 0
        node.pred = None
        node.visited = False 

    allNodes = [node for node in net.iterNodes()]
    if root:
        allNodes.remove(root)
        allNodes.insert(0, root)

    nodesToExamine = []

    for node in allNodes:
        
        if node.pre == 0:
            nodesToExamine.append(node)

        while nodesToExamine:        
            pivot = nodesToExamine[-1]
            if pivot.visited == False:            
                for downNode in pivot.iterDownstreamNodes():                
                    if downNode.visited == False:                    
                        nodesToExamine.append(downNode)
                        downNode.pred = pivot 
                pivot.visited = True
                time += 1
                pivot.pre = time 
            elif pivot.post > 0:
                nodesToExamine.pop() 
            else:
                time += 1
                pivot.post = time

def getMetaGraph(net):
    """
    Return a network that represents the meta graph of the input network. 
    At the end of the execution of this algorithm each node points to 
    its metanode
    """
    pass 


def hasPath(net, originNode, destNode):
    """
    Return true if the network has a path 
    from the origin node to the destination node
    """
    
    dfs(net, originNode) 

    node = destNode
    while node and node != originNode:
        node = node.pred 

    if node is None:
        return False
    return True

def predicate(elem1, elem2):
    """
    Compare the two input elements and return a positive 
    integer if elem2 is greater than elem1. If the first
    two coordinates of the input elments are the 
    comparisson is made using the second ones
    >>> elem1 = (1,4)
    >>> elem2 = (1,3) 
    >>> predicate(elem1, elem2)
    >>> -1    
    """ 
    if elem1[0] == elem2[0]:                
        if elem1[1] < elem2[1]:
            return -1 
        elif elem1[1] == elem2[1]:
            return 0
        else:
            return 1
    else:
        if elem1[0] < elem2[0]:
            return -1
        else:
            return 1

def nodesInLexicographicOrder(node1, node2):
    """
    Compare the two input elements and return a positive 
    integer if node2 is greater than node1. If the first
    two coordinates of the input elments are the 
    comparisson is made using the second ones
    >>> node1 = (1,4)
    >>> node2 = (1,3) 
    >>> predicate(node1, node2)
    >>> -1    
    """ 
    if node1.getX() == node2.getX():                
        if node1.getY() < node2.getY():
            return -1 
        elif node1.getY() == node2.getY():
            return 0
        else:
            return 1
    else:
        if node1.getX() < node2.getX():
            return -1
        else:
            return 1

def getTightHull(setOfPoints, step):
    """
    Return the points and and their corresponding 
    indices with the highest y values in each of 
    the intervals identified by the input step
    """
    points = sorted(setOfPoints, cmp=predicate)    

    hull = []
    hullIndices = []
    hull.append(points[0])
    i = 1

    maxY = -sys.maxint 
    pivotIndex = 0
    threshold = points[0][0] + step

    while i < len(points):
        #print i, points[i], threshold 
        while points[i][0] <= threshold:

            if i >= len(points) - 1:
                i += 1
                break 
            if points[i][1] > maxY:
                maxY = points[i][1]
                pivotIndex = i
            i += 1

        if pivotIndex == 0:
            threshold += step 
        else:
            threshold += step
            hull.append(points[pivotIndex])
            hullIndices.append(pivotIndex)
            maxY = - sys.maxint 
            pivotIndex = 0
                        

    return hull, hullIndices         

def getConvexHull3(points, step):
    """
    Modifield implementation of Graham's algorithm.
    The resulting polygon is no longer convex but will
    still contain all the given points. 
    """
    hull, hullIndices = getTightHull(points, step)

    bigHull = []
    for i, j in izip(hullIndices, hullIndices[1:]):
        
        #print i, j
       # print points[i:j+1]
        partialHull = getHull(points[i:j+1])
        partialHull.pop()
        bigHull.extend(partialHull)
    

    return bigHull

def getHull(points, upper=True):
    """
    Return the convex hull of the given points 
    """ 
    hull = []
    if upper:
        hull.append(points[0])
        hull.append(points[1])
        sequenceOfPoints = range(3, len(points))
        
    else:
        hull.append(points[-1])
        hull.append(points[-2])
        sequenceOfPoints = range(len(points) - 3, -1, -1)

    for i in sequenceOfPoints:
        hull.append(points[i])
        while len(hull) > 2 and not isRightTurn(hull[-3], hull[-2], hull[-1]):
            hull.pop(len(hull) - 2)

    return hull

def getSmallestPolygonContainingNetwork(network):
    """
    treat all the links as bidirectional
    """

    nodes = list(net.iterRoadNodes())
    sorted(nodes, nodesInLexicographicOrder)
    
    #make a direct copy of the network
    #add the opposing links if they do not exist
    #add all the movements

    #find the left most node
    #if the leftmost node does not have any incoming or outgoing links then
    #move to the next one
    #by making the links bydirectional you are also making the network connected
    #if you remove the connectors you are also removing the external links 

    




    
    


    
    

    
    
    

def getConvexHull2(setOfPoints):
    """
    Refactored Graham's scan algorithm
    """
    points = sorted(setOfPoints, cmp=predicate)
    upperHull = getHull(points, upper=True)
    lowerHull = getHull(points, upper=False)
    upperHull.extend(lowerHull[1:-1])
    return upperHull
        
def getConvexHull(setOfPoints):
    """
    Implementation of Graham's scan algorithm
    """
    points = sorted(setOfPoints, cmp=predicate)

    upper = []
    upper.append(points[0])
    upper.append(points[1])
    
    for i in range(3, len(points)):        
        upper.append(points[i])
        while len(upper) > 2 and not isRightTurn(upper[-3], upper[-2], upper[-1]):
            upper.pop(len(upper) - 2)

    lower = []
    lower.append(points[-1])
    lower.append(points[-2])

    for i in range(len(points) - 3, -1, -1):

        lower.append(points[i])
        while len(lower) > 2 and not isRightTurn(lower[-3], lower[-2], lower[-1]):
            lower.pop(len(lower) - 2)

    lower.pop(0)
    lower.pop(len(lower) -1) 

    upper.extend(lower)
    return upper 

def isPointInPolygon(point, polygon):
    """
    Returns true if the point is inside the polygon 
    Point should be a (x,y) tuple or list
    Polygon is a list of points in clockwise order
    """

    x, y = point
    p1 = [0, y]
    p2 = [x, y]
    
    numIntersections = 0
    for polyPoint1, polyPoint2 in pairwise(polygon):        
        if lineSegmentsCross(p1, p2, polyPoint1, polyPoint2, checkBoundaryConditions=True):
            numIntersections += 1

    if numIntersections == 0:
        return False
    elif numIntersections % 2 == 0:
        return False
    return True 
            
def getClosestNode(net, inputNode):
    """
    Return the closest node in the input network
    """
    minDist = sys.maxint 
    closestNode = None
    for node in net.iterNodes():
        dist = (node.getX() - inputNode.getX()) ** 2 + (node.getY() - inputNode.getY()) ** 2
        if dist < minDist:
            minDist = dist 
            closestNode = node 

    return closestNode, math.sqrt(minDist) 
