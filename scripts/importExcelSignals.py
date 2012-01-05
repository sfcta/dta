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

#import json
import pdb

import csv 
import difflib
from collections import defaultdict
import os
import pickle
import re
import xlrd
from itertools import izip, chain
import logging
import datetime

from MultiArray import MultiArray

import dta
from dta.DynameqScenario import DynameqScenario
from dta.DynameqNetwork import DynameqNetwork
from dta.Algorithms import pairwise, any2, all2 
from dta.TimePlan import TimePlan, PlanCollectionInfo
from dta.Phase import Phase
from dta.PhaseMovement import PhaseMovement

logging.basicConfig(filename = "logParse.txt",\
                        level = logging.DEBUG, \
                        filemode= "w", \
                        format = " %(levelname)-10s %(asctime)s %(message)s")

class ExcelCardError(Exception):
    pass

class MovementMappingError(ExcelCardError):
    pass

class SignalConversionError(ExcelCardError):
    pass

class ParsingCardError(ExcelCardError):
    pass

class ExcelSignalTimingError(ParsingCardError):
    pass

class StreetNameMappingError(ExcelCardError):
    pass


GREEN = 0
YELLOW = 1
RED = 2

TURN_LEFT = ("LT", "LT2")
TURN_THRU = ("TH")
TURN_RIGHT = ("RT", "RT2")

class SignalData(object):

    attrNames = ["fileName", "iName", "topLeftCell", "phaseSeqCell", "pedPhaseCell",\
                              "sigInterCell", "colPhaseData", "lastColPhaseData"] \
                              + ["gMov%d" % i for i in range(1, 9)]
    streets = ["Street0", "Street1", "Street2", "Street3"]

    mappingInfo = ["IntersectionName(for mapping)", "mapped Intersection Name", "mapped Node id"]

    def __init__(self):        

        self.fileName = None
        self.iName = None
        self.iiName = ""
        self.topLeftCell = None
        self.phaseSeqCell = None
        self.pedPhaseCell = None
        self.sigInterCell = None
        self.colPhaseData = None
        self.lastColPhaseData = None
        self.streetNames = []
        self.mappedNodeName = ""
        self.mappedNodeId = ""
        self.mappedNode = None

        self.mappedStreet = {}
        self.mappedMovements = defaultdict(list)  #indexed by the keys of the mappedStreet 
        self.signalTiming = {} # singal timing objects indexed by cso
        
        self.error = None

        #the group movement names
        self.gMov1 = ""
        self.gMov2 = ""
        self.gMov3 = ""
        self.gMov4 = ""
        self.gMov5 = ""
        self.gMov6 = ""
        self.gMov7 = ""
        self.gMov8 = ""

        self.phasingData = None
        self.sIntervals = {}

    def toDict(self):

        result = {}
        result["fileName"] = self.fileName
        result["intersectionName"] = self.iName
        result["mappedNodeName"] = self.mappedNodeName
        result["mappedNodeId"] = self.mappedNodeId
        
        result["phasing"] = {}
        result["phasing"]["phaseNumbers"] = self.phasingData.getElementsOfDimention(1)
        for streetName in self.phasingData.getElementsOfDimention(0):
            tmp = []
            for phaseElem in self.phasingData[streetName, :]:
                tmp.append(phaseElem)
            result["phasing"][streetName] = tmp
        
        result["timeOfDayPhasing"] = {}
        for key, value in self.signalTiming.iteritems():
            
            result["timeOfDayPhasing"][key] = value.__dict__
        return result 
        
    def __repr__(self):
        
        str1 = "\t".join([str(getattr(self, attr)) for attr in SignalData.attrNames])
        streetNames = ["",] * 4
        for i, name in enumerate(self.streetNames):
            streetNames[i] = name
        str2 = "\t".join(streetNames)
        return str1 + "\t" + str2 + "\t" + self.iiName + "\t" + self.mappedNodeName + "\t" + self.mappedNodeId

    def __str__(self):
        
        result = "\n\n%30s=%30s\n%30s=%30s\n%30s=%30s" % ("FileName", 
                     self.fileName, "Intersection Name", 
                       self.iName, "Internal Intersection Name", self.iiName)

        result += "\n%30s=%30s\n%30s=%30s" % ("mappedNodeName", self.mappedNodeName, "mappedNodeId", self.mappedNodeId)
        
        result += "\n\nPhasing Data\n"
        result += self.phasingData.asPrettyString()
        
        result += "\nTiming Data\n"
        for signalTiming in self.signalTiming.values():
            result += str(signalTiming)
        return result 

    def iterSignalTiming(self):
        """
        Return an iterator to the signal Timing objects
        """
        return iter(self.signalTiming.values())
    
    def getNumTimeIntervals(self):
        """
        Return the number of time intervals
        """
        if self.signalTiming:
            return len(self.signalTiming.values()[0])

    def getPhases(self, startHour, endHour):
        """
        Get the phases as list of dictionaries. By combining phasing data information
        such as the one in the following table 
        
        Phasing Data
                           1  2  3  4  5  6  7  8
          GEARY BLVD (EB)  G  G  Y  R  R  R  R  R
            10TH AVE (SB)  R  R  R  R  G  G  Y  R
          GEARY BLVD (WB)  G  G  Y  R  R  R  R  R
            10TH AVE (NB)  R  R  R  R  G  G  Y  R

        And the signal interval data for the time of day that is specified
        by the startHour and endHour input arguments
 
	Times: [47.0, 6.0, 3.5, 0.5, 8.0, 20.0, 3.5, 1.5]
        
        """

        pPhase = {}
        phases = []
        allRed = 0

        #pdb.set_trace()
        
        phasingData = self.phasingData
        groupMovements = phasingData.getElementsOfDimention(0)
        timeIndices = phasingData.getElementsOfDimention(1)
        timeIntervals = selectCSO(self, startHour, endHour).times


        for (timeIndex1, timeIndex2), (dur1, dur2) in izip(pairwise(timeIndices), pairwise(timeIntervals)):
            try:
                states1 = list(iter(phasingData[:, timeIndex1]))
                states2 = list(iter(phasingData[:, timeIndex2]))
            except ValueError, e:
                print e
                raise SignalConversionError(str(e))
            statePairs = list(izip(states1, states2))

            cPhase = {} # the current Phase

            activeMovs = [gMov for gMov in  groupMovements if
                          phasingData[gMov, timeIndex1] == "G"]    
            if any2(statePairs, lambda pair: pair == ("G", "R")):
                #collect all the green movements
                cPhase["Movs"] = activeMovs
                cPhase["green"] = dur1
                cPhase["yellow"] = 0
                cPhase["allRed"] = 0                

                if pPhase:
                    if pPhase["Movs"] == activeMovs:
                        cPhase["green"] += pPhase["green"]
                        phases.append(cPhase)
                    else:
                        phases.append(pPhase)
                        phases.append(cPhase)
                    pPhase = {}
                else:
                    phases.append(cPhase)
            elif any2(statePairs, lambda pair: pair == ("G", "Y")):
                cPhase["Movs"] = activeMovs
                cPhase["green"] = dur1
                cPhase["yellow"] = dur2
                cPhase["allRed"] = 0                

                if pPhase:
                    if pPhase["Movs"] == activeMovs:
                        cPhase["green"] += pPhase["green"]
                        phases.append(cPhase)
                    else:
                        phases.append(pPhase)
                        phases.append(cPhase)
                    pPhase = {}
                else:
                    phases.append(cPhase)
            elif all2(states1, lambda state: state == "R"):
                #pdb.set_trace()                
                #allRed += dur1
                #phases[-1]['yellow'] += dur1
                if phases:
                    phases[-1]['allRed'] += dur1
                else:
                    raise dta.DtaError("Signal starts with all red")
                
            elif any2(statePairs, lambda pair: pair == ("G", "G")):
                if not pPhase:
                    pPhase["Movs"] = activeMovs
                    pPhase["green"] = dur1
                    pPhase["yellow"] = 0
                    pPhase["allRed"] = 0
                    #allRed = 0
                else:
                    pPhase["green"] += dur1

        lastIndex = list(timeIndices)[-1]
        lastStates = list(iter(phasingData[:, lastIndex]))    
        #if all2(lastStates, lambda state: state == 'R'):
        #    phases[-1]['yellow'] += timeIntervals[-1]
        return phases

    def selectCSO(self, startTime, endTime):
        """
        returns the ExcelSignalTiming if there is one that is in operation during the 
        input hours. Otherwise it returns none
        """
        for cso, signalTiming in self.signalTiming.iteritems(): 

            if startTime >= signalTiming.startTime and endTime <= signalTiming.endTime:
                return cso

        for cso, signalTiming in self.signalTiming.iteritems(): 
            if signalTiming.startTime == 0 and signalTiming.endTime == 2400:
                return cso
        return None

