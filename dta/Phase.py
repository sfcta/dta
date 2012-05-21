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

class Phase(object):
    """
    Represents a generic phase class that can contain one or more 
    :py:class:`PhaseMovement' objects. 
    """
    
    TYPE_CUSTOM = 1
    TYPE_STANDARD = 0

    @classmethod
    def readFromDynameqString(self, net, timeplan, lineIter):
        """Parses the dynameq phase string defined in multiple lines of text and returns a
        Dynameq phase object. 
        lineIter is an iterator over the lines of a text file containing the Dynameq phase info. 
        net is an instance of :py:class:`DynameqNetwork'
        timePlan is an instance of :py:class:`TimePlan'
        """         
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

    def __init__(self, timePlan, green, yellow, red, phaseType=TYPE_STANDARD):
        """
        Constructor. 
        :py:class:`TimePlan' is the timeplan instance the phase
        green, red, and yellow are the green, yellow, and red times respectively (int or float) 
        """
        self._timePlan = timePlan
        self._node = timePlan.getNode()
        self._green = green
        self._yellow = yellow
        self._red = red
        self._phaseType = phaseType

        self._movements= []

    def getDynameqStr(self):
        """
        Return the dynameq representation of the phase as a string
        """
        if int(self._green) == self._green:
            green = str(int(self._green))
        else:
            green = str(self._green)

        if int(self._yellow) == self._yellow:
            yellow = str(int(self._yellow))
        else:
            yellow = str(self._yellow)

        if int(self._red) == self._red:
            red = str(int(self._red))
        else:
            red = str(self._red)
                    
        header = "PHASE\n%s %s %s %d" % (green, yellow, red, self._phaseType)
        body = "\n".join([repr(mov) for mov in self.iterMovements()]) 
        return "%s\n%s" % (header, body)

    def addMovement(self, movement):
        """
        Add the input movement to the phase. If the movement
        allready exists and exception will be thrown
        """
        if not self.getTimePlan().getNode().hasMovement(movement.getStartNode().getId(),
                                          movement.getEndNode().getId()):
            raise DtaError("Movement %s is not does not belong to node %d" % (movement.getId(),
                                                                                   movement.getAtNode().getId()))
        if self.hasMovement(movement.getStartNodeId(), 
                            movement.getEndNodeId()):
            raise DtaError("Movement %s already belongs to this phase" % movement.getId())
        
        self._movements.append(movement)
    
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
        """
        Return an iterator the the phase movements
        """
        return iter(self._movements)

    def getGreen(self):
        """
        Return the green time as an integer or float 
        """
        return self._green

    def getYellow(self):
        """
        Return the yellow time as an integer or float 
        """
        return self._yellow

    def getRed(self):
        """
        Return the red time as an integer or float 
        """
        return self._red 
