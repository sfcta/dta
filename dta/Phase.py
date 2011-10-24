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

from .PhaseMovement import PhaseMovement
from .DtaError import DtaError 

import nose.tools

class Phase(object):
    """Represents a dynameq phase"""
    
    TYPE_CUSTOM = 1
    TYPE_STANDARD = 0

    @classmethod
    def read(self, net, timeplan, lineIter):
        """read a phase string from the line iterator and return a Phase instance"""

        endOfFile = True
        try:
            currentLine = lineIter.next().strip() 
            while not currentLine.startswith("PLAN_INFO") \
                    and not currentLine.startswith("NODE"):

                assert currentLine.startswith("PHASE")
                endOfFile = True
                currentLine = lineIter.next().strip()                 
                green, yellow, red, phaseType = map(float, currentLine.split())
                phaseType = int(phaseType)
                phase = Phase(timeplan, green, yellow, red, phaseType)
                currentLine = lineIter.next().strip()

                while not currentLine.startswith("PHASE") and \
                        not currentLine.startswith("PLAN_INFO") and \
                        not currentLine.startswith("NODE"):
                    
                    if currentLine.strip() == "":
                        raise StopIteration
                    fields = currentLine.split()
                    inLinkId, outLinkId, capacityTag = map(int, fields)
                    capacityTag = int(capacityTag) 
                    inLink = net.getLinkForId(inLinkId) 
                    outLink = net.getLinkForId(outLinkId) 
                    movement = inLink.getOutgoingMovement(outLink.getEndNodeId())
                    movement = PhaseMovement(movement, capacityTag)                     
                    try:
                        phase.addMovement(movement)
                    except DtaError, e:
                        print str(e)
                    currentLine = lineIter.next().strip()
                yield phase
            endOfFile = False
            raise StopIteration
        except StopIteration:
            if endOfFile:
                yield phase
            raise StopIteration

    def __init__(self, timePlan, green, yellow, red, phaseType):
        
        self._timePlan = timePlan
        self._node = timePlan.getNode()
        self._green = green
        self._yellow = yellow
        self._red = red
        self._phaseType = phaseType

        self._movements= []

    def __repr__(self):
        """
        Return the string representation of the phase
        """
        header = "PHASE\n%.1f %.1f %.1f %d" % (self._green, self._yellow, self._red, self._phaseType)
        body = "\n".join([repr(mov) for mov in self.iterMovements()]) 
        return "%s\n%s" % (header, body)

    def __str__(self):
        """
        Return the string represtation of the phase
        """
        return self.__str__()

    def addMovement(self, movement):
        
        if not self.getTimePlan().getNode().hasMovement(movement.getStartNode().getId(),
                                          movement.getEndNode().getId()):
            raise DtaError("Movement %s is not does not belong to node node %d" % (movement.getIid(),
                                                                                   self.getAtNode().getId()))
        if self.hasMovement(movement.getStartNodeId(), 
                            movement.getEndNodeId()):
            raise DtaError("Movement %s already belongs to this phase" % movement.getIid())
        
        self._movements.append(movement)
    
    def deleteMovement(self, ):
        """Add the movement with the provided iid to the list of movements 
        served by the phase"""

        if not self.hasMovement(movementIid):
            raise DtaError("Movement to be deleted %s does not belog to the "
                             "phase" % str(movementIid))

        if self.getNumMovements() == 1:
            raise DtaError('I cannot delete a phase with only one movement. '
                             'Please delete the phase')
        movement = self.getMovement(movementIid)
        self._movements.pop(self._movements.index(movement))

    def getTimePlan(self):
        """
        Return the timeplan associated with this phase
        """
        return self._timePlan

    def getNumMovements(self):
        """
        Return the number of movements in the phase
        """
        return len(self._movements)
                
    def getMovement(self, startNodeId, endNodeId):
        """
        Return the movement from startNodeId to endNodeId
        """
        for movement in self.iterMovements():
            if movement.getStartNodeId() == startNodeId and \
                    movement.getEndNodeId() == endNodeId:
                return movement
        raise DtaError("Movement from %d to %d does not exist" % (startNodeId, endNodeId))

    def hasMovement(self, startNodeId, endNodeId):
        """
        Return True if the phase has the movement with the given iid
        else false
        """
        try:
            self.getMovement(startNodeId, endNodeId)
            return True
        except DtaError, e:
            return False

    def hasProtectedMovement(self, startNodeId, endNodeId):
        """
        Return True if the phase has a protected movement from 
        input start node to end node
        """
        try:
            mov = self.getMovement(startNodeId, endNodeId)
            if mov.isProtected():
                return True
            return False
        except DtaError, e:
            return False 
        
    def hasPermittedMovement(self, startNodeId, endNodeId):
        """
        Return True if the phase has a permitted movement from 
        start node to end node
        """
        try:
            mov = self.getMovement(startNodeId, endNodeId)
            if mov.isPermitted():
                return True
            return False
        except DtaError, e:
            return False 
        
    def iterMovements(self):
        """Return an iterator the the phase movements"""
        return iter(self._movements)