class PhaseState(object):
    """Represents the state of a phase for a specfic duration
    The state can be one of GREEN, YELLOW and RED:
    and the duration is a floating number
    """
    GREEN = 0
    YELLOW = 1
    RED = 2    

    def __init__(self, state, duration):
        self.state = state 
        self.duration = duration

class ExcelSignalTiming(object):
    """Contains the timing information for a particular period

    the timing consists of a list of floating numbers that each of which 
    corresponds to a different state of the timing plan

    """
    DEFAULT_VALUE = -1

    def __init__(self):

        self.cso = ExcelSignalTiming.DEFAULT_VALUE   # string the cso value
        self.cycle = ExcelSignalTiming.DEFAULT_VALUE  #float the cycle length 
        self.offset = ExcelSignalTiming.DEFAULT_VALUE  # float the offset
#        self.interval = [] # floats the interval values 

        self.isActuated = False

        self.startTime = 0
        self.endTime = 2400

        self.times = ()
        
    def setPhaseTimes(self, times):        

        for time in times:
            if not isinstance(time, float):
                raise ExcelSignalTimingError("Time values corresponding to phase states have to be float "
                                       "values and not: %s" % str(time))

#        state = times # [PhaseState(None, time) for time in times]
        self.times = times

    def __iter__(self):

        return iter(self.state)

    def __len__(self):

        return self.getNumIntervals()

    def getNumIntervals(self):

        return len(self.times)

    def __str__(self):

        return self.__repr__()

    def __repr__(self):

        if self.cycle == None:
            cycle = ExcelSignalTiming.DEFAULT_VALUE
        else:
            cycle = self.cycle 

        if self.offset == None:
            offset = ExcelSignalTiming.DEFAULT_VALUE
        else:
            offset = self.offset

        
        result = "\ncso= %s \ncycle= %.1f \noffset= %.1f \nstartTime= %s " \
            "endtime= %s \nisActuated %s" % (self.cso, cycle, offset,
                                          str(self.startTime), str(self.endTime), self.isActuated)
        result += "\n\tTimes: %s" % str(self.times)

        return result
                                          

#    def setPhaseStates(self, phaseStates):
#        if len(phaseStates) != len(self.state):
#            raise ExcelSignalTimingError("The number of phase states: %d and the number of "
#                                   "time steps %s are not equal" %(len(phaseStates), len(self.state)))
#        for signalTiming, phaseState in izip(self, phaseStates):
#            if phaseState not in [PhaseState.GREEN, PhaseState.YELLOW, PhaseState.RED]:
#                raise ExcelSignalTimingError("I do not recognise the following phase state: %s"
#                                       % phaseState)
#            signalTiming.state = phaseState
        
def findTopLeftCell(sheet):
    """Find the top left cell of the signal card containing 
    the intersection name and return its coordinates"""

    MAX_RANGE = 10 # max range to look for the top left cell 
    for i in range(MAX_RANGE):
        for j in range(MAX_RANGE):
            if str(sheet.cell_value(i, j)).strip():
                return (i, j)

    raise ParsingCardError("I cannot find top left cell of the sheet containing "
                           "the intersection name")

        
def getIntersectionName(sheet, topLeftCell):
    """
    Return the intersection name as found in the excel card. 
    TopLeftCell is a tuble that contains the location of the top left cell
    """
    return str(sheet.cell_value(topLeftCell[0], topLeftCell[1])).upper()

def findStreet(sheet, topLeftCell):
    """Find the cell containing the STREET keyword that marks
    the beggining of the phase sequencing information and return 
    its coordinates. If unsuccesfull raiseParsingCardError"""
    CELLS_TO_SEARCH = 40
    START_PHASE_SECTION = "STREET"
    for row in range(CELLS_TO_SEARCH):
        cell = (topLeftCell[0] + row, topLeftCell[1])
        try:
            value = str(sheet.cell_value(rowx=cell[0], colx=cell[1]))
        except IndexError:
            return None
        if value.upper().strip().startswith(START_PHASE_SECTION):
            return cell
    raise ParsingCardError("I cannot find the start of the phasing section")

def findPedestrianPhase(sheet, topLeftCell):
    
    CELLS_TO_SEARCH = 60
    for row in range(CELLS_TO_SEARCH):
        cell = (topLeftCell[0] + row, topLeftCell[1])
        try:
            value = str(sheet.cell_value(rowx=cell[0], colx=cell[1]))
        except IndexError:
            return None
        if "PEDS " in value.upper().strip() or \
                "PED " in value.upper().strip() or \
                "XING " in value.upper().strip() or \
                "MUNI " in value.upper().strip() or \
                "TRAIN " in value.upper().strip() or\
                "FLASHING " in value.upper().strip():
            return cell
    return None    

def findSignalIntervals(sheet, topLeftCell):
    
    CELLS_TO_SEARCH = 80
    for row in range(CELLS_TO_SEARCH):
        cell = (topLeftCell[0] + row, topLeftCell[1])
        try:
            value = str(sheet.cell_value(rowx=cell[0], colx=cell[1]))
        except IndexError:
            return None
        if "CSO" in value.upper().strip() or "DIAL" in value.upper().strip():
            return cell
    raise ParsingCardError("I cannot find the start of the singal interval field "
                           "marked by the keyworkd CSO or DIAL")

