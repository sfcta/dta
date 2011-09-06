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
    
    def __init__(self, net, timeStepInMin):

        self._net = net 

        self._timePeriods = self._getTimeLabels(net.getScenario().startTime, net.getScenario().endTime, timeStepInMin)
        #self._vehicleClassNames = [vehClass.name for vehicleClass in self.getScenario().iterVehicleClassGroups()]
        #self._centroidIds = sorted([node.getId() for node in net.iterNodes() if node.isCentroid()])

        assert isinstance(timeStepInMin, datetime.timedelta)

        #self._demand = la(self._timePeriods, self._vehicleClassNames, self._centroidIds)
        
    def _getTimeLabels(self, startTime, endTime, timeStep):
        
        assert isinstance(startTime, datetime.datetime)
        assert isinstance(startTime, datetime.datetime)
        assert isinstance(timeStep, datetime.timedelta) 
        assert startTime < endTime

        #if self._timeInMin(startTime) 

        assert (self._timeInMin(endTime) - self._timeInMin(startTime)) % self._timeInMin(timeStep) == 0

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
            


        

