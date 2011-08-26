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
from .Node import Node

class Link(object):
    """
    Base class that represents a link in a network.
    """
    
    #: Default label is an empty string
    DEFAULT_LABEL = ""
    
    def __init__(self, id_, startNode, endNode, label):
        """
        Constructor.
        
         * *id* is a unique identifier (unique within the containing network), an integer, or None
         * *startNode*, *endNode* are Nodes
         * *label* is a string. If None passed, will use default.
         
        """ 
        self._id    = id_     # integer id
        if label:   
            self._label = label
        else:
            self._label = Link.DEFAULT_LABEL
        
        if not isinstance(startNode, Node):
            raise DtaError("Initializing Link with non-Node startNode: %s" % str(startNode))
        
        if not isinstance(endNode, Node):
            raise DtaError("Initializing Link with non-Node endNode: %s" % str(endNode))

        #: a Node instance
        self._startNode = startNode
        #: a Node instance
        self._endNode   = endNode
                
    def getStartNode(self):
        """
        Accessor for startNode
        """
        return self._startNode
    
    def getEndNode(self):
        """
        Accessor for endNode
        """
        return self._endNode
    
    def euclideanLength(self):
        """
        Calculates the length based on simple Euclidean distance.
        """
        return math.sqrt( ((self._startNode.getX()-self._endNode.getX())*(self._startNode.getX()-self._endNode.getX())) +
                          ((self._startNode.getY()-self._endNode.getY())*(self._startNode.getY()-self._endNode.getY())) )
        
    def getReferenceAngle(self):
        """
        Visualizing the link as a straight vector from (0,0), returns the angle between <1,0> and this link.
        
        So returns a number in [0,2pi), increasing clockwise.
        
        These are based on the euclidean length of the link, so assumes a straight line.  If the link has no length,
        returns 0.
        
        """
        if self.euclideanLength() == 0: return 0
        
        angle = math.acos( (self._endNode.getX() - self._startNode.getX()) / self.euclideanLength() )
        # angle is in [0, pi]
        if angle > 0 and self._endNode.getY() > self._startNode.getY():
            angle = 2.0*math.pi - angle
        return angle
        
    def getOtherEnd(self, node):
        """
        Return the other end node than the one provided.
        """
        if self._startNode == node:
            return self._endNode
        elif self._endNode == node:
            return self._startNode 
        else:
            raise DtaError("Link %d does not have end node %d" % (Link.getId(),
                                                                      node.getId()))

    def getId(self):
        """
        Return the link id
        """
        return self._id


    def getOrientation(self):
        """Returs the orientation of the link in degrees from the North
        measured clockwise. Only the endpoints are used in the calculation"""

        x1 = self.startVertex.x
        y1 = self.startVertex.y
        x2 = self.endVertex.x
        y2 = self.endVertex.y

        orientation = 0
        if x2 > x1 and y2 <= y1:   # 2nd quarter
            orientation = math.atan(fabs(y2-y1)/fabs(x2-x1)) + pi/2
        elif x2 <= x1 and y2 < y1:   # 3th quarter
            orientation = math.atan(fabs(x2-x1)/fabs(y2-y1)) + pi
        elif x2 < x1 and y2 >= y1:  # 4nd quarter 
            orientation = math.atan(fabs(y2-y1)/fabs(x2-x1)) + 3 * pi/2
        elif x2 >= x1 and y2 > y1:  # 1st quarter
            orientation = math.atan(fabs(x2-x1)/fabs(y2-y1))
        else:
            orientation = 0.0

        return orientation * 180.0 / pi

    def getMinAngle(self, node1, edge1, node2, edge2):
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

    def getAcuteAngle(self, other):
        """
        Return the acute angle (0, 180) between this link and the input one.
        Both links are considered as line segments from start to finish (shapepoints 
        are not taken into account).
        """

        if self == other:
            return 0

        if self.getStartNode() == other.getEndNode() and \
                self.getEndNode() == other.getStartNode():
            return 180 

        if self.getStartNode() == other.getStartNode():
            p0 = self.getEndNode()
            p1 = self.getStartNode()
            p2 = other.getEndNode() 
        elif self.getEndNode() == other.getEndNode():
            p0 = self.getStartNode()
            p1 = self.getEndNode()
            p2 = other.getStartNode()
        elif self.getEndNode() == other.getStartNode():
            p0 = self.getStartNode()
            p1 = self.getEndNode()
            p2 = other.getEndNode()
        elif self.getStartNode() == other.getEndNode():
            p0 = self.getEndNode()
            p1 = self.getStartNode()
            p2 = other.getStartNode() 
        
        dx1 = p0.getX() - p1.getX()
        dy1 = p0.getY() - p1.getY()
        dx2 = p2.getX() - p1.getX()
        dy2 = p2.getY() - p1.getY()

        length1 = math.sqrt(dx1 ** 2 + dy1 ** 2)
        length2 = math.sqrt(dx2 ** 2 + dy2 ** 2)

        if length1 == 0:
            raise DtaError("The length of link %d cannot not be zero" % self.getId())
        if length2 == 0:
            raise DtaError("The length of link %d cannot not be zero" % other.getId())

        return abs(math.acos((dx1 * dx2 + dy1 * dy2) / (length1 * length2))) / math.pi * 180.0