def getFirstColumnOfPhasingData(sheet, signalData):
    
    if not signalData.phaseSeqCell:
        raise ParsingCardError("I cannot locate the first column of the phasing data "
                               "because the phase data section has not been previously identified")
    
    NUM_COL_TO_SEARCH = 10
    startX, startY = signalData.phaseSeqCell
    for col in range (startY + 1, startY + NUM_COL_TO_SEARCH):
        if sheet.cell_value(rowx=startX, colx=col) == 1:  # one is the first phase
            signalData.colPhaseData = col
            return
    raise ParsingCardError("I cannot locate the first column of the phasing data "
                           "identified by the keyword 1 in the same row with the "
                           "STREET keyword")

def getOperationTimes(sheet, signalData):
    
    i = signalData.topLeftCell[0] + 12
    j = signalData.colPhaseData

    found = False
    for x in range(i-5, i + 7):
#        myValues = [sheet.cell_value(x, y) for y in range(j, j + 13)]
#        print "\t", myValues
        for y in range(j, j + 13):
            #print x, y, str(sheet.cell_value(x, y)).strip().upper()
            if str(sheet.cell_value(x, y)).strip().upper() == "CYCLE":
                found = True
                for k in range(x + 1, x + 6):
                    cso = []
                    for l in range(y, y + 6):
                        cellValue = sheet.cell_value(k, l)
                        if cellValue:
                            if isinstance(cellValue, float):
                                cellValue = str(int(cellValue))
                            elif isinstance(cellValue, int):
                                cellValue = str(cellValue)
                            cso.append(cellValue)
                    strCso = "".join(cso)
                    if strCso.strip() and strCso in signalData.signalTiming:
                        #print "CSO is", strCso
                        gotStartTime = False
                        for m in range(signalData.topLeftCell[1], signalData.colPhaseData):
                           cellValue = sheet.cell_value(k, m) 
                           if str(cellValue).strip():
                               #print cellValue 
                               if isinstance(cellValue, float):
                                   if cellValue == 1.0:
                                       time = (0, 0, 0, 0, 0, 0)
                                   else:
                                       time = xlrd.xldate_as_tuple(cellValue, 0)
                                   #print "\t", time
                                   if gotStartTime == False:
                                       signalData.signalTiming[strCso].startTime = time[3] * 100 + time[4] 
                                       gotStartTime = True
                                   else:
                                       signalData.signalTiming[strCso].endTime = time[3] * 100 + time[4]
                        #print signalData.signalTiming[strCso]
    if found == False:
        raise ParsingCardError("I cannot find start and end times") 

def getSignalIntervalData(sheet, signalData):
    """
    Extracts the signal interval data from the supplied excel
    spreadsheet 
    """
    if not signalData.sigInterCell or not signalData.colPhaseData:
        return
    #pdb.set_trace()
    #begin with the signal interval data
    startX, startY = signalData.sigInterCell
    #find the first enry
    i = startX
    finishedReadingData = False
    while True:
        i += 1
        try:
            value = sheet.cell_value(rowx=i, colx=startY)
        except IndexError:
            break
        if str(value).strip():
            finishedReadingData = True
            row = []
            for j in range(startY, signalData.colPhaseData):
                value = sheet.cell_value(rowx=i,colx=j)

#                print "value = ", value, "at ", i, j
                if str(value):
                    row.append(value)
#            pdb.set_trace()
                    
            #you ought to have 3 values: CSO, CYCLE, OFFSET
            #read the rest of the row
            signalTiming = ExcelSignalTiming()

            try:
                strCso = str(int(float(row[0])))
            except ValueError, e:
                strCso = str(row[0])

            if len(row) == 3:
                strCycle = str(row[1])
                strOffset = str(row[2])
            elif len(row) == 2:
                strCycle = str(row[1])
                strOffset = "-"
            elif len(row) == 1:
                strCycle = "-"
                strOffset = "-"
            else:
                raise ParsingCardError("I cannot parse the cso,cycle,offset from row %d:%s"
                                        % (i, str(row)))              
            signalTiming.cso = strCso
            if strCso.endswith("-") and len(strCso) == 3:
                signalTiming.offset = 0
                if strCso.endswith("--"):
                    signalTiming.cycle = 0
                    signalTiming.isActuated = True
                else:
                    signalTiming.cycle = float(strCycle)
            elif strCso.endswith("--") and len(strCso) == 4:
                signalTiming.offset = 0
                signalTiming.cycle = float(strCycle)
            elif strCso == "FREE" or strCso == "free":
                signalTiming.isActuated = True
            else:
                try:
                    if "-" in strCycle:
                        signalTiming.cycle = None
                        signalTiming.isActuated = True
                    else:
                        signalTiming.cycle = float(strCycle)    
                    signalTiming.offset = float(strOffset) if "-" not in strOffset  else 0
                except ValueError, e:
                    raise ParsingCardError("I could not parse the cso,cycle,offset from row %d:%s"
                                           ", Error: %s" % (i, str(row), str(e)))
                
            j = signalData.colPhaseData
            timings = []
            signalData.signalTiming[signalTiming.cso] = signalTiming
            while True:
                try:
                    value = sheet.cell_value(rowx=i,colx=j)
                except IndexError:
                    if not signalData.lastColPhaseData:
                        signalData.lastColPhaseData = j - 1
                    signalData.sIntervals[row[0]] = row
                    signalTiming.setPhaseTimes(timings)
                    break                    
                if str(value).strip(): # I chanched this from value to value.strip()
                    if not isinstance(value, (int, float)):
                        raise ParsingCardError("The signal intervals are not numbers "
                                               "in row with CSO= %s. Problem reading: %s at %d, %d " 
                                               % (strCso, str(value), i, j))
                                           
                    row.append(value)
                    timings.append(value)
                #if you find an empty cell: stop reading 
                # and set the lastColPhaseData attribute 
                else:
                    if not signalData.lastColPhaseData:
                        signalData.lastColPhaseData = j - 1
                    signalData.sIntervals[row[0]] = row
                    signalTiming.setPhaseTimes(timings)
                    break
                j += 1
            #print signalData.iName, row
        else:
            if finishedReadingData:
                break

#        if i > startX + 10:
#            break


def fillPhaseInfo(phaseInfo):
    """The a list with the phase info for a movement group such as
       ['', u'G', '', u'Y', u'R', '', '', '', '', '', '', '']
       fill the empty strings with the state of the signal
    """
    for i in range(1, len(phaseInfo)):
        if phaseInfo[i] == "" and phaseInfo[i - 1] != "":
            phaseInfo[i] = phaseInfo[i - 1]
            
    for i in range(len(phaseInfo) - 1, -1, -1):
        if phaseInfo[i] == "" and phaseInfo[i + 1] != "":
            phaseInfo[i] = phaseInfo[i + 1]
                
