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
import copy
import csv
import la 
import datetime
from itertools import izip 

import numpy as np

from dta.Algorithms import hasPath 
from .DtaError import DtaError

class Demand(object):

    FORMAT_LINEAR = 'FORMAT:linear'
    FORMAT_FULL = 'FORMAT:full'    
    HEADER_LINE1 = '*DEMAND MATRIX ASCII FILE [FULL FORMAT]- GENERATED'
    VEHCLASS_SECTION = 'VEH_CLASS'
    DEFAULT_VEHCLASS = 'Default'
    DATA_SECTION = 'DATA'
    SLICE_SECTION = 'SLICE'

    YEAR = 2010
    MONTH = 1
    DAY = 1

    @classmethod
    def readCubeODTable(cls, fileName, net, vehicleClassName, 
                        startTime, endTime):
        """
        Reads the demand (linear format) from the input csv file. The fieldNames 
        should correspond to the names of the vehicle classes. 
        """

        demand = Demand(net, vehicleClassName, startTime, endTime, endTime - startTime)

        timeLabel = demand._datetimeToMilitaryTime(endTime)

        inputStream = open(fileName, "r")
        for record in csv.DictReader(inputStream):
            
            origin = int(record["ORIGIN"])
            destination = int(record["DESTINATION"])
            
            demand.setValue(timeLabel, origin, destination, float(record[vehicleClassName]))

        return demand

    @classmethod
    def read(cls, net, fileName):

        input = open(fileName, "rb")
        
        input.next() # <DYNAMEQ>
        input.next() # <VERSION> 
        input.next() # <MATRIX_FILE> 
        input.next() # * comment 
        line = input.next().strip() 
        if line != Demand.FORMAT_FULL:
            raise DtaError("I cannot read a demand format other than %s" % Demand.FORMAT_FULL)
        input.next() # VEH_CLASS 
        line = input.next().strip() 

        vehClassName = line
        #if line != Demand.DEFAULT_VEHCLASS:
        #    raise DtaError("I read a vehicle class other than the default one currently") 
        input.next() #DATA 
        line = input.next().strip()         

        startTime = datetime.datetime.strptime(line, "%H:%M")  
        line = input.next().strip()         
        endTime = datetime.datetime.strptime(line, "%H:%M")
    
        line = input.next().strip() #SLICE 
        assert line == "SLICE"        
        line = input.next().strip() # first time slice 
        timeSlice1 = datetime.datetime.strptime(line, "%H:%M") 

        timeStep = timeSlice1 - startTime 
        if timeStep.seconds == 0:
            raise DtaError("The time step defined by the first slice cannot be zero") 
        
        demand = Demand(net, vehClassName, startTime, endTime, timeStep)

        timeStepInMin = demand._timeInMin(timeStep)

        for i, timePeriod in enumerate(demand.iterTimePeriods()):

            timeLabel = demand._datetimeToMilitaryTime(timePeriod) 

            if timePeriod != demand.startTime + demand.timeStep: 
                line = input.next().strip()
                assert line == "SLICE"
                line = input.next().strip()            
            destinations = map(int, input.next().strip().split())
            for j, origin in enumerate(range(net.getNumCentroids())):
                fields = map(float, input.next().strip().split()) 
                demand._la[i, j, :] = np.array(fields[1:]) / ( 60.0 / timeStepInMin)

        return demand

    def __init__(self, net, vehClassName, startTime, endTime, timeStep):

        self._net = net 

        if startTime >= endTime:
            raise DtaError("Start time %s is grater or equal to the end time %s" %
                           startTime, endTime)
        if timeStep.seconds == 0:
            raise DtaError("Time step %s cannot be zero" % timeStep)         

        if (self._timeInMin(endTime) - self._timeInMin(startTime)) % self._timeInMin(timeStep) != 0:
            raise DtaError("Demand interval is not divisible by the demand time step") 

        self.startTime = startTime
        self.endTime = endTime
        self.timeStep = timeStep
        self.vehClassName = vehClassName

        self._timePeriods = self._getTimePeriods(startTime, endTime, timeStep)
        self._timeLabels = map(self._datetimeToMilitaryTime, self._getTimePeriods(startTime, endTime, timeStep))

        self._centroidIds = sorted([c.getId() for c in net.iterNodes() if c.isCentroid()]) 

        array = np.ndarray(shape=(self.getNumSlices(), len(self._centroidIds), len(self._centroidIds)))
        self._la = la.larry(array, [self._timeLabels, self._centroidIds, self._centroidIds], dtype=float)

        #TODO: what are you going to do with vehicle class names? 
        #self._vehicleClassNames = [vehClass.name for vehClass in self._net.getScenario().vehicleClassNames]

    def iterTimePeriods(self):
        """
        Return an iterator to the time periods associated with the demand time slices
        """
        return iter(self._timePeriods)

    def getNumSlices(self):
        """
        Return the number of time slices the demand has been split
        """
        return len(self._timePeriods)
        
    def _getTimePeriods(self, startTime, endTime, timeStep):
        """
        Return the time labels of the different time slices as a list
        """

        if (self._timeInMin(endTime) - self._timeInMin(startTime)) % self._timeInMin(timeStep) != 0:
            raise DtaError("Demand interval is not divisible by the demand time step") 
                           
        result = []
        time = copy.deepcopy(startTime)
        while time != endTime:
            time += timeStep
            result.append(time)

        return result 

    def _timeInMin(self, time):
        """
        Return input time in minutes. Input time should be a datetime.datetime or 
        datetime.timedelta object
        """
        
        if isinstance(time, datetime.datetime):
            return time.hour * 60 + time.minute 
        elif isinstance(time, datetime.timedelta):
            return time.seconds / 60 

    def _datetimeToMilitaryTime(self, time):
        """
        Return an integer that repreents the time of the day e.g. entering 5:00 PM will return 1700
        """
        return time.hour * 100 + time.minute
        
    def _militaryTimeToDayTime(self, militaryTime):
        """
        Return a datetime object that corresponds to the input military time. For example, if the input 
        military time is 1700 the following datetime object will be returned datetime(17, 0, 0)
        """
        
        strTime = str(militaryTime)
        assert 3 <= len(strTime) <= 4
        minutes = int(strTime[-2:])
        hours = int(strTime[:-2])
        return datetime.datetime(Demand.YEAR, Demand.MONTH, Demand.DAY, hours, minutes)         
                                               
    def setValue(self, timeLabel, origin, destination, value):
        """
        Set the value of the given timeLabel, origin, and destination
        """
        
        a = self._la.labelindex(timeLabel, axis=0)
        b = self._la.labelindex(origin, axis=1)
        c = self._la.labelindex(destination, axis=2) 
        
        self._la[a, b, c] = value 
    
    def getValue(self, timeLabel, origin, destination):
        """
        Return the value of the given time period, origin, and destination
        """
        return self._la.lix[[timeLabel], [origin], [destination]]

    def write(self, fileName):
        """
        Write the demand in the dynameq format
        """
        outputStream = open(fileName, "w") 

        outputStream.write("<DYNAMEQ>\n<VERSION_1.7>\n<MATRIX_FILE>\n")
        outputStream.write('%s %s %s\n' % ("Created by python DTA by SFCTA", 
                                           datetime.datetime.now().strftime("%x"), 
                                           datetime.datetime.now().strftime("%X")))
        outputStream.write('%s\n' % Demand.FORMAT_FULL)
        outputStream.write('%s\n' % Demand.VEHCLASS_SECTION)
        outputStream.write('%s\n' % self.vehClassName)
        outputStream.write('%s\n' % Demand.DATA_SECTION)
        outputStream.write("%s\n%s\n" % (self.startTime.strftime("%H:%M"),
                                         self.endTime.strftime("%H:%M")))

        timeStepInMin = self._timeInMin(self.timeStep)

        for i, timePeriod in enumerate(self._timePeriods):
            outputStream.write("SLICE\n%s\n" % timePeriod.strftime("%H:%M"))
            outputStream.write("\t%s\n" % '\t'.join(map(str, self._centroidIds)))

            timeLabel = self._datetimeToMilitaryTime(timePeriod)             

            for j, cent in enumerate(self._centroidIds):
                outputStream.write("%d\t%s\n" % (cent, "\t".join("%.2f" % (elem / (60.0 / timeStepInMin)) for elem in self._la[i, j, :])))

        outputStream.close()

    def __eq__(self, other):
        """
        Implementation of the == operator. The comparisson of the 
        two demand objects is made using both the data and the labels 
        of the underlying multidimensional arrays. 
        """
        
        def areEqual(array1, array2):
            
            for elem1, elem2 in izip(array1, array2):
                if elem1 != elem2:
                    return False
            return True
        
        d1 = self._la.copyx().flat
        d2 = other._la.copyx().flat 

        l1 = self._la.copylabel()
        l2 = other._la.copylabel()

        if not areEqual(d1,d2):
            return False
        if not areEqual(l1, l2):
            return False

        if self.startTime != other.startTime or self.endTime != other.endTime or \
                self.timeStep != other.timeStep:
            return False 

        if self._timePeriods != other._timePeriods or self._timeLabels != \
                other._timeLabels or self._centroidIds != other._centroidIds:
            return False

        if self.vehClassName != other.vehClassName:
            return False

        return True

    def applyTimeOfDayFactors(self, factorsInAList):
        """
        Apply the given time of day factors to the existing 
        demand object and return a new demand object with as many 
        time slices as the number of factors. Each time slice is 
        the result of the original table multiplied by a factor 
        in the list. 
        """
        if self.getNumSlices() != 1:
            raise DtaError("Time of day factors can be applied only to a demand that has only"
                           " one time slice") 
            
        if sum(factorsInAList) != 1:
            raise DtaError("The input time of day factors should sum up to 1.0") 

        
        newTimeStep = self.timeStep / len(factorsInAList) 

        newDemand = Demand(self._net, self.vehClassName, self.startTime, self.endTime, newTimeStep)

        for i in range(len(factorsInAList)):
            
            newDemand._la[i, :, :] = self._la[0, :, :] * factorsInAList[i] 

        return newDemand                            

    def removeInvalidODPairs(self):
        """
        Examine all the OD interchanges and remove those for which 
        a path does not exist from origin to destination
        """
        
        for originId in self._centroidIds:
            for destinationId in self._centroidIds:
                for timeLabel in self._timeLabels:
                    if self.getValue(timeLabel, originId, destinationId) > 0:
                        origin = self._net.getNodeForId(originId)
                        destination = self._net.getNodeForId(destinationId)
                        if not hasPath(self._net, origin, destination):
                            self.setValue(timeLabel, originId, destinationId, 0) 
                        
    def getTotalDemand(self):
        """
        Return the total number of trips
        """
        return self._la.sum() 
