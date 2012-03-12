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

import pdb

from .Phase import Phase
from .DtaError import DtaError 
from .Utils import Time


__all__ = ["PlanCollectionInfo", "TimePlan"]

class PlanCollectionInfo(object):
    """
    Contains user information for a collection of signals belonging to the
    same time period
    """
    
    def __init__(self, startTime, endTime, name, description):
        """
        A PlanCollectionInfo object represents the timeplans for a particular time period
        The inputs to the constructor are the start and end times as datetime.time objects
        and the name and description of the timeplans
        """
        assert isinstance(startTime, Time)
        assert isinstance(endTime, Time)
        self._startTime = startTime
        self._endTime = endTime
        self._name = name
        self._description = description

    def __str__(self):
        """
        Return the string representing the plan collection
        """            
        return self.__repr__()

    def __repr__(self):
        """
        Return the string representing the plan collection
        """
        #<DYNAMEQ>\n<VERSION_1.5>\n<CONTROL_PLANS_FILE>\n* %s\n
        return ("PLAN_INFO\n%s %s\n%s\n%s" %  
                (self._startTime.strftime("%H:%M"), 
                 self._endTime.strftime("%H:%M"),
                 self._name, self._description))
                    
    def getTimePeriod(self):
        """
        Return a tuple representing the time period
        of the plan collection
        """
        return self._startTime, self._endTime