def getPhasingData(sheet, signalData):

    if not signalData.phaseSeqCell:
        raise ParsingCardError("I cannot parse its phasing data1.")
    
    if not signalData.sigInterCell:
        raise ParsingCardError("I cannot parse its phasing data2.")

    if not signalData.colPhaseData:
        raise ParsingCardError("I cannot parse its phasing data3.")

    if not signalData.lastColPhaseData:
        raise ParsingCardError("I cannot parse its phasing data4.")        

    
    #pdb.set_trace()
    startX, startY = signalData.phaseSeqCell 

    endX, endY = signalData.sigInterCell

    movementIndex = 1
    phasingData = []
    movementNames = []

    intervalStateGreen = ["G", "G+G", "G*", "G G", "FY", "F", "G+F", "U", "T", "G + G", "G + F"]
    intervalStateYellow = ["Y", "SY"]
    intervalStateRed = ["R", "RH", "OFF"]
    intervalStateBlanck = [""]
    intervalStateValid = intervalStateGreen + intervalStateYellow + \
        intervalStateRed + intervalStateBlanck

    for i in range(startX + 1, endX):
        groupMovement = str(sheet.cell_value(rowx=i, colx=startY)).upper()
        if groupMovement == "" or "PEDS " in groupMovement or "PED " in groupMovement \
                or "XING " in groupMovement or "MUNI " in groupMovement or \
                "TRAIN " in groupMovement or "FLASHING " in groupMovement or \
                groupMovement == "MUNI" or " MUNI" in groupMovement or "RAIL" in groupMovement:
            continue
        else:
            #read the row of phasing states 
            singleMovementData = []
            allIntervalStatesValid = True
            for j in range(signalData.colPhaseData, signalData.lastColPhaseData + 1):
                intervalState = str(sheet.cell_value(rowx=i, colx=j)).upper().strip()
                #print i, j, intervalState
                if intervalState == "":
                    singleMovementData.append("")
                elif intervalState in intervalStateGreen:
                    singleMovementData.append("G")
                elif intervalState in intervalStateYellow:
                    singleMovementData.append("Y")
                elif intervalState in intervalStateRed or "-R-" in intervalStateRed:
                    singleMovementData.append("R")
                else:
                    allIntervalStatesValid = False
                    break
            if not allIntervalStatesValid:
                continue
            if singleMovementData == ["",] * len(singleMovementData):
                continue

        setattr(signalData, "gMov%d" % movementIndex, groupMovement)
        movementIndex += 1
        movementNames.append(groupMovement)

        #print signalData.iName, groupMovement, signalData.colPhaseData, signalData.lastColPhaseData, singleMovementData
        phasingData.append(singleMovementData)
    
#    print signalData.iName, phasingData
    if phasingData == []:
        raise ParsingCardError("I cannot parse its phasing data")
    numIntervals = len(phasingData[0])
    if numIntervals == 0:
        raise ParsingCardError("I cannot parse its phasing data. "
                               "The number of phase intervals is zero")
    
    if len(phasingData) <= 1:
        raise ParsingCardError("Signal has less than two group movements")

    #pdb.set_trace() 

    if len(phasingData) > 1:
        for i in range(len(phasingData) - 1):
            if len(phasingData[i]) != len(phasingData[i+1]):
                raise ParsingCardError("I cannot parse its phasing data. "
                               "Different number of phasing steps for "
                                       "different phasing movements")


    if signalData.getNumTimeIntervals() != len(phasingData[0]):
        raise ParsingCardError("The number of phase states %d is not the same "
                               "with the number of its signal intervals %d" % 
                               (len(phasingData[0]), 
                                signalData.getNumTimeIntervals()))

    ma = MultiArray("S1", [movementNames, range(1, numIntervals + 1)])
    for i, movName in enumerate(ma.getElementsOfDimention(0)):
        fillPhaseInfo(phasingData[i])
        for j in range(1, numIntervals + 1):
            intervalState = str(phasingData[i][j-1]).strip().upper()
            if intervalState == "G":
                ma[movName, j] = "G" # GREEN
            elif intervalState == "Y":
                ma[movName, j] = "Y" # YELLOW
            elif intervalState == "R":
                ma[movName, j] = "R" #RED
            else:
                raise ParsingCardError("Group movement \t%s\t. I cannot interpret "
                                       "the phase status \t%s" % (movName, 
                                                                intervalState))
                
    signalData.phasingData = ma

def extractStreetNames(intersection):
    """Split the Excel intersection string to two or more streetNames"""

    intersection = intersection.upper()
    regex = re.compile(r",| AND|\&|\@|\/")
    streetNames = regex.split(intersection)
    if len(streetNames) == 1:
        #log the error
        pass
    result = sorted([name.strip() for name in streetNames])
    return result

def cleanStreetName(streetName):

    corrections = {"TWELFTH":"12TH", "ELEVENTH":"11TH", "TENTH":"10TH", "NINTH":"9TH", "EIGHTH":"8TH", \
                            "SEVENTH":"7TH", "SIXTH":"6TH", "FIFTH":"5TH", "FOURTH":"4TH", "THIRD":"3RD", "SECOND":"2ND", \
                        "FIRST":"1ST", "O'FARRELL":"O FARRELL", "3RDREET":"3RD", "EMBARCADERO/KING":"THE EMBARCADERO", \
                   "VAN NESSNUE":"VAN NESS", "3RD #3":"3RD", "BAYSHORE #3":"BAYSHORE", \
                   "09TH":"9TH", "08TH":"8TH", "07TH":"7TH", "06TH":"6TH", "05TH":"5TH", "04TH":"4TH", "03RD":"3RD", "02ND":"2ND", \
                       "01ST":"1ST"}


    itemsToRemove = [" STREETS", " STREET", " STS.", " STS", " ST.", " ST", " ROAD", " RD.", " RD", \
                         " AVENUE", " AVE.", " AVE", " BLVD.", " BLVD", " BOULEVARD", "MASTER:", " DRIVE", \
                         " DR.", " WAY"]

    newStreetName = streetName.strip()
    for wrongName, rightName in corrections.items():
        if wrongName in streetName:
            newStreetName = streetName.replace(wrongName, rightName)
        if streetName == 'EMBARCADERO':
            newStreetName = "THE EMBARCADERO"
        if streetName.endswith(" DR"):
            newStreetName = streetName[:-3]
        if streetName.endswith(" AV"):
            newStreetName = streetName[:-3]

    for item in itemsToRemove:
        if item in newStreetName:
            newStreetName = newStreetName.replace(item, "")
    return newStreetName.strip()

def cleanStreetNames(streetNames):
    """Accept street names as a list and return a list 
    with the cleaned street names"""
    
    newStreetNames = map(cleanStreetName, streetNames)
    if len(newStreetNames) > 1 and newStreetNames[0] == "":
        newStreetNames.pop(0)
    return newStreetNames

