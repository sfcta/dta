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

class Link:
    """
    Base class that represents a link in a network.
    """
    
    def __init__(self, id, nodeA, nodeB, label):
        """
        Constructor.
        
         * *id* is a unique identifier (unique within the containing network), an integer
         * *nodeA*, *nodeB* are Nodes
         * *label* is a string, or None 
        """
        
        self.id    = id     # integer id
        self.label = label
        
        if not isinstance(nodeA, Node):
            raise DtaError("Initializing Link with non-Node A: %s" % str(nodeA))
        
        if not isinstance(nodeB, Node):
            raise DtaError("Initializing Link with non-Node A: %s" % str(nodeA))

        self.nodeA = nodeA  # a Node instance
        self.nodeB = nodeB  # a Node instance
        
        self.nodeA.addOutgoingLink(self)
        self.nodeB.addIncomingLink(self)
            
    def euclideanLength(self):
        """
        Calculates the length based on simple Euclidean distance.
        """
        return math.sqrt( ((self.nodeA.x-self.nodeB.x)*(self.nodeA.x-self.nodeB.x)) +
                          ((self.nodeA.y-self.nodeB.y)*(self.nodeA.y-self.nodeB.y)) )