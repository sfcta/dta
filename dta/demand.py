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

import copy
import csv
import la 
import datetime

import numpy as np

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
        if line != Demand.DEFAULT_VEHCLASS:
            raise DtaError("I read a vehicle class other than the default one currently") 
        input.next() #DATA 
        line = input.next().strip()         

        startTime = datetime.datetime.strptime(line, "%H:%M")  
        line = input.next().strip()         
        endTime = datetime.datetime.strptime(line, "%H:%M")
        
        firstSliceLocation = input.tell() 

        line = input.next().strip() #SLICE 
        assert line == "SLICE"        
        line = input.next().strip() # first time slice 
        timeStep1 = datetime.datetime.strptime(line, "%H:%M") 
        timeStep = datetime.timedelta(hours=timeStep1.hour, minutes=timeStep1.minute) 
        demand = Demand(net, startTime, endTime, timeStep)

        for i, timePeriod in enumerate(demand.iterTimePeriods()):

            timeLabel = demand._datetimeToMilitaryTime(timePeriod) 

            if timePeriod != demand.startTime + demand.timeStep: 
                line = input.next().strip()
                assert line == "SLICE"
                line = input.next().strip()            
            destinations = map(int, input.next().strip().split())
            for j, origin in enumerate(range(net.getNumCentroids())):
                fields = map(int, input.next().strip().split()) 
                demand._la[i, j, :] = np.array(fields[1:])

        return demand

    def __init__(self, net, startTime, endTime, timeStep):

        self._net = net 

        self.startTime = startTime
        self.endTime = endTime
        self.timeStep = timeStep

        assert isinstance(timeStep, datetime.timedelta)
        assert isinstance(startTime, datetime.datetime)
        assert isinstance(endTime, datetime.datetime)

        self._timePeriods = self._getTimeLabels(startTime, endTime, timeStep)
        self._timeLabels = map(self._datetimeToMilitaryTime, self._getTimeLabels(startTime, endTime, timeStep))

        self._centroidIds = sorted([c.getId() for c in net.iterNodes() if c.isCentroid()]) 

        array = np.ndarray(shape=(self.getNumSlices(), len(self._centroidIds), len(self._centroidIds)))
        self._la = la.larry(array, [self._timeLabels, self._centroidIds, self._centroidIds], dtype=float)

        self._vehicleClassNames = [vehClass.name for vehClass in self._net.getScenario().iterVehicleClassGroups()]

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
        
    def _getTimeLabels(self, startTime, endTime, timeStep):
        
        assert isinstance(startTime, datetime.datetime)
        assert isinstance(startTime, datetime.datetime)
        assert isinstance(timeStep, datetime.timedelta) 
        assert startTime < endTime

        if (self._timeInMin(endTime) - self._timeInMin(startTime)) % self._timeInMin(timeStep) != 0:
            raise DtaError("Demand interval is not divisible by the demand time step") 
                           
        result = []
        time = copy.deepcopy(startTime)
        while time != endTime:
            time += timeStep
            result.append(time)

        return result 

    def _timeInMin(self, time):
        
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
                               
    def readCubeODTable(self, fileName, fieldNames):
        """
        Reads the demand (linear format) from the input csv file. The fieldNames 
        should correspond to the names of the vehicle classes. 
        """
        
        inputStream = open(fileName, "r")

        for record in csv.DictReader(inputStream):
            
            origin = int(record["ORIGIN"])
            destination = int(record["DESTINATION"])
                       
            for fieldName in fieldNames:
                self.setValue(fieldName, origin, destination, record["fieldName"])

                
    def setValue(self, timePeriod, vehicleClass, origin, destination, value):
        
        pass

    def getValue(self, timePeriod, vehicleClass, origin, destination):
        
        pass
            
       
        