def writeSummary(excelCards):
    
    output = open("cardLayout.txt", "w")    
    output.write("\t".join(SignalData.attrNames))
    output.write("\t" + "\t".join(SignalData.streets))
    output.write("\t" + "\t".join(SignalData.mappingInfo) + "\n")
    for sd in excelCards:
        info = str(sd)
        output.write(info + "\n")    
    output.close()

def writeExtendedSummary(excelCards):
    
    output = open("extendedSummary.txt", "w")    
    output.write("\t".join(SignalData.attrNames))
    output.write("\t" + "\t".join(SignalData.streets))
    output.write("\t" + "\t".join(SignalData.mappingInfo) + "\n")
    cardNum = 0
    for sd in excelCards:
        cardinfo = str(sd)
        output.write("%d\t%s\t%s\t%s\n" %(cardNum, sd.iName, sd.iiName, cardinfo))
        if sd.phasingData:
            for gMovement in sd.phasingData.getElementsOfDimention(0):
                output.write("%d\t%s\t" % (cardNum, gMovement))
                output.write("\t".join(map(str, sd.mappedMovements[gMovement])) + "\n")
        cardNum += 1                  
    output.close()

def parseExcelCardFile(directory, fileName):
    """Reads the excel file parses its infomation and returns
    as SignalData object
    """
    sd = SignalData()
    sd.fileName = fileName
    book = xlrd.open_workbook(os.path.join(directory, fileName))
    sheet = book.sheet_by_index(0)
        
    sd.topLeftCell = findTopLeftCell(sheet)
    sd.iName = getIntersectionName(sheet, sd.topLeftCell)
    try:
        sd.phaseSeqCell = findStreet(sheet, sd.topLeftCell)
    except ParsingCardError, e:
        msg = 'Unable to find the start of the phasing section. filename %s' % fileName
        raise ParsingCardError(msg)
    sd.pedPhaseCell = findPedestrianPhase(sheet, sd.topLeftCell)
    sd.sigInterCell = findSignalIntervals(sheet, sd.topLeftCell)    
    getFirstColumnOfPhasingData(sheet, sd)
    getSignalIntervalData(sheet, sd)

    getOperationTimes(sheet, sd)

    getPhasingData(sheet, sd)
    return sd


def parseExcelCardsToSignalObjects(directory):
    """Reads the raw excel cards, extracts all the relevant infomation, instantiates 
    for each excel file an object called SignalData and stores the information
    and then pickles all the signal data objects into a file named: 

    excelCards.pkl"""

    excelCards = []
    problemCards = [] 

    numFiles = 0
    for fileName in os.listdir(directory):
        if not fileName.endswith("xls"):
            continue
        if fileName.startswith("System"):
            continue

        #if fileName == "3rd St_Innes_Ch_18.xls":
        #    pdb.set_trace()

        numFiles += 1
        #print "\n\n*****************************************************\n", numFiles, fileName, "\n*****************************************************\n"
        try:
            sd = parseExcelCardFile(directory, fileName)
            #print sd
            #print json.dumps(sd.toDict(),separators=(',',':'), indent=4)

            #print sd
        except ParsingCardError, e:
            #logging.error(str(e))

            
            print "%40s\t%s" % (fileName, str(e))
            problemCards.append(sd)
            sd.error = e
            continue
        #except Exception, e:
        #   logging.error("UnCaught exception. Card %s. %s" % (fileName, e))
        else:
            excelCards.append(sd)

#        if numFiles == 10:
#            break
    logging.info("Number of excel cards succesfully parsed = %d" % len(excelCards))
    return excelCards

def mapStreetNamesForManuallyMappedNodes(network, cards):
    """
    This function maps street names for the nodes that have been manually mapped    
    """
    CUTOFF = 0.7 # this parameter controls how close the strings need be
    result = []
    for card in cards:        
        streetNames = card.streetNames        
        node = net.getNodeForId(card.mappedNodeId)

        if len(node.getStreetNames()) != len(streetNames):
            print card.fileName, "\t", card.mappedNodeId, "\t", node.getStreetNames(), "\t", streetNames
            continue
            
        baseStreetNames = node.getStreetNames()
        for bName, mName in izip(baseStreetNames, streetNames):
            if not difflib.get_close_matches(bName, [mName], 1, CUTOFF):
                print card.fileName, "\t", card.mappedNodeId, "\t", node.getStreetNames(), "\t", streetNames, "\t", bName, "\t", mName
                break
            card.mappedStreet[mName] = bName            
        else:
            card.mappedNodeName = node.getName()
            result.append(card)
    return result

def findNodeWithSameStreetNames(network, excelCard, CUTOFF, mappedNodes):

    streetNames = excelCard.streetNames
    for node in network.iterRoadNodes():

        if node.getId() in mappedNodes.values():
            continue
        
        if len(node.getStreetNames()) != len(streetNames):
            continue

        baseStreetNames = node.getStreetNames()
        for bName, mName in izip(baseStreetNames, streetNames):
            if not difflib.get_close_matches(bName, [mName], 1, CUTOFF):
                break
            excelCard.mappedStreet[mName] = bName            
        else:

            mappedNodes[excelCard.iiName] = node.getId()
            excelCard.mappedNodeName = node.getName()
            excelCard.mappedNodeId = node.getId()

            return True
    return False
    
def mapMovements(excelCards, baseNetwork):
    
    logging.info("Number of excel cards read %d" % len(excelCards))
    
    def getStreetName(gMovName, streetNames):
        """Finds to which street the movement applies to and returns the 
        street"""
        for i in range(len(streetNames)):
            if streetNames[i] in gMovName:
                return streetNames[i]

        matches = difflib.get_close_matches(gMovName, streetNames, 1)
        if matches:
            bestMatchedStreetName = matches[0]
            return bestMatchedStreetName
        else:
            raise StreetNameMappingError("The group movement is not associated with any of the "
                                         "street names that identify the intersection.#%s#%s" % 
                                         (gMovName, str(streetNames)))
            
    def getDirections(gMovName):
        """Searches the movement name for a known set of strings that indicate the
        direction of the movment and returns the result(=the direction of the movement)
        Returns a string representing the direction: WB, EB, NB, SB
        """
        wbIndicators = ["WB,", ",WB", "WB/", "/WB", "WB&", "&WB", " WB", "WB ", "W/B", "(WB", "WB)", "(WB)", "(WESTBOUND)", "WESTBOUND", "WEST "]
        ebIndicators = ["EB,", ",EB", "EB/", "/EB","EB&", "&EB", " EB", "EB ", "E/B", "(EB", "(EB)", "EB)", "(EASTBOUND)", "EASTBOUND", "EAST "]        
        nbIndicators = ["NB,", ",NB", "NB/", "/NB","NB&", "&NB", " NB", "NB ", "N/B", "(NB", "NB)", "(NORTHBOUND)", "NORTHBOUND", "NORTH "]
        sbIndicators = ["SB,", ",SB", "SB/", "/SB","SB&", "&SB", " SB", "SB ", "S/B", "(SB", "SB)", "(SOUTHBOUND)", "SOUTHBOUND", "SOUTH "]
        
        indicators = {"WB":wbIndicators, "EB":ebIndicators, "NB":nbIndicators, "SB":sbIndicators}
        
        result = []
        for dir, dirIndicators in indicators.items():
            for indicator in dirIndicators:
                if indicator in gMovName:
                   result.append(dir)
                   break
        
        return result

    def getTurnType(gMovName):
        """Searches the movment name for a known set of turn type indicators such as
        LT and returns the turn type as a string which is one of the following:
        TURN_LEFT, TURN_THRU

        the function is being called by mapGroupMovments
        """

        result = []

        #todo ends with LT
        leftTurnIndicators = ["-L", "LEFT TURN", " LT", "NBLT", "SBLT", "WBLT", "EBLT","(NBLT)", "(SBLT)", "(WBLT)", "(EBLT)"]
