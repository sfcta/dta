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

from .DtaError import DtaError

class PhaseMovement(object):

    CUSTOM = 0
    PROTECTED = 1
    PERMITTED = 2
        
    def __init__(self, movement, capacityTag):

        self._movement = movement
        assert capacityTag in [PhaseMovement.PROTECTED, PhaseMovement.PERMITTED] 
        self._capacityTag = capacityTag

    def __repr__(self):
        """Return the standard string representaton of the phase 
        movement"""
        return "%s %s %d" % (self.getIncomingLink().getId(), self.getOutgoingLink().getId(), 
                             self._capacityTag)

    def __str__(self):
        """Return the standard string representaton of the phase 
        movement"""
        return self.__repr__()

    def getIncomingLink(self):
        """
        Returns the incomingLink, a :py:class:`Link` instance
        """
        return self._movement._incomingLink    
    
    def getOutgoingLink(self):
        """
        Returns the outgoung, a :py:class:`Link` instance
        """
        return self._movement._outgoingLink
    
    def getAtNode(self):
        """
        Returns the node at which the movement is happening
        """
        return self._movement._node  
    
    def getStartNode(self):
        """
        Returns the start node of incomingLink, a :py:class:`Link` instance
        """
        return self._movement._incomingLink.getStartNode()
    
    def getEndNode(self):
        """
        Returns the end node of outgoingLink, a :py:class:`Link` instance
        """        
        return self._movement._outgoingLink.getEndNode()

    def getMovement(self):
        """
        Return the underlying movememnt of the phase movement
        """
        return self._movement

    def isPermitted(self):
        """
        Return True if the movement is permitted otherwise False
        """
        return self._capacityTag == PhaseMovement.PERMITTED

    def setProtected(self):
        """
        Set the movement as protected
        """
        self._capacityTag = PhaseMovement.PROTECTED

    def setPermitted(self):
        """
        Set the movement as permitted
        """
        self._capacityTag = PhaseMovement.PERMITTED
    
    def __eq__(self, other):
        """
        implementation of the == operator
        """
        if self._movement == other._movement and \
                self._capacityTag == other._capacityTag:
            return True
        return False

    def getStartNodeId(self):
        """
        Returns the start node of incomingLink, a :py:class:`Link` instance
        """
        return self._movement._incomingLink.getStartNodeId()
    
    def getEndNodeId(self):
        """
        Returns the end node of outgoingLink, a :py:class:`Link` instance
        """        
        return self._movement._outgoingLink.getEndNodeId()