class TimePlan(object):
    """
    Represents a Dynameq timeplan
    
    .. todo:: Dynameq, eh?  What about just DTA?  And the Dynameq subclass?  And a holistic description
              of what a "time plan" is, anyhow?  (No it's not obvious.)

    """

    CONTROL_TYPE_CONSTANT = 0
    CONTROL_TYPE_PRETIMED = 1
    
    TURN_ON_RED_YES = 1
    TURN_ON_RED_NO = 0

    @classmethod
    def read(cls, net, fileName):
        """
        This method reads the time plans contained in the fileName
        file and adds them to the Dynameq Network object
        """

        try:
            lineIter = open(fileName, "r")
            while not lineIter.next().strip().startswith("PLAN_INFO"):
                continue
            currentLine = lineIter.next().strip()
 
            militaryStartStr, militaryEndStr = currentLine.split()
            
            startTime = Time.readFromString(militaryStartStr)
            endTime = Time.readFromString(militaryEndStr) 

            name = lineIter.next().strip()
            description = ""
            currentLine = lineIter.next()
            while not currentLine.startswith("NODE"):
                description += currentLine
                currentLine = lineIter.next()

            if not net.hasPlanCollectionInfo(startTime, endTime):                
                planCollectionInfo = net.addPlanCollectionInfo(startTime, endTime,
                                                    name, description)
            else:
                planCollectionInfo = net.getPlanCollectionInfo(startTime, endTime)
                                                                                         
            while True:
                currentLine = lineIter.next().strip()
                if currentLine == "":
                    raise StopIteration
                nodeId = int(currentLine)
                node = net.getNodeForId(nodeId)
                lineIter.next() # PLAN keyword
                type_, offset, sync, tor = map(int, lineIter.next().strip().split())
                
                timePlan = TimePlan(node, offset, planCollectionInfo, 
                                    syncPhase=sync, 
                                    turnOnRed=tor)
                                     
                for phase in Phase.read(net, timePlan, lineIter):
                    timePlan.addPhase(phase)
                yield timePlan
        except StopIteration:
            lineIter.close()
                    
    def __init__(self, node, offset, planCollectionInfo,
                 syncPhase=1, turnOnRed=TURN_ON_RED_YES):
        """
        Constructor.
        
        .. todo:: Documentation?
        """
        self._node = node
        self._planCollectionInfo = planCollectionInfo
        self._type = TimePlan.CONTROL_TYPE_PRETIMED
        self._offset = offset
        self._syncPhase = syncPhase
        self._turnOnRed = turnOnRed

        self._phases = []

    def __repr__(self):
        """
        Return a Dynameq parsable string that represents the time plan
        """
        nodeInfo = "NODE\n%s\n" % self.getNode().getId()
        planInfo = "PLAN\n%d %d %d %d\n" % (self._type, self._offset, self._syncPhase, self._turnOnRed)
        phases = "\n".join([repr(phase) for phase in self.iterPhases()])
        return "%s%s%s\n" % (nodeInfo, planInfo, phases)

    def __str__(self):
        """
        Return a Dynameq parsable string that represents the time plan
        """        
        return self.__repr__()

    def addPhase(self, phase):
        """
        Add the input phase instance to the timeplan's phases
        """
        assert isinstance(phase, Phase)
        self._phases.append(phase)

    def iterPhases(self):
        """
        Return an iterator to the phases in the timeplan
        """
        return iter(self._phases)

    def isValid(self):
         """
         Return True if the plan is valid otherwise return false
         """
         try:
             self.validate()
             return True
         except DtaError:
             return False

    def getNodeId(self):
        """
        Return the id of the node the timeplan applies
        """
        return self._node.id

    def getOffset(self):
        """
        Return the offset
        """
        return self._offset

    def getNumPhases(self):
        """
        Return the number of phases
        """
        return len(self._phases)

    def getNode(self):
        """
        Return the node the timeplan applies
        """
        return self._node

    def getPhase(self, phaseNum):
        """
        Return the phase with the given index
        """
        if phaseNum <= 0 or phaseNum > self.getNumPhases():
            return DtaError("Timeplan for node %s does not have a phase "
                                 "with index %d" % (self._node.id, phaseNum))
        return self._phases[phaseNum - 1]

    def getCycleLength(self):
        """
        Return the cycle length in seconds
        """
        return sum([phase._green + phase._yellow + phase._red for phase in self.iterPhases()])

    def getPlanInfo(self):
        """
        Return the plan info associated with this time plan, an instance of :py:class:`PlanCollectionInfo`.
        """
        return self._planCollectionInfo

    def setSyncPhase(self, syncPhase):
        """
        Set the syncing phase to the input value
        """
        if syncPhase <= 0:
            raise DtaError("Node %s. The sync phase %d cannot be less than 1 or greater than "
                               "the number of phases %d" % (self.getNodeId(), syncPhase, self.getNumPhases()))
        self._syncPhase = syncPhase 

    def validate(self):
        """
        Make the following checks to the timeplan. If any of them fails raise an error
        1. Sync Phase is a valid phase
        2. Number of phases is equal or greater than two
        3. The number of movements each phase has should be greater than zero
        4. The phase movements are exactly the same with the node movements:
               there is no node movement that is not served by a phase and there is
               not a phase movement that does not exist in the node. 
        5. If two movements conflict with each other then one of them is permitted and the other is protected
        """
        if self._offset < 0:
            raise DtaError("Node %s. The offset cannot be less than 0" % self.getNode().getId())
                   
        if self._syncPhase <= 0 or self._syncPhase > self.getNumPhases():
            raise DtaError("Node %s. The sync phase %d cannot be less than 1 or greater than "
                               "the number of phases %d" % (self.getNodeId(), self._syncPhase, self.getNumPhases()))
            
        if self.getNumPhases() < 2:
            raise DtaError("Node %s has a timeplan with less than 2 phases" % self._node.getId())

        for phase in self.iterPhases():
            if phase.getNumMovements() < 1:
                raise DtaError("Node %s The number of movements in a phase "
                                    "cannot be less than one" % self._node.getId())

        phaseMovements = set([mov.getId() for phase in self.iterPhases() 
                                for mov in phase.iterMovements()]) 

        #if right turns on red add the right turns 
        if self._turnOnRed == TimePlan.TURN_ON_RED_YES:
            for mov in self._node.iterMovements():
                if mov.isRightTurn():
                    phaseMovements.add(mov.getId())

        nodeMovements = set([mov.getId() for mov in self._node.iterMovements()])
        if phaseMovements != nodeMovements:
            nodeMovsNotInPhaseMovs = nodeMovements.difference(phaseMovements)
            phaseMovsNotInNodeMovs = phaseMovements.difference(nodeMovements)
            raise DtaError("Node %s. The phase movements are not the same with node movements."
                                "\tNode movements missing from the phase movements: \t%s"
                                "\tPhase movements not registered as node movements: \t%s" % 
                                (self.getNode().getId(), "\t".join(map(str, nodeMovsNotInPhaseMovs)),
                                 "\t".join(map(str, phaseMovsNotInNodeMovs))))
        
       #check that if two conflicting movements exist one of them is permitted or right turn
        for phase in self.iterPhases():
            for mov1 in phase.iterMovements():
                for mov2 in phase.iterMovements():
                   if mov1.getId() == mov2.getId():
                       continue
                   if not mov1.isInConflict(mov2):
                       continue
                   if mov1.isProtected() and mov2.isProtected():
                       if mov1.isRightTurn() or mov2.isRightTurn():
                           continue
                       raise DtaError("Movements %s, %s and %s, %s are in coflict and are both protected " %  (mov1.getId(), mov1.getTurnType(), mov2.getId(), mov2.getTurnType()))  
                                       

        #does it make sense to check there is no case where you have 3 simulataneous conflicting movements
        #permitted or protected? Probably
                               
    def setPermittedMovements(self):
        """
        Goes over the movements of the phase. If two protected movements
        conflict with each other it sets the one with the fewer number of
        lanes as a permitted one unless if both movements are
        through movmeents. In this case it raises an error. 
        """
        for phase in self.iterPhases():
            for mov1 in phase.iterMovements():
                for mov2 in phase.iterMovements():
                   if mov1.getId() == mov2.getId():
                       continue
                   if not mov1.isInConflict(mov2):
                       continue
                   if mov1.isThruTurn() and mov2.isThruTurn():                       
                       message =  ("Movements %s and %s are in coflict and are both protected "
                                   " and thru movements" %
                                   (mov1.getId(), mov2.getId()))
                       print message
                   else:
                       if mov1.isLeftTurn():
                           if mov2.isThruTurn():
                               mov1.setPermitted()
                           elif mov2.isRightTurn():
                               mov1.setPermitted()
                           elif mov2.isLeftTurn():
                               mov2.setPermitted()