#        rightTurnIndicators = ["-R", "RIGHT TURN", " RT"]
        thruTurnIndicators = [" THRU", " THROUGH", "(THRU)"]

        indicators = {TURN_LEFT:leftTurnIndicators, TURN_THRU:thruTurnIndicators}
        result = []
        for dir, dirIndicators in indicators.items():
            for indicator in dirIndicators:
                if indicator in gMovName:
                   result.extend(dir)
                   break

        return result

    def mapGroupMovements(mec, groupMovementNames, bNode):
        """
        Output: populate the mappedMovements dictonary of the excelCard object.
        The keys of the dictonary are the movement names and its values are
        all the iids of the corresponding movemens
        """
        streetNames = list(mec.streetNames)
        for gMovName in groupMovementNames:
            #for each group movement get the approach's street name
            try:
                stName = getStreetName(gMovName, streetNames)
            except StreetNameMappingError, e:
                raise StreetNameMappingError("%s#%d#%s" % (mec.fileName, mec.mappedNodeId, str(e)))
                
            gTurnTypes = getTurnType(gMovName)
            gDirections = getDirections(gMovName)

            f = open("temp_directons.txt", "a")
            f.write("%25s%20s%20s\n" % (gMovName, str(gTurnTypes), str(gDirections)))
            f.close()

            #if mec.fileName == "Fell_Pierce_Ch_18.xls":
            #    pdb.set_trace()

            if not stName:
                raise MovementMappingError("I cannot identify the approach of the group "
                                                 "movement %s in node %s stored as %s" 
                                                 % (gMovName, mec.iName, mec.iiName))
            bStName = mec.mappedStreet[stName]
            #collect all the links of the approach that have the same direction

            gLinks = []
            candLinks = [link for link in bNode.iterIncomingLinks() if link.getLabel() == bStName]
            for candLink in candLinks:
                if gDirections:
                    if set(getPossibleLinkDirections(candLink)) & set(gDirections):
                        gLinks.append(candLink)
                else:
                    gLinks.append(candLink)

            if len(gLinks) == 0:
                raise MovementMappingError("%s#%d#I cannot identify the links for the group "
                               "movement #%s# in node #%s# stored as #%s# candidate links are # %s" %
                                                 (mec.fileName, mec.mappedNodeId, gMovName, mec.iName, mec.iiName, str(["%s,%s" % (candLink.getLabel(), candLink.getDirection()) for candLink in candLinks])))

            gMovements = []
            if gTurnTypes:
                availableMovs = list(chain(*[link.iterOutgoingMovements() for link in gLinks]))
                for mov in availableMovs: 
                   if mov.getTurnType() in gTurnTypes:
                       gMovements.append(mov)

                if len(gMovements) == 0:
                    raise MovementMappingError("%s # %d # cannot identify the movements for the group "
                  "movement %s in node %s stored as %s. The streetNames are: %s , the directions of the group are %s. The available movemements are %s" 
                                           % (mec.fileName, mec.mappedNodeId, gMovName, mec.iName, mec.iiName, 
                                              str(mec.streetNames), str(gDirections), str([mov.getDirection() for mov in availableMovs])))
                       
            else:    
                gMovements = list(chain(*[link.iterOutgoingMovements() for link in gLinks]))

            if len(gMovements) == 0:
                raise MovementMappingError("%s#%d#I cannot identify the movements for the group "
                  "movement %s in node %s stored as %s. The streetNames are: %s , the directions of the group are %s " 
                                           % (mec.fileName, mec.mappedNodeId, gMovName, mec.iName, mec.iiName, 
                                              str(mec.streetNames), str(gDirections)))
#                    `                       "group are: %s and the turn types: %s" %     
#                                                 (gMovName, mec.iName, mec.iiName, gDirections, gTurnTypes))
                

            gMovements = sorted(gMovements, key = lambda elem: elem.getId())

            for mov in gMovements:
                mec.mappedMovements[gMovName].append(mov.getId())


    index = defaultdict(int)
    excelCardsWithMovements = []    
    for mec in excelCards:

        if mec.mappedNodeId == -9999:
            continue
        #if there is a match
        if mec.mappedNodeId and mec.phasingData: 
            #get the mapped node
            if not baseNetwork.hasNodeForId(int(mec.mappedNodeId)):
                continue
            bNode = baseNetwork.getNodeForId(int(mec.mappedNodeId))
            #get the groupMovementNames
            groupMovementNames = mec.phasingData.getElementsOfDimention(0)

            numGroupMovements = len(groupMovementNames)
            numSteps = len(mec.phasingData.getElementsOfDimention(1))
            index[numGroupMovements] += 1

#            if numGroupMovements == len(mec.streetNames):
                #for each group movement get the approach's street name
            try:
                mapGroupMovements(mec, groupMovementNames, bNode)
            except MovementMappingError, e:
                print e
                #logging.error(str(e))
                continue
#                print e
            except StreetNameMappingError, e:
                print e
                #logging.error(str(e))
                continue
#                print e

        if len(mec.mappedMovements) == 0:
            logging.error("Signal %s. No mapped movements" % mec.fileName)
            continue
            #raise MovementMappingError("Signal %s. No mapped movements" % mec.fileName)

        if len(mec.mappedMovements) == 1:
            logging.error("Signal %s. Only one of the group movements has been mapped" %
                          mec.fileName)
            continue
#            raise MovementMappingError("Signal %s. Cannot generate a signal with "
#                                    "only one movement" % mec.fileName)

        groupMovements = mec.phasingData.getElementsOfDimention(0)
        if len(mec.mappedMovements) != len(groupMovements):
            logging.error("Signal %s. Not all movements have been mapped" % mec.fileName)
            continue

#            raise MovementMappingError("Signal %s. Not all movements have been mapped" %
#                                    mec.fileName)
        for gMov in groupMovements:
            if len(mec.mappedMovements[gMov]) == 0:
                logging.error("Signal %s. The group movement %s is not mapped to "
                              "any link movements" % (mec.fileName, gmov))
                continue
