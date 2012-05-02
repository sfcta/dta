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
import datetime
from itertools import izip 

import numpy as np

import dta
from dta.Algorithms import hasPath 
from dta.DtaError import DtaError
from dta.MultiArray import MultiArray
from dta.Utils import Time

class Demand(object):
    """
    Class that represents the demand matrix for a :py:class:`Network`
    """

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

        timeSpan = endTime - startTime 
        demand = Demand(net, vehicleClassName, startTime, endTime, timeSpan)
        totTrips = 0
        numIntrazonalTrips = 0
        inputStream = open(fileName, "r")
    
        for record in csv.DictReader(inputStream):
            
            origin = int(record["O"])
            destination = int(record["D"])
            trips = float(record[vehicleClassName])
            totTrips += trips
            tripsInHourlyFlows = trips * (60.0 / timeSpan.getMinutes())
            
            if tripsInHourlyFlows == 0:
                continue
            if origin == destination:
                numIntrazonalTrips += trips
                continue
            if not net.hasCentroidForId(origin):
                dta.DtaLogger.error("Origin zone %d does not exist" % origin)
                continue 
            if not net.hasCentroidForId(destination):
                dta.DtaLogger.error("Destination zone %s does not exist" % destination)
                continue
            demand.setValue(endTime, origin, destination, tripsInHourlyFlows)

        dta.DtaLogger.info("The cube table has the following fields: %s" % ",".join(record.keys()))
          
        dta.DtaLogger.info("Read %10.2f %-16s from %s" % (totTrips, "%s TRIPS" % vehicleClassName, fileName))
        if numIntrazonalTrips > 0:
            dta.DtaLogger.error("Disregarded intrazonal Trips %f" % numIntrazonalTrips)
        if totTrips - demand.getTotalNumTrips() - numIntrazonalTrips > 1:
            dta.DtaLogger.error("The total number of trips in the Cube table transfered to Dynameq is not the same.")
                    
        return demand

    @classmethod
    def readDynameqTable(cls, net, fileName):
        """
        Read the dynameq demand stored in the fileName that pertains to the 
        dynameq network a :py:class:`DynameqNetwork`instance
        """
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

        startTime = Time.readFromString(line)
        line = input.next().strip()
        endTime = Time.readFromString(line)        
    
        line = input.next().strip() #SLICE 
        assert line == "SLICE"        
        line = input.next().strip() # first time slice
        
        timeSlice1 = Time.readFromString(line)

        timeStep = timeSlice1 - startTime 
        if timeStep.getMinutes() == 0:
            raise DtaError("The time step defined by the first slice cannot be zero") 
        
        demand = Demand(net, vehClassName, startTime, endTime, timeStep)
        _npyArray = demand._demandTable.getNumpyArray()

        timeStepInMin = timeStep.getMinutes()

        for i, timePeriod in enumerate(demand.iterTimePeriods()):
            if timePeriod != demand.startTime + demand.timeStep: 
                line = input.next().strip()
                assert line == "SLICE"
                line = input.next().strip()            
            destinations = map(int, input.next().strip().split())
            for j, origin in enumerate(range(net.getNumCentroids())):
                fields = map(float, input.next().strip().split()) 
                #_npyArray[i,j,:] = np.array(fields[1:]) / ( 60.0 / timeStepInMin)
                _npyArray[i,j,:] = np.array(fields[1:])
                
        return demand

    def __init__(self, net, vehClassName, startTime, endTime, timeStep):
        """
        Constructor that initializes an empty Demand table that has three dimensions:
        time, origin taz, destination taz. 
        
        *net* is a dta.Network instance
        *vehClassName* is a string 
        *startTime*, *endTime* and *timeStep* are dta.Utils.Time instancess 
        """
        self._net = net 

        if startTime >= endTime:
            raise DtaError("Start time %s is grater or equal to the end time %s" %
                           startTime, endTime)
        if timeStep.getMinutes() == 0:
            raise DtaError("Time step %s cannot be zero" % timeStep)         

        if ((endTime - startTime) % timeStep) != 0:
            raise DtaError("Demand interval is not divisible by the demand time step") 

        self.startTime = startTime
        self.endTime = endTime
        self.timeStep = timeStep
        self.vehClassName = vehClassName

        self._timePeriods = self._getTimePeriods(startTime, endTime, timeStep)
        self._timeLabels = self._timePeriods # map(self._datetimeToMilitaryTime, self._getTimePeriods(startTime, endTime, timeStep))

        self._centroidIds = sorted([c.getId() for c in net.iterNodes() if c.isCentroid()]) 

        self._demandTable = MultiArray("d", [self._timeLabels, self._centroidIds, self._centroidIds])
                                             
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
        if ((endTime - startTime) % timeStep) != 0:
            raise DtaError("Demand interval is not divisible by the demand time step") 
                           
        result = []
        #TODO: this is interesting. The following line fails
        #time = copy.deepcopy(startTime)
        time = Time(startTime.hour, startTime.minute)
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
                                               
    def setValue(self, timeLabel, origin, destination, value):
        """
        Set the value of the given timeLabel, origin, and destination
        """
        self._demandTable[timeLabel, origin, destination] = value  
    
    def getValue(self, timeLabel, origin, destination):
        """
        Return the value of the given time period, origin, and destination
        """
        return self._demandTable[timeLabel, origin, destination]

    def writeDynameqTable(self, fileName):
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

        timeStepInMin = self.timeStep.getMinutes()

        _npyArray = self._demandTable.getNumpyArray()
        
        for i, timePeriod in enumerate(self._timePeriods):
            outputStream.write("SLICE\n%s\n" % timePeriod.strftime("%H:%M"))
            outputStream.write("\t%s\n" % '\t'.join(map(str, self._centroidIds)))

            for j, cent in enumerate(self._centroidIds):
                #outputStream.write("%d\t%s\n" % (cent, "\t".join("%.2f" % (elem / (60.0 / timeStepInMin)) for elem in _npyArray[i, j, :])))
                outputStream.write("%d\t%s\n" % (cent, "\t".join("%.2f" % elem for elem in _npyArray[i, j, :])))                
                

        outputStream.close()

    def __eq__(self, other):
        """
        Implementation of the == operator. The comparisson of the 
        two demand objects is made using both the data and the labels 
        of the underlying multidimensional arrays. 
        """        
        if self.startTime != other.startTime or self.endTime != other.endTime or \
                self.timeStep != other.timeStep:
            return False 

        if self._timePeriods != other._timePeriods or self._timeLabels != \
                other._timeLabels or self._centroidIds != other._centroidIds:
            return False

        if self.vehClassName != other.vehClassName:
            return False

        if not self._demandTable == other._demandTable:
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
        "TODO: fix the implementation of this method" 
        raise Exception("This is not the correct implementation. Change it") 
        if self.getNumSlices() != 1:
            raise DtaError("Time of day factors can be applied only to a demand that has only"
                           " one time slice") 
            
        if sum(factorsInAList) != 1:
            raise DtaError("The input time of day factors should sum up to 1.0") 
        
        newTimeStepInMin = self.timeStep.getMinutes() / len(factorsInAList)
        newTimeStep = Time.fromMinutes(newTimeStepInMin)
        
        newDemand = Demand(self._net, self.vehClassName, self.startTime, self.endTime, newTimeStep)
        pdb.set_trace() 
        _npyArrayOld = self._demandTable.getNumpyArray() 
        _npyArrayNew = newDemand._demandTable.getNumpyArray()

        for i in range(len(factorsInAList)):            
            _npyArrayNew[i, :, :] = _npyArrayOld[i, :, :] * factorsInAList[i] 

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
                        
    def getTotalNumTrips(self):
        """
        Return the total number of trips for all time periods
        """
        return self._demandTable.getSum() * self.timeStep.getMinutes() / 60.0

