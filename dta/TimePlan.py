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
import datetime
import time 

from .Phase import Phase
from .DtaError import DtaError 

class PlanCollectionInfo(object):
    """Contains user information for a collection of signals belonging to the
    same time period"""
    def __init__(self, militaryStartTime, militaryEndTime, name, description):
        self._startTime = militaryStartTime
        self._endTime = militaryEndTime
        self._name = name
        self._description = description

    def __str__(self):
        """Return the string representation of the oject"""
        return self.__repr__()

    def __repr__(self):
        """Return the parseable string representaton of the object"""
        #stInMin = getTimeInMin(self._startTime)
        #endInMin = getTimeInMin(self._endTime) 
        #startTime = getMilitaryTimeAsString(stInMin)
        #endTime = getMilitaryTimeAsString(endInMin) 

        return ("<DYNAMEQ>\n<VERSION_1.5>\n<CONTROL_PLANS_FILE>\n* %s\nPLAN_INFO\n%s %s\n%s\n%s" %  
                (time.ctime(), self._startTime.strftime("%H:%M"), 
                 self._endTime.strftime("%H:%M"),
                 self._name, self._description))
                    
    def getTimePeriod(self):
        return self._startTime, self._endTime

class TimePlan(object):
    """Represents a Dynameq timeplan"""

    CONTROL_TYPE_CONSTANT = 0
    CONTROL_TYPE_PRETIMED = 1
    
    TURN_ON_RED_YES = 1
    TURN_ON_RED_NO = 0

    @classmethod
    def read(cls, net, fileName):

        try:
            lineIter = open(fileName, "r")
            while not lineIter.next().strip().startswith("PLAN_INFO"):
                continue
            currentLine = lineIter.next().strip()
 
            militaryStartStr, militaryEndStr = currentLine.split()
            
            startTime = datetime.datetime.strptime(militaryStartStr, "%H:%M") 
            endTime = datetime.datetime.strptime(militaryEndStr, "%H:%M") 

            name = lineIter.next().strip()
            description = ""
            currentLine = lineIter.next()
            while not currentLine.startswith("NODE"):
                description += currentLine
                currentLine = lineIter.next()

            planCollectionInfo = PlanCollectionInfo(startTime, endTime,
                                                    name, description)
                        
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
                    
    #TODO if I enter TimePlan.TURN_ON_RED_YES in the constructor I get an error??????
    def __init__(self, node, offset, planCollectionInfo,
                 syncPhase=1, turnOnRed=1):

        self._node = node
        self._planCollectionInfo = planCollectionInfo
        self._type = TimePlan.CONTROL_TYPE_PRETIMED
        self._offset = offset
        self._syncPhase = syncPhase
        self._turnOnRed = turnOnRed

        self._phases = []

    def __repr__(self):

        nodeInfo = "NODE\n%s\n" % self.getNode().getId()
        planInfo = "PLAN\n%d %d %d %d\n" % (self._type, self._offset, self._syncPhase, self._turnOnRed)
        phases = "\n".join([repr(phase) for phase in self.iterPhases()])
        return "%s%s%s\n" % (nodeInfo, planInfo, phases)

    def __str__(self):
        
        return self.__repr__()

    def addPhase(self, phase):
        """Add the input phase instance to the timeplan's phases"""
        assert isinstance(phase, Phase)
        self._phases.append(phase)

    def iterPhases(self):
        """Return an iterator to the phases in the timeplan"""
        return iter(self._phases)

    def isValid(self):
         """Return True if the plan is valid otherwise return false"""
         try:
             self.validate()
             return True
         except DtaError:
             return False

    def getNodeId(self):
        """Return the id of the node the timeplan applies"""
        return self._node.id

    def getNumPhases(self):
        """Return the number of phases"""
        return len(self._phases)

    def getNode(self):
        """Return the node the timeplan applies"""
        return self._node

    def getPhase(self, phaseNum):
        """Return the phase with the given index"""
        if phaseNum <= 0 or phaseNum > self.getNumPhases():
            return DtaError("Timeplan for node %s does not have a phase "
                                 "with index %d" % (self._node.id, phaseNum))
        return self._phases[phaseNum - 1]

    def getCycleLength(self):
        """Return the cycle length in seconds"""
        return sum([phase.green + phase.yellow + phase.red for phase in self.iterPhases()])

    def getPlanInfo(self):
        """
        Return the plan info associated with this time plan
        """
        return self._planCollectionInfo

    def setSyncPhase(self, syncPhase):
        
        if syncPhase <= 0:
            raise DtaError("Node %s. The sync phase %d cannot be less than 1 or greater than "
                               "the number of phases %d" % (self.getNodeId(), syncPhase, self.getNumPhases()))
        self._syncPhase = syncPhase 

    def validate(self):
        """If the timeplan is not valide raise DtaError"""

        if self._syncPhase <= 0 or self._syncPhase > self.getNumPhases():
            raise DtaError("Node %s. The sync phase %d cannot be less than 1 or greater than "
                               "the number of phases %d" % (self.getNodeId(), self._syncPhase, self.getNumPhases()))
            

        if self.getNumPhases() < 2:
            raise DtaError("Node %s has a timeplan with less than 2 phases" % self._node.iid)

        for phase in self.iterPhases():
            if phase.getNumMovements() < 1:
                raise DtaError("Node %s The number of movements in a phase "
                                    "cannot be less than one" % self._node.iid)

        for phase in self.iterPhases():
            for movement in phase.iterMovements():
                if movement.isUTurn():
                    raise DtaError("Node %s. The movement %s is a UTurn and should not have been "
                                        "entered as a phase movement" % (self.getNode().iid, 
                                                                         str(movement.iid)))

        phaseMovements = set([mov.iid for phase in self.iterPhases() 
                                for mov in phase.iterMovements()]) 

        if self._turnOnRed == 1:
            for mov in self._node.iterMovements():
                if mov.isRightTurn():
                    phaseMovements.add(mov.iid)

        nodeMovements = set([mov.iid for mov in self._node.iterMovements() if not mov.isUTurn()])
        if phaseMovements != nodeMovements:
            nodeMovsNotInPhaseMovs = nodeMovements.difference(phaseMovements)
            phaseMovsNotInNodeMovs = phaseMovements.difference(nodeMovements)
            raise DtaError("Node %s. The phase movements are not the same with node movements."
                                "\nNode movements missing from the phase movements: \n\t%s"
                                "\nPhase movements not registered as node movements: \n\t%s" % 
                                (self.getNode().iid, "\n\t".join(map(str, nodeMovsNotInPhaseMovs)),
                                 "\n\t".join(map(str, phaseMovsNotInNodeMovs))))
        
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
                   print mov1.getId(), mov1.getTurnType(), mov2.getId(), mov2.getTurnType()
                   if mov1.isThruTurn() and mov2.isThruTurn():
                       pdb.set_trace()
                       raise DtaError("Movements %s and %s are in coflict and are both protected "
                                      " and thru movements" %
                                      (mov1.getId(), mov2.getId()))
                   else:
                       if mov1.isLeftTurn():
                           if mov2.isThruTurn():
                               mov1.setPermitted()
                           elif mov2.isRightTurn():
                               mov2.setPermitted()
                           elif mov2.isLeftTurn():
                               mov2.setPermitted()



                       #if mov1.getNumLanes() <= mov2.getNumLanes():                               