#                raise MovementMappingError("Signal %s. The group movmement %s is not mapped"
#                                        "to any link movemenets" % (mec.iName, gMov))
        excelCardsWithMovements.append(mec)

    return excelCardsWithMovements

def selectCSO(excelCard, startTime, endTime):
    """
    returns the ExcelSignalTiming if there is one that is in operation during the 
    input hours. Otherwise it returns none
    """
    for signalTiming in excelCard.iterSignalTiming():
        
        if startTime >= signalTiming.startTime and endTime <= signalTiming.endTime:
            return signalTiming

    for signalTiming in excelCard.iterSignalTiming():
        if signalTiming.startTime == 0 and signalTiming.endTime == 2400:
            return signalTiming

    return None
        
def readNetIndex():

    index = {}
    for line in open('/Users/michalis/Documents/myPythonPrograms/pbTools/pbProjects/doyleDTA/indexSep1v2.txt'):
        links = line.strip().split(',')
        index[tuple(links[0].split())] = [tuple(link.split()) for link in links[1:]]
    
    return index

def pickleCards(outfileName, cards):
    """
    Pickle the cards into the outfileName
    """
    outputStream = open(outfileName, "wb")
    pickle.dump(cards, outputStream)
    outputStream.close()    

def unPickleCards(fileName):
    """
    Unpickle the cards stored in the file and return them
    """
    pkl_file = open(fileName, "rb")
    excelCards = pickle.load(pkl_file)
    pkl_file.close()
    return excelCards

def getExcelFileNames(directory):

    fileNames = []
    for fileName in os.listdir(directory):
        if not fileName.endswith("xls"):
            continue
        if fileName.startswith("System"):
            continue
        fileNames.append(fileName)

    return fileNames

def mapIntersections(excelCards, mappedingFile):
    """for each excel card in the find the node in the base network 
    it corresponds"""

    mapping = {}
    cardsByName = {}
    for card in excelCards:
        cardsByName[card.fileName] = card
        
    iStream = open(mappingFile, "r")
    for rec in csv.DictReader(iStream):
        if float(rec["Distance"]) > 90:
            continue
        mapping[rec["FNAME"]] = rec["ID_1"]
        if rec["FNAME"] in cardsByName:
            cardsByName[rec["FNAME"]].mappedNodeId = int(float(rec["ID_1"]))
        else:
            pass
            #print rec["FNAME"]
        
    #excelCard.mappedNodeName = node.streetNames
    #excelCard.mappedNodeId = node.iid

    output = open("/Users/michalis/Dropbox/tmp/mappedCards.txt", "w")
    #output = open("mappedCards.txt", "w") 
    for card in excelCards:
        if card.mappedNodeId:
            output.write("%s\t%s\n" % (card.fileName, card.mappedNodeId))
        else:
            card.mappedNodeId = "-9999"
            output.write("%s\t%s\n" % (card.fileName, card.mappedNodeId))            
            
    output.close()
    return excelCards

def getTestScenario(): 
    """
    return a test scenario
    """
    projectFolder = "/Users/michalis/Documents/workspace/dta/dev/testdata/dynameqNetwork_gearySubset"
    prefix = 'smallTestNet' 

    scenario = DynameqScenario(datetime.datetime(2010,1,1,0,0,0), 
                               datetime.datetime(2010,1,1,4,0,0))
    scenario.read(projectFolder, prefix) 

    return scenario 

def getNet():
    
    testScenario = getTestScenario()
    folder = "/Users/michalis/Documents/workspace/dta/dev/testdata/CubeNetworkSource_renumberExternalsOnly/"
    #folder = "/Users/michalis/Documents/workspace/dta/dev/testdata/cubeSubarea_sfCounty/dynameqNetwork"
    net = DynameqNetwork(scenario=testScenario)
    net.read(dir=folder, file_prefix="sf9")
    #net.removeShapePoints()    
    net.removeCentroidConnectorsFromIntersections(splitReverseLinks=True)      
    return net 

def assignCardNames(excelCards): 

    for sd in excelCards:
        
        streetNames = extractStreetNames(sd.iName)
        sd.streetNames = sorted(cleanStreetNames(streetNames))
        sd.iiName = ",".join(sd.streetNames)
    
def mapIntersectionsByName(network, excelCards):
    """for each excel card in the find the node in the base network 
    it corresponds"""

    mappedExcelCards = []

    numMappedNodesV1 = 0
    mappedNodes = {}
    for sd in excelCards:

#        mappedNodeName = difflib.get_close_matches(sd.iiName, network.intersectionByName.keys(), 1, 0.85)
#        if mappedNodeName:
#            numMappedNodesV1 += 1

        if findNodeWithSameStreetNames(network, sd, 0.9, mappedNodes):
            mappedExcelCards.append(sd)
            print "Mapped ", sd.fileName, "to", sd.mappedNodeId
        else:
            print "Failed to map ", sd.fileName

    print "Number of cards are", len(excelCards), " Number of mapped nodes are ", len(mappedNodes)

def getPossibleLinkDirections(link):
    """Return a two element tuple containing the possible directions of the link.
    Example (NB, WB)"""

    result = []

    orientation = link.getOrientation()
    if orientation >= 270 or orientation < 90:
        result.append("NB")
    else:
        result.append("SB")

    if orientation >= 0 and orientation < 180:
        result.append("EB")
    else:
        result.append("WB")

    return tuple(result)

def simpleMovementFactory(incomingLink, outgoingLink):

    mov = dta.Movement(incomingLink.getEndNode(),
                   incomingLink,
                   outgoingLink,
                   30,
                   dta.VehicleClassGroup("all", "-", "#ffff00"))

    return mov                                                                                           
def addAllMovements(net):
    
    for node in net.iterNodes():
        for incomingLink in node.iterIncomingLinks():
            if incomingLink.isVirtualLink():
                continue
            for outgoingLink in node.iterOutgoingLinks():
                if outgoingLink.isVirtualLink():
                    continue
                if not incomingLink.hasOutgoingMovement(outgoingLink.getEndNodeId()) and \
                   not incomingLink.getStartNodeId() == outgoingLink.getEndNodeId():
                    mov = simpleMovementFactory(incomingLink, outgoingLink)
                    incomingLink.addOutgoingMovement(mov)

def removePartOfTheNetwork(net):
    """
    This function removes all the nodes that are south of 
    node 4761. This function was used earlier in the 
    development process
    """
    n = net.getNodeForId(27297)
    nodesToDelete = []
    for node in net.iterNodes():
        if node.getY() < n.getY():
            nodesToDelete.append(node)

    for node in nodesToDelete:
        net.removeNode(node)

def convertSignalToDynameq(node, card, planInfo):
    """
    Convert the excel signal described by the card object to
    a Dynameq time plan and return it. The input planInfo
    object determines the time period of operation
    """
    startTime, endTime = planInfo.getTimePeriod()
    cso = card.selectCSO(startTime, endTime)
    if not cso:
        raise dta.DtaError("Unable to find CSO")
    
    offset = card.signalTiming[cso].offset
    dPlan = TimePlan(node, offset, planInfo)

    startTime, endTime= planInfo.getTimePeriod() 
    excelPhases = card.getPhases(startTime, endTime)
    
    for excelPhase in excelPhases:

        groupMovemenents = excelPhase["Movs"]
        green = excelPhase["green"]
        yellow = excelPhase["yellow"]
        red = excelPhase["allRed"]

        dPhase = Phase(dPlan, green, yellow, red, Phase.TYPE_STANDARD)

        for groupMovement in groupMovemenents:
            dMovsAsStr = card.mappedMovements[groupMovement]
            for dMovStr in dMovsAsStr:
                n1, n2, n3 = map(int, dMovStr.split())
                dMov = node.getMovement(n1, n3)
                phaseMovement = PhaseMovement(dMov, PhaseMovement.PROTECTED)
                if not dPhase.hasMovement(phaseMovement.getStartNodeId(),
                                          phaseMovement.getEndNodeId()):                    
                    dPhase.addMovement(phaseMovement)
                    
        dPlan.addPhase(dPhase)

    return dPlan

def checkType2Cards(net):
    
    cardsDirectory = "/Users/michalis/Documents/workspace/dta/dev/testdata/cubeSubarea_sfCounty/excelSignalCards2/type2" 
    cards = parseExcelCardsToSignalObjects(cardsDirectory)
    assignCardNames(cards)
    mapIntersectionsByName(net, cards)
    #success rate is 38 out of 122 
    
def manuallyDetermineMappedNodeId(net, cardsDirectory):

    fileNames = os.listdir(cardsDirectory)
    
    cards = parseExcelCardsToSignalObjects(cardsDirectory)
    assignCardNames(cards)
    cardsByName = {}
    for card in cards:
        cardsByName[card.fileName] = card

    result = []
    for record in csv.DictReader(open("mappedIntersections_manualEdits_dt20111208.csv", "r")):
        if record["status"] == "2":
            nodeId = record["manualCubeNode"].strip()
            if nodeId:
                id_ = int(nodeId) 
                if net.hasNodeForId(id_):
                    cardsByName[record["fileName"]].mappedNodeId = int(nodeId)
                    result.append(cardsByName[record["fileName"]])
                else:
                    print "File ", record["fileName"], " does has been mapped to an non-existing node", id_
            else:
                print "File ", record["fileName"], " does not have a mapped node id"

    return result 

def getMappedCards(net, cardsDirectory): 

    excelCards = parseExcelCardsToSignalObjects(cardsDirectory)

    cards = excelCards
    assignCardNames(cards)
    mapIntersectionsByName(net, cards)

    #this is the folder where cards with type 2 errors reside
    cardsDirectoryManuallyMapped = "/Users/michalis/Documents/workspace/dta/dev/testdata/cubeSubarea_sfCounty/excelSignalCards2/type2"
    cards2 = manuallyDetermineMappedNodeId(net, cardsDirectoryManuallyMapped)

    assignCardNames(cards2)
    cards3 = mapStreetNamesForManuallyMappedNodes(net, cards2)
    cards.extend(cards3)

    #output = open("mappedIntersections.txt", "w")
    
    #for card in excelCards:
    #    print "%s\t%s\t%s\t%s" % (card.fileName, card.streetNames, card.mappedNodeId, card.mappedNodeName)
    #    output.write("%s\t%s\t%s\t%s\n" % (card.fileName, card.streetNames, card.mappedNodeId, card.mappedNodeName))

    #output.close()

    return cards 

def mapAllMovements(net, cards):

    cardsWithMovements = mapMovements(cards, net)

    return cardsWithMovements

def exportToJSON(cards):

    output = open("excelSignals.json", "w")
    for card in cards:
        output.write(json.dumps(card.toDict(),separators=(',',':'), indent=4))
    output.close()

def createDynameqSignals(net, cardsWithMovements, startTime, endTime):
    """
    Create a dynameq signal for each excel card object for
    the specified input preriod
    """
    planInfo = net.addPlanCollectionInfo(startTime, endTime, "test", "excelSignalsToDynameq")
    allPlans = []
    for card in cardsWithMovements:
        nodeId = card.mappedNodeId
        node = net.getNodeForId(nodeId)
        try:
            dPlan = convertSignalToDynameq(node, card, planInfo)
            dPlan.setPermittedMovements()            
            dPlan.validate()
        except ExcelCardError, e:
            print e
            continue
        except dta.DtaError, e:
            print str(e)
            #pdb.set_trace()
            continue

        allPlans.append(dPlan)
        
    return allPlans

def verifySingleSignal(net, fileName):

    directory, fn = os.path.split(fileName)
    sd = parseExcelCardFile(directory, fn)
    cards = [sd]
    assignCardNames(cards)
    mapIntersectionsByName(net, cards)

    if not sd.mappedNodeId:
        print "The card was not mapped to a Cube node" 
    else:
        node = net.getNodeForId(sd.mappedNodeId)
        print "%20s,%s" % ("Cube int name", node.getStreetNames())
        print "%20s,%s" % ("Excel card name", str(sd.streetNames))
        mapMovements(cards, net)

        for movDir, nodeTriplets in sd.mappedMovements.iteritems():
            print movDir            
            for nodeTriplet in nodeTriplets:
                print "\t\t%s" % nodeTriplet
        
def plotSignalTimes(net):

    pass 

if __name__ == "__main__":
      
    net = getNet()

    #net.writeNodesToShp("/Users/michalis/Dropbox/tmp/nodes9_2")
    #net.writeLinksToShp("/Users/michalis/Dropbox/tmp/links9_2")
    
    addAllMovements(net)

    #cardsDirectory = "/Users/michalis/Documents/workspace/dta/dev/testdata/cubeSubarea_sfCounty/excelSignalCards2/"
    #fileName = os.path.join(cardsDirectory, "10th Ave_California_Ch_12.xls") 
    #verifySingleSignal(net, fileName)

    #cards = getMappedCards(net)

    #print "Num excel files", len(excelFileNames)
    pCardsFile4 = "/Users/michalis/Documents/workspace/dta/dev/testdata/cubeSubarea_sfCounty/intermediateSignalFiles/excelCards4.pkl"    

    #pickleCards(pCardsFile4, cards)
    cards = unPickleCards(pCardsFile4)    

    #
    #for card in cards:
    #    print card.iName, card.streetNames, card.mappedStreet
    #print len(cards)

    cardsWithMovements = mapAllMovements(net, cards)
    allPlans = createDynameqSignals(net, cardsWithMovements, 1530, 1830)
    pdb.set_trace()
    net.write("test", "test")
    

    

    

              
    

    


    

